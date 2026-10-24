
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent
file = base / "dataset" / "AP_Crop_Suitability_Dataset_v3_Audited.csv"

df = pd.read_csv(file)
df.columns = df.columns.str.strip()

features = [
    "N_kg_ha", "P_kg_ha", "K_kg_ha", "pH",
    "Temperature_C", "Humidity_pct", "Rainfall_mm",
    "Soil_Moisture_pct"
]

print("\n1. AVERAGE CONDITIONS BY LABEL")
print(df.groupby("Suitable")[features].mean().round(2).T)

print("\n2. SOIL TYPE COUNTS BY LABEL")
print(pd.crosstab(df["Soil_Type"], df["Suitable"]))

print("\n3. WATER AVAILABILITY BY LABEL")
print(pd.crosstab(df["Water_Availability"], df["Suitable"]))

print("\n4. SAMPLE UNSUITABLE RECORDS")
print(
    df[df["Suitable"] == 0][
        ["Crop", "District", "Soil_Type", "pH",
         "Temperature_C", "Rainfall_mm", "Water_Availability",
         "Suitability_Score"]
    ].head(10).to_string(index=False)
)

print("\n5. SAMPLE SUITABLE RECORDS")
print(
    df[df["Suitable"] == 1][
        ["Crop", "District", "Soil_Type", "pH",
         "Temperature_C", "Rainfall_mm", "Water_Availability",
         "Suitability_Score"]
    ].head(10).to_string(index=False)
)

