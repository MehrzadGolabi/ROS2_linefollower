# ROS 2 Line-Follower Robot

This repository contains the source code and configuration for a high-performance ROS 2 (Jazzy) line-follower robot. It supports both IR-based and Computer Vision-based line following.

## 🚀 Quick Start / Cheat Sheet

| Task | Command |
| --- | --- |
| **Bringup (Physical Robot)** | `ros2 launch linebot robot.launch.py` |
| **Bringup (Simulation)** | `ros2 launch linebot sim.launch.py` |
| **Manual Control (Keyboard)** | `ros2 run teleop_twist_keyboard teleop_twist_keyboard` |
| **View Camera Stream** | `ros2 run rqt_image_view rqt_image_view` |
| **IR Line Following** | `ros2 launch linefollower_ir linefollower_ir_launch.py` |
| **CV Line Following** | `ros2 launch linefollower_cv linefollower_cv_launch.py` |
| **Visualize System (RViz)** | `rviz2` |

---
