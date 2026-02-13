import unittest
from unittest.mock import MagicMock, patch
import rclpy
from std_msgs.msg import String
from geometry_msgs.msg import TwistStamped
import sys
import os
import time
from rclpy.time import Time

# Ensure we can import the node
sys.path.append(os.path.join(os.getcwd(), 'src/linefollower_ir'))
from linefollower_ir.linefollower_ir_node import LinefollowerIrNode

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

    def test_hard_left_commitment_reproduction(self):
        """
        Reproduce the issue where a hard turn is lost prematurely.
        Currently, sending '00111' then '11111' immediately switches to 'lost' behavior.
        """
        # 1. Trigger Hard Left
        msg = String()
        msg.data = "00111"
        self.node.ir_callback(msg)
        
        # Verify initial hard turn
        self.node.cmd_vel_pub.publish.assert_called()
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        self.assertEqual(twist.twist.angular.z, self.node.angular_speed * 0.8)
        
        # 2. Immediately send '11111' (lost line)
        # In the current implementation, this should exit the hard turn logic.
        msg.data = "11111"
        self.node.ir_callback(msg)
        
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        
        # EXPECTATION for REPRODUCTION:
        # Currently, it will NOT be Hard Left (angular.z will be 0.0 or slow search)
        # We want to assert that it IS still Hard Left to fail the current logic.
        print(f"\nAfter '11111', angular.z is: {twist.twist.angular.z}")
        
        # This assertion is expected to FAIL with the current code
        self.assertEqual(twist.twist.angular.z, self.node.angular_speed * 0.8, 
                         "Robot should maintain Hard Left even if line is temporarily lost")

    def test_hard_right_commitment_reproduction(self):
        """Same for Hard Right."""
        # 1. Trigger Hard Right
        msg = String()
        msg.data = "11100"
        self.node.ir_callback(msg)
        
        # Verify initial hard turn
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        self.assertEqual(twist.twist.angular.z, -self.node.angular_speed * 0.8)
        
        # 2. Immediately send '11111'
        msg.data = "11111"
        self.node.ir_callback(msg)
        
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        
        # This assertion is expected to FAIL with the current code
        self.assertEqual(twist.twist.angular.z, -self.node.angular_speed * 0.8,
                         "Robot should maintain Hard Right even if line is temporarily lost")

if __name__ == '__main__':
    unittest.main()