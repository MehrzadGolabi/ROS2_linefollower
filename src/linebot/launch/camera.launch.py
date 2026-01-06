from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='camera_ros',
            executable='camera_node',
            name='camera',
            parameters=[{
                'camera': 0,
                'role': 'viewfinder',
                'format': 'RGB888',
                'width': 320,
                'height': 240,
                'FrameDurationLimits': [33333, 33333]
            }]
        )
    ])
