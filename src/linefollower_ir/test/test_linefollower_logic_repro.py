import unittest
from unittest.mock import MagicMock
import rclpy
from std_msgs.msg import String
from geometry_msgs.msg import TwistStamped
import sys
import os

# Ensure we can import the node
# Note: In a real ROS 2 environment, we would use colcon test or set PYTHONPATH
# For this reproduction, we'll use the same trick as the existing test
sys.path.append(os.path.join(os.getcwd(), 'src/linefollower_ir'))
from linefollower_ir.linefollower_ir_node import LinefollowerIrNode

class TestIrLogicRepro(unittest.TestCase):
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

    def test_repro_right_offset_11101(self):
        """Test the 11101 pattern which is reported to cause a stop or insufficient motion."""
        msg = String()
        msg.data = "11101"
        self.node.ir_callback(msg)
        
        self.node.cmd_vel_pub.publish.assert_called_once()
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        
        # User reports linear.x: 0.03 which is very low (stiction)
        # We want to ensure linear velocity is sufficient (e.g., > 0.05 at minimum)
        # And angular velocity is corrective (negative for right turn)
        print(f"\nPattern 11101 -> linear.x: {twist.twist.linear.x}, angular.z: {twist.twist.angular.z}")
        
        # Current logic (from linefollower_ir_node.py):
        # elif ir_str in ["11001", "11101"]:
        #     twist.twist.linear.x = self.linear_speed * 0.5
        #     twist.twist.angular.z = -self.angular_speed * 0.5
        # Default linear_speed is 0.2, so 0.2 * 0.5 = 0.1.
        # User reported 0.03, which is strange if parameters are default.
        
        self.assertGreater(twist.twist.linear.x, 0.05, "Linear velocity too low to overcome stiction")
        self.assertLess(twist.twist.angular.z, -0.1, "Should be turning right")

    def test_repro_left_offset_10111(self):
        """Test the 10111 pattern which is reported to cause a stop or insufficient motion."""
        msg = String()
        msg.data = "10111"
        self.node.ir_callback(msg)
        
        self.node.cmd_vel_pub.publish.assert_called_once()
        twist = self.node.cmd_vel_pub.publish.call_args[0][0]
        
        print(f"\nPattern 10111 -> linear.x: {twist.twist.linear.x}, angular.z: {twist.twist.angular.z}")
        
        # Current logic:
        # elif ir_str in ["10011", "10111"]:
        #     twist.twist.linear.x = self.linear_speed * 0.5
        #     twist.twist.angular.z = self.angular_speed * 0.5
            
        self.assertGreater(twist.twist.linear.x, 0.05, "Linear velocity too low to overcome stiction")
        self.assertGreater(twist.twist.angular.z, 0.1, "Should be turning left")

if __name__ == '__main__':
    unittest.main()