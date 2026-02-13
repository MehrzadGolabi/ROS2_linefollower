import os
import sys
import unittest
from unittest.mock import MagicMock

from linefollower_ir.linefollower_ir_node import LinefollowerIrNode
import rclpy
from rclpy.time import Duration, Time
from std_msgs.msg import String

# Ensure we can import the node
sys.path.append(os.path.join(os.getcwd(), 'src/linefollower_ir'))


class TestCommittedTurns(unittest.TestCase):

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
        self.node.cmd_vel_pub = MagicMock()

        # Mock clock for time-based logic
        self.current_time = Time(seconds=100, nanoseconds=0)
        self.node.get_clock().now = MagicMock(return_value=self.current_time)

    def tearDown(self):
        self.node.destroy_node()

    def test_hard_left_commitment_time(self):
        """Verify that hard left is maintained during the minimum duration."""
        # 1. Trigger Hard Left
        msg = String(data='00111')
        self.node.ir_callback(msg)

        # Verify initial hard turn
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        self.assertEqual(twist.twist.angular.z, self.node.angular_speed * 0.8)

        # 2. Advance time by 0.25s (less than 0.5s default)
        self.current_time += Duration(seconds=0, nanoseconds=250000000)
        self.node.get_clock().now.return_value = self.current_time

        # 3. Send '11111' (lost line)
        msg.data = '11111'
        self.node.ir_callback(msg)

        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        self.assertEqual(twist.twist.angular.z, self.node.angular_speed * 0.8,
                         'Should maintain turn during commitment period')

    def test_hard_left_commitment_exit(self):
        """Verify that hard left exits after duration AND center detection."""
        # 1. Trigger Hard Left
        msg = String(data='00111')
        self.node.ir_callback(msg)

        # 2. Advance time by 0.6s (more than 0.5s default)
        self.current_time += Duration(seconds=0, nanoseconds=600000000)
        self.node.get_clock().now.return_value = self.current_time

        # 3. Send '11111' (lost line)
        msg.data = '11111'
        self.node.ir_callback(msg)

        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        self.assertEqual(twist.twist.angular.z, self.node.angular_speed * 0.8,
                         'Should maintain turn after time if line not centered')

        # 4. Send '11011' (centered)
        msg.data = '11011'
        self.node.ir_callback(msg)

        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        self.assertEqual(twist.twist.angular.z, 0.0,
                         'Should exit turn when line is centered after time')
        self.assertEqual(twist.twist.linear.x, self.node.linear_speed)

    def test_hard_right_commitment_time(self):
        """Verify that hard right is maintained during the minimum duration."""
        # 1. Trigger Hard Right
        msg = String(data='11100')
        self.node.ir_callback(msg)

        # Verify initial hard turn
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        self.assertEqual(twist.twist.angular.z, -self.node.angular_speed * 0.8)

        # 2. Advance time by 0.2s
        self.current_time += Duration(seconds=0, nanoseconds=200000000)
        self.node.get_clock().now.return_value = self.current_time

        # 3. Send '11111'
        msg.data = '11111'
        self.node.ir_callback(msg)

        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        self.assertEqual(twist.twist.angular.z, -self.node.angular_speed * 0.8)


if __name__ == '__main__':
    unittest.main()
