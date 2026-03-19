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

// ── Trimmed mean ──────────────────────────────────────────────────────────
float trimmedMean(HX711 &scale, uint8_t n) {
  long samples[n];
  for (uint8_t i = 0; i < n; i++) {
    samples[i] = (long)scale.get_value(1) >> SHIFT_BITS;
  }
  for (uint8_t i = 0; i < n - 1; i++) {
    for (uint8_t j = 0; j < n - i - 1; j++) {
      if (samples[j] > samples[j + 1]) {
        long tmp       = samples[j];
        samples[j]     = samples[j + 1];
        samples[j + 1] = tmp;
      }
    }
  }
  uint8_t trim  = n / 5;
  float   sum   = 0;
  uint8_t count = 0;
  for (uint8_t i = trim; i < n - trim; i++) {
    sum += samples[i];
    count++;
  }
  return (count > 0) ? (sum / count) : 0.0f;
}

bool initScale(HX711 &scale, uint8_t dout, uint8_t clk) {
  scale.begin(dout, clk);
  uint32_t start = millis();
  while (!scale.is_ready()) {
    if (millis() - start > 5000) {
      Serial.println("ERR: HX711 init timeout");
      return false;
    }
    delay(10);
  }
  return true;
}

// ── Setup ─────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(500);  // no while(!Serial) — works on both USB host and bare power

  Serial.println("Initializing sensors...");
  initScale(scale1, DOUT1, CLK1);
  initScale(scale2, DOUT2, CLK2);
  initScale(scale3, DOUT3, CLK3);
  initScale(scale4, DOUT4, CLK4);

  Serial.println("Taring...");
  for (int i = 0; i < 5; i++) { scale1.tare(); delay(500); }
  for (int i = 0; i < 5; i++) { scale2.tare(); delay(500); }
  for (int i = 0; i < 5; i++) { scale3.tare(); delay(500); }
  for (int i = 0; i < 5; i++) { scale4.tare(); delay(500); }
  Serial.println("READY");
}

// ── Loop ──────────────────────────────────────────────────────────────────
void loop() {
  // Accept "TARE" command from Python
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "TARE") {
      Serial.println("Taring...");
      scale1.tare(); scale2.tare(); scale3.tare(); scale4.tare();
      Serial.println("Tare complete");
    }
  }

  if (scale1.is_ready() && scale2.is_ready() &&
      scale3.is_ready() && scale4.is_ready()) {

    float p1 = trimmedMean(scale1, AVG_N);
    float p2 = trimmedMean(scale2, AVG_N);
    float p3 = trimmedMean(scale3, AVG_N);
    float p4 = trimmedMean(scale4, AVG_N);

    String data = "0," + String(p1, 1) + "," + String(p2, 1) + ","
                       + String(p3, 1) + "," + String(p4, 1);
    Serial.println(data);
    delay(LOOP_DELAY_MS);
  }
}
