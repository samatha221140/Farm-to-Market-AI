
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent
path = base / "dataset" / "AP_Crop_Suitability_Dataset_v3_Audited.csv"

df = pd.read_csv(path)
df.columns = df.columns.str.strip()

print("\n1. MOST COMMON SCORES")
print(df["Suitability_Score"].value_counts().head(15))

print("\n2. SCORE AND LABEL AGREEMENT")
print(
    pd.crosstab(
        pd.cut(
            df["Suitability_Score"],
            bins=[0, 60, 70, 80, 90, 100],
            include_lowest=True
        ),
        df["Suitable"]
    )
)

print("\n3. SUITABILITY BY CROP AND SCORE")
print(
    df.groupby("Crop").agg(
        Mean_Score=("Suitability_Score", "mean"),
        Score_Std=("Suitability_Score", "std"),
        Suitable_Count=("Suitable", "sum"),
        Suitable_Score_Min=(
            "Suitability_Score",
            lambda x: x[df.loc[x.index, "Suitable"] == 1].min()
        ),
        Unsuitable_Score_Max=(
            "Suitability_Score",
            lambda x: x[df.loc[x.index, "Suitable"] == 0].max()
        )
    ).round(2).to_string()
)
