import rclpy
import sys
import os
import numpy as np
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

# Add src/linefollower_cv to path
sys.path.append(os.path.join(os.getcwd(), 'src/linefollower_cv'))
from linefollower_cv.linefollower_cv_node import LinefollowerCvNode

def test_processing():
    try:
        rclpy.init()
        node = LinefollowerCvNode()
        bridge = CvBridge()
        
        # Create a 320x240 image with a black line in the center
        # White background
        img = np.ones((240, 320, 3), dtype=np.uint8) * 255
        # Vertical black line at x=160
        cv2.line(img, (160, 0), (160, 240), (0, 0, 0), 10)
        
        msg = bridge.cv2_to_imgmsg(img, encoding="bgr8")
        
        # We need to set parameters correctly for 320x240 if they aren't already
        # but the node reads them from its declaration defaults or yaml.
        
        # Call the callback. 
        # Note: it will try to publish to '/joy_vel'.
        node.camera_callback(msg)
        
        print("SUCCESS: Node processed 320x240 image without crash.")
        node.destroy_node()
        rclpy.shutdown()
    except Exception as e:
        print(f"FAILURE: {e}")
        # traceback
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_processing()
