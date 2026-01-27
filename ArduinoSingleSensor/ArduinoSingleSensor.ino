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


  // zero the sensor at no load
  scale.tare();
  for(int i = 0; i < 5; i++) {
      scale.tare();
      delay(500);
    }
}


void loop() {
  if (scale.is_ready()) {
    // raw counts minus tare offset (still "ADC units")
    float p1 = scale.get_value(AVG_N);
   
    // Placeholder values for sensors 2-4 (replace when you add more HX711s)
    float p2 = 0;
    float p3 = 0;
    float p4 = 0;
   
    // Send as comma-separated values (no spaces)
    Serial.println(p1, 0);
    // Serial.print(",");
    // Serial.print(p2, 35000);
    // Serial.print(",");
    // Serial.print(p3, 35000);
    // Serial.print(",");
    // Serial.println(p4, 35000);
   
    delay(LOOP_DELAY_MS);
  }
}