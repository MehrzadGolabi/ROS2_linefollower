#!/usr/bin/env python3
"""
Line Following CV Node - Enhanced Version with Edge Case Handling

Uses OpenCV to detect a black line on white background and
publishes velocity commands to follow it.

Features:
- Multiple detection points for curve anticipation
- PID control for smooth steering
- Dynamic speed control (slows down at curves)
- Line gap handling with dead reckoning
- Blurred line handling with adaptive preprocessing
- Cul-de-sac detection and recovery
- Sharp turn detection and handling
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import TwistStamped
from cv_bridge import CvBridge
import cv2
import time
import numpy as np
from enum import Enum


class FollowerState(Enum):
    """State machine for line follower operational modes."""
    NORMAL = 1
    GAP_BRIDGING = 2
    SHARP_TURN = 3
    CUL_DE_SAC_RECOVERY = 4


class LinefollowerCvNode(Node):

    def __init__(self):
        super().__init__('linefollower_cv_node')
        
        # Declare parameters with defaults
        self.declare_parameter('camera_topic', '/camera/image_raw')
        self.declare_parameter('cmd_vel_topic', '/joy_vel')
        
        # Speed parameters
        self.declare_parameter('max_linear_speed', 0.2)
        self.declare_parameter('min_linear_speed', 0.05)
        
        # PID gains
        self.declare_parameter('kp', 0.01)  # Proportional gain
        self.declare_parameter('ki', 0.0001)  # Integral gain
        self.declare_parameter('kd', 0.05)  # Derivative gain
        
        # ROI parameters
        self.declare_parameter('roi_y_start', 150)
        self.declare_parameter('roi_y_end', 240)
        self.declare_parameter('roi_x_start', 60)
        self.declare_parameter('roi_x_end', 260)
        
        # Multi-point detection rows (percentage of ROI height from top)
        # Near = close to robot, Far = looking ahead
        self.declare_parameter('detection_row_near', 0.85)   # 85% down (close)
        self.declare_parameter('detection_row_mid', 0.60)    # 60% down (middle)
        self.declare_parameter('detection_row_far', 0.35)    # 35% down (far/lookahead)
        
        # Weights for multi-point detection
        self.declare_parameter('weight_near', 0.5)
        self.declare_parameter('weight_mid', 0.3)
        self.declare_parameter('weight_far', 0.2)
        
        # Edge detection
        self.declare_parameter('canny_threshold_low', 50)
        self.declare_parameter('canny_threshold_high', 150)

        # Gap handling parameters
        self.declare_parameter('enable_gap_bridging', True)
        self.declare_parameter('max_gap_frames', 10)
        self.declare_parameter('gap_confidence_decay', 0.95)
        self.declare_parameter('gap_recovery_smoothing', 0.7)

        # Preprocessing parameters
        self.declare_parameter('enable_preprocessing', True)
        self.declare_parameter('blur_kernel_size', 5)
        self.declare_parameter('use_clahe', True)
        self.declare_parameter('clahe_clip_limit', 2.0)
        self.declare_parameter('clahe_tile_grid_size', 8)
        self.declare_parameter('use_adaptive_canny', True)
        self.declare_parameter('adaptive_canny_sigma', 0.33)
        self.declare_parameter('use_morphology', False)
        self.declare_parameter('morph_kernel_size', 5)
        self.declare_parameter('morph_op_type', 'close')
        self.declare_parameter('morph_iterations', 1)
        self.declare_parameter('morph_apply_after_canny', True)

        # Sharp turn detection parameters
        self.declare_parameter('enable_sharp_turn_detection', True)
        self.declare_parameter('sharp_turn_threshold', 0.4)
        self.declare_parameter('sharp_turn_exit_threshold', 0.2)
        self.declare_parameter('sharp_turn_min_speed', 0.03)
        self.declare_parameter('sharp_turn_kp_multiplier', 1.5)
        self.declare_parameter('sharp_turn_anticipation', 0.1)

        # Cul-de-sac detection parameters
        self.declare_parameter('enable_cul_de_sac_detection', True)
        self.declare_parameter('cul_de_sac_confidence_frames', 5)
        self.declare_parameter('cul_de_sac_turn_speed', 0.3)
        self.declare_parameter('cul_de_sac_behavior', 'rotate_in_place')
        self.declare_parameter('cul_de_sac_edge_threshold', 10)
        self.declare_parameter('cul_de_sac_center_threshold', 5)

        # Debug
        self.declare_parameter('show_debug_windows', True)
        
        # Get parameter values
        camera_topic = self.get_parameter('camera_topic').value
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.max_speed = self.get_parameter('max_linear_speed').value
        self.min_speed = self.get_parameter('min_linear_speed').value
        self.kp = self.get_parameter('kp').value
        self.ki = self.get_parameter('ki').value
        self.kd = self.get_parameter('kd').value
        self.roi_y_start = self.get_parameter('roi_y_start').value
        self.roi_y_end = self.get_parameter('roi_y_end').value
        self.roi_x_start = self.get_parameter('roi_x_start').value
        self.roi_x_end = self.get_parameter('roi_x_end').value
        self.row_near_pct = self.get_parameter('detection_row_near').value
        self.row_mid_pct = self.get_parameter('detection_row_mid').value
        self.row_far_pct = self.get_parameter('detection_row_far').value
        self.weight_near = self.get_parameter('weight_near').value
        self.weight_mid = self.get_parameter('weight_mid').value
        self.weight_far = self.get_parameter('weight_far').value
        self.canny_low = self.get_parameter('canny_threshold_low').value
        self.canny_high = self.get_parameter('canny_threshold_high').value

        # Gap handling parameters
        self.enable_gap_bridging = self.get_parameter('enable_gap_bridging').value
        self.max_gap_frames = self.get_parameter('max_gap_frames').value
        self.gap_confidence_decay = self.get_parameter('gap_confidence_decay').value
        self.gap_recovery_smoothing = self.get_parameter('gap_recovery_smoothing').value

        # Preprocessing parameters
        self.enable_preprocessing = self.get_parameter('enable_preprocessing').value
        self.blur_kernel_size = self.get_parameter('blur_kernel_size').value
        self.use_clahe = self.get_parameter('use_clahe').value
        self.clahe_clip_limit = self.get_parameter('clahe_clip_limit').value
        self.clahe_tile_grid_size = self.get_parameter('clahe_tile_grid_size').value
        self.use_adaptive_canny = self.get_parameter('use_adaptive_canny').value
        self.adaptive_canny_sigma = self.get_parameter('adaptive_canny_sigma').value
        self.use_morphology = self.get_parameter('use_morphology').value
        self.morph_kernel_size = self.get_parameter('morph_kernel_size').value
        self.morph_op_type = self.get_parameter('morph_op_type').value
        self.morph_iterations = self.get_parameter('morph_iterations').value
        self.morph_apply_after_canny = self.get_parameter('morph_apply_after_canny').value

        # Sharp turn parameters
        self.enable_sharp_turn = self.get_parameter('enable_sharp_turn_detection').value
        self.sharp_turn_threshold = self.get_parameter('sharp_turn_threshold').value
        self.sharp_turn_exit_threshold = self.get_parameter('sharp_turn_exit_threshold').value
        self.sharp_turn_min_speed = self.get_parameter('sharp_turn_min_speed').value
        self.sharp_turn_kp_mult = self.get_parameter('sharp_turn_kp_multiplier').value
        self.sharp_turn_anticipation = self.get_parameter('sharp_turn_anticipation').value

        # Cul-de-sac parameters
        self.enable_cul_de_sac = self.get_parameter('enable_cul_de_sac_detection').value
        self.cul_de_sac_conf_frames = self.get_parameter('cul_de_sac_confidence_frames').value
        self.cul_de_sac_turn_speed = self.get_parameter('cul_de_sac_turn_speed').value
        self.cul_de_sac_behavior = self.get_parameter('cul_de_sac_behavior').value
        self.cul_de_sac_edge_thresh = self.get_parameter('cul_de_sac_edge_threshold').value
        self.cul_de_sac_center_thresh = self.get_parameter('cul_de_sac_center_threshold').value

        self.show_debug = self.get_parameter('show_debug_windows').value
        
        # CV Bridge for image conversion
        self.bridge = CvBridge()
        
        # Velocity message (TwistStamped for twist_mux compatibility)
        self.vel_msg = TwistStamped()
        self.vel_msg.header.frame_id = 'base_link'
        
        # PID state
        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_time = time.time()

        # State machine
        self.current_state = FollowerState.NORMAL

        # Gap handling state
        self.last_valid_error = 0.0
        self.frames_since_last_detection = 0
        self.smoothed_error = 0.0

        # Sharp turn state
        self.sharp_turn_active = False
        self.sharp_turn_direction = 0  # -1 for left, 1 for right

        # Cul-de-sac state
        self.cul_de_sac_counter = 0
        self.cul_de_sac_recovery_active = False
        self.cul_de_sac_recovery_start_time = None

        # CLAHE object (create once for efficiency)
        if self.use_clahe:
            self.clahe = cv2.createCLAHE(
                clipLimit=self.clahe_clip_limit,
                tileGridSize=(self.clahe_tile_grid_size, self.clahe_tile_grid_size)
            )
        else:
            self.clahe = None

        # Morphology kernel
        if self.use_morphology:
            self.morph_kernel = np.ones(
                (self.morph_kernel_size, self.morph_kernel_size),
                np.uint8
            )
        else:
            self.morph_kernel = None
        
        # Create subscriber and publisher
        self.camera_sub = self.create_subscription(
            Image,
            camera_topic,
            self.camera_callback,
            10
        )
        
        self.cmd_vel_pub = self.create_publisher(
            TwistStamped,
            cmd_vel_topic,
            10
        )
        
        # Calculate ROI dimensions
        self.roi_width = self.roi_x_end - self.roi_x_start
        self.roi_height = self.roi_y_end - self.roi_y_start
        self.roi_center_x = self.roi_width // 2
        
        # Calculate detection row positions
        self.row_near = int(self.roi_height * self.row_near_pct)
        self.row_mid = int(self.roi_height * self.row_mid_pct)
        self.row_far = int(self.roi_height * self.row_far_pct)
        
        self.get_logger().info(f'Enhanced Line Follower started!')
        self.get_logger().info(f'  Camera: {camera_topic}')
        self.get_logger().info(f'  Cmd vel: {cmd_vel_topic}')
        self.get_logger().info(f'  PID: Kp={self.kp}, Ki={self.ki}, Kd={self.kd}')
        self.get_logger().info(f'  Speed range: {self.min_speed} - {self.max_speed}')
        self.get_logger().info(f'  Detection rows: near={self.row_near}, mid={self.row_mid}, far={self.row_far}')

    def preprocess_image(self, roi):
        """Apply preprocessing pipeline for robust edge detection.

        Args:
            roi: Input ROI image (BGR format)

        Returns:
            Preprocessed grayscale image ready for Canny edge detection
        """
        if not self.enable_preprocessing:
            # Just convert to grayscale if preprocessing disabled
            return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (self.blur_kernel_size, self.blur_kernel_size), 0)

        # Apply CLAHE for contrast enhancement
        if self.use_clahe and self.clahe is not None:
            enhanced = self.clahe.apply(blurred)
        else:
            enhanced = blurred

        # Apply morphological operations if enabled
        if self.use_morphology and self.morph_kernel is not None:
            # Otsu's thresholding
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Morphological closing to fill gaps
            enhanced = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, self.morph_kernel)

        return enhanced

    def adaptive_canny_thresholds(self, image):
        """Calculate adaptive Canny thresholds based on image statistics.

        Args:
            image: Grayscale image

        Returns:
            Tuple of (low_threshold, high_threshold)
        """
        if not self.use_adaptive_canny:
            return self.canny_low, self.canny_high

        # Calculate median pixel value
        median_intensity = np.median(image)

        # Compute adaptive thresholds
        sigma = self.adaptive_canny_sigma
        low = int(max(0, (1.0 - sigma) * median_intensity))
        high = int(min(255, (1.0 + sigma) * median_intensity))

        return low, high

    def update_line_memory(self, error, line_detected):
        """Update line memory for gap bridging.

        Args:
            error: Current error value
            line_detected: Boolean indicating if line was detected
        """
        if line_detected:
            # Update smoothed error with exponential moving average
            alpha = self.gap_recovery_smoothing
            self.smoothed_error = alpha * error + (1 - alpha) * self.smoothed_error
            self.last_valid_error = self.smoothed_error
            self.frames_since_last_detection = 0
        else:
            self.frames_since_last_detection += 1

    def handle_line_gap(self):
        """Apply dead reckoning when line is lost.

        Returns:
            Tuple of (error, speed_factor) to use during gap
        """
        if self.frames_since_last_detection <= self.max_gap_frames:
            # Use last known error with decaying confidence
            decay = self.gap_confidence_decay ** self.frames_since_last_detection
            error = self.last_valid_error
            speed_factor = decay
            return error, speed_factor
        else:
            # Gap too long, stop and search
            return 0.0, 0.0

    def detect_sharp_turn(self, center_near, center_far):
        """Detect sharp turns based on lateral deviation.

        Args:
            center_near: Line center at near detection point
            center_far: Line center at far detection point

        Returns:
            Tuple of (is_sharp_turn, turn_direction)
            turn_direction: +1 for left (positive angular_z), -1 for right (negative angular_z), 0 for none
        """
        if not self.enable_sharp_turn:
            return False, 0

        if center_near is None or center_far is None:
            return False, 0

        # Calculate lateral deviation
        lateral_deviation = abs(center_far - center_near)
        normalized_deviation = lateral_deviation / self.roi_width

        # Check if sharp turn
        if normalized_deviation > self.sharp_turn_threshold:
            # IMPORTANT: ROS convention: positive angular_z = LEFT turn (CCW)
            # If center_far < center_near, line is curving LEFT, need positive angular_z
            # So: LEFT turn = +1, RIGHT turn = -1
            turn_direction = 1 if center_far < center_near else -1
            return True, turn_direction
        elif self.sharp_turn_active and normalized_deviation < self.sharp_turn_exit_threshold:
            # Exit sharp turn mode
            self.sharp_turn_active = False
            return False, 0

        return self.sharp_turn_active, self.sharp_turn_direction

    def apply_sharp_turn_control(self, base_speed, base_kp):
        """Modify control parameters for sharp turns.

        Args:
            base_speed: Base linear speed
            base_kp: Base Kp gain

        Returns:
            Tuple of (modified_speed, modified_kp, weight_near, weight_mid, weight_far)
        """
        if self.sharp_turn_active:
            # Aggressive speed reduction
            speed = max(self.sharp_turn_min_speed, base_speed * 0.3)
            # Increase PID gain
            kp = base_kp * self.sharp_turn_kp_mult
            # Weight near point more heavily
            return speed, kp, 0.8, 0.15, 0.05
        else:
            # Normal weights
            return base_speed, base_kp, self.weight_near, self.weight_mid, self.weight_far

    def detect_cul_de_sac(self, edged):
        """Detect U-shaped cul-de-sac pattern.

        Args:
            edged: Edge-detected image

        Returns:
            Boolean indicating if cul-de-sac detected
        """
        if not self.enable_cul_de_sac:
            return False

        # Check at near row (close to robot)
        row = self.row_near
        if row >= edged.shape[0]:
            return False

        roi_width = edged.shape[1]

        # Count white pixels on left edge
        left_edge = edged[row, 0:int(roi_width * 0.2)]
        left_count = np.sum(left_edge == 255)

        # Count white pixels on right edge
        right_edge = edged[row, int(roi_width * 0.8):roi_width]
        right_count = np.sum(right_edge == 255)

        # Count white pixels in center
        center = edged[row, int(roi_width * 0.3):int(roi_width * 0.7)]
        center_count = np.sum(center == 255)

        # Cul-de-sac if strong edges on both sides, empty center
        is_cul_de_sac = (
            left_count > self.cul_de_sac_edge_thresh and
            right_count > self.cul_de_sac_edge_thresh and
            center_count < self.cul_de_sac_center_thresh
        )

        # Require consecutive frames for confirmation
        if is_cul_de_sac:
            self.cul_de_sac_counter += 1
            if self.cul_de_sac_counter >= self.cul_de_sac_conf_frames:
                return True
        else:
            self.cul_de_sac_counter = 0

        return False

    def execute_cul_de_sac_recovery(self):
        """Execute recovery maneuver for cul-de-sac.

        Returns:
            Tuple of (linear_speed, angular_speed) for recovery
        """
        if not self.cul_de_sac_recovery_active:
            # Start recovery
            self.cul_de_sac_recovery_active = True
            self.cul_de_sac_recovery_start_time = time.time()
            self.get_logger().info('Cul-de-sac detected! Starting recovery...')

        elapsed = time.time() - self.cul_de_sac_recovery_start_time

        if self.cul_de_sac_behavior == 'rotate_in_place':
            # Rotate in place 180 degrees
            # At angular speed of 0.3 rad/s, 180° (π rad) takes ~10.5 seconds
            if elapsed < 10.5:
                return 0.0, self.cul_de_sac_turn_speed
            else:
                # Recovery complete
                self.cul_de_sac_recovery_active = False
                self.cul_de_sac_counter = 0
                self.current_state = FollowerState.NORMAL
                self.get_logger().info('Cul-de-sac recovery complete!')
                return 0.0, 0.0
        else:
            # Three-point turn (simplified: reverse, rotate, forward)
            if elapsed < 2.0:
                # Reverse
                return -0.05, 0.0
            elif elapsed < 12.5:
                # Rotate 180°
                return 0.0, self.cul_de_sac_turn_speed
            else:
                # Recovery complete
                self.cul_de_sac_recovery_active = False
                self.cul_de_sac_counter = 0
                self.current_state = FollowerState.NORMAL
                self.get_logger().info('Cul-de-sac recovery complete!')
                return 0.0, 0.0

    def find_line_center(self, edged, row):
        """Find the center of the line at a specific row."""
        if row >= edged.shape[0] or row < 0:
            return None

        white_indices = []
        for index, value in enumerate(edged[row]):
            if value == 255:
                white_indices.append(index)

        if len(white_indices) >= 2:
            # Return center between first and last edge
            return (white_indices[0] + white_indices[-1]) // 2
        elif len(white_indices) == 1:
            # Only one edge found, use it as reference
            return white_indices[0]
        return None

    def camera_callback(self, msg):
        """Process camera image and publish velocity commands."""
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            return

        # Extract Region of Interest
        roi = frame[self.roi_y_start:self.roi_y_end,
                    self.roi_x_start:self.roi_x_end]

        if roi.size == 0:
            self.get_logger().warn('Empty ROI! Check camera resolution and parameters.')
            return

        # Handle cul-de-sac recovery state
        if self.current_state == FollowerState.CUL_DE_SAC_RECOVERY:
            linear, angular = self.execute_cul_de_sac_recovery()
            self.vel_msg.header.stamp = self.get_clock().now().to_msg()
            self.vel_msg.twist.linear.x = linear
            self.vel_msg.twist.angular.z = angular
            self.cmd_vel_pub.publish(self.vel_msg)
            return

        # Preprocess image
        preprocessed = self.preprocess_image(roi)

        # Apply Canny edge detection with adaptive thresholds
        canny_low, canny_high = self.adaptive_canny_thresholds(preprocessed)
        edged = cv2.Canny(preprocessed, canny_low, canny_high)
        
        # Check for cul-de-sac before normal line detection
        if self.detect_cul_de_sac(edged):
            self.current_state = FollowerState.CUL_DE_SAC_RECOVERY
            self.get_logger().info('Cul-de-sac detected!')
            return

        # Multi-point detection
        center_near = self.find_line_center(edged, self.row_near)
        center_mid = self.find_line_center(edged, self.row_mid)
        center_far = self.find_line_center(edged, self.row_far)

        # Debug: Log detection point values
        if center_near is not None and center_far is not None:
            lateral_dev = abs(center_far - center_near)
            norm_dev = lateral_dev / self.roi_width if self.roi_width > 0 else 0
            self.get_logger().info(
                f'Detection: near={center_near}, far={center_far}, '
                f'deviation={norm_dev:.3f}, threshold={self.sharp_turn_threshold}',
                throttle_duration_sec=1.0
            )

        # Detect sharp turn
        is_sharp_turn, turn_direction = self.detect_sharp_turn(center_near, center_far)
        if is_sharp_turn and not self.sharp_turn_active:
            self.sharp_turn_active = True
            self.sharp_turn_direction = turn_direction
            self.current_state = FollowerState.SHARP_TURN
            self.get_logger().info(f'Sharp turn detected: {"left" if turn_direction > 0 else "right"}')
        elif not is_sharp_turn and self.sharp_turn_active:
            # Exit sharp turn mode - reset all flags
            self.sharp_turn_active = False
            self.sharp_turn_direction = 0
            self.current_state = FollowerState.NORMAL
            self.get_logger().info('Sharp turn complete, returning to normal')

        # Get dynamic weights based on state
        _, _, weight_near, weight_mid, weight_far = self.apply_sharp_turn_control(
            self.max_speed, self.kp
        )

        # Calculate weighted error from multiple points
        errors = []
        weights = []

        if center_near is not None:
            errors.append(self.roi_center_x - center_near)
            weights.append(weight_near)
            if self.show_debug:
                cv2.circle(edged, (center_near, self.row_near), 4, 255, 2)
                cv2.line(edged, (self.roi_center_x, self.row_near),
                        (center_near, self.row_near), 255, 1)

        if center_mid is not None:
            errors.append(self.roi_center_x - center_mid)
            weights.append(weight_mid)
            if self.show_debug:
                cv2.circle(edged, (center_mid, self.row_mid), 4, 255, 2)
                cv2.line(edged, (self.roi_center_x, self.row_mid),
                        (center_mid, self.row_mid), 255, 1)

        if center_far is not None:
            errors.append(self.roi_center_x - center_far)
            weights.append(weight_far)
            if self.show_debug:
                cv2.circle(edged, (center_far, self.row_far), 4, 255, 2)
                cv2.line(edged, (self.roi_center_x, self.row_far),
                        (center_far, self.row_far), 255, 1)

        # Calculate weighted average error
        line_detected = len(errors) > 0
        gap_speed_factor = 1.0  # Default: no gap reduction

        if line_detected:
            total_weight = sum(weights)
            error = sum(e * w for e, w in zip(errors, weights)) / total_weight
            # If we were in gap bridging, return to normal
            if self.current_state == FollowerState.GAP_BRIDGING:
                self.current_state = FollowerState.NORMAL
                self.get_logger().info('Line recovered, returning to normal')
        else:
            # No line detected - handle gap
            if self.enable_gap_bridging:
                error, gap_speed_factor = self.handle_line_gap()
                self.current_state = FollowerState.GAP_BRIDGING
                # Clear sharp turn state when entering gap
                if self.sharp_turn_active:
                    self.sharp_turn_active = False
                    self.sharp_turn_direction = 0
                    self.get_logger().info('Gap detected, clearing sharp turn state')
            else:
                error = 0.0
                gap_speed_factor = 0.0

        # Update line memory
        self.update_line_memory(error, line_detected)

        # Calculate curve indicator (difference between near and far errors)
        curve_ahead = 0.0
        if center_near is not None and center_far is not None:
            curve_ahead = abs((self.roi_center_x - center_far) - (self.roi_center_x - center_near))
        
        # PID control
        current_time = time.time()
        dt = current_time - self.prev_time
        if dt <= 0:
            dt = 0.033  # Default to ~30Hz

        # Get modified Kp for sharp turns
        _, effective_kp, _, _, _ = self.apply_sharp_turn_control(self.max_speed, self.kp)

        # Proportional
        p_term = effective_kp * error

        # Integral (with anti-windup)
        self.integral += error * dt
        self.integral = max(-500, min(500, self.integral))  # Clamp integral
        i_term = self.ki * self.integral

        # Derivative
        derivative = (error - self.prev_error) / dt
        d_term = self.kd * derivative

        # Total angular velocity
        angular_z = p_term + i_term + d_term

        # Add turn anticipation for sharp turns
        if self.sharp_turn_active:
            angular_z += self.sharp_turn_anticipation * self.sharp_turn_direction

        # Dynamic speed control
        # Slow down based on: 1) current error, 2) curve ahead
        error_factor = 1.0 - min(abs(error) / (self.roi_width / 2), 0.7)
        curve_factor = 1.0 - min(curve_ahead / (self.roi_width / 3), 0.5)
        speed_factor = min(error_factor, curve_factor)

        # Apply gap speed reduction if in gap bridging mode
        if self.current_state == FollowerState.GAP_BRIDGING:
            speed_factor *= gap_speed_factor

        linear_speed = self.min_speed + (self.max_speed - self.min_speed) * speed_factor

        # Apply sharp turn speed limit
        if self.sharp_turn_active:
            sharp_turn_speed, _, _, _, _ = self.apply_sharp_turn_control(linear_speed, self.kp)
            linear_speed = sharp_turn_speed
        
        # Update PID state
        self.prev_error = error
        self.prev_time = current_time
        
        # Publish velocity command
        self.vel_msg.header.stamp = self.get_clock().now().to_msg()
        self.vel_msg.twist.linear.x = linear_speed
        self.vel_msg.twist.angular.z = float(angular_z)
        self.cmd_vel_pub.publish(self.vel_msg)
        
        # Debug visualization
        if self.show_debug:
            # Draw center reference line
            cv2.line(edged, (self.roi_center_x, 0),
                    (self.roi_center_x, self.roi_height), 128, 1)

            # Draw detection rows
            cv2.line(edged, (0, self.row_near), (self.roi_width, self.row_near), 128, 1)
            cv2.line(edged, (0, self.row_mid), (self.roi_width, self.row_mid), 128, 1)
            cv2.line(edged, (0, self.row_far), (self.roi_width, self.row_far), 128, 1)

            # Add text info
            cv2.putText(roi, f'Err: {error:.1f}', (10, 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(roi, f'Spd: {linear_speed:.2f}', (10, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(roi, f'Ang: {angular_z:.3f}', (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(roi, f'State: {self.current_state.name}', (10, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Show gap frames if in gap bridging
            if self.current_state == FollowerState.GAP_BRIDGING:
                cv2.putText(roi, f'Gap: {self.frames_since_last_detection}/{self.max_gap_frames}',
                           (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            cv2.imshow('ROI', roi)
            cv2.imshow('Edge Detection', edged)
            cv2.waitKey(1)

    def destroy_node(self):
        """Clean up on shutdown."""
        self.vel_msg.header.stamp = self.get_clock().now().to_msg()
        self.vel_msg.twist.linear.x = 0.0
        self.vel_msg.twist.angular.z = 0.0
        self.cmd_vel_pub.publish(self.vel_msg)
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = LinefollowerCvNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
