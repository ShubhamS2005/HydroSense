import pandas as pd
import time
from datetime import datetime
import os
import serial
import gspread
import joblib
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials

from twilio.rest import Client


ACCOUNT_SID="ACc612ceff513688356d3f970b20dbe848"
AUTH_TOKEN="fd592e476269312cf9c9829f016736d3"
TWILIO_NUMBER="+16626771421"
USER_NUMBER = "+919557235244"

sms_client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(message):
    try:
        sms_client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=USER_NUMBER
        )
        print("📩 SMS Sent!")
    except Exception as e:
        print("SMS Error:", e)

print("Program Started...")


# -----------------------------
# File Setup
# -----------------------------
file = "data.csv"

columns = [
    "timestamp",
    "raw_flow1", "raw_flow2", "raw_flow3",
    "flow1_cal", "flow2_cal", "flow3_cal",
    "diff12_cal", "diff23_cal", "max_diff",
    "flag",
    "zone",
    "severity",
    "status",
    "raw_diff12", "raw_diff23",
    "ratio12_cal", "ratio23_cal",
    "reason",
    "rule_zone", "rule_severity", "rule_status",
    "ml_zone", "ml_severity",
    "final_zone", "final_severity", "final_status",
    "decision_source"
]

if not os.path.exists(file):
    pd.DataFrame(columns=columns).to_csv(file, index=False)

# -----------------------------
# Google Sheets Setup
# -----------------------------
try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1IBhZU0lZrZ1bY5e0MZMdcTYMtjm0xSFWIDvWg6dFHUs").worksheet("Sheet7")
    print("✅ Google Sheets Connected")
except Exception as e:
    print("⚠️ Google Sheets Error:", e)
    sheet = None

# -----------------------------
# Serial Setup
# -----------------------------
try:
    ser = serial.Serial('COM7', 9600, timeout=1)
    ser.dtr = False
    ser.rts = False
    ser.reset_input_buffer()
    print("✅ Connected to ESP8266")
except serial.SerialException as e:
    print(f"[ERROR] Serial Port Error: {e}")
    exit(1)

# -----------------------------
# Load ML Models
# -----------------------------
USE_ML = True

try:
    zone_model = joblib.load("saved_models/zone_model.pkl")
    severity_model = joblib.load("saved_models/severity_model.pkl")
    zone_encoder = joblib.load("saved_models/zone_label_encoder.pkl")
    severity_encoder = joblib.load("saved_models/severity_label_encoder.pkl")
    print("✅ ML models loaded successfully")
except Exception as e:
    print("⚠️ ML models not loaded, running threshold-only mode:", e)
    USE_ML = False

# -----------------------------
# Threshold Settings
# Primary layer gets more weight
# -----------------------------
NO_FLOW_THRESHOLD = 0.10
LOW_FLOW_THRESHOLD = 0.30

MEDIUM_DIFF_THRESHOLD = 0.12
HIGH_DIFF_THRESHOLD = 0.30
CRITICAL_DIFF_THRESHOLD = 0.60

RATIO_LOW_WARNING = 0.90
RATIO_HIGH_WARNING = 1.10
RATIO_LOW_CRITICAL = 0.75
RATIO_HIGH_CRITICAL = 1.25


# -----------------------------
# Helper Functions
# -----------------------------
def safe_ratio(a, b):
    return a / b if b > 0.001 else 0.0


def rule_based_decision(flow1_cal, flow2_cal, flow3_cal, diff12_cal, diff23_cal, ratio12_cal, ratio23_cal):
    """
    Primary rule-based leak detection.
    This gets higher weight than ML.
    """
    avg_flow = (flow1_cal + flow2_cal + flow3_cal) / 3.0

    # No flow
    if avg_flow <= NO_FLOW_THRESHOLD:
        return "NORMAL", "LOW", "No Flow", 0, "No water flow detected"

    # Very low flow
    if avg_flow <= LOW_FLOW_THRESHOLD:
        return "NORMAL", "LOW", "Low Flow", 0, "Very low but stable flow"

    # Decide leak zone using calibrated diffs
    if diff12_cal > diff23_cal:
        zone = "LEAK_1_2"
        main_diff = diff12_cal
        main_ratio = ratio12_cal
    else:
        zone = "LEAK_2_3"
        main_diff = diff23_cal
        main_ratio = ratio23_cal

    # Severity from thresholds
    if main_diff >= CRITICAL_DIFF_THRESHOLD or main_ratio <= RATIO_LOW_CRITICAL or main_ratio >= RATIO_HIGH_CRITICAL:
        return zone, "HIGH", "Leak Detected", 1, f"Critical threshold breach at {zone}"

    if main_diff >= HIGH_DIFF_THRESHOLD or main_ratio <= RATIO_LOW_WARNING or main_ratio >= RATIO_HIGH_WARNING:
        return zone, "MEDIUM", "Flow Imbalance", 1, f"Moderate threshold imbalance at {zone}"

    if main_diff >= MEDIUM_DIFF_THRESHOLD:
        return zone, "MEDIUM", "Flow Imbalance", 0, f"Mild threshold imbalance at {zone}"

    return "NORMAL", "LOW", "Normal", 0, "Thresholds indicate stable flow"


def ml_decision(flow1_cal, flow2_cal, flow3_cal, pressure, diff12_cal, diff23_cal, ratio12_cal, ratio23_cal):
    """
    Secondary ML layer.
    """
    if not USE_ML:
        return "NORMAL", "LOW"

    input_df = pd.DataFrame([{
        "flow1_cal": flow1_cal,
        "flow2_cal": flow2_cal,
        "flow3_cal": flow3_cal,
        "pressure": pressure,
        "diff12_cal": diff12_cal,
        "diff23_cal": diff23_cal,
        "ratio12_cal": ratio12_cal,
        "ratio23_cal": ratio23_cal
    }])

    zone_pred = zone_model.predict(input_df)[0]
    severity_pred = severity_model.predict(input_df)[0]

    ml_zone = zone_encoder.inverse_transform([zone_pred])[0]
    ml_severity = severity_encoder.inverse_transform([severity_pred])[0]

    return ml_zone, ml_severity


def hybrid_decision(rule_zone, rule_severity, rule_status, rule_flag,
                    ml_zone, ml_severity, flow1_cal, flow2_cal, flow3_cal,
                    diff12_cal, diff23_cal):
    """
    Hybrid fusion:
    - Rules have priority
    - ML supports or upgrades only in ambiguous cases
    """

    avg_flow = (flow1_cal + flow2_cal + flow3_cal) / 3.0

    # Case 1: rule says no flow / normal -> trust it strongly
    if rule_status == "No Flow":
        return rule_zone, rule_severity, rule_status, "RULE_PRIMARY"

    # Case 2: hard leak from thresholds -> trust rule strongly
    if rule_flag == 1 and rule_severity == "HIGH":
        return rule_zone, rule_severity, "Leak Detected", "RULE_PRIMARY"

    # Case 3: if both agree -> strong confidence
    if rule_zone == ml_zone and rule_severity == ml_severity:
        final_status = "Leak Detected" if rule_zone != "NORMAL" else "Normal"
        return rule_zone, rule_severity, final_status, "RULE+ML_AGREE"

    # Case 4: if rule says NORMAL but ML says leak
    # only accept ML if flow is active and diff is meaningful
    if rule_zone == "NORMAL" and ml_zone != "NORMAL":
        if avg_flow > LOW_FLOW_THRESHOLD and max(diff12_cal, diff23_cal) > MEDIUM_DIFF_THRESHOLD:
            final_status = "Flow Imbalance"
            return ml_zone, ml_severity, final_status, "ML_SUPPORT"
        else:
            return rule_zone, rule_severity, "Normal", "RULE_PRIMARY"

    # Case 5: if rule detects leak and ML disagrees, keep rule
    if rule_zone != "NORMAL" and ml_zone == "NORMAL":
        final_status = "Leak Detected" if rule_severity == "HIGH" else "Flow Imbalance"
        return rule_zone, rule_severity, final_status, "RULE_PRIMARY"

    # Case 6: both say leak but different zones
    # use bigger diff to choose zone, severity prefers higher one
    if rule_zone != "NORMAL" and ml_zone != "NORMAL" and rule_zone != ml_zone:
        zone = "LEAK_1_2" if diff12_cal >= diff23_cal else "LEAK_2_3"

        severity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        final_severity = rule_severity if severity_order[rule_severity] >= severity_order[ml_severity] else ml_severity
        final_status = "Leak Detected" if final_severity == "HIGH" else "Flow Imbalance"
        return zone, final_severity, final_status, "HYBRID_RESOLVE"

    # default fallback
    final_status = "Leak Detected" if rule_zone != "NORMAL" else "Normal"
    return rule_zone, rule_severity, final_status, "RULE_PRIMARY"


def build_reason(final_zone, final_severity, final_status, decision_source):
    if final_status == "No Flow":
        return "No water flow detected"
    if final_zone == "NORMAL":
        return f"Stable flow pattern ({decision_source})"
    if final_severity == "HIGH":
        
        return f"High leak detected at {final_zone} ({decision_source})"
    if final_severity == "MEDIUM":
        return f"Moderate imbalance detected at {final_zone} ({decision_source})"
    return f"Low anomaly at {final_zone} ({decision_source})"


# -----------------------------
# Main Loop
# -----------------------------
while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        if not line:
            continue

        # Ignore debug lines
        if "[" in line or "START" in line:
            print("[INFO]", line)
            continue

        parts = line.split(",")

        # Expected 13 values from ESP
        if len(parts) != 13:
            print(f"[WARN] Bad data ({len(parts)} fields): {line}")
            continue

        # -----------------------------
        # Parse Data from ESP
        # -----------------------------
        raw_flow1   = float(parts[0])
        raw_flow2   = float(parts[1])
        raw_flow3   = float(parts[2])

        flow1_cal   = float(parts[3])
        flow2_cal   = float(parts[4])
        flow3_cal   = float(parts[5])

        diff12_cal  = float(parts[6])
        diff23_cal  = float(parts[7])
        max_diff    = float(parts[8])

        flag        = int(parts[9])   # old ESP threshold flag
        zone        = parts[10].strip()
        severity    = parts[11].strip()
        status      = parts[12].strip()

        # -----------------------------
        # Extra Derived Features
        # -----------------------------
        raw_diff12 = abs(raw_flow1 - raw_flow2)
        raw_diff23 = abs(raw_flow2 - raw_flow3)

        ratio12_cal = safe_ratio(flow1_cal, flow2_cal)
        ratio23_cal = safe_ratio(flow2_cal, flow3_cal)

        pressure = 1.0  # fixed for now

        # -----------------------------
        # Primary Rule-Based Decision
        # -----------------------------
        rule_zone, rule_severity, rule_status, rule_flag, rule_reason = rule_based_decision(
            flow1_cal, flow2_cal, flow3_cal,
            diff12_cal, diff23_cal,
            ratio12_cal, ratio23_cal
        )

        # -----------------------------
        # Secondary ML Decision
        # -----------------------------
        ml_zone, ml_severity = ml_decision(
            flow1_cal, flow2_cal, flow3_cal, pressure,
            diff12_cal, diff23_cal,
            ratio12_cal, ratio23_cal
        )

        # -----------------------------
        # Final Hybrid Decision
        # -----------------------------
        final_zone, final_severity, final_status, decision_source = hybrid_decision(
            rule_zone, rule_severity, rule_status, rule_flag,
            ml_zone, ml_severity,
            flow1_cal, flow2_cal, flow3_cal,
            diff12_cal, diff23_cal
        )

        reason = build_reason(final_zone, final_severity, final_status, decision_source)

        # -----------------------------
        # SMS Alert Logic
        # -----------------------------
        if final_zone != "NORMAL" and final_severity in ["HIGH", "MEDIUM"]:
            sms_message = (
                f"Leak Alert!\n"
                f"Zone: {final_zone}\n"
                f"Severity: {final_severity}\n"
                f"Status: {final_status}\n"
                f"Reason: {reason}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            send_sms(sms_message)

        # -----------------------------
        # Save Data
        # -----------------------------
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_row = [
            timestamp,
            raw_flow1, raw_flow2, raw_flow3,
            flow1_cal, flow2_cal, flow3_cal,
            diff12_cal, diff23_cal, max_diff,
            flag,
            zone,
            severity,
            status,
            raw_diff12, raw_diff23,
            ratio12_cal, ratio23_cal,
            reason,
            rule_zone, rule_severity, rule_status,
            ml_zone, ml_severity,
            final_zone, final_severity, final_status,
            decision_source
        ]

        pd.DataFrame([new_row], columns=columns).to_csv(file, mode='a', header=False, index=False)

        if sheet:
            try:
                sheet.append_row([str(x) for x in new_row], value_input_option='USER_ENTERED')
            except Exception as e:
                print("⚠️ Sheets error:", e)

        print(
            f"{timestamp} | "
            f"ESP: {zone}/{severity}/{status} | "
            f"RULE: {rule_zone}/{rule_severity}/{rule_status} | "
            f"ML: {ml_zone}/{ml_severity} | "
            f"FINAL: {final_zone}/{final_severity}/{final_status} | "
            f"SRC: {decision_source}"
        )

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(0.1)