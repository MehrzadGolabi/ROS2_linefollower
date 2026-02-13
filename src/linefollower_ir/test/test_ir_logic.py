import os
import sys
import unittest
from unittest.mock import MagicMock

from linefollower_ir.linefollower_ir_node import LinefollowerIrNode
import rclpy
from std_msgs.msg import String

# Ensure we can import the node
sys.path.append(os.path.join(os.getcwd(), 'src/linefollower_ir'))


class TestIrLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not rclpy.ok():
            rclpy.init()

    @classmethod
    def tearDownClass(cls):
        if rclpy.ok():
            rclpy.shutdown()

    def setUp(self):
        self.node = LinefollowerIrNode()
        # Mock the publisher to capture outputs
        self.node.cmd_vel_pub = MagicMock()

    def tearDown(self):
        self.node.destroy_node()

    def test_center(self):
        msg = String()
        msg.data = '11011'
        self.node.ir_callback(msg)

        self.node.cmd_vel_pub.publish.assert_called_once()
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        # Expect moving forward with little to no rotation
        self.assertGreater(twist.twist.linear.x, 0.0)
        self.assertAlmostEqual(twist.twist.angular.z, 0.0, delta=0.1)

    def test_turn_left(self):
        msg = String()
        msg.data = '10011'
        self.node.ir_callback(msg)

        self.node.cmd_vel_pub.publish.assert_called_once()
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        # Expect positive angular velocity (left turn)
        self.assertGreater(twist.twist.angular.z, 0.1)

    def test_decimal_input(self):
        msg = String()
        msg.data = '27'  # '11011' in binary
        self.node.ir_callback(msg)

        self.node.cmd_vel_pub.publish.assert_called_once()
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        # Should be interpreted as 11011
        self.assertGreater(twist.twist.linear.x, 0.0)
        self.assertAlmostEqual(twist.twist.angular.z, 0.0, delta=0.1)

    def test_turn_right(self):
        msg = String()
        msg.data = '11001'
        self.node.ir_callback(msg)

        self.node.cmd_vel_pub.publish.assert_called_once()
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        # Expect negative angular velocity (right turn)
        self.assertLess(twist.twist.angular.z, -0.1)

    def test_lost(self):
        msg = String()
        msg.data = '00000'
        self.node.ir_callback(msg)

        # Behavior for lost depends on state machine, maybe search or stop.
        # Assuming simple stop or search for now, just checking it handles it without crash
        self.node.cmd_vel_pub.publish.assert_called_once()


if __name__ == '__main__':
    unittest.main()
