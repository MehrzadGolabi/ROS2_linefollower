#include <micro_ros_arduino.h>

#include <Wire.h>
#include <AS5600.h>

#include <stdio.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

#include <std_msgs/msg/int32.h>

rcl_publisher_t publisher;
std_msgs__msg__Int32 msg;
rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;
rcl_timer_t timer;

AS5600 as5600; // Creating Sensor object

#define LED_PIN 13

/*Sensor Variables Begin*/
unsigned long lastTime = 0;
unsigned long elapsedTime = 0;
float lastAngle = 0;
float rpm = 0.0;
/*Sensor Variables End*/

#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}

float toAngle(float val){ // Converting 12-bit value to 360 deg

  float Angle = (val*360.0)/4095.0;

  return Angle;
}

void angleCalc(){

  unsigned long currentTime = millis();
  float deltaTimeMs = (currentTime-lastTime);
  float deltaTimeMinutes = deltaTimeMs / 60000.0;

  if(deltaTimeMs >= 30){
    float currentAngle = toAngle(as5600.readAngle());
    float deltaAngle= currentAngle-lastAngle;

    if(deltaAngle > 180) deltaAngle -= 360;
    if(deltaAngle < -180) deltaAngle += 360;

    float deltaRev = deltaAngle / 360.0;

    rpm = (deltaRev / deltaTimeMinutes) * -1.0;

    lastAngle = currentAngle;
    lastTime = millis();
  } 
}

void error_loop(){
  while(1){
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(100);
  }
}

void timer_callback(rcl_timer_t * timer, int64_t last_call_time)
{  
  RCLC_UNUSED(last_call_time);
  if (timer != NULL) {
    RCSOFTCHECK(rcl_publish(&publisher, &msg, NULL));
    msg.data=(uint32_t)rpm;
  }
}

void setup() {

  /*Sensor initialization Begin*/
  Serial.begin(115200);
  Wire.begin();
  lastAngle = toAngle(as5600.readAngle());
  lastTime = millis();
  /*Sensor initialization End*/

  set_microros_transports();
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  
  
  delay(2000);

  allocator = rcl_get_default_allocator();

  //create init_options
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));

  // create node
  RCCHECK(rclc_node_init_default(&node, "ESP32_Node", "", &support));

  // create publisher
  RCCHECK(rclc_publisher_init_default(
    &publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "Right_Motor_RPM"));

  // create timer,
  const unsigned int timer_timeout = 400;
  RCCHECK(rclc_timer_init_default(
    &timer,
    &support,
    RCL_MS_TO_NS(timer_timeout),
    timer_callback));

  // create executor
  RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
  RCCHECK(rclc_executor_add_timer(&executor, &timer));

  msg.data = 0;
}

void loop() {
  //delay(100);
  RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));
  angleCalc();
}
