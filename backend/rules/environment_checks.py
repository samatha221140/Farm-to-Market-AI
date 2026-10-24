
def check_environment(farm):
    warnings = []

    # General soil pH screening, not crop-specific suitability
    ph = float(farm["pH"])

    if ph < 5.5:
        warnings.append(
            "Soil is strongly acidic. Verify with a soil test."
        )
    elif ph < 6.5:
        warnings.append(
            "Soil is acidic. Check crop-specific pH requirements."
        )
    elif ph <= 7.5:
        warnings.append(
            "Soil pH is near neutral. Crop suitability still needs checking."
        )
    elif ph <= 8.5:
        warnings.append(
            "Soil is alkaline. Check crop tolerance and soil conditions."
        )
    else:
        warnings.append(
            "Soil is strongly alkaline. Get local soil-test guidance."
        )

    # Don't infer crop suitability from weather values alone
    warnings.append(
        "Temperature and rainfall must be assessed for the "
        "crop, district, and growing season."
    )

    return warnings


if __name__ == "__main__":
    sample_farm = {
        "pH": 6.8,
        "Temperature_C": 28,
        "Rainfall_mm": 700
    }

    for warning in check_environment(sample_farm):
        print("-", warning)
