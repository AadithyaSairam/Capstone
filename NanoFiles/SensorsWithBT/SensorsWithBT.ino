#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "HX711.h"

#define DOUT1 3
#define CLK1  2
#define DOUT2 5
#define CLK2  4
#define DOUT3 7
#define CLK3  6
#define DOUT4 12
#define CLK4  11

HX711 scale1, scale2, scale3, scale4;

const uint8_t  AVG_N         = 10;
const uint16_t LOOP_DELAY_MS = 10;
const uint8_t  SHIFT_BITS    = 10;

BLEServer*         pServer         = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// ── Trimmed mean: discard top/bottom 20%, average middle 60% ─────────────
float trimmedMean(HX711 &scale, uint8_t n) {
  long samples[n];
  for (uint8_t i = 0; i < n; i++) {
    samples[i] = (long)scale.get_value(1) >> SHIFT_BITS;
  }

  // Bubble sort
  for (uint8_t i = 0; i < n - 1; i++) {
    for (uint8_t j = 0; j < n - i - 1; j++) {
      if (samples[j] > samples[j + 1]) {
        long tmp       = samples[j];
        samples[j]     = samples[j + 1];
        samples[j + 1] = tmp;
      }
    }
  }

  // Average middle 60%
  uint8_t trim  = n / 5;
  float   sum   = 0;
  uint8_t count = 0;
  for (uint8_t i = trim; i < n - trim; i++) {
    sum += samples[i];
    count++;
  }
  return (count > 0) ? (sum / count) : 0.0f;
}

// ── BLE callbacks ─────────────────────────────────────────────────────────
class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
    if (Serial) Serial.println("Client connected!");
  }
  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    if (Serial) Serial.println("Client disconnected!");
    BLEDevice::startAdvertising();
  }
};

class MyCharacteristicCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic* pCharacteristic) {
    std::string value = pCharacteristic->getValue();
    if (value.length() > 0) {
      String command = String(value.c_str());
      if (Serial) Serial.println("Received command: " + command);
      if (command == "TARE") {
        if (Serial) Serial.println("Taring all sensors...");
        scale1.tare(); scale2.tare(); scale3.tare(); scale4.tare();
        if (Serial) Serial.println("Tare complete!");
      }
    }
  }
};

// ── Setup ─────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(500);  // short settle — no while(!Serial), that blocks on battery

  BLEDevice::init("ESP32_LoadCells");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService* pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ   |
    BLECharacteristic::PROPERTY_WRITE  |
    BLECharacteristic::PROPERTY_NOTIFY |
    BLECharacteristic::PROPERTY_INDICATE
  );
  pCharacteristic->addDescriptor(new BLE2902());
  pCharacteristic->setCallbacks(new MyCharacteristicCallbacks());
  pService->start();

  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);
  BLEDevice::startAdvertising();
  if (Serial) Serial.println("BLE initialized");

  scale1.begin(DOUT1, CLK1); delay(500);
  scale2.begin(DOUT2, CLK2); delay(500);
  scale3.begin(DOUT3, CLK3); delay(500);
  scale4.begin(DOUT4, CLK4); delay(500);

  if (Serial) Serial.println("Taring...");
  for (int i = 0; i < 5; i++) { scale1.tare(); delay(500); }
  if (Serial) Serial.println("Done 1...");
  for (int i = 0; i < 5; i++) { scale2.tare(); delay(500); }
  if (Serial) Serial.println("Done 2...");
  for (int i = 0; i < 5; i++) { scale3.tare(); delay(500); }
  if (Serial) Serial.println("Done 3...");
  for (int i = 0; i < 5; i++) { scale4.tare(); delay(500); }
  if (Serial) Serial.println("Ready");
}

// ── Loop ──────────────────────────────────────────────────────────────────
void loop() {
  if (scale1.is_ready() && scale2.is_ready() &&
      scale3.is_ready() && scale4.is_ready()) {

    float p1 = trimmedMean(scale1, AVG_N);
    float p2 = trimmedMean(scale2, AVG_N);
    float p3 = trimmedMean(scale3, AVG_N);
    float p4 = trimmedMean(scale4, AVG_N);

    String data = "0," + String(p1, 1) + "," + String(p2, 1) + ","
                       + String(p3, 1) + "," + String(p4, 1);

    if (Serial) Serial.println(data);   // skipped silently on battery

    if (deviceConnected) {
      pCharacteristic->setValue(data.c_str());
      pCharacteristic->notify();
    }

    delay(LOOP_DELAY_MS);
  }
}
