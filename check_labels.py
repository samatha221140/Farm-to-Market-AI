
import pandas as pd
from pathlib import Path

# Find the dataset relative to this Python file
project_folder = Path(__file__).resolve().parent
csv_path = project_folder / "dataset" / "AP_Crop_Suitability_Dataset_v3_Audited.csv"

print("Reading file:", csv_path)

df = pd.read_csv(csv_path)

# Remove accidental spaces around column names
df.columns = df.columns.str.strip()

print("\nDATASET SHAPE:", df.shape)

print("\nALL COLUMN NAMES:")
for column in df.columns:
    print(repr(column))

print("\nLABEL COUNTS:")
print(df["Suitable"].value_counts())

if "Suitability_Score" in df.columns:
    print("\nSCORE RANGE BY LABEL:")
    print(
        df.groupby("Suitable")["Suitability_Score"]
        .agg(["count", "min", "max", "mean", "median"])
    )
else:
    print("\nSuitability_Score is not in this CSV.")
    print("This may be the model-ready dataset rather than the audited dataset.")

if "Crop" in df.columns:
    print("\nLABEL COUNTS BY CROP:")
    print(pd.crosstab(df["Crop"], df["Suitable"]))

print("\nCHECK COMPLETED")
