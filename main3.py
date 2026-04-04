import pandas as pd
import time
from datetime import datetime
import os
import serial
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------
# File Setup
# -----------------------------
file = "data.csv"

if not os.path.exists(file):
    pd.DataFrame(columns=[
        "timestamp",
        "flow1", "flow2", "flow3",
        "pressure",
        "diff12", "diff23",
        "flow_ratio_12", "flow_ratio_23",
        "flag",
        "zone",
        "risk",
        "reason"
    ]).to_csv(file, index=False)

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
    sheet = client.open_by_key("1IBhZU0lZrZ1bY5e0MZMdcTYMtjm0xSFWIDvWg6dFHUs").worksheet("Sheet4")
    print("✅ Google Sheets Connected")
except Exception as e:
    print("⚠️ Google Sheets Error:", e)
    sheet = None

# -----------------------------
# Serial Setup
# -----------------------------
try:
    ser = serial.Serial('COM7', 115200, timeout=1)
    ser.dtr = False
    ser.rts = False
    ser.reset_input_buffer()
    print("✅ Connected to ESP8266")
except serial.SerialException as e:
    print(f"[ERROR] Serial Port Error: {e}")
    exit(1)

# -----------------------------
# Main Loop
# -----------------------------
# -----------------------------
# Main Loop
# -----------------------------
while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        if not line:
            continue

        if "START" in line:
            print("[INFO] ESP Ready")
            continue

        parts = line.split(",")

        if len(parts) != 4:
            print(f"[WARN] Bad data: {line}")
            continue

        # -----------------------------
        # Parse Data
        # -----------------------------
        flow1 = float(parts[0])
        flow2 = float(parts[1])
        flow3 = float(parts[2])
        pressure = float(parts[3])

        # -----------------------------
        # Compute
        # -----------------------------
        diff12 = abs(flow1 - flow2)
        diff23 = abs(flow2 - flow3)

        # ✅ Safe Ratio
        if flow1 < 0.1:
            flow_ratio_12 = 1
        else:
            flow_ratio_12 = flow2 / flow1

        if flow2 < 0.1:
            flow_ratio_23 = 1
        else:
            flow_ratio_23 = flow3 / flow2

        # -----------------------------
        # Leak Detection Logic
        # -----------------------------
        LEAK_DIFF_THRESHOLD = 0.9
        LEAK_RATIO_THRESHOLD = 1.3
        IMBALANCE_DIFF_THRESHOLD = 0.3

        flag = 0
        zone = "NORMAL"

        if flow1 == 0 and flow2 == 0 and flow3 == 0:
            risk = "LOW"
            reason = "No Flow"

        elif (diff12 > LEAK_DIFF_THRESHOLD or diff23 > LEAK_DIFF_THRESHOLD) and \
             (flow_ratio_12 > LEAK_RATIO_THRESHOLD or flow_ratio_23 > LEAK_RATIO_THRESHOLD):

            risk = "HIGH"
            flag = 1

            if diff12 > diff23:
                zone = "LEAK_1_2"
                reason = "Leak between S1-S2"
            else:
                zone = "LEAK_2_3"
                reason = "Leak between S2-S3"

        elif diff12 > IMBALANCE_DIFF_THRESHOLD or diff23 > IMBALANCE_DIFF_THRESHOLD:
            risk = "MEDIUM"
            reason = "Imbalance"

        else:
            risk = "LOW"
            reason = "Normal"

        # -----------------------------
        # Send command to Arduino
        # -----------------------------
        if risk == "HIGH":
            ser.write(b"ON\n")
        else:
            ser.write(b"OFF\n")

        # -----------------------------
        # Save Data
        # -----------------------------
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_row = [
            timestamp,
            flow1, flow2, flow3,
            pressure,
            diff12, diff23,
            flow_ratio_12, flow_ratio_23,
            flag,
            zone,
            risk,
            reason
        ]

        pd.DataFrame([new_row]).to_csv(file, mode='a', header=False, index=False)

        if sheet:
            try:
                sheet.append_row(
                    [str(x) for x in new_row],
                    value_input_option='USER_ENTERED'
                )
            except Exception as e:
                print("⚠️ Sheets error:", e)

        print(f"{timestamp} | {zone} | {risk}")

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(0.1)