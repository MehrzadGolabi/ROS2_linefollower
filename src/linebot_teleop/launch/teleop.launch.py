from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='linebot_teleop',
            executable='teleop_node',
            name='teleop_node',
            output='screen',
            emulate_tty=True
        )
    ])
