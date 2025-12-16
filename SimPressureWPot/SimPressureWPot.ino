// Arduino code to read potentiometer and send pressure data

const int POT_PIN = A0;  // Potentiometer connected to A0

void setup() {
  Serial.begin(9600);  // Start serial communication
  pinMode(POT_PIN, INPUT);
}

void loop() {
  // Read potentiometer (0-1023)
  int potValue = analogRead(POT_PIN);
  
  // Map to pressure range (0-100)
  int pressure1 = map(potValue, 0, 1023, 0, 100);
  
  // Simulate other 3 sensors with dummy values (or add more pots!)
  int pressure2 = 30;
  int pressure3 = 50;
  int pressure4 = 70;
  
  // Send comma-separated values
  Serial.print(pressure1);
  Serial.print(",");
  Serial.print(pressure2);
  Serial.print(",");
  Serial.print(pressure3);
  Serial.print(",");
  Serial.println(pressure4);
  
  delay(100);  // Send data every 100ms
}
