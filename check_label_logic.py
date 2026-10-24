
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent
path = base / "dataset" / "AP_Crop_Suitability_Dataset_v3_Audited.csv"

df = pd.read_csv(path)
df.columns = df.columns.str.strip()

print("ROWS WHERE LABEL IS 0 BUT SCORE > 60:")
print(df[(df["Suitable"] == 0) &
         (df["Suitability_Score"] > 60)].shape[0])

print("\nROWS WHERE LABEL IS 1 BUT SCORE <= 60:")
print(df[(df["Suitable"] == 1) &
         (df["Suitability_Score"] <= 60)].shape[0])

print("\nSAMPLE SUITABLE ROWS:")
print(
    df[df["Suitable"] == 1][
        ["Crop", "Soil_Type", "N_kg_ha", "P_kg_ha",
         "K_kg_ha", "pH", "Rainfall_mm",
         "Water_Availability", "Suitability_Score"]
    ].head(10).to_string(index=False)
)
