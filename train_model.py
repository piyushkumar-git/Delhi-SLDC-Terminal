import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

print("Loading dataset...")
df = pd.read_csv("delhi_power_processed.csv")

features = ['hour', 'day_of_week', 'is_weekend', 'temperature_C', 'humidity']
target = 'demand_MW'

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training optimized Random Forest model...")
# 1. We reduced estimators to 50 and limited max_depth to 12
# This stops the trees from growing infinitely and bloating the file size
model = RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42)
model.fit(X_train, y_train)

print("Saving compressed model...")
# 2. We added 'compress=3' to physically zip the .pkl file internally
joblib.dump(model, "delhi_power_demand_model.pkl", compress=3)

print("Done! The model is now tiny and ready for GitHub.")