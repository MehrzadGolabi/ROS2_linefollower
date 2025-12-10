#include <Wire.h>
#include <AS5600.h>

AS5600 as5600;

float toAngle(float val){

  float Angle = (val*360.0)/4095.0;

  return Angle;
}

unsigned long lastTime = 0;
unsigned long elapsedTime = 0;
float lastAngle = 0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);
  Wire.begin();
  lastAngle = toAngle(as5600.readAngle());
  lastTime = millis();
}


void loop() {
  // put your main code here, to run repeatedly:
  unsigned long currentTime = millis();
  float deltaTimeMs = (currentTime-lastTime);
  float deltaTimeMinutes = deltaTimeMs / 60000.0;

  if(deltaTimeMs >= 30){
    float currentAngle = toAngle(as5600.readAngle());
    float deltaAngle= currentAngle-lastAngle;

    if(deltaAngle > 180) deltaAngle -= 360;
    if(deltaAngle < -180) deltaAngle += 360;

    float deltaRev = deltaAngle / 360.0;

    float rpm = (deltaRev / deltaTimeMinutes) * -1.0;

    lastAngle = currentAngle;
    lastTime = millis();

    if(currentTime - elapsedTime >= 500){
    Serial.println((int)rpm);
    elapsedTime = currentTime;
    }

  } 
}


//code benazaram okie, ehtemalan bayad ye door ba i2c ham emtehan konim, roi as5600 ye moghavemat hast mishe address i2c ro avaz kard, chand ta ro roi yek bus bezarim




