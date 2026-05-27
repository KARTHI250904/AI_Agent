from openai import OpenAI
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from pydantic import BaseModel
from database import init_db, get_connection
from model import predict_risk, explain_prediction
from auth import verify_password, create_token, SECRET_KEY, ALGORITHM
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = FastAPI()
security = HTTPBearer()

# =====================================================
# AUTH
# =====================================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except Exception:
        raise HTTPException(status_code=403, detail="Invalid token")


# =====================================================
# MODELS
# =====================================================
class Employee(BaseModel):

    employee_id: int
    # normalized values
    login_hour: float
    location_change: int
    network: int
    sensitive: int
    # normalized values
    records: float
    download: int

class Login(BaseModel):
    username: str
    password: str


# =====================================================
# STARTUP
# =====================================================
@app.on_event("startup")
def startup():
    init_db()


# =====================================================
# LOGIN
# =====================================================
@app.post("/login")
def login(user: Login):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE username=%s",
        (user.username,)
    )

    db_user = cursor.fetchone()

    conn.close()

    if not db_user or not verify_password(
        user.password,
        db_user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_token({
        "username": user.username,
        "role": db_user["role"]
    })

    return {
        "access_token": token
    }



# =====================================================
# RISK DECISION
# =====================================================
def decision(score):

    if score < 0.20:
        return "LOW RISK"

    elif score < 0.50:
        return "MEDIUM RISK"

    elif score < 0.75:
        return "HIGH RISK"

    return "CRITICAL RISK"


# =====================================================
# CUSTOM EXPLANATION FUNCTION
# =====================================================
def explain(
    login_hour,
    location_change,
    network,
    sensitive,
    records,
    download
):

    reasons = []

    if login_hour < 6 or login_hour > 22:
        reasons.append("Unusual login time")

    if location_change == 1:
        reasons.append("Location changed")

    if network == 1:
        reasons.append("Using unsecured network")

    if sensitive == 1:
        reasons.append("Sensitive data accessed")

    if records > 5000:
        reasons.append("High volume data access")

    if download == 1:
        reasons.append("Download attempt detected")

    return ", ".join(reasons) if reasons else "Normal behavior"


# =====================================================
# ANALYZE
# =====================================================
@app.post("/analyze")
def analyze(emp: Employee):

    features = [
        emp.login_hour,
        emp.location_change,
        emp.network,
        emp.sensitive,
        emp.records,
        emp.download
    ]

    # ========================================
    # PREDICT RISK SCORE
    # ========================================
    raw_score = predict_risk(features)

    try:
        score = float(raw_score)
    except Exception:
        score = 0.0

    # Keep score between 0 and 1
    score = max(0.0, min(score, 1.0))

    decision_result = decision(score)

    # ========================================
    # FEATURE IMPORTANCE / SHAP
    # ========================================
    raw_shap_values = explain_prediction(features)

    shap_values = []

    try:
        for value in raw_shap_values:
            shap_values.append(
                round(abs(float(value)), 4)
            )

    except Exception:
        shap_values = [0, 0, 0, 0, 0, 0]

    # Ensure exactly 6 values
    while len(shap_values) < 6:
        shap_values.append(0)

    shap_values = shap_values[:6]

    # ========================================
    # CUSTOM REASON
    # ========================================
    custom_reason = explain(
        emp.login_hour,
        emp.location_change,
        emp.network,
        emp.sensitive,
        emp.records,
        emp.download
    )

    # ========================================
    # EXPLANATION
    # ========================================
    explanation = {
        "message": "AI-based anomaly detection",

        "feature_importance": shap_values,

        "input_data": {
            "login_hour": emp.login_hour,
            "location_change": emp.location_change,
            "network": emp.network,
            "sensitive": emp.sensitive,
            "records": emp.records,
            "download": emp.download
        },

        "reason": custom_reason
    }

    # ========================================
    # SAVE LOG
    # ========================================
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO logs
        (employee_id, risk_score, decision, explanation)
        VALUES (%s,%s,%s,%s)
        """,
        (
            emp.employee_id,
            score,
            decision_result,
            str(explanation)
        )
    )

    conn.commit()
    conn.close()

    # ========================================
    # RESPONSE
    # ========================================
    return {
        "risk_score": round(score, 2),
        "decision": decision_result,
        "explanation": explanation
    }


# =====================================================
# ADMIN LOGS
# =====================================================
@app.get("/logs")
def get_logs(user=Depends(get_current_user)):

    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM logs ORDER BY id DESC"
    )

    data = cursor.fetchall()

    conn.close()

    return data