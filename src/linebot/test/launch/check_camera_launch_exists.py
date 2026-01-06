import os
import sys
from ament_index_python.packages import get_package_share_directory

def test_camera_launch_exists():
    try:
        # We need to check if the file exists in the SOURCE directory for the TDD phase
        # because we haven't built/installed yet. 
        # But 'get_package_share_directory' looks in install.
        # So we will check the local path relative to the workspace root.
        
        # Assuming we run this from workspace root
        launch_path = "src/linebot/launch/camera.launch.py"
        
        if not os.path.exists(launch_path):
            print(f"FAILURE: {launch_path} does not exist.")
            sys.exit(1)
        print("SUCCESS: camera.launch.py exists.")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_camera_launch_exists()
