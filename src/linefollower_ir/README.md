# linefollower_ir

A ROS 2 package for line following using a 5-array IR sensor.

## Nodes

### linefollower_ir_node

Subscribes to raw IR sensor data and publishes velocity commands.

#### Subscribed Topics

*   `/ir_sensors` (`std_msgs/msg/String`): The raw sensor string (e.g., "11011"). '0' indicates line detected, '1' indicates background.

#### Published Topics

*   `/joy_vel` (`geometry_msgs/msg/TwistStamped`): Velocity commands.

#### Parameters

*   `linear_speed` (double, default: 0.2): Forward speed.
*   `angular_speed` (double, default: 1.0): Turning speed.
*   `recovery_speed` (double, default: 0.5): Not currently used.

## Usage

Launch via `linebot` launch files:
```bash
ros2 launch linebot robot.launch.py mode:=ir
```
