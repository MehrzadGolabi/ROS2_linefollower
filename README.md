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

## 📦 Workspace Packages

### 🤖 linebot (Core Bringup)
The primary package for system orchestration and hardware/simulation bringup.

#### 🏁 Robot Bringup
Starts the physical robot, including motor drivers, encoders, and selected sensors.
- **Command:** `ros2 launch linebot robot.launch.py`
- **Arguments:**
  | Argument | Default | Description |
  | --- | --- | --- |
  | `mode` | `camera` | Sensor mode: `camera`, `ir`, or `hybrid` |
  | `camera_topic` | `/camera/image_raw` | Topic to subscribe for images |
  | `use_ros2_control` | `true` | Use ros2_control framework |
  | `rviz` | `false` | Launch RViz for debugging |
- **Key Nodes:** `ros2_control_node`, `robot_state_publisher`, `twist_mux`, `twist_stamper`

#### 🎮 Simulation
Launches the robot in the Gazebo Sim environment.
- **Command:** `ros2 launch linebot sim.launch.py`
- **Arguments:**
  | Argument | Default | Description |
  | --- | --- | --- |
  | `world` | `linefollow.sdf` | SDF world file to load |
  | `use_sim_time` | `true` | Sync with simulator clock |
- **Key Nodes:** `gz_sim`, `ros_gz_bridge`, `robot_state_publisher`

---

### 👁️ linefollower_cv (Computer Vision)
Handles high-speed line detection and navigation using OpenCV.

#### 🚀 Launch CV Node
- **Command:** `ros2 launch linefollower_cv linefollower_cv_launch.py`
- **Arguments:**
  | Argument | Default | Description |
  | --- | --- | --- |
  | `camera_topic` | `/camera/image_raw` | Topic to subscribe for images |
- **Key Nodes:** `linefollower_cv_node`

---

### 📡 linefollower_ir (IR Sensors)
State-machine based line following using the 5-array IR sensor.

#### 🚀 Launch IR Node
- **Command:** `ros2 launch linefollower_ir linefollower_ir_launch.py`
- **Key Nodes:** `linefollower_ir_node`

---

## 🛠️ External ROS 2 Tools

### ⌨️ teleop_twist_keyboard
Standard tool for manual control of the robot using the keyboard.
- **Command:** `ros2 run teleop_twist_keyboard teleop_twist_keyboard`
- **Usage:** Follow the on-screen instructions to use keys like `i`, `j`, `l`, `k` for movement.

### 🖼️ rqt_image_view
A GUI tool to view camera streams and processed images.
- **Command:** `ros2 run rqt_image_view rqt_image_view`
- **Usage:** Select the desired image topic (e.g., `/camera/image_raw` or `/line_image`) from the dropdown menu.

### 📊 RViz2
The primary visualization tool for ROS 2.
- **Command:** `rviz2`
- **Usage:** Used to monitor robot state, sensor data (Lidar, Odometry), and coordinate frames.

---

## 📖 Scenario-Based Tutorials

### 1. Running in IR Line-Following Mode
Use this mode for high-reliability line following using the infrared sensor array.
1.  **Bringup the robot in IR mode:**
    ```bash
    ros2 launch linebot robot.launch.py mode:=ir
    ```
2.  **Start the IR line-follower logic:**
    ```bash
    ros2 launch linefollower_ir linefollower_ir_launch.py
    ```

### 2. Running in Computer Vision Mode
Use this mode for advanced navigation using the camera.
1.  **Bringup the robot in camera mode:**
    ```bash
    ros2 launch linebot robot.launch.py mode:=camera
    ```
2.  **Start the CV line-follower logic:**
    ```bash
    ros2 launch linefollower_cv linefollower_cv_launch.py
    ```
3.  **Optional: View processed image:**
    ```bash
    ros2 run rqt_image_view rqt_image_view
    ```
    (Select `/line_image` to see the detection result)

### 3. Running in Simulation
Test your algorithms in a virtual environment.
1.  **Launch the simulator:**
    ```bash
    ros2 launch linebot sim.launch.py
    ```
2.  **Optional: Control manually to test bridges:**
    ```bash
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
    ```