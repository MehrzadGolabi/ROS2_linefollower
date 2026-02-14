import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    camera_topic = LaunchConfiguration('camera_topic')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )

    declare_camera_topic = DeclareLaunchArgument(
        'camera_topic',
        default_value='/camera/image_raw',
        description='Topic for camera images'
    )

    config = os.path.join(
        get_package_share_directory('linefollower_cv'),
        'config',
        'linefollower_cv_params.yaml',
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_camera_topic,
        Node(
            package='linefollower_cv',
            executable='linefollower_cv_node',
            name='linefollower_cv_node',
            output='screen',
            parameters=[
                config,
                {
                    'use_sim_time': use_sim_time,
                    'camera_topic': camera_topic
                }
            ],
        ),
    ])
