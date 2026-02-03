# Linefollower CV

The `linefollower_cv` package provides a computer vision-based line following capability using OpenCV. It processes camera images to detect a black line on a white background and publishes velocity commands to navigate the robot.

## Node: `linefollower_cv_node`

This node implements the core logic for visual line following.

### Features
*   **Multi-point Detection**: Uses three detection rows (near, mid, far) to calculate error and anticipate curves.
*   **PID Control**: Implements a PID controller for smooth steering corrections.
*   **Dynamic Speed Control**: Adjusts linear speed based on current error and upcoming curves (slows down when turning).
*   **Debug Visualization**: Optional display of the processed image with overlays for tuning.

### Subscribed Topics

*   `camera_topic` (sensor_msgs/Image): The input video stream from the robot's camera.
    *   Default: `/camera/image_raw`

### Published Topics

*   `cmd_vel_topic` (geometry_msgs/TwistStamped): Velocity commands for the robot base.
    *   Default: `/joy_vel`

### Parameters

#### General
*   `camera_topic` (string): Topic name for camera subscription.
*   `cmd_vel_topic` (string): Topic name for velocity publication.
*   `show_debug_windows` (bool): If true, opens OpenCV windows showing the ROI and edge detection result. Default: `True`.

#### Speed Control
*   `max_linear_speed` (double): Maximum forward speed (m/s) on straight paths. Default: `0.4`.
*   `min_linear_speed` (double): Minimum forward speed (m/s) during sharp turns. Default: `0.15`.

#### PID Controller
*   `kp` (double): Proportional gain. Default: `0.03`.
*   `ki` (double): Integral gain. Default: `0.0001`.
*   `kd` (double): Derivative gain. Default: `0.016`.

#### Region of Interest (ROI)
Defines the rectangular area of the image to process.
*   `roi_y_start` (int): Top Y coordinate. Default: `150`.
*   `roi_y_end` (int): Bottom Y coordinate. Default: `240`.
*   `roi_x_start` (int): Left X coordinate. Default: `60`.
*   `roi_x_end` (int): Right X coordinate. Default: `260`.

#### Detection Configuration
*   `detection_row_near` (double): "Near" detection row as a percentage of ROI height (from top). Default: `0.85`.
*   `detection_row_mid` (double): "Middle" detection row. Default: `0.60`.
*   `detection_row_far` (double): "Far" detection row. Default: `0.35`.
*   `weight_near` (double): Weight influence of the near point. Default: `0.5`.
*   `weight_mid` (double): Weight influence of the mid point. Default: `0.3`.
*   `weight_far` (double): Weight influence of the far point. Default: `0.2`.
*   `canny_threshold_low` (int): Lower threshold for Canny edge detector. Default: `50`.
*   `canny_threshold_high` (int): Upper threshold for Canny edge detector. Default: `150`.

## Algorithm Details

1.  **Image Preprocessing**: The input image is cropped to the configured ROI.
2.  **Edge Detection**: Canny edge detection is applied to find high-contrast boundaries (the line edges).
3.  **Center Finding**: The algorithm scans three specific rows (near, mid, far) to find the center of the line (midpoint between two edges).
4.  **Error Calculation**: A weighted average error is calculated based on the deviation of the line center from the image center at the three rows.
5.  **Control Output**:
    *   **Angular Velocity**: Computed using the PID controller based on the weighted error.
    *   **Linear Velocity**: Reduced dynamically if the error is large or if a sharp curve is detected ahead (difference between near and far centers).
