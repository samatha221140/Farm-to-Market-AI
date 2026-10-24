from pathlib import Path
import sys

# Ensure local rules package imports work whether called from backend/ or rules/
RULES_DIR = Path(__file__).resolve().parent
if str(RULES_DIR) not in sys.path:
    sys.path.insert(0, str(RULES_DIR))

from crop_rules import CROP_RULES
from crop_seasons import CROP_SEASONS
from farm_input_validator import validate_farm_inputs
from environment_checks import check_environment
from crop_environment_rules import (
    CROP_ENVIRONMENT_RULES,
    check_crop_environment,
)

# Reference agronomic profiles derived from the dataset and regional ICAR/APAU benchmarks
CROP_PROFILES = {
    "Bajra":        {"N": 46.7, "P": 25.2, "K": 36.0, "temp": 29.8, "rain": 508.3, "humidity": 61.9},
    "Bengal Gram":  {"N": 22.9, "P": 29.9, "K": 42.7, "temp": 24.5, "rain": 512.7, "humidity": 61.7},
    "Black Gram":   {"N": 25.1, "P": 28.7, "K": 42.0, "temp": 27.7, "rain": 587.9, "humidity": 62.0},
    "Chilli":       {"N": 86.1, "P": 39.2, "K": 58.3, "temp": 25.6, "rain": 879.3, "humidity": 61.3},
    "Cotton":       {"N": 67.2, "P": 31.3, "K": 46.1, "temp": 27.7, "rain": 687.6, "humidity": 63.0},
    "Green Gram":   {"N": 24.1, "P": 30.5, "K": 38.6, "temp": 29.2, "rain": 455.8, "humidity": 59.3},
    "Groundnut":    {"N": 30.1, "P": 35.9, "K": 41.9, "temp": 25.4, "rain": 657.7, "humidity": 62.3},
    "Jowar":        {"N": 56.7, "P": 31.4, "K": 40.7, "temp": 29.9, "rain": 607.2, "humidity": 58.8},
    "Maize":        {"N": 79.3, "P": 42.7, "K": 45.3, "temp": 25.9, "rain": 665.8, "humidity": 62.9},
    "Red Gram":     {"N": 24.5, "P": 30.6, "K": 39.1, "temp": 27.3, "rain": 821.4, "humidity": 61.6},
    "Rice":         {"N": 81.8, "P": 40.8, "K": 45.2, "temp": 27.5, "rain": 1542.9, "humidity": 60.2},
    "Sugarcane":    {"N": 136.0, "P": 53.5, "K": 98.0, "temp": 28.1, "rain": 1231.9, "humidity": 60.1},
}


def nutrient_match(value, target, weight=10.0):
    """Return similarity score with agronomic asymmetry: surplus nutrients are penalized much less than deficits."""
    if value >= target:
        # Extra fertility is tolerated well by plants
        tolerance = max(target * 1.5, 40.0)
        diff = value - target
    else:
        # Nutrient deficiency harms crop yield
        tolerance = max(target * 0.75, 15.0)
        diff = target - value
    score = max(0.0, 1.0 - (diff / tolerance))
    return round(score * weight, 2)


def range_match(value, low, high, weight=10.0):
    """Return full points if within [low, high], with proportional drop outside."""
    if low <= value <= high:
        return weight
    span = max(high - low, 5.0)
    if value < low:
        diff = low - value
    else:
        diff = value - high
    fraction = max(0.0, 1.0 - (diff / span))
    return round(fraction * weight, 2)


def recommend_crops(farm, top_n=5):
    """
    Recommend crops based on:
    - Water Availability
    - Weather (Temperature, Humidity, Rainfall)
    - Soil Nutrients (N, P, K)
    - Soil pH
    - Soil Type
    - Season
    """
    errors = validate_farm_inputs(farm)

    if errors:
        return {
            "errors": errors,
            "recommendations": [],
            "warnings": [],
            "message": "Please correct the farm inputs."
        }

    soil_type = farm["Soil_Type"]
    water = farm["Water_Availability"]
    season = farm["Season"]
    temp = float(farm["Temperature_C"])
    rainfall = float(farm["Rainfall_mm"])
    humidity = float(farm.get("Humidity_pct", 65.0))
    ph = float(farm["pH"])

    water_level = {"Low": 1, "Medium": 2, "High": 3}
    actual_water = water_level[water]

    results = []

    for crop, rules in CROP_RULES.items():
        profile = CROP_PROFILES.get(crop)
        if profile is None:
            continue

        env_rules = CROP_ENVIRONMENT_RULES.get(crop, {})
        reasons = []
        breakdown = {}

        # 1. Soil Compatibility (20 points)
        if soil_type in rules["soil_types"]:
            soil_pts = 20.0
            reasons.append(f"Soil Type Match: {soil_type} soil is well-suited for {crop}.")
        else:
            soil_pts = 4.0
            reasons.append(f"Suboptimal Soil: {crop} prefers {', '.join(rules['soil_types'])}; {soil_type} soil needs conditioning.")
        breakdown["soil_score"] = soil_pts

        # 2. Water Availability (20 points)
        required_water = water_level[rules["water_need"]]
        if actual_water >= required_water:
            # Sensitive to waterlogging: dryland millets suffer in waterlogged soils
            if actual_water == 3 and crop in ["Bajra"]:
                water_pts = 8.0
                reasons.append(f"Waterlogging Risk: {crop} prefers low-rainfall/dryland conditions; canal waterlogging harms root systems.")
            else:
                water_pts = 20.0
                reasons.append(f"Water Availability Match: {water} availability comfortably satisfies the {rules['water_need']} requirement.")
        else:
            # Insufficient water
            deficit = required_water - actual_water
            if deficit == 1:
                water_pts = 7.0
                reasons.append(f"Water Deficit: {crop} needs {rules['water_need']} water; current {water} water may need irrigation.")
            else:
                water_pts = 0.0
                reasons.append(f"Severe Water Limitation: {crop} requires {rules['water_need']} water but farm has {water} availability.")
        breakdown["water_score"] = water_pts

        # 3. N-P-K Nutrients (20 points total: N=7, P=6.5, K=6.5)
        n_pts = nutrient_match(float(farm["N_kg_ha"]), profile["N"], weight=7.0)
        p_pts = nutrient_match(float(farm["P_kg_ha"]), profile["P"], weight=6.5)
        k_pts = nutrient_match(float(farm["K_kg_ha"]), profile["K"], weight=6.5)
        npk_pts = round(n_pts + p_pts + k_pts, 1)
        breakdown["npk_score"] = npk_pts
        reasons.append(f"Nutrient Affinity: N/P/K profile alignment score {npk_pts}/20.")

        # 4. Temperature Suitability (10 points)
        temp_range = env_rules.get("temperature", (20, 35))
        temp_pts = range_match(temp, temp_range[0], temp_range[1], weight=10.0)
        breakdown["temperature_score"] = temp_pts
        if temp_pts >= 8.5:
            reasons.append(f"Temperature Optimal: {temp}°C is within optimal range {temp_range[0]}–{temp_range[1]}°C.")
        else:
            reasons.append(f"Temperature Advisory: {temp}°C (optimal is {temp_range[0]}–{temp_range[1]}°C).")

        # 5. Rainfall & Humidity (15 points total: Rain=10, Humidity=5)
        rain_range = env_rules.get("rainfall", (400, 1000))
        rain_pts = range_match(rainfall, rain_range[0], rain_range[1], weight=10.0)
        humidity_pts = nutrient_match(humidity, profile["humidity"], weight=5.0)
        climate_pts = round(rain_pts + humidity_pts, 1)
        breakdown["rainfall_score"] = rain_pts
        breakdown["humidity_score"] = humidity_pts
        breakdown["climate_score"] = climate_pts

        # 6. Soil pH Suitability (10 points)
        ph_range = env_rules.get("ph", (6.0, 7.8))
        ph_pts = range_match(ph, ph_range[0], ph_range[1], weight=10.0)
        breakdown["ph_score"] = ph_pts
        if ph_pts >= 8.5:
            reasons.append(f"Soil pH Match: pH {ph} is within target range {ph_range[0]}–{ph_range[1]}.")
        else:
            reasons.append(f"Soil pH Advisory: pH {ph} (target is {ph_range[0]}–{ph_range[1]}).")

        # 7. Season Match (5 points bonus / adjustment)
        crop_seasons = CROP_SEASONS.get(crop, [])
        if season in crop_seasons or "Verify locally" in str(crop_seasons) or "Long-duration" in str(crop_seasons):
            season_pts = 5.0
            reasons.append(f"Growing Season: Aligns with {season} season cultivation.")
        else:
            season_pts = 1.0
            reasons.append(f"Season Note: Typically cultivated in {', '.join(crop_seasons) if crop_seasons else 'other seasons'}.")
        breakdown["season_score"] = season_pts

        # Total points out of 100
        raw_total = soil_pts + water_pts + npk_pts + temp_pts + rain_pts + humidity_pts + ph_pts + season_pts
        # Max achievable is 20 + 20 + 20 + 10 + 10 + 5 + 10 + 5 = 100
        score = round(min(100.0, max(0.0, raw_total)), 1)

        checks = check_crop_environment(crop, farm)

        results.append({
            "crop": crop,
            "score": score,
            "reasons": reasons,
            "breakdown": breakdown,
            "water_requirement": rules["water_need"],
            "suitable_soils": rules["soil_types"],
            "description": env_rules.get("optimal_desc", ""),
            "environment_checks": checks,
            "status": "Highly Recommended" if score >= 80 else ("Recommended" if score >= 65 else "Moderate Suitability")
        })

    # Sort descending by suitability score
    results.sort(key=lambda item: (-item["score"], item["crop"]))
    top_candidates = results[:top_n]

    return {
        "errors": [],
        "recommendations": top_candidates,
        "warnings": check_environment(farm),
        "message": f"Top {top_n} crops ranked based on water availability, weather, N-P-K, pH, and soil type."
    }


if __name__ == "__main__":
    sample_farm = {
        "N_kg_ha": 40,
        "P_kg_ha": 25,
        "K_kg_ha": 30,
        "pH": 6.8,
        "Temperature_C": 28,
        "Humidity_pct": 65,
        "Rainfall_mm": 700,
        "Soil_Type": "Red",
        "Water_Availability": "Low",
        "Season": "Kharif",
    }

    res = recommend_crops(sample_farm, top_n=5)
    print("TOP 5 CROPS:")
    for c in res["recommendations"]:
        print(f"{c['crop']}: {c['score']}% - {c['status']}")
