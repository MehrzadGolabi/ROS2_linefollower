#!/usr/bin/env python3
"""
Line Following CV Node - Enhanced Version

Uses OpenCV to detect a black line on white background and 
publishes velocity commands to follow it.

Features:
- Multiple detection points for curve anticipation
- PID control for smooth steering
- Dynamic speed control (slows down at curves)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import TwistStamped
from cv_bridge import CvBridge
import cv2
import time


class LinefollowerCvNode(Node):

    def __init__(self):
        super().__init__('linefollower_cv_node')
        
        # Declare parameters with defaults
        self.declare_parameter('camera_topic', '/camera/depth/image_raw/image')
        self.declare_parameter('cmd_vel_topic', '/joy_vel')
        
        # Speed parameters
        self.declare_parameter('max_linear_speed', 0.1)
        self.declare_parameter('min_linear_speed', 0.05)
        
        # PID gains
        self.declare_parameter('kp', 0.015)  # Proportional gain
        self.declare_parameter('ki', 0.0001)  # Integral gain
        self.declare_parameter('kd', 0.00001)  # Derivative gain
        
        # ROI parameters
        self.declare_parameter('roi_y_start', 300)
        self.declare_parameter('roi_y_end', 480)
        self.declare_parameter('roi_x_start', 120)
        self.declare_parameter('roi_x_end', 520)
        
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
        self.show_debug = self.get_parameter('show_debug_windows').value
        
        # CV Bridge for image conversion
        self.bridge = CvBridge()
        
        # Velocity message (TwistStamped for twist_mux compatibility)
        self.vel_msg = TwistStamped()
        
        # PID state
        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_time = time.time()
        
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
        
        # Apply Canny edge detection
        edged = cv2.Canny(roi, self.canny_low, self.canny_high)
        
        # Multi-point detection
        center_near = self.find_line_center(edged, self.row_near)
        center_mid = self.find_line_center(edged, self.row_mid)
        center_far = self.find_line_center(edged, self.row_far)
        
        # Calculate weighted error from multiple points
        errors = []
        weights = []
        
        if center_near is not None:
            errors.append(self.roi_center_x - center_near)
            weights.append(self.weight_near)
            if self.show_debug:
                cv2.circle(edged, (center_near, self.row_near), 4, 255, 2)
                cv2.line(edged, (self.roi_center_x, self.row_near), 
                        (center_near, self.row_near), 255, 1)
        
        if center_mid is not None:
            errors.append(self.roi_center_x - center_mid)
            weights.append(self.weight_mid)
            if self.show_debug:
                cv2.circle(edged, (center_mid, self.row_mid), 4, 255, 2)
                cv2.line(edged, (self.roi_center_x, self.row_mid), 
                        (center_mid, self.row_mid), 255, 1)
        
        if center_far is not None:
            errors.append(self.roi_center_x - center_far)
            weights.append(self.weight_far)
            if self.show_debug:
                cv2.circle(edged, (center_far, self.row_far), 4, 255, 2)
                cv2.line(edged, (self.roi_center_x, self.row_far), 
                        (center_far, self.row_far), 255, 1)
        
        # Calculate weighted average error
        if errors:
            total_weight = sum(weights)
            error = sum(e * w for e, w in zip(errors, weights)) / total_weight
        else:
            error = 0.0  # No line detected, go straight
        
        # Calculate curve indicator (difference between near and far errors)
        curve_ahead = 0.0
        if center_near is not None and center_far is not None:
            curve_ahead = abs((self.roi_center_x - center_far) - (self.roi_center_x - center_near))
        
        # PID control
        current_time = time.time()
        dt = current_time - self.prev_time
        if dt <= 0:
            dt = 0.033  # Default to ~30Hz
        
        # Proportional
        p_term = self.kp * error
        
        # Integral (with anti-windup)
        self.integral += error * dt
        self.integral = max(-500, min(500, self.integral))  # Clamp integral
        i_term = self.ki * self.integral
        
        # Derivative
        derivative = (error - self.prev_error) / dt
        d_term = self.kd * derivative
        
        # Total angular velocity
        angular_z = p_term + i_term + d_term
        
        # Dynamic speed control
        # Slow down based on: 1) current error, 2) curve ahead
        error_factor = 1.0 - min(abs(error) / (self.roi_width / 2), 0.7)
        curve_factor = 1.0 - min(curve_ahead / (self.roi_width / 3), 0.5)
        speed_factor = min(error_factor, curve_factor)
        
        linear_speed = self.min_speed + (self.max_speed - self.min_speed) * speed_factor
        
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
