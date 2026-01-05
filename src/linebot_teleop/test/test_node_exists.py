import os
import unittest


class TestNodeExists(unittest.TestCase):

    def test_node_file_exists(self):
        node_path = os.path.join(
            os.path.dirname(__file__), '..', 'linebot_teleop', 'teleop_node.py')
        self.assertTrue(os.path.exists(node_path), f'Node file not found at {node_path}')


if __name__ == '__main__':
    unittest.main()
