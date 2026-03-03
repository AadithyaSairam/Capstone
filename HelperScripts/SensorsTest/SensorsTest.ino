#include "HX711.h"

#define DOUT1 3
#define CLK1  2
#define DOUT2 5
#define CLK2  4
#define DOUT3 7
#define CLK3  6
#define DOUT4 9
#define CLK4  8

HX711 scales[4];
const uint8_t DOUT_PINS[] = {DOUT1, DOUT2, DOUT3, DOUT4};
const uint8_t CLK_PINS[]  = {CLK1,  CLK2,  CLK3,  CLK4};

void setup() {
  Serial.begin(9600);
  Serial.println("=== HX711 HARDWARE DIAGNOSTIC ===");

  // --- TEST 1: Initialization ---
  Serial.println("\n[TEST 1] Initializing sensors...");
  for (int i = 0; i < 4; i++) {
    scales[i].begin(DOUT_PINS[i], CLK_PINS[i]);
    delay(500);
    if (scales[i].is_ready()) {
      Serial.print("  Sensor "); Serial.print(i + 1); Serial.println(": PASS (ready)");
    } else {
      Serial.print("  Sensor "); Serial.print(i + 1); Serial.println(": FAIL (not ready - check wiring)");
    }
  }

  // --- TEST 2: Raw read (no tare) ---
  Serial.println("\n[TEST 2] Raw 24-bit reads (intentionally unshifted to catch hardware faults)...");
  for (int i = 0; i < 4; i++) {
    if (scales[i].is_ready()) {
      long raw = scales[i].get_value(3);  // Full 24-bit, no shift
      Serial.print("  Sensor "); Serial.print(i + 1);
      Serial.print(" raw 24-bit: "); Serial.println(raw);
      if (raw == 0 || raw == -1L || raw == 8388607L) {
        Serial.println("    ^ WARNING: Suspicious value, check DOUT/CLK connections");
      }
    }
  }


  // --- TEST 3: Tare stability ---
  Serial.println("\n[TEST 3] Tare stability (values in 12-bit space)...");
  for (int i = 0; i < 4; i++) {
    if (!scales[i].is_ready()) continue;
    long readings[5];
    for (int j = 0; j < 5; j++) {
      scales[i].tare();
      readings[j] = scales[i].get_value(5) >> SHIFT_BITS;  // ← shifted
      delay(300);
    }
    long minVal = readings[0], maxVal = readings[0];
    for (int j = 1; j < 5; j++) {
      if (readings[j] < minVal) minVal = readings[j];
      if (readings[j] > maxVal) maxVal = readings[j];
    }
    long spread = maxVal - minVal;
    Serial.print("  Sensor "); Serial.print(i + 1);
    Serial.print(" post-tare spread (12-bit): "); Serial.print(spread);
    Serial.println(spread < 2 ? "  -> STABLE" : "  -> NOISY (check power/ground)");
  }


  // --- TEST 4: Cross-talk check ---
  Serial.println("\n[TEST 4] Reading all sensors simultaneously...");
  bool allReady = true;
  for (int i = 0; i < 4; i++) allReady &= scales[i].is_ready();
  if (allReady) {
    for (int i = 0; i < 4; i++) {
      long val = scales[i].get_value(10) >> SHIFT_BITS;
      Serial.print("  S"); Serial.print(i + 1); Serial.print("="); Serial.print(val);
      if (i < 3) Serial.print("  ");
    }
    Serial.println();
    Serial.println("  -> If values drift while others are read, check shared power decoupling");
  }

  Serial.println("\n=== DIAGNOSTIC COMPLETE ===");
  Serial.println("Open Serial Plotter to monitor live values below:");
}

void loop() {
  // Live streaming for Serial Plotter — same format as your production code
  bool allReady = true;
  for (int i = 0; i < 4; i++) allReady &= scales[i].is_ready();

  if (allReady) {
    for (int i = 0; i < 4; i++) {
      long val = scales[i].get_value(5) >> 12;
      Serial.print(val);
      if (i < 3) Serial.print(",");
    }
    Serial.println();
    delay(100);
  }
}
