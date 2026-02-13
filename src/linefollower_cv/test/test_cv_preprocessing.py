import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import cv2
import rclpy
import os
import sys
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

# Ensure we can import the node
sys.path.append(os.path.join(os.getcwd(), 'src/linefollower_cv'))
from linefollower_cv.linefollower_cv_node import LinefollowerCvNode

class TestCvPreprocessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not rclpy.ok():
            rclpy.init()

    @classmethod
    def tearDownClass(cls):
        if rclpy.ok():
            rclpy.shutdown()

    def setUp(self):
        # Initialize node with default parameters
        self.node = LinefollowerCvNode()
        self.bridge = CvBridge()

    def tearDown(self):
        self.node.destroy_node()

    def test_new_parameters_existence(self):
        """Test that the new required parameters exist in the node."""
        self.assertTrue(self.node.has_parameter('clahe_tile_grid_size'))
        self.assertTrue(self.node.has_parameter('morph_op_type'))
        self.assertTrue(self.node.has_parameter('morph_iterations'))
        self.assertTrue(self.node.has_parameter('morph_apply_after_canny'))

    def test_morphology_pre_canny(self):
        """Test that pre-Canny morphology is applied correctly."""
        # Enable morphology and set to pre-Canny
        self.node.use_morphology = True
        self.node.morph_apply_after_canny = False
        self.node.morph_op = cv2.MORPH_OPEN # Bridges gaps in BLACK lines
        self.node.morph_kernel = np.ones((5, 5), np.uint8)
        self.node.morph_iterations = 3
        
        # Create a synthetic image with a SMALL gap (10 pixels)
        img_bgr = np.ones((100, 100, 3), dtype=np.uint8) * 255
        cv2.line(img_bgr, (50, 0), (50, 45), (0, 0, 0), 2)
        cv2.line(img_bgr, (50, 55), (50, 100), (0, 0, 0), 2)
        
        preprocessed = self.node.preprocess_image(img_bgr)
        
        # Check if the gap at row 50 is closed (pixel at row 50, col 50 should be black/dark)
        self.assertEqual(preprocessed[50, 50], 0, "Morphological opening should have filled the 10px gap in black line")

    def test_adaptive_canny_thresholds(self):
        """Test that adaptive Canny thresholds respond to image brightness."""
        # Bright image
        bright = np.ones((100, 100), dtype=np.uint8) * 200
        low_b, high_b = self.node.adaptive_canny_thresholds(bright)
        
        # Dark image
        dark = np.ones((100, 100), dtype=np.uint8) * 50
        low_d, high_d = self.node.adaptive_canny_thresholds(dark)
        
        self.assertGreater(low_b, low_d, "Bright image should have higher thresholds than dark image")
        self.assertGreater(high_b, high_d, "Bright image should have higher thresholds than dark image")

    def test_morphology_post_canny(self):
        """Test that post-Canny morphology is applied during camera_callback."""
        # Setup node for post-canny closing
        self.node.use_morphology = True
        self.node.morph_apply_after_canny = True
        self.node.morph_op = cv2.MORPH_CLOSE # Bridges gaps in WHITE edges
        self.node.morph_kernel = np.ones((5, 5), np.uint8)
        self.node.morph_iterations = 3
        
        # Mock publisher to avoid actual ROS 2 communication issues in test
        self.node.cmd_vel_pub = MagicMock()
        
        # Create a synthetic image with a small gap in the line
        img_bgr = np.ones((480, 640, 3), dtype=np.uint8) * 255
        cv2.line(img_bgr, (320, 0), (320, 235), (0, 0, 0), 5)
        cv2.line(img_bgr, (320, 245), (320, 480), (0, 0, 0), 5)
        
        # Let's mock cv2.morphologyEx to verify it's called
        with patch('cv2.morphologyEx', wraps=cv2.morphologyEx) as mock_morph:
            msg = self.bridge.cv2_to_imgmsg(img_bgr, encoding="bgr8")
            self.node.camera_callback(msg)
            
            # Verify morphologyEx was called
            self.assertTrue(mock_morph.called, "cv2.morphologyEx should be called for post-Canny morphology")

if __name__ == '__main__':
    unittest.main()
