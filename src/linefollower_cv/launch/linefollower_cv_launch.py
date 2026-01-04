import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    
    package_dir = get_package_share_directory('linefollower_cv')
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    # Config file path
    config_file = os.path.join(
        package_dir,
        'config',
        'linefollower_cv_params.yaml',
    )

    # Line follower node
    linefollower_node = Node(
        package='linefollower_cv',
        executable='linefollower_cv_node',
        name='linefollower_cv_node',
        output='screen',
        parameters=[
            config_file,
            {'use_sim_time': use_sim_time}
        ],
    )

    return LaunchDescription([
        declare_use_sim_time,
        linefollower_node,
    ])
