
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent
path = base / "dataset" / "AP_Crop_Suitability_Dataset_v3_Audited.csv"

df = pd.read_csv(path)
df.columns = df.columns.str.strip()

print("\nDATASET SHAPE:")
print(df.shape)

print("\nCOLUMN TYPES:")
print(df.dtypes.to_string())

print("\nUNIQUE CROP NAMES:")
print(sorted(df["Crop"].dropna().unique()))

print("\nCATEGORICAL VALUES:")
for col in ["District", "Soil_Type", "Soil_Texture",
            "Water_Source", "Water_Availability"]:
    if col in df.columns:
        print(f"\n{col}:")
        print(sorted(df[col].dropna().unique()))
