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
        ir_str = msg.data.strip()
        twist = TwistStamped()
        twist.header.stamp = self.get_clock().now().to_msg()
        
        if len(ir_str) < 5:
            return

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
            # All background (Line Lost or Gap)
            # Stop for safety or search? Arduino code says "Hard Right".
            # Wait, Arduino code says:
            # else if (infraRed == "11111") {
            #   // Hard Right
            #   driveMotorA(SPEED_TURN);
            #   driveMotorB(SPEED_TURN); 
            # }
            # Wait, driveMotorA(SPEED) and B(SPEED) means GO STRAIGHT?
            # Or is it a rotate?
            # driveMotorA is Left Motor. driveMotorB is Right Motor.
            # If both are positive SPEED_TURN, it goes straight.
            # But "Hard Right" comment is there.
            
            # Let's check "Hard Right" logic earlier:
            # driveMotorA(SPEED_TURN); driveMotorB(-SPEED_TURN); -> Rotate Right.
            
            # For "11111": driveMotorA(SPEED_TURN); driveMotorB(SPEED_TURN);
            # This looks like "Go Straight". Maybe it assumes if lost, keep going?
            
            # I will act conservative: Stop.
            twist.twist.linear.x = 0.0
            twist.twist.angular.z = 0.0
            
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