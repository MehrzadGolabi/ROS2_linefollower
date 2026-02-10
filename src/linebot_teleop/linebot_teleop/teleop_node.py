import os
import select
import sys
import termios
import tty

from geometry_msgs.msg import Twist, TwistStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile

MSG = """
Control Your Linebot!
---------------------------
Moving around:
        w
   a    s    d

w/s : increase/decrease linear velocity
a/d : increase/decrease angular velocity
z   : toggle speed mode (Normal/Fast)

space key : force stop

CTRL-C to quit
"""

E_MSG = """
Communications Failed
"""


class TeleopNode(Node):
    def __init__(self):
        super().__init__('teleop_node')

        # Parameters
        self.declare_parameters(
            namespace='',
            parameters=[
                ('stamped', True),
                ('frame_id', 'base_link'),
                ('topic_name', 'joy_vel'),
                ('max_linear_vel', 0.22),
                ('max_angular_vel', 2.84),
                ('lin_vel_step_size', 0.01),
                ('ang_vel_step_size', 0.1),
            ]
        )

        self.stamped = self.get_parameter('stamped').value
        self.frame_id = self.get_parameter('frame_id').value
        self.topic_name = self.get_parameter('topic_name').value
        self.max_linear_vel = self.get_parameter('max_linear_vel').value
        self.max_angular_vel = self.get_parameter('max_angular_vel').value
        self.lin_vel_step_size = self.get_parameter('lin_vel_step_size').value
        self.ang_vel_step_size = self.get_parameter('ang_vel_step_size').value

        # State
        self.speed_multiplier = 1.0
        self.target_linear_velocity = 0.0
        self.target_angular_velocity = 0.0
        self.control_linear_velocity = 0.0
        self.control_angular_velocity = 0.0
        self.settings = None
        if os.name != 'nt':
            try:
                self.settings = termios.tcgetattr(sys.stdin)
            except Exception:
                self.get_logger().warn('Could not get terminal settings (not a TTY?)')

        # Publisher
        qos = QoSProfile(depth=10)
        if self.stamped:
            self.publisher_ = self.create_publisher(TwistStamped, self.topic_name, qos)
        else:
            self.publisher_ = self.create_publisher(Twist, self.topic_name, qos)

        self.get_logger().info(
            f'Teleop Node Started. Stamped: {self.stamped}, Max Lin: {self.max_linear_vel}')

    def update_target_velocity(self, key):
        if key == 'w':
            self.target_linear_velocity = self.check_linear_limit_velocity(
                self.target_linear_velocity + self.lin_vel_step_size)
        elif key == 's':
            self.target_linear_velocity = self.check_linear_limit_velocity(
                self.target_linear_velocity - self.lin_vel_step_size)
        elif key == 'a':
            self.target_angular_velocity = self.check_angular_limit_velocity(
                self.target_angular_velocity + self.ang_vel_step_size)
        elif key == 'd':
            self.target_angular_velocity = self.check_angular_limit_velocity(
                self.target_angular_velocity - self.ang_vel_step_size)
        elif key == 'z':
            self.speed_multiplier = 2.0 if self.speed_multiplier == 1.0 else 1.0
        elif key == ' ':
            self.target_linear_velocity = 0.0
            self.control_linear_velocity = 0.0
            self.target_angular_velocity = 0.0
            self.control_angular_velocity = 0.0

    def get_status_message(self):
        mode = 'Fast' if self.speed_multiplier == 2.0 else 'Normal'
        return (f'Currently: Speed Mode: {mode} | '
                f'Linear: {self.target_linear_velocity:.2f} | '
                f'Angular: {self.target_angular_velocity:.2f}')

    def constrain(self, input_vel, low_bound, high_bound):
        if input_vel < low_bound:
            input_vel = low_bound
        elif input_vel > high_bound:
            input_vel = high_bound
        return input_vel

    def check_linear_limit_velocity(self, velocity):
        return self.constrain(
            velocity,
            -self.max_linear_vel * self.speed_multiplier,
            self.max_linear_vel * self.speed_multiplier)

    def check_angular_limit_velocity(self, velocity):
        return self.constrain(
            velocity,
            -self.max_angular_vel * self.speed_multiplier,
            self.max_angular_vel * self.speed_multiplier)

    def make_simple_profile(self, output_vel, input_vel, slop):
        if input_vel > output_vel:
            output_vel = min(input_vel, output_vel + slop)
        elif input_vel < output_vel:
            output_vel = max(input_vel, output_vel - slop)
        else:
            output_vel = input_vel
        return output_vel

    def get_key(self):
        # Basic non-blocking key read
        if os.name == 'nt':
            # Windows support (minimal)
            return ''

        try:
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                key = sys.stdin.read(1)
            else:
                key = ''
            if self.settings:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        except Exception:
            key = ''
        return key

    def publish_velocity(self):
        self.control_linear_velocity = self.make_simple_profile(
            self.control_linear_velocity,
            self.target_linear_velocity,
            (self.lin_vel_step_size / 2.0))

        self.control_angular_velocity = self.make_simple_profile(
            self.control_angular_velocity,
            self.target_angular_velocity,
            (self.ang_vel_step_size / 2.0))

        if self.stamped:
            twist_stamped = TwistStamped()
            twist_stamped.header.stamp = self.get_clock().now().to_msg()
            twist_stamped.header.frame_id = self.frame_id
            twist_stamped.twist.linear.x = self.control_linear_velocity
            twist_stamped.twist.linear.y = 0.0
            twist_stamped.twist.linear.z = 0.0
            twist_stamped.twist.angular.x = 0.0
            twist_stamped.twist.angular.y = 0.0
            twist_stamped.twist.angular.z = self.control_angular_velocity
            self.publisher_.publish(twist_stamped)
        else:
            twist = Twist()
            twist.linear.x = self.control_linear_velocity
            twist.linear.y = 0.0
            twist.linear.z = 0.0
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = self.control_angular_velocity
            self.publisher_.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = TeleopNode()

    status = 0
    try:
        print(MSG)
        while rclpy.ok():
            key = node.get_key()
            if key in ['w', 'a', 'd', ' ', 's', 'z']:
                node.update_target_velocity(key)
                print(node.get_status_message())
                status += 1
            elif key == '\x03':  # CTRL-C
                break

            if status == 20:
                print(MSG)
                status = 0

            node.publish_velocity()
            # Sleep briefly to avoid 100% CPU usage and allow other tasks
            # rclpy.spin_once(node, timeout_sec=0.1) # spin_once blocks for timeout or event
            # Since we are in a tight loop reading keys, we might not want to spin too long.
            # But we need to spin to handle parameters updates if we wanted them dynamic, etc.
            # For this simple teleop, just publishing is fine.
            # But to be safe and allow callbacks (like logging), let's spin once with 0 timeout.
            rclpy.spin_once(node, timeout_sec=0.0)

    except Exception as e:
        print(e)

    finally:
        # Publish stop
        node.target_linear_velocity = 0.0
        node.target_angular_velocity = 0.0
        node.control_linear_velocity = 0.0
        node.control_angular_velocity = 0.0
        node.publish_velocity()

        if node.settings and os.name != 'nt':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
