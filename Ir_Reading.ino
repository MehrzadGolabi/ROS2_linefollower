String infraRed="";

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(36, INPUT);
  pinMode(39, INPUT);
  pinMode(34, INPUT);
  pinMode(35, INPUT);
  pinMode(32, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

  digitalRead(36) ? infraRed+="1" : infraRed+="0";
  digitalRead(39) ? infraRed+="1" : infraRed+="0";
  digitalRead(34) ? infraRed+="1" : infraRed+="0";
  digitalRead(35) ? infraRed+="1" : infraRed+="0";
  digitalRead(32) ? infraRed+="1" : infraRed+="0";

  Serial.println(infraRed);
  infraRed="";
  delay(100);
}
