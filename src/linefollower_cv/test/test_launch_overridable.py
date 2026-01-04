import sys

def test_launch_overridable():
    launch_path = "src/linefollower_cv/launch/linefollower_cv_launch.py"
    try:
        with open(launch_path, 'r') as f:
            content = f.read()
            if "camera_topic" not in content or "DeclareLaunchArgument" not in content:
                 print(f"FAILURE: 'camera_topic' argument not found in {launch_path}")
                 sys.exit(1)
            print("SUCCESS: 'camera_topic' argument found.")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_launch_overridable()
