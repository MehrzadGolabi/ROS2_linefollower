import os
import sys


def test_launch_overridable():
    # Try to find the launch file relative to this test script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(test_dir)
    launch_path = os.path.join(package_dir, 'launch', 'linefollower_cv_launch.py')

    try:
        with open(launch_path, 'r') as f:
            content = f.read()
            if 'camera_topic' not in content or 'DeclareLaunchArgument' not in content:
                print(f"FAILURE: 'camera_topic' argument not found in {launch_path}")
                sys.exit(1)
            print('SUCCESS: Launch file appears to support overridable camera_topic.')
    except Exception as e:
        print(f'FAILURE: {e}')
        sys.exit(1)


if __name__ == '__main__':
    test_launch_overridable()
