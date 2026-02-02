#include "HX711.h"

// First HX711
#define DOUT1 3
#define CLK1  2

// Second HX711
#define DOUT2 5
#define CLK2  4

// Third HX711
#define DOUT3 7
#define CLK3  6

// Fourth HX711
#define DOUT4 9
#define CLK4  8

HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;

const uint8_t AVG_N = 10;
const uint16_t LOOP_DELAY_MS = 100;
const uint8_t SHIFT_BITS = 12;  // 24-12 = 12 effective bits

void setup() {
  Serial.begin(9600);
  
  // Initialize all HX711s
  scale1.begin(DOUT1, CLK1);
  delay(500);
  
  scale2.begin(DOUT2, CLK2);
  delay(500);
  
  scale3.begin(DOUT3, CLK3);
  delay(500);
  
  scale4.begin(DOUT4, CLK4);
  delay(500);

  // Tare all sensors (no load)
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
  
  Serial.println("Ready");
  delay(1000);
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
   
    // Send as comma-separated values
    Serial.print(p1, 0);
    Serial.print(",");
    Serial.print(p2, 0);
    Serial.print(",");
    Serial.print(p3, 0);
    Serial.print(",");
    Serial.println(p4, 0);
   
    delay(LOOP_DELAY_MS);
  }
}
