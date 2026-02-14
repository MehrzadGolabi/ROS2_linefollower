import os
import sys
import unittest
from unittest.mock import MagicMock

import numpy as np
import rclpy
from sensor_msgs.msg import Image


class TestAngularCapping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        # Ensure we can import the node
        sys.path.append(os.path.join(os.getcwd(), 'src/linefollower_cv'))
        from linefollower_cv.linefollower_cv_node import LinefollowerCvNode
        self.node = LinefollowerCvNode()
        # Mock the publisher to avoid actual ROS 2 communication issues in unit tests
        self.node.cmd_vel_pub = MagicMock()

    def tearDown(self):
        self.node.destroy_node()

    def test_angular_speed_capping_positive(self):
        """Test that angular speed is capped at max_angular_speed for positive values."""
        # Set a very high KP to ensure a large angular output
        self.node.kp = 100.0
        self.node.max_angular_speed = 0.5  # This is what we WANT to happen

        # Mocking finding the center to force a large error
        self.node.find_line_center = MagicMock(return_value=0)
        self.node.roi_center_x = 100
        self.node.current_state = MagicMock()  # Avoid side effects

        # Mock Image message
        msg = Image()

        # We need to bypass some CV logic or mock it
        self.node.bridge.imgmsg_to_cv2 = MagicMock(
            return_value=np.ones((480, 640, 3), dtype=np.uint8))
        self.node.preprocess_image = MagicMock(return_value=np.zeros((100, 200), dtype=np.uint8))
        self.node.adaptive_canny_thresholds = MagicMock(return_value=(50, 150))
        self.node.detect_cul_de_sac = MagicMock(return_value=False)
        self.node.detect_sharp_turn = MagicMock(return_value=(False, 0))

        # Trigger callback
        self.node.camera_callback(msg)

        # Check published message
        args, _ = self.node.cmd_vel_pub.publish.call_args
        published_msg = args[0]

        self.assertLessEqual(published_msg.twist.angular.z, 0.5)

    def test_angular_speed_capping_negative(self):
        """Test that angular speed is capped at -max_angular_speed for negative values."""
        self.node.kp = 100.0
        self.node.max_angular_speed = 0.5

        # Line on the far right
        self.node.find_line_center = MagicMock(return_value=200)
        self.node.roi_center_x = 100

        msg = Image()

        self.node.bridge.imgmsg_to_cv2 = MagicMock(
            return_value=np.ones((480, 640, 3), dtype=np.uint8))
        self.node.preprocess_image = MagicMock(return_value=np.zeros((100, 200), dtype=np.uint8))
        self.node.adaptive_canny_thresholds = MagicMock(return_value=(50, 150))
        self.node.detect_cul_de_sac = MagicMock(return_value=False)
        self.node.detect_sharp_turn = MagicMock(return_value=(False, 0))

        self.node.camera_callback(msg)

        args, _ = self.node.cmd_vel_pub.publish.call_args
        published_msg = args[0]

        self.assertGreaterEqual(published_msg.twist.angular.z, -0.5)


if __name__ == '__main__':
    unittest.main()
