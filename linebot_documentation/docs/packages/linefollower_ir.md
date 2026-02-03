# Linefollower IR

The `linefollower_ir` package implements a state-machine-based line follower using a 5-channel Infrared (IR) sensor array. It is designed for high-reliability navigation by reacting to discrete sensor states.

## Node: `linefollower_ir_node`

This node subscribes to the raw sensor data and publishes velocity commands.

### Subscribed Topics

*   `/ir_sensors` (std_msgs/String): A string representing the state of the 5 IR sensors.
    *   Format: A 5-character string of '0's and '1's (e.g., "11011").
    *   '0': Line detected (black).
    *   '1': Background detected (white).

### Published Topics

*   `/joy_vel` (geometry_msgs/TwistStamped): Velocity commands for the robot base.

### Parameters

*   `linear_speed` (double): The base forward speed (m/s). Default: `0.2`.
*   `angular_speed` (double): The base turning speed (rad/s). Default: `1.0`.

## Logic and States

The node interprets the 5-bit sensor pattern to determine the robot's position relative to the line.

| Sensor Pattern | Action | Linear Speed | Angular Speed |
| :--- | :--- | :--- | :--- |
| `11011` | **Forward**: Center sensor is on the line. | `linear_speed` | 0.0 |
| `10011`, `10111` | **Turn Left**: Slight deviation to the right. | `0.5 * linear_speed` | `0.5 * angular_speed` |
| `00011`, `00111`, `01111` | **Hard Left**: Significant deviation to the right. | `0.05` | `angular_speed` |
| `11001`, `11101` | **Turn Right**: Slight deviation to the left. | `0.5 * linear_speed` | `-0.5 * angular_speed` |
| `11100`, `11110`, `11000` | **Hard Right**: Significant deviation to the left. | `0.05` | `-angular_speed` |
| `11111` | **Search/Lost**: No line detected. | `0.2` | `0.2` (Slow turn) |
| *Other* | **Stop**: Unknown state. | 0.0 | 0.0 |
