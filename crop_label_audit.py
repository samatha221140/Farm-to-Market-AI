
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent
path = base / "dataset" / "AP_Crop_Suitability_Dataset_v3_Audited.csv"

df = pd.read_csv(path)
df.columns = df.columns.str.strip()

summary = df.groupby("Crop").agg(
    Records=("Suitable", "size"),
    Suitable_Count=("Suitable", "sum"),
    Mean_Score=("Suitability_Score", "mean"),
    Min_Score=("Suitability_Score", "min"),
    Max_Score=("Suitability_Score", "max"),
    Mean_Rainfall=("Rainfall_mm", "mean"),
    Mean_pH=("pH", "mean"),
    Mean_Moisture=("Soil_Moisture_pct", "mean")
).round(2)

summary["Unsuitable_Count"] = (
    summary["Records"] - summary["Suitable_Count"]
)

print("\nCROP-WISE LABEL AUDIT")
print(summary.to_string())

output = base / "crop_label_audit.csv"
summary.to_csv(output)

print(f"\nSummary saved to: {output}")
print("\nReminder: labels are AI-generated and not yet verified.")
