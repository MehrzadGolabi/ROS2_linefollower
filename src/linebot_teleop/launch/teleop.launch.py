from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    stamped = LaunchConfiguration('stamped')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')

    declare_stamped = DeclareLaunchArgument(
        'stamped',
        default_value='true',
        description='Use stamped twist messages'
    )

    declare_cmd_vel_topic = DeclareLaunchArgument(
        'cmd_vel_topic',
        default_value='key_vel',
        description='Topic to publish velocity commands to'
    )

    node = Node(
        package='linebot_teleop',
        executable='teleop_node',
        name='teleop_node',
        output='screen',
        emulate_tty=True,
        parameters=[{'stamped': stamped}],
        remappings=[('cmd_vel', cmd_vel_topic)]
    )

    return LaunchDescription([
        declare_stamped,
        declare_cmd_vel_topic,
        node
    ])
