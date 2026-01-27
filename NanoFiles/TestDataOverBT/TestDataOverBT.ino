#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32_Sensor"); // Bluetooth device name
  Serial.println("Bluetooth device started, ready to pair!");
}

void loop() {
  if (SerialBT.connected()) {
    // Generate test data
    float sensor1 = random(0, 100) / 10.0;
    float sensor2 = random(200, 300) / 10.0;
    unsigned long timestamp = millis();
    
    // Send CSV data
    String data = String(timestamp) + "," + String(sensor1, 2) + "," + String(sensor2, 2);
    SerialBT.println(data);
    
    Serial.println("Sent: " + data);
    delay(1000); // Send every second
  } else {
    Serial.println("Waiting for connection...");
    delay(2000);
  }
}
