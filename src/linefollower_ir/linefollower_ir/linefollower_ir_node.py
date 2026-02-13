#!/usr/bin/env python3

"""
Node for IR-based line following.

This node subscribes to IR sensor data and publishes velocity commands
to steer the robot along a line.
"""

from geometry_msgs.msg import TwistStamped

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class LinefollowerIrNode(Node):
    """
    ROS 2 node for IR line following.

    Maps 5-bit IR sensor patterns to differential drive velocity commands.
    """

    def __init__(self):
        """Initialize parameters, subscribers, and publishers."""
        super().__init__('linefollower_ir_node')

        # Parameters
        self.declare_parameter('linear_speed', 0.2)
        self.declare_parameter('angular_speed', 1.0)
        # New parameter for stiction
        self.declare_parameter('min_turn_speed', 0.08)
        self.declare_parameter('min_turn_duration', 0.5)

        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.min_turn_speed = self.get_parameter('min_turn_speed').value
        self.min_turn_duration = self.get_parameter('min_turn_duration').value

        # State for committed turns
        self.is_hard_turning = False
        self.turn_start_time = None
        self.hard_turn_angular_z = 0.0

        # Subscribers and Publishers
        self.ir_sub = self.create_subscription(
            String, '/ir_sensors', self.ir_callback, 10)
        self.cmd_vel_pub = self.create_publisher(
            TwistStamped, '/joy_vel', 10)

        self.get_logger().info('IR Line Follower Node Started (Revised Logic)')

    def ir_callback(self, msg):
        """
        Process IR sensor data and publish velocity commands.

        :param msg: String message containing IR sensor states.
        """
        ir_data = msg.data.strip()

        # Normalize IR data to 5-bit binary string
        if ir_data.isdigit() and len(ir_data) < 5:
            try:
                val = int(ir_data)
                ir_str = format(val, '05b')
            except ValueError:
                ir_str = ir_data
        else:
            ir_str = ir_data

        if len(ir_str) != 5:
            # Handle unexpected data length
            self.get_logger().warn(f'Invalid IR data length: {ir_str}')
            return

        twist = TwistStamped()
        twist.header.stamp = self.get_clock().now().to_msg()
        twist.header.frame_id = 'base_link'

        linear_x = 0.0
        angular_z = 0.0

        # Check for committed turn
        if self.is_hard_turning:
            elapsed = (self.get_clock().now() - self.turn_start_time).nanoseconds / 1e9
            if elapsed < self.min_turn_duration:
                # Still committed by time
                linear_x = self.min_turn_speed
                angular_z = self.hard_turn_angular_z
            elif ir_str == '11011':
                # Time passed AND center detected: exit commitment
                self.is_hard_turning = False
                self.get_logger().info('Committed turn completed')
            else:
                # Time passed but center not yet detected: maintain turn
                linear_x = self.min_turn_speed
                angular_z = self.hard_turn_angular_z

        # If not (or no longer) hard turning, process patterns
        if not self.is_hard_turning:
            # Mapping: '0' = Line (Black), '1' = Background (White)
            # SENSORS: [Left2, Left1, Center, Right1, Right2]

            if ir_str == '11011':
                # Perfectly Centered
                linear_x = self.linear_speed
                angular_z = 0.0

            elif ir_str in ['10011', '10111']:
                # Slight Left Offset -> Turn Left
                linear_x = max(self.linear_speed * 0.75, self.min_turn_speed)
                angular_z = self.angular_speed * 0.4

            elif ir_str in ['00111', '01111', '00011', '00110']:
                # Strong Left Offset -> Hard Left
                linear_x = self.min_turn_speed
                angular_z = self.angular_speed * 0.8
                # Enter commitment
                self.is_hard_turning = True
                self.turn_start_time = self.get_clock().now()
                self.hard_turn_angular_z = angular_z
                self.get_logger().info(f'Entering committed Hard Left (IR: {ir_str})')

            elif ir_str in ['11001', '11101']:
                # Slight Right Offset -> Turn Right
                linear_x = max(self.linear_speed * 0.75, self.min_turn_speed)
                angular_z = -self.angular_speed * 0.4

            elif ir_str in ['11100', '11110', '11000', '01100']:
                # Strong Right Offset -> Hard Right
                linear_x = self.min_turn_speed
                angular_z = -self.angular_speed * 0.8
                # Enter commitment
                self.is_hard_turning = True
                self.turn_start_time = self.get_clock().now()
                self.hard_turn_angular_z = angular_z
                self.get_logger().info(f'Entering committed Hard Right (IR: {ir_str})')

            elif ir_str in ['00000', '01010', '10101']:
                # Full line or confusing pattern: move slowly forward
                linear_x = self.min_turn_speed
                angular_z = 0.0

            elif ir_str == '11111':
                # No line detected: Stop or slow search
                linear_x = self.min_turn_speed
                angular_z = 0.0
                self.get_logger().debug('Line lost')

            else:
                # Any other case (multiple sensors but not centered)
                # Try to infer direction based on which side has more '0's
                zeros_left = ir_str[:2].count('0')
                zeros_right = ir_str[3:].count('0')

                if zeros_left > zeros_right:
                    linear_x = self.min_turn_speed
                    angular_z = self.angular_speed * 0.6
                elif zeros_right > zeros_left:
                    linear_x = self.min_turn_speed
                    angular_z = -self.angular_speed * 0.6
                else:
                    linear_x = 0.0
                    angular_z = 0.0

        twist.twist.linear.x = linear_x
        twist.twist.angular.z = angular_z

        self.cmd_vel_pub.publish(twist)
        self.get_logger().info(
            f'IR: {ir_str} -> L: {linear_x:.2f}, A: {angular_z:.2f}',
            throttle_duration_sec=0.5)


def main(args=None):
    """Initialize and spin the node."""
    rclpy.init(args=args)
    node = LinefollowerIrNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()