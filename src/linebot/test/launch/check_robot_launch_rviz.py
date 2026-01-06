import sys

def test_robot_launch_rviz_arg():
    launch_path = "src/linebot/launch/robot.launch.py"
    try:
        with open(launch_path, 'r') as f:
            content = f.read()
            if "'rviz'" not in content or "hardware_debug.rviz" not in content:
                 print(f"FAILURE: 'rviz' argument or hardware_debug.rviz not found in {launch_path}")
                 sys.exit(1)
            print("SUCCESS: 'rviz' argument and config found.")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_robot_launch_rviz_arg()
