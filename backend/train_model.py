

"""
Farm-to-Market-AI: Phase 1 crop-suitability classifier
Run from VS Code with: python train_model.py

Expected project layout:
Farm-to-Market-AI/
  dataset/
    AP_Crop_Suitability_Dataset_v3_ModelReady.csv
  backend/
    train_model.py

Important: this is a prototype using an AI-generated/synthetic dataset.
Do not use its predictions as real agricultural advice until the labels and
input values have been validated against trusted local agricultural sources.
"""

from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_PATH = PROJECT_DIR / "dataset" / "AP_Crop_Suitability_Dataset_v3_ModelReady.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "crop_suitability_model.pkl"
REPORT_PATH = MODEL_DIR / "evaluation_report.json"

def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at:\n{DATA_PATH}\n\n"
            "Download AP_Crop_Suitability_Dataset_v3_ModelReady.csv and place "
            "it inside your project's dataset folder."
        )

    df = pd.read_csv(DATA_PATH)
    if "Suitable" not in df.columns:
        raise ValueError("The dataset must contain a 'Suitable' target column.")

    X = df.drop(columns=["Suitable"])
    y = df["Suitable"].astype(int)

    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()

    preprocessing = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("numeric", SimpleImputer(strategy="median"), numeric_cols),
        ],
        remainder="drop",
    )

    pipeline = Pipeline(
        steps=[("preprocessing", preprocessing),
            ("classifier", RandomForestClassifier(
                n_estimators=300,
                random_state=42,
                class_weight="balanced",
            )),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(
        y_test, predictions, output_dict=True, zero_division=0
    )
    matrix = confusion_matrix(y_test, predictions).tolist()

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    evaluation = {
        "rows": int(len(df)),
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "accuracy": round(float(accuracy), 4),
        "confusion_matrix_labels_order": ["0 = not suitable", "1 = suitable"],
        "confusion_matrix": matrix,
        "classification_report": report,
        "warning": (
            "Prototype evaluation on a synthetic/AI-generated dataset. "
            "This score is not evidence of real-world agricultural accuracy."
        ),
    }
    REPORT_PATH.write_text(json.dumps(evaluation, indent=2), encoding="utf-8")

    print("\n=== Farm-to-Market-AI: Model Evaluation ===")
    print(f"Dataset rows: {len(df)}")
    print(f"Training rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")
    print(f"Test accuracy: {accuracy:.2%}")
    print("\nConfusion matrix (rows=true class, columns=predicted class):")
    print(matrix)
    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Evaluation report saved to: {REPORT_PATH}")
    print("\nCAUTION: Treat these results as a software prototype only. "
          "Validate the dataset before claiming real-world accuracy.")

if __name__ == "__main__":
    main()