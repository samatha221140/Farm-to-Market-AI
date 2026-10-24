
import pandas as pd
from pathlib import Path
base = Path(__file__).resolve().parent.parent
path = base / "dataset" / "AP_Crop_Suitability_Dataset_v3_Audited.csv"


df = pd.read_csv(path)
df.columns = df.columns.str.strip()

features = [
    "N_kg_ha",
    "P_kg_ha",
    "K_kg_ha",
    "pH",
    "Temperature_C",
    "Rainfall_mm",
]

print("\nOVERALL NUMERICAL RANGES")
print(df[features].describe().round(2).to_string())

print("\nCROP-WISE MEDIAN VALUES")
print(
    df.groupby("Crop")[features]
    .median()
    .round(2)
    .to_string()
)

print("\nCROP-WISE MINIMUM AND MAXIMUM")
for crop, group in df.groupby("Crop"):
    print(f"\n{crop}")
    for feature in features:
        print(
            f"  {feature}: "
            f"{group[feature].min():.2f} to "
            f"{group[feature].max():.2f}"
        )
