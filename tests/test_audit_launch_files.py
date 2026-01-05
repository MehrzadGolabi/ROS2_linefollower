import os
import sys
import unittest

# Add the project root to the path so we can import from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts import audit_launch_files

class TestAuditLaunchFiles(unittest.TestCase):
    def test_find_all_launch_files(self):
        launch_files = audit_launch_files.find_launch_files('src')
        
        # Expected files (subset to verify logic)
        expected_files = [
            'src/linebot/launch/robot.launch.py',
            'src/linefollower_cv/launch/linefollower_cv_launch.py',
            'src/linefollower_ir/launch/linefollower_ir_launch.py'
        ]
        
        # Normalize paths for comparison
        launch_files = [os.path.normpath(p) for p in launch_files]
        expected_files = [os.path.normpath(p) for p in expected_files]

        for f in expected_files:
            self.assertIn(f, launch_files, f"Failed to find {f}")

if __name__ == '__main__':
    unittest.main()
