#include "HX711.h"

#define DOUT1 3
#define CLK1  2
#define DOUT2 5
#define CLK2  4
#define DOUT3 7
#define CLK3  6
#define DOUT4 9
#define CLK4  8

const uint8_t SHIFT_BITS = 12;
const uint8_t SENSOR_TO_TEST = 2;  // ← CHANGE THIS (1, 2, 3, or 4)

uint8_t DOUT_PINS[] = {DOUT1, DOUT2, DOUT3, DOUT4};
uint8_t CLK_PINS[]  = {CLK1,  CLK2,  CLK3,  CLK4};

HX711 scale;

void setup() {
  Serial.begin(9600);
  uint8_t idx = SENSOR_TO_TEST - 1;

  Serial.println("================================");
  Serial.print("TESTING SENSOR "); Serial.println(SENSOR_TO_TEST);
  Serial.print("DOUT=pin"); Serial.print(DOUT_PINS[idx]);
  Serial.print("  CLK=pin"); Serial.println(CLK_PINS[idx]);
  Serial.println("================================");

  // TEST 1: Init
  Serial.println("\n[TEST 1] Initializing...");
  scale.begin(DOUT_PINS[idx], CLK_PINS[idx]);
  delay(500);
  if (scale.is_ready()) {
    Serial.println("✓ PASS: Sensor ready");
  } else {
    Serial.println("✗ FAIL: Not ready — check wiring/chip");
    while (true);  // Stop here, no point continuing
  }

  // TEST 2: Tare
  Serial.println("\n[TEST 2] Taring (5x)...");
  for (int i = 0; i < 5; i++) {
    scale.tare();
    delay(500);
    Serial.print("  Tare "); Serial.print(i + 1); Serial.println(" done");
  }
  Serial.println("✓ Tare complete");

  // TEST 3: Stability
  Serial.println("\n[TEST 3] Stability check (5 samples)...");
  long readings[5];
  for (int i = 0; i < 5; i++) {
    float raw = scale.get_value(5);
    readings[i] = (long)raw >> SHIFT_BITS;
    Serial.print("  Sample "); Serial.print(i + 1);
    Serial.print(": "); Serial.println(readings[i]);
    delay(300);
  }
  long minVal = readings[0], maxVal = readings[0];
  for (int i = 1; i < 5; i++) {
    if (readings[i] < minVal) minVal = readings[i];
    if (readings[i] > maxVal) maxVal = readings[i];
  }
  long spread = maxVal - minVal;
  Serial.print("  Spread: "); Serial.print(spread);
  Serial.println(spread < 2 ? "  ✓ STABLE" : "  ✗ NOISY — check power/ground");

  Serial.println("\n================================");
  Serial.print("SENSOR "); Serial.print(SENSOR_TO_TEST);
  Serial.println(" READY — live values below:");
  Serial.println("================================\n");
}

void loop() {
  if (scale.is_ready()) {
    float raw = scale.get_value(10);
    long val = (long)raw >> SHIFT_BITS;
    Serial.println(val);
    delay(100);
  }
}
