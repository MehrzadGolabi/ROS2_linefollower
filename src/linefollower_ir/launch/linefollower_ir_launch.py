import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )

    config = os.path.join(
        get_package_share_directory('linefollower_ir'),
        'config',
        'linefollower_ir_params.yaml',
    )

    return LaunchDescription([
        declare_use_sim_time,
        Node(
            package='linefollower_ir',
            executable='linefollower_ir_node',
            name='linefollower_ir_node',
            output='screen',
            parameters=[
                config,
                {'use_sim_time': use_sim_time}
            ],
        ),
    ])
