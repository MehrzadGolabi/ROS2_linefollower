import select
import sys
import termios
import tty

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node


class TeleopNode(Node):

    def __init__(self):
        super().__init__('teleop_node')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.speed = 0.5
        self.turn = 1.0
        self.get_logger().info('Teleop Node Started')

    def get_twist_from_key(self, key):
        twist = Twist()
        key = key.lower()
        if key == 'w':
            twist.linear.x = self.speed
        elif key == 's':
            twist.linear.x = -self.speed
        elif key == 'a':
            twist.angular.z = self.turn
        elif key == 'd':
            twist.angular.z = -self.turn
        elif key == ' ':
            # Safety stop: already zeroed, but made explicit
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        return twist

    def getKey(self):
        # Basic non-blocking key read (implementation placeholder)
        settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key


def main(args=None):
    rclpy.init(args=args)
    node = TeleopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
