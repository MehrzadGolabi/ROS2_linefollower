import unittest
import shutil

class TestCheckDependencies(unittest.TestCase):
    def test_tools_exist(self):
        # We expect these tools to be available in the environment
        tools = ['ros2', 'rviz2'] 
        # rqt_image_view and teleop_twist_keyboard might be ros2 run <pkg> <exec>
        # so checking for binary might fail if they are python scripts or not in path directly but standard
        
        for tool in tools:
            self.assertTrue(shutil.which(tool), f"{tool} not found in PATH")

if __name__ == '__main__':
    unittest.main()