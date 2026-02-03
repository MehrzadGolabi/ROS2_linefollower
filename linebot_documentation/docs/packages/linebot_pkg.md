# Linebot Bringup

The `linebot` package is the main entry point for the robot's operation. It manages the launch of hardware interfaces, controllers, sensor drivers, and high-level logic nodes.

## Launch Files

### `robot.launch.py`

This is the primary launch file for the physical robot. It orchestrates the entire system startup.

**Command:**
```bash
ros2 launch linebot robot.launch.py [arguments]
```

**Arguments:**

*   `mode` (string, default: `camera`): Determines which sensors and logic nodes to launch.
    *   `camera`: Launches the camera driver and the `linefollower_cv` node.
    *   `ir`: Launches the `linefollower_ir` node.
    *   `hybrid`: Launches both.
*   `use_ros2_control` (bool, default: `true`): Enables the `ros2_control` framework for hardware abstraction.
*   `rviz` (bool, default: `false`): If `true`, launches RViz2 with a pre-configured view for hardware debugging.
*   `use_sim_time` (bool, default: `false`): Should be `false` for physical hardware.

**Nodes Launched:**

1.  **`robot_state_publisher`**: Publishes the URDF model and TF transforms.
2.  **`ros2_control_node`**: Manages the hardware interface (`diffdrive_arduino`) and controllers.
3.  **Controllers**:
    *   `diff_drive_controller`: Handles differential drive kinematics.
    *   `joint_state_broadcaster`: Publishes joint states.
4.  **`twist_mux`**: Multiplexes velocity commands from different sources (e.g., navigation, teleop, joyful).
5.  **`twist_stamper`**: Converts `Twist` messages to `TwistStamped` for compatibility.
6.  **Sensor Nodes**:
    *   **Camera**: Launches `camera.launch.py` (if mode is `camera` or `hybrid`).
    *   **Logic**: Launches `linefollower_cv` or `linefollower_ir` based on the mode.

### `sim.launch.py`

Launches the robot in the Gazebo Sim environment.

**Command:**
```bash
ros2 launch linebot sim.launch.py [arguments]
```

**Arguments:**

*   `world` (string): Path to the SDF world file. Default: `linefollow.sdf`.
*   `use_sim_time` (bool): Default: `true`.

## Hardware Interface

The system uses `ros2_control` with a custom hardware interface provided by the `diffdrive_arduino` package. This interface communicates with the microcontroller (ESP32/Arduino) to read encoders/sensors and write motor commands.

*   **Config**: `src/linebot/config/controller.yaml`
*   **URDF**: `src/linebot/description/robot.urdf.xacro`
