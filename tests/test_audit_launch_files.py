import os
import sys
import unittest

# Add the project root to the path so we can import from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts import audit_launch_files

class TestAuditLaunchFiles(unittest.TestCase):
    def test_find_all_launch_files(self):
        launch_files = audit_launch_files.find_launch_files('src')
        
        # Expected files (subset to verify logic)
        expected_files = [
            'src/linebot/launch/robot.launch.py',
            'src/linefollower_cv/launch/linefollower_cv_launch.py',
            'src/linefollower_ir/launch/linefollower_ir_launch.py'
        ]
        
        # Normalize paths for comparison
        launch_files = [os.path.normpath(p) for p in launch_files]
        expected_files = [os.path.normpath(p) for p in expected_files]

        for f in expected_files:
            self.assertIn(f, launch_files, f"Failed to find {f}")

    def test_extract_launch_arguments(self):
        # Create a dummy launch file content
        dummy_content = """
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'mode',
            default_value='sim',
            description='Operation mode'
        ),
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Logging level'
        ),
    ])
"""
        # We need to mock reading a file. For simplicity in this environment, 
        # I'll just test a function that takes content string if I design it that way.
        # Let's assume audit_launch_files.extract_arguments_from_content(content)
        
        args = audit_launch_files.extract_arguments_from_content(dummy_content)
        
        expected_args = {
            'mode': {'default': 'sim', 'description': 'Operation mode'},
            'log_level': {'default': 'info', 'description': 'Logging level'}
        }
        
        self.assertEqual(args, expected_args)

    def test_extract_launch_nodes(self):
        dummy_content = """
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='my_talker'
        ),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        )
    ])
"""
        nodes = audit_launch_files.extract_nodes_from_content(dummy_content)
        
        expected_nodes = [
            {'package': 'demo_nodes_cpp', 'executable': 'talker', 'name': 'my_talker'},
            {'package': 'turtlesim', 'executable': 'turtlesim_node', 'name': 'sim'}
        ]
        
        self.assertEqual(nodes, expected_nodes)

if __name__ == '__main__':
    unittest.main()
