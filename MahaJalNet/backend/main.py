from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import math

app = FastAPI(title="MahaJalNet AI Flood API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Load AI Model
# -----------------------------

MODEL_FILE = "ai_model/flood_model.json"

with open(MODEL_FILE, "r") as file:
    model = json.load(file)

training_data = model["training_data"]
k = model["k"]


# -----------------------------
# Input Data
# -----------------------------

class FloodData(BaseModel):
    rainfall: float
    water_level: float
    humidity: float
    drainage_blockage: float


# -----------------------------
# Normalize Input
# -----------------------------

def normalize(data):

    return [
        data[0] / 150,
        data[1] / 100,
        data[2] / 100,
        data[3] / 100
    ]


# -----------------------------
# Distance Calculation
# -----------------------------

def distance(a, b):

    total = 0

    for i in range(len(a)):
        total += (a[i] - b[i]) ** 2

    return math.sqrt(total)


# -----------------------------
# AI Prediction
# -----------------------------

def predict_flood(point):

    point = normalize(point)

    distances = []

    for features, label in training_data:

        d = distance(point, features)

        distances.append((d, label))

    distances.sort(key=lambda x: x[0])

    nearest = distances[:k]

    votes = {}

    for _, label in nearest:

        votes[label] = votes.get(label, 0) + 1

    prediction = max(votes, key=votes.get)

    confidence = (votes[prediction] / k) * 100

    return prediction, confidence


# -----------------------------
# Home API
# -----------------------------

@app.get("/")
def home():

    return {
        "project": "MahaJalNet",
        "system": "AI Flood Prediction",
        "status": "running"
    }


# -----------------------------
# AI Prediction API
# -----------------------------

@app.post("/predict")
def predict(data: FloodData):

    values = [
        data.rainfall,
        data.water_level,
        data.humidity,
        data.drainage_blockage
    ]

    risk, confidence = predict_flood(values)

    return {
        "rainfall_mm": data.rainfall,
        "water_level_percent": data.water_level,
        "humidity_percent": data.humidity,
        "drainage_blockage_percent": data.drainage_blockage,
        "predicted_flood_risk": risk,
        "confidence": round(confidence, 2)
    }