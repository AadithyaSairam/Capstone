#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;

// UUIDs for BLE service and characteristic
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
      // Restart advertising
      BLEDevice::startAdvertising();
    }
};

void setup() {
  Serial.begin(115200);
  
  // Create BLE Device
  BLEDevice::init("ESP32_Sensor");
  
  // Create BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  // Create BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);
  
  // Create BLE Characteristic
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ   |
                      BLECharacteristic::PROPERTY_WRITE  |
                      BLECharacteristic::PROPERTY_NOTIFY |
                      BLECharacteristic::PROPERTY_INDICATE
                    );
  
  // Add descriptor
  pCharacteristic->addDescriptor(new BLE2902());
  
  // Start service
  pService->start();
  
  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);
  BLEDevice::startAdvertising();
  
  Serial.println("BLE device ready! Waiting for connections...");
}

void loop() {
  if (deviceConnected) {
    // Generate test data
    float sensor1 = random(0, 100);
    float sensor2 = random(0, 100);
    float sensor3 = random(0, 100);
    float sensor4 = random(0, 100);
    unsigned long timestamp = millis();
    
    // Create CSV string
    String data = String(timestamp) + "," + String(sensor1, 2) + "," + String(sensor2, 2) + "," + String(sensor3, 2) + "," + String(sensor4, 2);
    
    // Send via BLE
    pCharacteristic->setValue(data.c_str());
    pCharacteristic->notify();
    
    Serial.println("Sent: " + data);
    delay(1000);
  } else {
    Serial.println("Waiting for connection...");
    delay(2000);
  }
}
