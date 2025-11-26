from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np

def is_anomalous(market_df, test_point, contamination=0.05):
    features = ["Quantity", "Net Weight (kg)", "Total Value (USD)"]
    market_df = market_df.dropna(subset=features)

    if len(market_df) < 10:
        return None, None

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(market_df[features])

    # Prediction
    prediction = model.predict([test_point])[0]  # -1 = anomaly
    anomaly = prediction == -1

    # Score (more negative = more anomalous)
    score_raw = model.decision_function([test_point])[0]

    # Normalize to 0–100 risk score (lower scores → higher risk)
    min_score = model.decision_function(market_df[features]).min()
    max_score = model.decision_function(market_df[features]).max()
    risk_score = 100 * (1 - (score_raw - min_score) / (max_score - min_score))
    risk_score = round(risk_score, 2)

    return anomaly, risk_score
