// ============================================================
// HydroSense Water Leakage Detection System
// ESP8266 NodeMCU - Final Updated Version
// Calibrated + Severity Based + Alert LEDs + 4s Buzzer Delay
// ============================================================

#include <string.h>

// ---------------- Pin Definitions ----------------
#define SENSOR1_PIN   4    // D2
#define SENSOR2_PIN   14   // D5
#define SENSOR3_PIN   12   // D6

#define LED_MAIN      5    // D1
#define BUZZER_PIN    13   // D7

#define LED_ALERT1    16   // D0
#define LED_ALERT2    15   // D8

// ---------------- Configuration ----------------
#define FLOW_CALIBRATION     7.5f
#define SAMPLE_INTERVAL_MS   1000

// Minimum calibrated flow to consider system active
#define MIN_FLOW_ACTIVE      0.7f

// Leak thresholds
#define THRESH_MEDIUM        0.80f
#define THRESH_HIGH          1.60f

// Exponential smoothing factor
#define SMOOTH_ALPHA         0.30f

// Calibration factors
const float K1 = 1.0f;
const float K2 = 0.76422677f;
const float K3 = 0.85095465f;

// ---------------- Pulse Counters ----------------
volatile unsigned long pulseCount1 = 0;
volatile unsigned long pulseCount2 = 0;
volatile unsigned long pulseCount3 = 0;

// ---------------- Flow Variables ----------------
float flow1 = 0.0f, flow2 = 0.0f, flow3 = 0.0f;
float flow1_cal = 0.0f, flow2_cal = 0.0f, flow3_cal = 0.0f;
float diff12_cal = 0.0f, diff23_cal = 0.0f, max_diff = 0.0f;

// ---------------- Timing ----------------
unsigned long lastSampleTime = 0;
unsigned long lastBlinkTime = 0;
unsigned long lastBuzzerToggleTime = 0;

// ---------------- Leak Confirmation Delay ----------------
unsigned long leakStartTime = 0;
bool leakTimerStarted = false;
bool buzzerEnabled = false;

const unsigned long BUZZER_DELAY = 0;   // 4 seconds

// ---------------- Alert States ----------------

bool alertState = false;
bool ledToggle = false;
bool buzzerToggle = false;

const unsigned long blinkIntervalMedium = 500;
const unsigned long blinkIntervalHigh   = 250;
const unsigned long buzzerIntervalHigh  = 200;

// ---------------- Output States ----------------
const char* zone = "NORMAL";
const char* severity = "LOW";
const char* statusText = "No Flow";
int flag = 0;

// ============================================================
// Interrupt Service Routines
// ============================================================
ICACHE_RAM_ATTR void pulseISR1() { pulseCount1++; }
ICACHE_RAM_ATTR void pulseISR2() { pulseCount2++; }
ICACHE_RAM_ATTR void pulseISR3() { pulseCount3++; }

// ============================================================
// Helper Functions
// ============================================================
void resetLeakTimer() {
  leakStartTime = 0;
  leakTimerStarted = false;
  buzzerEnabled = false;
}

void turnAllOutputsOff() {
  digitalWrite(LED_MAIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_ALERT1, LOW);
  digitalWrite(LED_ALERT2, LOW);

  alertState = false;
  ledToggle = false;
  buzzerToggle = false;
}

void setLowAlert() {
  turnAllOutputsOff();
}

void setMediumAlert() {
  digitalWrite(LED_MAIN, HIGH);
  digitalWrite(BUZZER_PIN, LOW);
  alertState = true;
}

void setHighAlert() {
  digitalWrite(LED_MAIN, HIGH);
  alertState = true;
}

void updateAlertEffects() {
  unsigned long now = millis();

  if (!alertState) {
    digitalWrite(LED_ALERT1, LOW);
    digitalWrite(LED_ALERT2, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    return;
  }

  if (strcmp(severity, "MEDIUM") == 0) {
    if (now - lastBlinkTime >= blinkIntervalMedium) {
      lastBlinkTime = now;
      ledToggle = !ledToggle;
      digitalWrite(LED_ALERT1, ledToggle);
      digitalWrite(LED_ALERT2, !ledToggle);
    }

    digitalWrite(BUZZER_PIN, LOW);
  }
  else if (strcmp(severity, "HIGH") == 0) {
    if (now - lastBlinkTime >= blinkIntervalHigh) {
      lastBlinkTime = now;
      ledToggle = !ledToggle;
      digitalWrite(LED_ALERT1, ledToggle);
      digitalWrite(LED_ALERT2, !ledToggle);
    }

    // Buzzer only after 4-second persistence
    if (buzzerEnabled) {
      if (now - lastBuzzerToggleTime >= buzzerIntervalHigh) {
        lastBuzzerToggleTime = now;
        buzzerToggle = !buzzerToggle;
        digitalWrite(BUZZER_PIN, buzzerToggle);
      }
    } else {
      digitalWrite(BUZZER_PIN, LOW);
    }
  }
  else {
    digitalWrite(LED_ALERT1, LOW);
    digitalWrite(LED_ALERT2, LOW);
    digitalWrite(BUZZER_PIN, LOW);
  }
}

void classifyLeak(float d12, float d23, float f1c, float f2c, float f3c) {
  max_diff = max(d12, d23);

  // Default
  zone = "NORMAL";
  severity = "LOW";
  statusText = "No Flow";
  flag = 0;

  bool systemActive = (f1c > MIN_FLOW_ACTIVE || f2c > MIN_FLOW_ACTIVE || f3c > MIN_FLOW_ACTIVE);

  if (!systemActive) {
    zone = "NORMAL";
    severity = "LOW";
    statusText = "No Flow";
    flag = 0;
    resetLeakTimer();
    setLowAlert();
    return;
  }

  if (max_diff < THRESH_MEDIUM) {
    zone = "NORMAL";
    severity = "LOW";
    statusText = "Stable Flow";
    flag = 0;
    resetLeakTimer();
    setLowAlert();
  }
  else if (max_diff < THRESH_HIGH) {
    zone = (d12 > d23) ? "LEAK_1_2" : "LEAK_2_3";
    severity = "MEDIUM";
    statusText = "Flow Imbalance";
    flag = 1;
    resetLeakTimer();
    setMediumAlert();
  }
  else {
    zone = (d12 > d23) ? "LEAK_1_2" : "LEAK_2_3";
    severity = "HIGH";
    statusText = "Leak Detected";
    flag = 1;

    if (!leakTimerStarted) {
      leakStartTime = millis();
      leakTimerStarted = true;
    }

    if (millis() - leakStartTime >= BUZZER_DELAY) {
      buzzerEnabled = true;
    }

    setHighAlert();
  }
}

// ============================================================
// Setup
// ============================================================
void setup() {
  Serial.begin(9600);
  delay(3000);

  pinMode(SENSOR1_PIN, INPUT_PULLUP);
  pinMode(SENSOR2_PIN, INPUT_PULLUP);
  pinMode(SENSOR3_PIN, INPUT_PULLUP);

  pinMode(LED_MAIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_ALERT1, OUTPUT);
  pinMode(LED_ALERT2, OUTPUT);

  turnAllOutputsOff();
  resetLeakTimer();

  attachInterrupt(digitalPinToInterrupt(SENSOR1_PIN), pulseISR1, RISING);
  attachInterrupt(digitalPinToInterrupt(SENSOR2_PIN), pulseISR2, RISING);
  attachInterrupt(digitalPinToInterrupt(SENSOR3_PIN), pulseISR3, RISING);

  Serial.println("START");
}

// ============================================================
// Main Loop
// ============================================================
void loop() {
  unsigned long now = millis();

  if (now - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = now;

    // Safe read
    noInterrupts();
    unsigned long p1 = pulseCount1;
    unsigned long p2 = pulseCount2;
    unsigned long p3 = pulseCount3;
    pulseCount1 = 0;
    pulseCount2 = 0;
    pulseCount3 = 0;
    interrupts();

    // Raw flow calculation
    float newFlow1 = (float)p1 / FLOW_CALIBRATION;
    float newFlow2 = (float)p2 / FLOW_CALIBRATION;
    float newFlow3 = (float)p3 / FLOW_CALIBRATION;

    // Exponential smoothing
    flow1 = (1.0f - SMOOTH_ALPHA) * flow1 + SMOOTH_ALPHA * newFlow1;
    flow2 = (1.0f - SMOOTH_ALPHA) * flow2 + SMOOTH_ALPHA * newFlow2;
    flow3 = (1.0f - SMOOTH_ALPHA) * flow3 + SMOOTH_ALPHA * newFlow3;

    // Calibration
    flow1_cal = flow1 * K1;
    flow2_cal = flow2 * K2;
    flow3_cal = flow3 * K3;

    // Differences
    diff12_cal = abs(flow1_cal - flow2_cal);
    diff23_cal = abs(flow2_cal - flow3_cal);

    // Classification
    classifyLeak(diff12_cal, diff23_cal, flow1_cal, flow2_cal, flow3_cal);

    // Serial Output:
    // rawFlow1,rawFlow2,rawFlow3,flow1_cal,flow2_cal,flow3_cal,diff12_cal,diff23_cal,max_diff,flag,zone,severity,status
    Serial.print(flow1, 3); Serial.print(",");
    Serial.print(flow2, 3); Serial.print(",");
    Serial.print(flow3, 3); Serial.print(",");

    Serial.print(flow1_cal, 3); Serial.print(",");
    Serial.print(flow2_cal, 3); Serial.print(",");
    Serial.print(flow3_cal, 3); Serial.print(",");

    Serial.print(diff12_cal, 3); Serial.print(",");
    Serial.print(diff23_cal, 3); Serial.print(",");
    Serial.print(max_diff, 3); Serial.print(",");

    Serial.print(flag); Serial.print(",");
    Serial.print(zone); Serial.print(",");
    Serial.print(severity); Serial.print(",");
    Serial.println(statusText);
  }

  updateAlertEffects();

  // Optional manual serial commands
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "ON") {
      digitalWrite(LED_MAIN, HIGH);
      digitalWrite(LED_ALERT1, HIGH);
      digitalWrite(LED_ALERT2, HIGH);
      digitalWrite(BUZZER_PIN, HIGH);
    }
    else if (cmd == "OFF") {
      resetLeakTimer();
      turnAllOutputsOff();
    }
  }
}