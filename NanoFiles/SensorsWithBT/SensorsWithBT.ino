#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "HX711.h"

// HX711 pins
#define DOUT1 3
#define CLK1  2
#define DOUT2 5
#define CLK2  4
#define DOUT3 7
#define CLK3  6
#define DOUT4 9
#define CLK4  8

HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;

const uint8_t AVG_N = 10;
const uint8_t SHIFT_BITS = 12;

// BLE variables
BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("Client connected!");
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("Client disconnected!");
      BLEDevice::startAdvertising();
    }
};

class MyCharacteristicCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
      std::string value = pCharacteristic->getValue();
      
      if (value.length() > 0) {
        String command = String(value.c_str());
        Serial.println("Received command: " + command);
        
        if (command == "TARE") {
          Serial.println("Taring all sensors...");
          
          scale1.tare();
          scale2.tare();
          scale3.tare();
          scale4.tare();
          
          Serial.println("Tare complete!");
        }
      }
    }
};

void setup() {
  Serial.begin(115200);
  
  // Initialize BLE
  BLEDevice::init("ESP32_LoadCells");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ   |
                      BLECharacteristic::PROPERTY_WRITE  |
                      BLECharacteristic::PROPERTY_NOTIFY |
                      BLECharacteristic::PROPERTY_INDICATE
                    );
  pCharacteristic->addDescriptor(new BLE2902());
  pService->start();
  
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);
  BLEDevice::startAdvertising();
  
  Serial.println("BLE initialized");

  pCharacteristic->setCallbacks(new MyCharacteristicCallbacks());
  
  // Initialize HX711s
  scale1.begin(DOUT1, CLK1);
  delay(500);
  scale2.begin(DOUT2, CLK2);
  delay(500);
  scale3.begin(DOUT3, CLK3);
  delay(500);
  scale4.begin(DOUT4, CLK4);
  delay(500);

  // Tare all sensors
  Serial.println("Taring sensor 1...");
  for(int i = 0; i < 5; i++) {
    scale1.tare();
    delay(500);
  }
  
  Serial.println("Taring sensor 2...");
  for(int i = 0; i < 5; i++) {
    scale2.tare();
    delay(500);
  }
  
  Serial.println("Taring sensor 3...");
  for(int i = 0; i < 5; i++) {
    scale3.tare();
    delay(500);
  }
  
  Serial.println("Taring sensor 4...");
  for(int i = 0; i < 5; i++) {
    scale4.tare();
    delay(500);
  }
  
  Serial.println("Ready - BLE and sensors initialized");
}

void loop() {
  if (scale1.is_ready() && scale2.is_ready() && scale3.is_ready() && scale4.is_ready()) {
    // Read all sensors (12-bit effective)
    long raw_p1 = scale1.get_value(AVG_N);
    float p1 = (raw_p1 >> SHIFT_BITS);
    
    long raw_p2 = scale2.get_value(AVG_N);
    float p2 = (raw_p2 >> SHIFT_BITS);
    
    long raw_p3 = scale3.get_value(AVG_N);
    float p3 = (raw_p3 >> SHIFT_BITS);
    
    long raw_p4 = scale4.get_value(AVG_N);
    float p4 = (raw_p4 >> SHIFT_BITS);
    
    unsigned long timestamp = millis();
    
    // Create CSV string: timestamp,p1,p2,p3,p4
    String data = String(timestamp) + "," + String(p1, 0) + "," + String(p2, 0) + "," + String(p3, 0) + "," + String(p4, 0);
    
    // Send via Serial (for debugging)
    Serial.println(data);
    
    // Send via BLE if connected
    if (deviceConnected) {
      pCharacteristic->setValue(data.c_str());
      pCharacteristic->notify();
    }
    
    delay(100);
  }
}
