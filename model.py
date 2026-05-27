import numpy as np
from sklearn.ensemble import IsolationForest

try:
    import shap
except Exception:
    shap = None

# Train model
def train_model():
    data = np.array([
        [9, 0, 0, 0, 50, 0],
        [10, 0, 0, 0, 100, 0],
        [11, 0, 0, 1, 200, 0],
        [14, 0, 0, 0, 150, 0],
        [16, 0, 0, 0, 300, 0],
        [18, 0, 0, 1, 400, 0],
    ])
    model = IsolationForest(contamination=0.2, random_state=42)
    model.fit(data)
    return model, data

model, background_data = train_model()

# SHAP explainer (uses KernelExplainer for compatibility)

print("SHAP LOADING...")

try:
    explainer = shap.KernelExplainer(model.decision_function, background_data[:50])
    print("SHAP LOADED SUCCESSFULLY")
except Exception as e:
    print("SHAP ERROR:", e)
    explainer = None

def predict_risk(features):
    features = np.array(features).reshape(1, -1)

    score_raw = model.decision_function(features)[0]

    # Normalize score (important)
    score_raw = model.decision_function(features)[0]

    # normalize between 0 and 1 properly
    score = (0.5 - score_raw)

    # clamp values
    score = max(0, min(score, 1))

    return min(max(score, 0), 1)

def explain_prediction(features):
    features = np.array(features).reshape(1, -1)

    if explainer is None:
        return ["SHAP not available"] * features.shape[1]

    shap_values = explainer.shap_values(features)
    return shap_values[0].tolist()