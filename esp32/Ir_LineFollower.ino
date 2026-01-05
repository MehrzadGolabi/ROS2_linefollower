// --- TB6612FNG Motor Driver Pins ---
// STBY: Must be HIGH for the driver to work
const int STBY_PIN = 23; 

// Motor A (Left)
const int PWMA = 13; // Speed control (PWM)
const int AIN1 = 12; // Direction
const int AIN2 = 14; // Direction

// Motor B (Right)
const int PWMB = 25; // Speed control (PWM)
const int BIN1 = 26; // Direction
const int BIN2 = 27; // Direction

// --- Tuning Settings ---
const int SPEED_BASE = 255; // Base speed (0-255)
const int SPEED_TURN = 190; // Turning speed
// If motors hum but don't move, increase these numbers slightly.

String infraRed = "";

void setup() {
  //Serial.begin(115200);

  // 1. Sensor Pins (Inputs)
  pinMode(36, INPUT);
  pinMode(39, INPUT);
  pinMode(34, INPUT);
  pinMode(35, INPUT);
  pinMode(32, INPUT);

  // 2. Motor Pins (Outputs)
  pinMode(STBY_PIN, OUTPUT);
  
  pinMode(PWMA, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  
  pinMode(PWMB, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);

  // 3. Enable the Motor Driver
  digitalWrite(STBY_PIN, HIGH);
}

void loop() {
  // --- Read Sensors ---
  infraRed = "";
  digitalRead(36) ? infraRed += "1" : infraRed += "0";
  digitalRead(39) ? infraRed += "1" : infraRed += "0";
  digitalRead(34) ? infraRed += "1" : infraRed += "0";
  digitalRead(35) ? infraRed += "1" : infraRed += "0";
  digitalRead(32) ? infraRed += "1" : infraRed += "0";

  // Debug (Optional)
  // Serial.println(infraRed);

  // --- Logic ---
  // Assuming "1" = Line Detected (Black)
  // Adjust logic if your sensor outputs "0" for black.

  if (infraRed == "11011") {
    // Center: Go Straight
    driveMotorA(SPEED_BASE);
    driveMotorB(SPEED_BASE);
  } 
  else if (infraRed == "10011" || infraRed == "10111") {
    // Left Detected: Turn Left
    driveMotorA(SPEED_TURN / 3); // Slow down left
    driveMotorB(SPEED_TURN);     // Speed up right
  }
  else if (infraRed == "00011" || infraRed == "00111" || infraRed == "01111") {
    // Hard Left
    driveMotorA(-SPEED_TURN); // Reverse left wheel for sharp turn
    driveMotorB(SPEED_TURN);
  }
  else if (infraRed == "11001" || infraRed == "11101") {
    // Right Detected: Turn Right
    driveMotorA(SPEED_TURN);
    driveMotorB(SPEED_TURN / 3); // Slow down right
  }
  else if (infraRed == "11100" || infraRed == "11110" || infraRed == "11000") {
    // Hard Right
    driveMotorA(SPEED_TURN);
    driveMotorB(-SPEED_TURN); // Reverse right wheel
  }
  else if (infraRed == "11111") {
    // Hard Right
    driveMotorA(SPEED_TURN);
    driveMotorB(SPEED_TURN); // Reverse right wheel
  }
  else {
    // No line or all black: Stop
    driveMotorA(0);
    driveMotorB(0);
  }

  // No delay needed for fast reaction
}

// --- Helper Functions for TB6612FNG ---

// Drive Motor A (Left)
// Speed: -255 to 255 (Negative = Reverse)
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
  analogWrite(PWMA, speed);
}

// Drive Motor B (Right)
void driveMotorB(int speed) {
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
  analogWrite(PWMB, speed);
}