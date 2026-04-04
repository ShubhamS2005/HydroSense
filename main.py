import pandas as pd
import random
import time
from datetime import datetime
import joblib
import os

# Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from twilio.rest import Client


ACCOUNT_SID="ACf2d2eb9d56fcbf14ab27ded52e271ec0"
AUTH_TOKEN="d35cc1e34ed9727c61da8fb966bc9a20"
TWILIO_NUMBER="+19205161572"
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


# ==============================
# LOAD MODEL
# ==============================
model = joblib.load("model.pkl")

# ==============================
# LOCAL CSV SETUP
# ==============================
file = "data.csv"

if not os.path.exists(file):
    pd.DataFrame(columns=[
        "timestamp", "flow_node1", "flow_node2",
        "pressure", "flow_diff", "risk", "reason"
    ]).to_csv(file, index=False)

# ==============================
# GOOGLE SHEETS SETUP
# ==============================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

client = gspread.authorize(creds)

# 🔥 BEST PRACTICE: use sheet ID instead of name
sheet = client.open_by_key("1IBhZU0lZrZ1bY5e0MZMdcTYMtjm0xSFWIDvWg6dFHUs").sheet1

# ==============================
# DATA GENERATOR
# ==============================
def generate_data():
    flow1 = random.randint(95, 105)
    flow2 = flow1 - random.randint(0, 5)
    pressure = round(random.uniform(1.1, 1.3), 2)

    # Simulate leak
    if random.random() < 0.3:
        flow2 -= random.randint(20, 40)
        pressure -= 0.5

    return flow1, flow2, pressure

# ==============================
# MAIN LOOP
# ==============================
while True:
    flow1, flow2, pressure = generate_data()

    # Feature engineering
    flow_diff = flow1 - flow2

    # ML input
    input_data = pd.DataFrame([[flow1, flow2, pressure, flow_diff]],
        columns=['flow_node1', 'flow_node2', 'pressure', 'flow_diff']
    )

    # ML prediction
    ml_prediction = model.predict(input_data)

    # ==============================
    # 🔥 FINAL HYBRID LOGIC (BALANCED)
    # ==============================

    if flow_diff > 12:
        risk = "HIGH"
        reason = "High Flow Difference"

    elif pressure < 0.9:
        risk = "HIGH"
        reason = "Low Pressure"

    elif ml_prediction[0] == -1 and flow_diff > 6:
        risk = "MEDIUM"
        reason = "ML Suspicious Pattern"

    else:
        risk = "LOW"
        reason = "Normal"

    

    # ==============================
    # TIMESTAMP
    # ==============================
    timestamp = datetime.now()

    # ==============================
    # SAVE TO LOCAL CSV
    # ==============================
    new_row = pd.DataFrame([[timestamp, flow1, flow2, pressure, flow_diff, risk, reason]],
        columns=["timestamp", "flow_node1", "flow_node2", "pressure", "flow_diff", "risk", "reason"]
    )

    new_row.to_csv(file, mode='a', header=False, index=False)

    # ==============================
    # SAVE TO GOOGLE SHEETS
    # ==============================
    try:
        sheet.append_row([
            str(timestamp),
            flow1,
            flow2,
            pressure,
            flow_diff,
            risk,
            reason
        ])
    except Exception as e:
        print("⚠️ Cloud update failed:", e)

    # ==============================
    # CONSOLE OUTPUT
    # ==============================
    if risk == "HIGH":
        print(f"🚨 {timestamp} | F1:{flow1} F2:{flow2} P:{pressure} → HIGH ({reason})")

    elif risk == "MEDIUM":
        print(f"⚠️ {timestamp} | F1:{flow1} F2:{flow2} P:{pressure} → MEDIUM ({reason})")

    else:
        print(f"✅ {timestamp} | F1:{flow1} F2:{flow2} P:{pressure} → NORMAL")
    
    # if risk == "HIGH":
    #     alert_msg = f"""
    #  LEAK DETECTED!
    # Time: {timestamp}
    # Flow1: {flow1}
    # Flow2: {flow2}
    # Pressure: {pressure}
    # Reason: {reason}
    # """
    #     send_sms(alert_msg)

    time.sleep(3)