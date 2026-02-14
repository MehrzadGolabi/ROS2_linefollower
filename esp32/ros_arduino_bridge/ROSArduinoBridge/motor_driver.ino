/***************************************************************
   Motor driver definitions
   
   Add a "#elif defined" block to this file to include support
   for a particular motor driver.  Then add the appropriate
   #define near the top of the main ROSArduinoBridge.ino file.
   
   *************************************************************/

#ifdef USE_BASE
   
#ifdef POLOLU_VNH5019
  /* Include the Pololu library */
  #include "DualVNH5019MotorShield.h"

  /* Create the motor driver object */
  DualVNH5019MotorShield drive;
  
  /* Wrap the motor driver initialization */
  void initMotorController() {
    drive.init();
  }

  /* Wrap the drive motor set speed function */
  void setMotorSpeed(int i, int spd) {
    if (i == LEFT) drive.setM1Speed(spd);
    else drive.setM2Speed(spd);
  }

  // A convenience function for setting both motor speeds
  void setMotorSpeeds(int leftSpeed, int rightSpeed) {
    setMotorSpeed(LEFT, leftSpeed);
    setMotorSpeed(RIGHT, rightSpeed);
  }
#elif defined POLOLU_MC33926
  /* Include the Pololu library */
  #include "DualMC33926MotorShield.h"

  /* Create the motor driver object */
  DualMC33926MotorShield drive;
  
  /* Wrap the motor driver initialization */
  void initMotorController() {
    drive.init();
  }

  /* Wrap the drive motor set speed function */
  void setMotorSpeed(int i, int spd) {
    if (i == LEFT) drive.setM1Speed(spd);
    else drive.setM2Speed(spd);
  }

  // A convenience function for setting both motor speeds
  void setMotorSpeeds(int leftSpeed, int rightSpeed) {
    setMotorSpeed(LEFT, leftSpeed);
    setMotorSpeed(RIGHT, rightSpeed);
  }
#elif defined L298_MOTOR_DRIVER
  void initMotorController() {
    digitalWrite(RIGHT_MOTOR_ENABLE, HIGH);
    digitalWrite(LEFT_MOTOR_ENABLE, HIGH);
  }
  
  void setMotorSpeed(int i, int spd) {
    unsigned char reverse = 0;
  
    if (spd < 0)
    {
      spd = -spd;
      reverse = 1;
    }
    if (spd > 255)
      spd = 255;
    
    if (i == LEFT) { 
      if      (reverse == 0) { analogWrite(LEFT_MOTOR_FORWARD, spd); analogWrite(LEFT_MOTOR_BACKWARD, 0); }
      else if (reverse == 1) { analogWrite(LEFT_MOTOR_BACKWARD, spd); analogWrite(LEFT_MOTOR_FORWARD, 0); }
    }
    else /*if (i == RIGHT) //no need for condition*/ {
      if      (reverse == 0) { analogWrite(RIGHT_MOTOR_FORWARD, spd); analogWrite(RIGHT_MOTOR_BACKWARD, 0); }
      else if (reverse == 1) { analogWrite(RIGHT_MOTOR_BACKWARD, spd); analogWrite(RIGHT_MOTOR_FORWARD, 0); }
    }
  }
  
  void setMotorSpeeds(int leftSpeed, int rightSpeed) {
    setMotorSpeed(LEFT, leftSpeed);
    setMotorSpeed(RIGHT, rightSpeed);
  }
#elif defined CYTRON_MDD3A

  /* Include the Pololu library */
  #include "CytronMotorDriver.h"

  /* Configure the motor driver. */
  CytronMD motor_left(PWM_PWM, M1A, M1B);
  CytronMD motor_right(PWM_PWM, M2A, M2B);
  
  void initMotorController() {
  }
  
  /* Wrap the drive motor set speed function */
  void setMotorSpeed(int i, int spd) {
    if (i == LEFT) motor_left.setSpeed(spd);
    else motor_right.setSpeed(spd);
  }

  /* A convenience function for setting both motor speeds */
  void setMotorSpeeds(int leftSpeed, int rightSpeed) {
    setMotorSpeed(LEFT, leftSpeed);
    setMotorSpeed(RIGHT, rightSpeed);
  }

#elif defined TB6612_MOTOR_DRIVER

  void initMotorController() {
    pinMode(STBY_PIN, OUTPUT);

    pinMode(AIN1, OUTPUT);
    pinMode(AIN2, OUTPUT);
    pinMode(BIN1, OUTPUT);
    pinMode(BIN2, OUTPUT);

    // Attach PWM pins with proper frequency for TB6612 (auto channel management)
    ledcAttach(PWMA, PWM_FREQUENCY, PWM_RESOLUTION);
    ledcAttach(PWMB, PWM_FREQUENCY, PWM_RESOLUTION);

    // Enable the Motor Driver
    digitalWrite(STBY_PIN, HIGH);
  }

  // Helper function for Motor A (Left)
  void driveMotorA(int speed) {
    if (speed > 0) {
      digitalWrite(AIN1, HIGH);
      digitalWrite(AIN2, LOW);
    } else if (speed < 0) {
      digitalWrite(AIN1, LOW);
      digitalWrite(AIN2, HIGH);
      speed = -speed; // Make speed positive for PWM
    } else {
      digitalWrite(AIN1, LOW);
      digitalWrite(AIN2, LOW); // Brake
    }
    if (speed > 255) speed = 255;
    ledcWrite(PWMA, speed);
  }

  // Helper function for Motor B (Right)
  void driveMotorB(int speed) {
    speed = -speed;  // Invert: right motor is mirror-mounted
    if (speed > 0) {
      digitalWrite(BIN1, HIGH);
      digitalWrite(BIN2, LOW);
    } else if (speed < 0) {
      digitalWrite(BIN1, LOW);
      digitalWrite(BIN2, HIGH);
      speed = -speed;
    } else {
      digitalWrite(BIN1, LOW);
      digitalWrite(BIN2, LOW); // Brake
    }
    if (speed > 255) speed = 255;
    ledcWrite(PWMB, speed);
  }

  void setMotorSpeed(int i, int spd) {
    if (i == LEFT) driveMotorA(spd);
    else driveMotorB(spd);
  }

  void setMotorSpeeds(int leftSpeed, int rightSpeed) {
    setMotorSpeed(LEFT, leftSpeed);
    setMotorSpeed(RIGHT, rightSpeed);
  }

#else
  #error A motor driver must be selected!
#endif

#endif