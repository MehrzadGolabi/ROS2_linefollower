#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import TwistStamped

class LinefollowerIrNode(Node):
    def __init__(self):
        super().__init__("linefollower_ir_node")
        
        # Parameters
        self.declare_parameter("linear_speed", 0.2)
        self.declare_parameter("angular_speed", 1.0)
        
        self.linear_speed = self.get_parameter("linear_speed").value
        self.angular_speed = self.get_parameter("angular_speed").value
        
        # Subscribers and Publishers
        # Subscribe to the string topic published by the hardware interface
        self.ir_sub = self.create_subscription(String, "/ir_sensors", self.ir_callback, 10)
        # Publish TwistStamped to /joy_vel (which is muxed)
        self.cmd_vel_pub = self.create_publisher(TwistStamped, "/joy_vel", 10)
        
        self.get_logger().info("IR Line Follower Node Started")

    def ir_callback(self, msg):
        ir_data = msg.data.strip()
        
        # If the data is a decimal number (0-31 from hardware bridge), convert to 5-bit binary string
        # Valid decimal values (0-31) will have length < 5. Binary strings have length 5.
        if ir_data.isdigit() and len(ir_data) < 5:
            try:
                val = int(ir_data)
                ir_str = format(val, '05b')
            except ValueError:
                ir_str = ir_data
        else:
            ir_str = ir_data

        twist = TwistStamped()
        twist.header.stamp = self.get_clock().now().to_msg()
        twist.header.frame_id = "base_link"
        
        if len(ir_str) < 5:
            return

        self.get_logger().info(f"IR State: {ir_str}")
        
        # Logic based on '0' = Line, '1' = Background (inferred from Arduino code)
        
        if ir_str == "11011":
            # Center: Go Straight
            twist.twist.linear.x = self.linear_speed
            twist.twist.angular.z = 0.0
            
        elif ir_str in ["10011", "10111"]:
            # Left Detected: Turn Left
            twist.twist.linear.x = self.linear_speed * 0.5
            twist.twist.angular.z = self.angular_speed * 0.5
            
        elif ir_str in ["00011", "00111", "01111"]:
            # Hard Left
            twist.twist.linear.x = 0.05
            twist.twist.angular.z = self.angular_speed
            
        elif ir_str in ["11001", "11101"]:
            # Right Detected: Turn Right
            twist.twist.linear.x = self.linear_speed * 0.5
            twist.twist.angular.z = -self.angular_speed * 0.5
            
        elif ir_str in ["11100", "11110", "11000"]:
            # Hard Right
            twist.twist.linear.x = 0.05
            twist.twist.angular.z = -self.angular_speed
            
        elif ir_str == "11111":
            twist.twist.linear.x = 0.2
            twist.twist.angular.z = 0.2
            
        else:
            # Default stop
            twist.twist.linear.x = 0.0
            twist.twist.angular.z = 0.0
            
        self.cmd_vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = LinefollowerIrNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()