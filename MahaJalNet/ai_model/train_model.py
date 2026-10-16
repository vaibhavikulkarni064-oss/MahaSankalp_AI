import csv
import json
import math
import random


DATASET = "ai_model/flood_dataset.csv"
MODEL_FILE = "ai_model/flood_model.json"


# -----------------------------
# Load Dataset
# -----------------------------

X = []
y = []

with open(DATASET, "r") as file:

    reader = csv.DictReader(file)

    for row in reader:

        features = [
            float(row["rainfall_mm"]),
            float(row["water_level_percent"]),
            float(row["humidity_percent"]),
            float(row["drainage_blockage_percent"])
        ]

        X.append(features)
        y.append(row["flood_risk"])


# -----------------------------
# Normalize Data
# -----------------------------

def normalize(data):

    return [
        data[0] / 150,
        data[1] / 100,
        data[2] / 100,
        data[3] / 100
    ]


X = [normalize(row) for row in X]


# -----------------------------
# Train/Test Split
# -----------------------------

combined = list(zip(X, y))

random.seed(42)
random.shuffle(combined)

split = int(len(combined) * 0.8)

train_data = combined[:split]
test_data = combined[split:]


# -----------------------------
# K-Nearest Neighbors
# -----------------------------

def distance(a, b):

    total = 0

    for i in range(len(a)):
        total += (a[i] - b[i]) ** 2

    return math.sqrt(total)


def predict(point, training_data, k=7):

    distances = []

    for features, label in training_data:

        d = distance(point, features)

        distances.append((d, label))

    distances.sort(key=lambda x: x[0])

    nearest = distances[:k]

    votes = {}

    for _, label in nearest:

        votes[label] = votes.get(label, 0) + 1

    return max(votes, key=votes.get)


# -----------------------------
# Test Model
# -----------------------------

correct = 0

for features, actual in test_data:

    predicted = predict(features, train_data)

    if predicted == actual:
        correct += 1


accuracy = (correct / len(test_data)) * 100


# -----------------------------
# Save Model
# -----------------------------

model = {
    "algorithm": "K-Nearest Neighbors",
    "k": 7,
    "training_data": train_data
}

with open(MODEL_FILE, "w") as file:

    json.dump(model, file)


# -----------------------------
# Output
# -----------------------------

print("--------------------------------")
print("MahaJalNet AI Model")
print("--------------------------------")

print("Algorithm: K-Nearest Neighbors")
print("Training records:", len(train_data))
print("Testing records:", len(test_data))
print("Model accuracy:", round(accuracy, 2), "%")

print("Model saved:", MODEL_FILE)

print("--------------------------------")