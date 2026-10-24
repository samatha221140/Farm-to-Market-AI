# Agronomic environmental thresholds for Andhra Pradesh and South Indian agro-climatic zones
CROP_ENVIRONMENT_RULES = {
    "Bajra": {
        "temperature": (20, 40),
        "ph": (6.0, 8.2),
        "rainfall": (350, 750),
        "optimal_desc": "Hardy dryland millet; drought tolerant; requires warm sunny weather.",
    },
    "Bengal Gram": {
        "temperature": (15, 32),
        "ph": (6.0, 8.0),
        "rainfall": (350, 700),
        "optimal_desc": "Thrives in cool to mild weather; sensitive to waterlogging.",
    },
    "Black Gram": {
        "temperature": (22, 36),
        "ph": (6.0, 7.8),
        "rainfall": (450, 850),
        "optimal_desc": "Short duration pulse; performs best in warm humid climate.",
    },
    "Chilli": {
        "temperature": (20, 35),
        "ph": (5.8, 7.5),
        "rainfall": (500, 1200),
        "optimal_desc": "Commercial cash crop; needs well-drained fertile soil with moderate moisture.",
    },
    "Cotton": {
        "temperature": (21, 38),
        "ph": (5.5, 8.5),
        "rainfall": (500, 1000),
        "optimal_desc": "Deep rooted fiber crop; needs warm season and deep black or red soil.",
    },
    "Green Gram": {
        "temperature": (22, 38),
        "ph": (6.2, 7.8),
        "rainfall": (350, 750),
        "optimal_desc": "Quick maturing pulse; fits well in intercropping and low rainfall zones.",
    },
    "Groundnut": {
        "temperature": (22, 34),
        "ph": (5.8, 7.6),
        "rainfall": (450, 950),
        "optimal_desc": "Important oilseed; needs friable, sandy-loam or red soil for pod development.",
    },
    "Jowar": {
        "temperature": (22, 38),
        "ph": (6.0, 8.5),
        "rainfall": (400, 850),
        "optimal_desc": "Drought-hardy cereal; withstands high temperatures and water stress.",
    },
    "Maize": {
        "temperature": (18, 35),
        "ph": (5.8, 7.8),
        "rainfall": (500, 1100),
        "optimal_desc": "High nutrient feeder; requires steady moisture and fertile well-drained soil.",
    },
    "Red Gram": {
        "temperature": (20, 36),
        "ph": (6.0, 7.8),
        "rainfall": (500, 1000),
        "optimal_desc": "Deep rooted drought-resilient pulse; excellent for dryland farming.",
    },
    "Rice": {
        "temperature": (20, 38),
        "ph": (5.5, 7.8),
        "rainfall": (900, 2500),
        "optimal_desc": "Major staple crop; requires high water availability or canal/borewell irrigation.",
    },
    "Sugarcane": {
        "temperature": (22, 38),
        "ph": (6.0, 8.2),
        "rainfall": (900, 2200),
        "optimal_desc": "Long duration commercial crop; needs abundant water and high fertility.",
    },
}


def check_crop_environment(crop, farm):
    rules = CROP_ENVIRONMENT_RULES.get(crop)

    if rules is None:
        return [
            "Crop-specific environmental rules not configured yet; verify locally."
        ]

    warnings = []

    if "temperature" in rules and "Temperature_C" in farm:
        low, high = rules["temperature"]
        temperature = float(farm["Temperature_C"])

        if not (low <= temperature <= high):
            warnings.append(
                f"Temperature {temperature}°C is outside the optimal range ({low}–{high}°C)."
            )

    if "ph" in rules and "pH" in farm:
        low, high = rules["ph"]
        ph = float(farm["pH"])

        if not (low <= ph <= high):
            warnings.append(
                f"Soil pH {ph} is outside the optimal range ({low}–{high})."
            )

    if "rainfall" in rules and "Rainfall_mm" in farm:
        low, high = rules["rainfall"]
        rain = float(farm["Rainfall_mm"])

        if rain < low:
            warnings.append(
                f"Rainfall {rain} mm is below optimal ({low}–{high} mm); supplementary irrigation advised."
            )
        elif rain > high:
            warnings.append(
                f"Rainfall {rain} mm is above optimal ({low}–{high} mm); ensure proper field drainage."
            )

    if warnings:
        return warnings

    return [
        "Optimal environmental match: temperature, pH, and rainfall align with crop requirements."
    ]
