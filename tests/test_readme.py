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
            self.assertIn('### 🤖 linebot (Core Bringup)', content)
            self.assertIn('### 👁️ linefollower_cv (Computer Vision)', content)
            self.assertIn('### 📡 linefollower_ir (IR Sensors)', content)
            self.assertIn('## 🛠️ External ROS 2 Tools', content)
            self.assertIn('### ⌨️ teleop_twist_keyboard', content)
            self.assertIn('### 🖼️ rqt_image_view', content)
            self.assertIn('### 📊 RViz2', content)
            self.assertIn('## 📖 Scenario-Based Tutorials', content)
            self.assertIn('### 1. Running in IR Line-Following Mode', content)
            self.assertIn('### 2. Running in Computer Vision Mode', content)
            self.assertIn('### 3. Running in Simulation', content)

if __name__ == '__main__':
    unittest.main()