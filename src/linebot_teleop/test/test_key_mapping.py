import unittest

from linebot_teleop.teleop_node import TeleopNode
import rclpy


class TestKeyMapping(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = TeleopNode()

    def tearDown(self):
        self.node.destroy_node()

    def test_wasd_mapping(self):
        # We need to expose a method in TeleopNode that translates a key to a Twist msg
        # Let's assume it's called get_twist_from_key(key)

        mappings = {
            'w': (0.5, 0.0),  # (linear_x, angular_z)
            's': (-0.5, 0.0),
            'a': (0.0, 1.0),
            'd': (0.0, -1.0),
            'W': (0.5, 0.0),  # Case insensitive
            'S': (-0.5, 0.0),
            'A': (0.0, 1.0),
            'D': (0.0, -1.0),
            ' ': (0.0, 0.0),  # Safety stop
            'x': (0.0, 0.0),  # Unknown key
            '': (0.0, 0.0)    # No key pressed
        }

        for key, expected in mappings.items():
            twist = self.node.get_twist_from_key(key)
            self.assertEqual(twist.linear.x, expected[0], f"Failed for key '{key}' linear.x")
            self.assertEqual(twist.angular.z, expected[1], f"Failed for key '{key}' angular.z")

    def test_get_key(self):
        from unittest.mock import patch

        # Mock termios, tty, select and sys.stdin
        with patch('linebot_teleop.teleop_node.termios'), \
             patch('linebot_teleop.teleop_node.tty'), \
             patch('linebot_teleop.teleop_node.select.select') as mock_select, \
             patch('linebot_teleop.teleop_node.sys.stdin') as mock_stdin:

            mock_stdin.fileno.return_value = 0

            # Simulate key press 'w'
            mock_select.return_value = ([mock_stdin], [], [])
            mock_stdin.read.return_value = 'w'

            key = self.node.getKey()
            self.assertEqual(key, 'w')

            # Simulate no key press
            mock_select.return_value = ([], [], [])
            key = self.node.getKey()
            self.assertEqual(key, '')


if __name__ == '__main__':
    unittest.main()
