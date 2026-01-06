import os
import sys

def test_robot_launch_has_mode_arg():
    launch_path = "src/linebot/launch/robot.launch.py"
    try:
        with open(launch_path, 'r') as f:
            content = f.read()
            # Simple check for the string 'mode' inside DeclareLaunchArgument context
            # This is a heuristic.
            if "'mode'" not in content:
                 print(f"FAILURE: 'mode' argument not found in {launch_path}")
                 sys.exit(1)
            print("SUCCESS: 'mode' argument found.")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_robot_launch_has_mode_arg()
