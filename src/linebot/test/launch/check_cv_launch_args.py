import os
import sys

def test_cv_launch_args():
    launch_path = "src/linebot/launch/robot.launch.py"
    try:
        with open(launch_path, 'r') as f:
            content = f.read()
            if "launch_arguments={" in content and "'camera_topic': '/camera/image_raw'" in content:
                print("SUCCESS: launch_arguments for camera_topic found.")
            else:
                print(f"FAILURE: launch_arguments for camera_topic not found in {launch_path}")
                sys.exit(1)
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_cv_launch_args()
