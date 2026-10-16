def calculate_flood_risk(water_level, rainfall):
    """
    Calculate flood risk based on water level and rainfall.
    Values:
    water_level = percentage (0-100)
    rainfall = mm
    """

    if water_level >= 80 or rainfall >= 80:
        risk = "CRITICAL"

    elif water_level >= 60 or rainfall >= 50:
        risk = "HIGH"

    elif water_level >= 40 or rainfall >= 25:
        risk = "MODERATE"

    else:
        risk = "LOW"

    return risk


# Test
water_level = 32
rainfall = 18

risk = calculate_flood_risk(water_level, rainfall)

print("Water Level:", water_level, "%")
print("Rainfall:", rainfall, "mm")
print("Flood Risk:", risk)