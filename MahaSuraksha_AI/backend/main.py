from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random

app = FastAPI(title="MahaSuraksha AI")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# DATA MODEL
# =========================

class FraudData(BaseModel):
    victim_name: str
    phone: str
    fraud_type: str
    amount: float
    suspicious_activity: str
    description: str


# =========================
# AI RISK ANALYSIS
# =========================

def calculate_risk(data):

    score = 0

    # Amount based risk
    if data.amount >= 100000:
        score += 40
    elif data.amount >= 50000:
        score += 30
    elif data.amount >= 10000:
        score += 20
    elif data.amount >= 1000:
        score += 10
    else:
        score += 5


    # Fraud type risk
    high_risk_types = [
        "Bank Fraud",
        "Investment Fraud",
        "Digital Extortion"
    ]

    medium_risk_types = [
        "UPI Fraud",
        "Phishing"
    ]

    if data.fraud_type in high_risk_types:
        score += 25

    elif data.fraud_type in medium_risk_types:
        score += 18

    else:
        score += 10


    # Suspicious activity risk
    activity_scores = {

        "OTP Sharing": 20,

        "Remote Access": 20,

        "Suspicious Transaction": 18,

        "Fake Website": 15,

        "Unknown Link": 12,

        "Unknown Call": 10

    }

    score += activity_scores.get(
        data.suspicious_activity,
        8
    )


    # Description based check
    keywords = [
        "otp",
        "password",
        "pin",
        "bank",
        "account",
        "urgent",
        "threat",
        "money",
        "payment"
    ]

    description = data.description.lower()

    keyword_count = 0

    for word in keywords:

        if word in description:
            keyword_count += 1


    score += min(keyword_count * 2, 10)


    # Limit score
    score = min(score, 100)


    # Risk classification
    if score >= 80:

        risk = "CRITICAL"

        message = (
            "Immediate attention required. "
            "The incident shows strong indicators "
            "of serious cyber fraud."
        )

    elif score >= 60:

        risk = "HIGH"

        message = (
            "High-risk incident detected. "
            "The case should be reviewed quickly."
        )

    elif score >= 35:

        risk = "MEDIUM"

        message = (
            "Moderate risk detected. "
            "Further verification is recommended."
        )

    else:

        risk = "LOW"

        message = (
            "Low risk detected, but the incident "
            "should still be recorded and reviewed."
        )


    return score, risk, message


# =========================
# HOME API
# =========================

@app.get("/")
def home():

    return {

        "project": "MahaSuraksha AI",

        "system":
        "Cyber Crime Intelligence System",

        "status":
        "running"

    }


# =========================
# FRAUD ANALYSIS API
# =========================

@app.post("/analyse")
def analyse_fraud(data: FraudData):

    score, risk, message = calculate_risk(data)


    case_id = (
        "MSA-"
        + datetime.now().strftime("%Y%m%d")
        + "-"
        + str(random.randint(1000, 9999))
    )


    return {

        "case_id": case_id,

        "risk_score": score,

        "risk_level": risk,

        "message": message,

        "status": "Case Registered"

    }