#include "HX711.h"

#define DOUT 3
#define CLK  2

HX711 scale;

const uint8_t AVG_N = 10;
const uint16_t LOOP_DELAY_MS = 100;

void setup() {
  Serial.begin(9600);
  scale.begin(DOUT, CLK);
  delay(2000);
  
  // Tare Channel A (gain 128)
  Serial.println("Taring Channel A...");
  scale.set_gain(128);
  for(int i = 0; i < 5; i++) {
    scale.tare();
    delay(500);
  }
  
  // Tare Channel B (gain 32)
  Serial.println("Taring Channel B...");
  scale.set_gain(32);
  for(int i = 0; i < 5; i++) {
    scale.tare();
    delay(500);
  }
  
  Serial.println("Ready");
  delay(1000);
}

void loop() {
  if (scale.is_ready()) {
    // Read Channel A
    scale.set_gain(128);
    float p1 = scale.get_value(AVG_N);
    
    // Read Channel B
    scale.set_gain(32);
    float p2 = scale.get_value(AVG_N);
    
    // Output as comma-separated
    Serial.print(p1, 0);
    Serial.print(",");
    Serial.println(p2, 0);
  }
  
  delay(LOOP_DELAY_MS);
}
