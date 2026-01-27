import os
import sys

def test_robot_launch_default_mode():
    launch_path = "src/linebot/launch/robot.launch.py"
    try:
        with open(launch_path, 'r') as f:
            content = f.read()
            if "default_value='teleop'" in content:
                 print("SUCCESS: default_value='teleop' found.")
            else:
                 print(f"FAILURE: default_value='teleop' not found in {launch_path}")
                 sys.exit(1)
                 
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_robot_launch_default_mode()
