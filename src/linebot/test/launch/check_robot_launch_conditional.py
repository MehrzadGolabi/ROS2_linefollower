import sys

def test_robot_launch_conditional():
    launch_path = "src/linebot/launch/robot.launch.py"
    try:
        with open(launch_path, 'r') as f:
            content = f.read()
            if "IncludeLaunchDescription" not in content:
                 print(f"FAILURE: IncludeLaunchDescription not found in {launch_path}")
                 sys.exit(1)
            # We expect PythonExpression for the complex condition (mode == x or mode == y)
            if "PythonExpression" not in content:
                 print(f"FAILURE: PythonExpression not found in {launch_path}")
                 sys.exit(1)
        print("SUCCESS")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_robot_launch_conditional()
