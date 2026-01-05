#!/usr/bin/env python3
import rclpy
from rclpy.node import Node


class LinefollowerIrNode(Node):

    def __init__(self):
        super().__init__("linefollower_ir_node")
        example_param = self.declare_parameter("example_param", "default_value").value
        self.get_logger().info(f"Declared parameter 'example_param'. Value: {example_param}")
        self.get_logger().info("Hello world from the Python node linefollower_ir_node")


def main(args=None):
    rclpy.init(args=args)

    linefollower_ir_node = LinefollowerIrNode()

    try:
        rclpy.spin(linefollower_ir_node)
    except KeyboardInterrupt:
        pass

    linefollower_ir_node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
