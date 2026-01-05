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
            '': (0.0, 0.0)    # No key pressed
        }

        for key, expected in mappings.items():
            twist = self.node.get_twist_from_key(key)
            self.assertEqual(twist.linear.x, expected[0], f"Failed for key '{key}' linear.x")
            self.assertEqual(twist.angular.z, expected[1], f"Failed for key '{key}' angular.z")


if __name__ == '__main__':
    unittest.main()
