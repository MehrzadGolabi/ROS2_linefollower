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
        # We need to mock the publisher creation because it requires a live ROS context
        # and we might want to test logic in isolation.
        # However, rclpy.init() is called in setUpClass, so basic Node init should work.
        self.node = TeleopNode()

        # Manually set parameters/constants for testing if they aren't defaulted yet
        # These match the defaults we expect to implement
        self.node.lin_vel_step_size = 0.01
        self.node.ang_vel_step_size = 0.1
        self.node.max_linear_vel = 0.22
        self.node.max_angular_vel = 2.84

        # Reset state
        self.node.target_linear_velocity = 0.0
        self.node.target_angular_velocity = 0.0

    def tearDown(self):
        self.node.destroy_node()

    def test_incremental_linear_velocity(self):
        # Initial state
        self.assertAlmostEqual(self.node.target_linear_velocity, 0.0)

        # Press 'w' to increase (forward)
        self.node.update_target_velocity('w')
        self.assertAlmostEqual(self.node.target_linear_velocity, 0.01)

        # Press 'w' again
        self.node.update_target_velocity('w')
        self.assertAlmostEqual(self.node.target_linear_velocity, 0.02)

        # Press 's' to decrease (backward)
        self.node.update_target_velocity('s')
        self.assertAlmostEqual(self.node.target_linear_velocity, 0.01)

        # Press 's' again
        self.node.update_target_velocity('s')
        self.assertAlmostEqual(self.node.target_linear_velocity, 0.0)

        # Press 's' again to go negative
        self.node.update_target_velocity('s')
        self.assertAlmostEqual(self.node.target_linear_velocity, -0.01)

    def test_incremental_angular_velocity(self):
        # Initial state
        self.assertAlmostEqual(self.node.target_angular_velocity, 0.0)

        # Press 'a' to increase (turn left)
        self.node.update_target_velocity('a')
        self.assertAlmostEqual(self.node.target_angular_velocity, 0.1)

        # Press 'd' to decrease (turn right)
        self.node.update_target_velocity('d')
        self.assertAlmostEqual(self.node.target_angular_velocity, 0.0)

        self.node.update_target_velocity('d')
        self.assertAlmostEqual(self.node.target_angular_velocity, -0.1)

    def test_stop(self):
        # Set some speed
        self.node.target_linear_velocity = 0.1
        self.node.target_angular_velocity = 0.5

        # Press ' ' (space) to stop
        self.node.update_target_velocity(' ')
        self.assertAlmostEqual(self.node.target_linear_velocity, 0.0)
        self.assertAlmostEqual(self.node.target_angular_velocity, 0.0)

    def test_speed_toggle(self):
        # Initial state should be Normal (multiplier 1.0)
        self.assertEqual(self.node.speed_multiplier, 1.0)

        # Press 'z' to toggle to Fast (2.0)
        self.node.update_target_velocity('z')
        self.assertEqual(self.node.speed_multiplier, 2.0)

        # Press 'z' again to toggle back to Normal (1.0)
        self.node.update_target_velocity('z')
        self.assertEqual(self.node.speed_multiplier, 1.0)

    def test_status_message(self):
        # Initial status should show Normal
        msg = self.node.get_status_message()
        self.assertIn('Speed Mode: Normal', msg)

        # Toggle to Fast
        self.node.update_target_velocity('z')
        msg = self.node.get_status_message()
        self.assertIn('Speed Mode: Fast', msg)


if __name__ == '__main__':
    unittest.main()
