#include <Wire.h>
#include <AS5600.h>

AS5600 as5600;

float toAngle(float val){

  float Angle = (val*360.0)/4095.0;

  return Angle;
}

unsigned long lastTime1 = 0 , lastTime2 = 0;
unsigned long elapsedTime = 0;
float lastAngle1 = 0, lastAngle2 = 0;
float rpm1 = 0, rpm2 = 0;

unsigned int sensorIndex = 0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);
  Wire.begin();
  Wire.beginTransmission(0x70);  
  Wire.write(1 << 0);          
  Wire.endTransmission();
  lastAngle1 = toAngle(as5600.readAngle());
  Wire.beginTransmission(0x70);  
  Wire.write(1 << 1);          
  Wire.endTransmission();
  lastAngle2 = toAngle(as5600.readAngle());
  lastTime1 = millis();
  lastTime2 = millis();
}


void loop() {
  // put your main code here, to run repeatedly:
  if(sensorIndex == 0){
    Wire.beginTransmission(0x70);  
    Wire.write(1 << 0);          
    Wire.endTransmission();
    unsigned long currentTime = millis();
    float deltaTimeMs = (currentTime-lastTime1);
    float deltaTimeMinutes = deltaTimeMs / 60000.0;

    if(deltaTimeMs >= 30){
      float currentAngle = toAngle(as5600.readAngle());
      float deltaAngle= currentAngle-lastAngle1;

      if(deltaAngle > 180) deltaAngle -= 360;
      if(deltaAngle < -180) deltaAngle += 360;

      float deltaRev = deltaAngle / 360.0;

      rpm1 = (deltaRev / deltaTimeMinutes) * -1.0;

      lastAngle1 = currentAngle;
      lastTime1 = millis();

      if(currentTime - elapsedTime >= 200){
      //Serial.print("Sensor1: ");  
      //Serial.print((int)rpm);
      //Serial.print("   ");
      sensorIndex = 1;
      elapsedTime = currentTime;
      }
    }
  }
  else{
    Wire.beginTransmission(0x70);  
    Wire.write(1 << 1);          
    Wire.endTransmission();
    unsigned long currentTime = millis();
    float deltaTimeMs = (currentTime-lastTime2);
    float deltaTimeMinutes = deltaTimeMs / 60000.0;

    if(deltaTimeMs >= 30){
      float currentAngle = toAngle(as5600.readAngle());
      float deltaAngle= currentAngle-lastAngle2;

      if(deltaAngle > 180) deltaAngle -= 360;
      if(deltaAngle < -180) deltaAngle += 360;

      float deltaRev = deltaAngle / 360.0;

      rpm2 = (deltaRev / deltaTimeMinutes) * -1.0;

      lastAngle2 = currentAngle;
      lastTime2 = millis();

      if(currentTime - elapsedTime >= 200){
      Serial.print("Sensor1: ");
      Serial.print((int)rpm1);
      Serial.print("   ");
      Serial.print("Sensor2: ");
      Serial.println((int)rpm2);
      sensorIndex = 0;
      elapsedTime = currentTime;
      }
    }
  } 
}




