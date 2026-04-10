# 💧 Smart Water Leakage Detection System  
### IoT | Real-Time Monitoring | Data Analytics | Web & Mobile Integration  

---

## 📌 Overview
The Smart Water Leakage Detection System is an IoT-based solution designed to monitor, detect, and localize water leakage in real time. The system integrates ESP8266 (NodeMCU), multi-point flow sensors, Python-based data processing, and cloud/web interfaces to provide accurate leak detection with severity classification.

It uses flow imbalance analysis and intelligent threshold logic to identify leakage zones, helping in efficient water management and reducing water wastage.

---

## 🎯 Key Highlights
- Leak localization (zone-based detection)  
- Real-time flow monitoring  
- Severity classification (LOW / MEDIUM / HIGH)  
- Cloud integration using Google Sheets  
- Local data storage (CSV)  
- Web dashboard visualization  
- Mobile app support  
- Alert system (buzzer/speaker)  

---

## 🛠️ Tech Stack

### Hardware
- ESP8266 (NodeMCU)  
- Water Flow Sensors (3-point system)  
- Buzzer / Speaker  
- Relay Module (optional)  

### Software
- Arduino IDE (Embedded C/C++)  
- Python  
- Pandas  
- PySerial  
- gspread (Google Sheets API)  
- HTML, CSS, JavaScript  

---

## ⚙️ System Architecture

Flow Sensors → ESP8266 → Serial Communication → Python Processing → CSV + Google Sheets → Web/App Dashboard  

---

## 🔄 Workflow
1. ESP8266 reads flow sensor data in real-time  
2. Sends raw and calibrated values via serial communication  
3. Python script processes data:
   - Parses incoming values  
   - Calculates flow differences and ratios  
   - Detects leakage conditions  
   - Identifies zone and severity  
4. Data is stored locally (CSV) and on cloud (Google Sheets)  
5. Web dashboard and mobile app display results  

---

## 🧠 Detection Logic

- diff12 = |flow1 - flow2|  
- diff23 = |flow2 - flow3|  

### Decision Rules
- Large difference → Leakage detected  
- Position of imbalance → Determines zone  
- Magnitude → Determines severity  

### Additional Logic
- Flow ratio calculation  
- No-flow condition detection  
- Human-readable reason generation  

---

## 📂 Project Structure

Water-Leakage-Detection/  
│── arduino/  
│   └── flow_sensor_code.ino  
│  
│── python/  
│   └── data_logger.py  
│  
│── web/  
│   ├── index.html  
│   ├── dashboard.js  
│   └── styles.css  
│  
│── app/  
│   └── mobile_app_files/  
│  
│── data/  
│   └── data.csv  
│  
│── credentials.json  
│── README.md  

---

## 🔌 Python Module Responsibilities
- Serial communication with ESP8266  
- Real-time data parsing  
- Feature engineering (differences & ratios)  
- Leakage detection logic  
- CSV logging  
- Google Sheets integration  
- Console output monitoring  

---

## 📊 Sample Output

2026-04-07 22:30:10 | Zone: Zone 2 | Severity: HIGH | Status: Leak Detected  

---

## 📍 Applications
- Smart homes  
- Industrial pipelines  
- Water supply systems  
- Agriculture irrigation  
- Smart city infrastructure  

---
---

## 🤖 AI/ML Integration

This project incorporates data-driven techniques for intelligent leakage detection. The system analyzes flow patterns using derived features such as flow differences and ratios to detect anomalies.

### Current Approach
- Feature Engineering:
  - Flow differences (diff12, diff23)
  - Flow ratios (ratio12, ratio23)
- Rule-based anomaly detection using thresholds  
- Classification of leakage severity (LOW / MEDIUM / HIGH)  

### ML Extension (Future Scope)
- Supervised learning models (e.g., Decision Tree, Random Forest) for leak prediction  
- Time-series analysis for pattern recognition  
- Anomaly detection using Isolation Forest  
- Predictive maintenance using historical data  

This approach enables the system to evolve from rule-based detection to fully intelligent AI-driven leakage prediction.

## 🔮 Future Enhancements
- AI/ML-based leakage prediction  
- SMS / mobile notifications  
- Automatic valve control system  
- Map-based leak visualization  
- Advanced analytics dashboard  

---

## 👨‍💻 Author
Roshni kumari , Shubham Srivastava ,Aman Kumar Ranjan ,Kush Bansal
B.Tech Computer Science Engineering  

---

## ⭐ Conclusion
This project provides a scalable, efficient, and intelligent solution for real-time water leakage detection using IoT and data analytics, helping to conserve water and improve monitoring systems.

---
