import math


def validate_farm_inputs(farm):
    errors = []

    # Map possible alternative input field names to canonical names
    aliases_map = {
        "N_kg_ha": ["N_kg_ha", "N", "n", "nitrogen"],
        "P_kg_ha": ["P_kg_ha", "P", "p", "phosphorus"],
        "K_kg_ha": ["K_kg_ha", "K", "k", "potassium"],
        "pH": ["pH", "ph", "Ph"],
        "Temperature_C": ["Temperature_C", "temperature", "temp"],
        "Rainfall_mm": ["Rainfall_mm", "rainfall", "rain"],
        "Humidity_pct": ["Humidity_pct", "humidity", "Humidity"],
        "Soil_Type": ["Soil_Type", "soil_type", "soil"],
        "Water_Availability": ["Water_Availability", "water_availability", "water"],
        "Season": ["Season", "season"],
    }

    # Normalize keys into canonical farm dictionary
    for canonical, alt_list in aliases_map.items():
        if canonical not in farm:
            for alt in alt_list:
                if alt in farm:
                    farm[canonical] = farm[alt]
                    break

    # 1. Validate numeric inputs
    numeric_limits = {
        "N_kg_ha": (0, 500),
        "P_kg_ha": (0, 500),
        "K_kg_ha": (0, 500),
        "pH": (0, 14),
        "Temperature_C": (-10, 60),
        "Rainfall_mm": (0, 10000),
        "Humidity_pct": (0, 100),
    }

    # Default humidity to 65 if omitted
    if "Humidity_pct" not in farm or farm["Humidity_pct"] is None:
        farm["Humidity_pct"] = 65.0

    for field, (minimum, maximum) in numeric_limits.items():
        if field not in farm or farm[field] is None or farm[field] == "":
            errors.append(f"Missing input: {field}")
            continue

        try:
            value = float(farm[field])
        except (ValueError, TypeError):
            errors.append(f"{field} must be a number.")
            continue

        if not math.isfinite(value):
            errors.append(f"{field} must be a finite number.")
            continue

        if not minimum <= value <= maximum:
            errors.append(
                f"{field} must be between {minimum} and {maximum}."
            )
            continue

        farm[field] = value

    # 2. Normalize soil names
    soil_aliases = {
        "alluvial": "Alluvial",
        "black": "Black",
        "clay": "Clay",
        "loamy": "Loamy",
        "red": "Red",
        "sandy": "Sandy",
    }

    soil_value = farm.get("Soil_Type")

    if isinstance(soil_value, str):
        normalized_soil = soil_value.strip().lower()

        if normalized_soil.endswith(" soil"):
            normalized_soil = normalized_soil[:-5].strip()

        if normalized_soil in soil_aliases:
            farm["Soil_Type"] = soil_aliases[normalized_soil]
        else:
            errors.append(
                "Invalid Soil_Type. Use Alluvial, Black, Clay, Loamy, "
                "Red, or Sandy."
            )
    else:
        errors.append(
            "Invalid Soil_Type. Use Alluvial, Black, Clay, Loamy, Red, or Sandy."
        )

    # 3. Normalize water availability
    water_aliases = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
    }

    water_value = farm.get("Water_Availability")

    if isinstance(water_value, str):
        normalized_water = water_value.strip().lower()

        if normalized_water in water_aliases:
            farm["Water_Availability"] = water_aliases[normalized_water]
        else:
            errors.append(
                "Invalid Water_Availability. Use Low, Medium, or High."
            )
    else:
        errors.append(
            "Invalid Water_Availability. Use Low, Medium, or High."
        )

    # 4. Normalize season
    season_aliases = {
        "kharif": "Kharif",
        "rabi": "Rabi",
        "summer": "Summer",
        "zaid": "Summer",
    }

    season_value = farm.get("Season")

    if isinstance(season_value, str):
        normalized_season = season_value.strip().lower()

        if normalized_season in season_aliases:
            farm["Season"] = season_aliases[normalized_season]
        else:
            errors.append("Season must be Kharif, Rabi, or Summer.")
    else:
        # Default to Kharif if not specified
        farm["Season"] = "Kharif"

    return errors
