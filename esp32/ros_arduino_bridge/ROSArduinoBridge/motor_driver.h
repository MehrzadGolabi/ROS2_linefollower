/***************************************************************
   Motor driver function definitions - by James Nugen
   *************************************************************/

#ifdef L298_MOTOR_DRIVER
  #define RIGHT_MOTOR_BACKWARD 5
  #define LEFT_MOTOR_BACKWARD  6
  #define RIGHT_MOTOR_FORWARD  9
  #define LEFT_MOTOR_FORWARD   10
  #define RIGHT_MOTOR_ENABLE 12
  #define LEFT_MOTOR_ENABLE 13
#endif

#ifdef CYTRON_MDD3A

  /* Include the Pololu library */
  #include "CytronMotorDriver.h"
  
  #define M1A 18
  #define M1B 19
  #define M2A 32
  #define M2B 33

  extern CytronMD motor_left;
  extern CytronMD motor_right;
#endif

#ifdef TB6612_MOTOR_DRIVER
  // STBY: Must be HIGH for the driver to work
  #define STBY_PIN 23

  // Motor A (Left)
  #define PWMA 13 // Speed control (PWM)
  #define AIN1 14 // Direction
  #define AIN2 12 // Direction

  // Motor B (Right)
  #define PWMB 25 // Speed control (PWM)
  #define BIN1 26 // Direction
  #define BIN2 27 // Direction

  // PWM Configuration for TB6612
  #define PWM_FREQUENCY 20000 // 20 kHz - optimal for TB6612FNG
  #define PWM_RESOLUTION 8    // 8-bit resolution (0-255)
#endif

void initMotorController();
void setMotorSpeed(int i, int spd);
void setMotorSpeeds(int leftSpeed, int rightSpeed);