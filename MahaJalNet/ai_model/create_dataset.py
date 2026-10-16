import csv
import random

data = []

for _ in range(1000):

    rainfall = random.randint(0, 150)
    water_level = random.randint(0, 100)
    humidity = random.randint(40, 100)
    drainage_blockage = random.randint(0, 100)

    score = (
        rainfall * 0.35
        + water_level * 0.40
        + humidity * 0.05
        + drainage_blockage * 0.20
    )

    if score >= 70:
        risk = "CRITICAL"
    elif score >= 50:
        risk = "HIGH"
    elif score >= 30:
        risk = "MODERATE"
    else:
        risk = "LOW"

    data.append([
        rainfall,
        water_level,
        humidity,
        drainage_blockage,
        risk
    ])


file_path = "ai_model/flood_dataset.csv"

with open(file_path, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "rainfall_mm",
        "water_level_percent",
        "humidity_percent",
        "drainage_blockage_percent",
        "flood_risk"
    ])

    writer.writerows(data)


print("Dataset created successfully!")
print("Total records:", len(data))
print("File:", file_path)