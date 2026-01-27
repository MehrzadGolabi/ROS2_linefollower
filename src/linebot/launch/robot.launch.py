import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import RegisterEventHandler, DeclareLaunchArgument, IncludeLaunchDescription
from launch.event_handlers import OnProcessStart
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import LaunchConfiguration, Command, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource


# Image Transport Republishers
# terminal command example: ros2 run image_transport republish raw compressed --ros-args -r in:=/camera/image_raw -r out/compressed:=/camera/image_raw/compressed
def image_transport_republisher(transport, camera_topics, condition=None):
    base_topic = camera_topics.split('/')[-1]
    
    return Node(
        package='image_transport',
        executable='republish',
        name=f'image_transport_republish_{transport}_{base_topic}',
        arguments=['raw', transport],
        remappings=[
            ('in', f'/camera/{camera_topics}'),
            (f'out/{transport}', f'/camera/{camera_topics}/{transport}'),
        ],
        condition=condition
    )

def generate_launch_description():

    package_name= 'linebot'
    package_dir= get_package_share_directory(package_name) 

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_ros2_control = LaunchConfiguration('use_ros2_control')
    mode = LaunchConfiguration('mode')

    declare_use_sim_time= DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='If true, use simulated clock'
    )
    
    declare_use_ros2_control = DeclareLaunchArgument(
        'use_ros2_control',
        default_value='true',
        description='If true, use ros2_control'
    )

    declare_mode = DeclareLaunchArgument(
        'mode',
        default_value='teleop',
        description='Sensor mode: camera, ir, hybrid, or teleop'
    )

    declare_rviz = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        description='Launch RViz with hardware debug config'
    )

    # Declare the path to files
    robot_description_xacro_file = os.path.join(
        package_dir,
        'description',
        'robot.urdf.xacro'
    )

    rviz_config_file_dir = os.path.join(
        package_dir, 
        'config', 
        'linebot_config.rviz'
    )

    robot_controllers_file_dir = os.path.join(
        package_dir, 
        'config', 
        'controller.yaml'
    )

    
    twist_mux_params_file = os.path.join(
        package_dir, 
        'config', 
        'twist_mux.yaml'
    )

    enable_ir_val = PythonExpression(["'true' if ('", mode, "' == 'ir' or '", mode, "' == 'hybrid') else 'false'"])

    # robot_state_publisher setup    
    robot_description_config = Command ([
        'xacro ', 
        robot_description_xacro_file, 
        ' use_ros2_control:=', 
        use_ros2_control,
        ' enable_ir:=',
        enable_ir_val
        ])
    
    params = {
        'robot_description': ParameterValue(robot_description_config, value_type=str), 
        'use_sim_time': use_sim_time,
        'use_ros2_control': use_ros2_control
    }

    # robot_state_publisher node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
        
    )
 
    # Image Transport Republishers Node
    camera = 'image_raw'
    depth_camera = 'depth/image_raw'
    
    camera_condition = IfCondition(
        PythonExpression(["'", mode, "' == 'camera' or '", mode, "' == 'hybrid'"])
    )

    ir_condition = IfCondition(
        PythonExpression(["'", mode, "' == 'ir' or '", mode, "' == 'hybrid'"])
    )

    image_transports = ['compressed','compressedDepth', 'theora', 'zstd' ]  
    node_image_republishers = [image_transport_republisher(transport, depth_camera, condition=camera_condition) 
                          for transport in image_transports]
 
    # controller spawn
    node_ros2_control = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[params, 
                    robot_controllers_file_dir
                    ],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )
    
    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_controller", 
                   "--param-file", 
                   robot_controllers_file_dir
        ],
    )

    node_twist_mux = Node(
        package="twist_mux",
        executable="twist_mux",
        name='twist_mux',
        output='screen',
        parameters=[
            twist_mux_params_file,
            {'use_stamped': True},
        ],
        remappings=[
            ('cmd_vel_out', 
             'diff_drive_controller/cmd_vel'),
        ],
    )

    node_twist_stamper = Node(
        package="twist_stamper",
        executable="twist_stamper",
        name='twist_stamper',
        output='screen',
        remappings=[
            ('cmd_vel_in', 'cmd_vel_smoothed'),
            ('cmd_vel_out', 'nav_vel'),
        ],
    )

    register_node_ros2_control = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action= node_robot_state_publisher,
            on_start= [node_ros2_control],
        )
    )

    register_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action= node_ros2_control,
            on_start=[joint_state_broadcaster_spawner],
        )
    )

    register_diff_drive_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action= joint_state_broadcaster_spawner,
            on_start=[diff_drive_controller_spawner],
        )
    )

    camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(package_dir, 'launch', 'camera.launch.py')
        ),
        condition=camera_condition
    )

    linefollower_cv_pkg = get_package_share_directory('linefollower_cv')
    linefollower_cv_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(linefollower_cv_pkg, 'launch', 'linefollower_cv_launch.py')
        ),
        condition=camera_condition,
        launch_arguments={
            'use_sim_time': use_sim_time,
            'camera_topic': '/camera/image_raw'
        }.items()
    )

    linefollower_ir_pkg = get_package_share_directory('linefollower_ir')
    linefollower_ir_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(linefollower_ir_pkg, 'launch', 'linefollower_ir_launch.py')
        ),
        condition=ir_condition,
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # rviz2 node
    rviz_config_file = os.path.join(
        package_dir, 
        'config', 
        'hardware_debug.rviz'
    )

    node_rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen'
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Add the nodes to the launch description
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_use_ros2_control)
    ld.add_action(declare_mode)
    ld.add_action(declare_rviz)

    ld.add_action(register_node_ros2_control)
    ld.add_action(register_joint_state_broadcaster_spawner)
    ld.add_action(register_diff_drive_controller_spawner)

    ld.add_action(node_robot_state_publisher)
    ld.add_action(node_twist_mux)
    ld.add_action(node_twist_stamper)
    for node_republisher in node_image_republishers:
        ld.add_action(node_republisher)
    
    ld.add_action(camera_launch)
    ld.add_action(linefollower_cv_launch)
    ld.add_action(linefollower_ir_launch)
    ld.add_action(node_rviz2)

    # Generate the launch description  
    return ld

    