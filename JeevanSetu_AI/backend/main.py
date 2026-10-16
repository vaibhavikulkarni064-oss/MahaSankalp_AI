from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random


app = FastAPI(
    title="JeevanSetu AI",
    description="Smart Healthcare Emergency Coordination System"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================
# DATA MODEL
# =========================

class HealthData(BaseModel):

    patient_name: str
    age: int
    emergency_type: str
    phone: str
    condition: str
    description: str


# =========================
# AI PRIORITY ANALYSIS
# =========================

def calculate_priority(data):

    score = 0


    # Condition risk
    condition_scores = {

        "Unconscious": 45,

        "Critical": 40,

        "Serious": 30,

        "Stable": 10

    }

    score += condition_scores.get(
        data.condition,
        10
    )


    # Emergency type risk
    emergency_scores = {

        "Accident": 25,

        "Breathing Difficulty": 30,

        "Chest Pain": 30,

        "Severe Injury": 30,

        "High Fever": 15,

        "Pregnancy Emergency": 30,

        "Other": 10

    }

    score += emergency_scores.get(
        data.emergency_type,
        10
    )


    # Age factor
    if data.age <= 5 or data.age >= 65:

        score += 15

    elif data.age <= 12 or data.age >= 50:

        score += 10

    else:

        score += 5


    # Description analysis
    keywords = [

        "breathing",
        "unconscious",
        "bleeding",
        "chest",
        "pain",
        "accident",
        "injury",
        "pregnancy",
        "severe",
        "critical"

    ]

    description = data.description.lower()


    keyword_count = 0

    for word in keywords:

        if word in description:

            keyword_count += 1


    score += min(
        keyword_count * 2,
        10
    )


    # Maximum score
    score = min(
        score,
        100
    )


    # Priority classification

    if score >= 80:

        priority = "CRITICAL"

        message = (
            "Immediate medical attention is required. "
            "The case shows strong emergency indicators."
        )

    elif score >= 60:

        priority = "HIGH"

        message = (
            "High priority case detected. "
            "Prompt medical attention is recommended."
        )

    elif score >= 35:

        priority = "MEDIUM"

        message = (
            "Moderate priority detected. "
            "Medical evaluation is recommended."
        )

    else:

        priority = "LOW"

        message = (
            "Low priority detected. "
            "Routine medical consultation may be considered."
        )


    return score, priority, message


# =========================
# HOME API
# =========================

@app.get("/")
def home():

    return {

        "project":
        "JeevanSetu AI",

        "system":
        "Smart Healthcare Emergency Coordination",

        "status":
        "running"

    }


# =========================
# HEALTH ANALYSIS API
# =========================

@app.post("/analyse")
def analyse_health(
    data: HealthData
):

    score, priority, message = \
        calculate_priority(data)


    # Generate case ID
    case_id = (

        "JSA-"

        + datetime.now().strftime(
            "%Y%m%d"
        )

        + "-"

        + str(
            random.randint(
                1000,
                9999
            )
        )

    )


    return {

        "case_id":
        case_id,

        "score":
        score,

        "priority":
        priority,

        "message":
        message,

        "status":
        "Emergency Case Registered"

    }