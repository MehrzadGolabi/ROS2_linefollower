import unittest
import os

class TestREADME(unittest.TestCase):
    def test_readme_exists(self):
        self.assertTrue(os.path.exists('README.md'))

    def test_readme_sections(self):
        with open('README.md', 'r') as f:
            content = f.read()
            self.assertIn('# ROS 2 Line-Follower Robot', content)
            self.assertIn('## 🚀 Quick Start / Cheat Sheet', content)

if __name__ == '__main__':
    unittest.main()