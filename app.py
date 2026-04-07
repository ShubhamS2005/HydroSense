from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['GET'])
def predict():
    try:
        # Simulated real sensor values
        f1 = random.uniform(5, 30)
        f2 = random.uniform(5, 30)
        f3 = random.uniform(5, 30)

        total_flow = f1 + f2 + f3

        if total_flow > 50:
            leak = "YES"
            probability = 0.95
            severity = "High"
            zone = "Zone 1-2"
        elif total_flow > 30:
            leak = "NO"
            probability = 0.45
            severity = "Medium"
            zone = "Zone 2-3"
        else:
            leak = "NO"
            probability = 0.05
            severity = "Low"
            zone = "Stable"

        return jsonify({
            "flow1": round(f1, 2),
            "flow2": round(f2, 2),
            "flow3": round(f3, 2),
            "leak": leak,
            "leak_probability": probability,
            "severity": severity,
            "zone": zone
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "HydroSensi API Running 🚀"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True,threaded=True)