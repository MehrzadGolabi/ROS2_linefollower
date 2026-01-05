import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('linefollower_ir'),
        'config',
        'linefollower_ir_params.yaml',
    )

    return LaunchDescription([
        Node(
            package='linefollower_ir',
            executable='linefollower_ir_node',
            name='linefollower_ir_node',
            output='screen',
            parameters=[config],
        ),
    ])
