import os

from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
import pytest


def test_launch_file_exists():
    package_name = 'linebot_teleop'
    launch_file_name = 'teleop.launch.py'

    try:
        share_dir = get_package_share_directory(package_name)
        launch_path = os.path.join(share_dir, 'launch', launch_file_name)
        assert os.path.exists(launch_path), \
            f'Launch file {launch_file_name} not found in {share_dir}'
    except PackageNotFoundError:
        pytest.fail(f'Package {package_name} not found')
