import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Load dataset
df = pd.read_csv("synthetic_data.csv")

# ✅ Feature engineering
df['flow_diff'] = df['flow_node1'] - df['flow_node2']

# ✅ Use full dataset (important)
X = df[['flow_node1', 'flow_node2', 'pressure', 'flow_diff']]

# ✅ Train Isolation Forest (less sensitive)
model = IsolationForest(
    contamination=0.05,   # reduced false positives
    random_state=42
)

model.fit(X)

# ✅ Save model
joblib.dump(model, "model.pkl")

print("✅ Model trained and saved successfully!")