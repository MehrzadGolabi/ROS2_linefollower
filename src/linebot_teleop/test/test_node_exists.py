import unittest
import os

class TestNodeExists(unittest.TestCase):
    def test_teleop_node_file_exists(self):
        # This test expects the main node file to exist
        node_path = os.path.join(os.path.dirname(__file__), '..', 'linebot_teleop', 'teleop_node.py')
        self.assertTrue(os.path.exists(node_path), f"File not found: {node_path}")

if __name__ == '__main__':
    unittest.main()