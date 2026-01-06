/* Functions for various sensor types */

float microsecondsToCm(long microseconds)
{
  // The speed of sound is 340 m/s or 29 microseconds per cm.
  // The ping travels out and back, so to find the distance of the
  // object we take half of the distance travelled.
  return microseconds / 29 / 2;
}

long Ping(int pin) {
  long duration, range;

  // The PING))) is triggered by a HIGH pulse of 2 or more microseconds.
  // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
  delayMicroseconds(2);
  digitalWrite(pin, HIGH);
  delayMicroseconds(5);
  digitalWrite(pin, LOW);

  // The same pin is used to read the signal from the PING))): a HIGH
  // pulse whose duration is the time (in microseconds) from the sending
  // of the ping to the reception of its echo off of an object.
  pinMode(pin, INPUT);
  duration = pulseIn(pin, HIGH);

  // convert the time into meters
  range = microsecondsToCm(duration);
  
  return(range);
}

// IR Sensor Pins (ESP32)
const int irPins[] = {36, 39, 34, 35, 32};

void initIRSensors() {
  for (int i = 0; i < 5; i++) {
    pinMode(irPins[i], INPUT);
  }
}

// Returns a 5-bit integer representing the sensor states
int readIRSensors() {
  int result = 0;
  for (int i = 0; i < 5; i++) {
    if (digitalRead(irPins[i])) {
      result |= (1 << (4 - i)); // MSB is pin 36, LSB is pin 32
    }
  }
  return result;
}