#include "HX711.h"

// All HX711 pins
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
const uint16_t LOOP_DELAY_MS = 1;
const uint8_t SHIFT_BITS = 12;  // 24-12 = 12 effective bits

// ===== CHANGE THIS TO SELECT WHICH SENSOR TO CALIBRATE =====
const uint8_t ACTIVE_SENSOR = 1;  // 1, 2, 3, or 4
// ============================================================

void setup() {
  Serial.begin(9600);  // Match your notebook baudrate
  
  Serial.print("Calibrating Sensor ");
  Serial.println(ACTIVE_SENSOR);
  
  // Initialize all sensors
  scale1.begin(DOUT1, CLK1);
  delay(500);
  scale2.begin(DOUT2, CLK2);
  delay(500);
  scale3.begin(DOUT3, CLK3);
  delay(500);
  scale4.begin(DOUT4, CLK4);
  delay(500);

  // Tare only the active sensor
  Serial.print("Taring sensor ");
  Serial.print(ACTIVE_SENSOR);
  Serial.println("...");
  
  for(int i = 0; i < 5; i++) {
    if (ACTIVE_SENSOR == 1) scale1.tare();
    else if (ACTIVE_SENSOR == 2) scale2.tare();
    else if (ACTIVE_SENSOR == 3) scale3.tare();
    else if (ACTIVE_SENSOR == 4) scale4.tare();
    delay(500);
  }
  
  Serial.println("Ready for calibration");
  delay(1000);
}

void loop() {
  long raw_value = 0;
  bool ready = false;
  
  // Read only the active sensor
  if (ACTIVE_SENSOR == 1 && scale1.is_ready()) {
    raw_value = scale1.get_value(AVG_N);
    ready = true;
  }
  else if (ACTIVE_SENSOR == 2 && scale2.is_ready()) {
    raw_value = scale2.get_value(AVG_N);
    ready = true;
  }
  else if (ACTIVE_SENSOR == 3 && scale3.is_ready()) {
    raw_value = scale3.get_value(AVG_N);
    ready = true;
  }
  else if (ACTIVE_SENSOR == 4 && scale4.is_ready()) {
    raw_value = scale4.get_value(AVG_N);
    ready = true;
  }
  
  if (ready) {
    // Apply bit reduction
    float value = (raw_value >> SHIFT_BITS);
    
    // Send ONLY the number (no labels, matches your notebook format)
    Serial.println(value, 0);
    
    delay(LOOP_DELAY_MS);
  }
}
