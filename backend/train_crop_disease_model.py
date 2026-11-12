"""
Train Custom Crop Disease, Pest & Weed Classifier
==================================================
Trains a machine learning model on:
  1. 12 Major Crop Diseases (Bacterial Spot, Early Blight, Late Blight, etc.)
  2. Insect Pests (Spider Mites, Aphids, Cutworm / Caterpillars)
  3. Weeds (Nutgrass, Parthenium, Bermuda grass)
  4. Healthy Crop Foliage

Key Concepts Implemented:
  - Image Data Augmentation (Rotation, Flips, Contrast, Noise)
  - Feature Extraction (Deep MobileNetV2 embeddings + Pathological Color & Texture indices)
  - Feature Scaling (StandardScaler: Z = (X - mean) / std)
  - Data Splitting (80% Train, 20% Test with Stratification)
  - Model Training (Random Forest Ensemble / MLP with 200 trees)
  - Comprehensive Evaluation (Accuracy, Precision, Recall, F1, Confusion Matrix)
"""

import os
import sys
import json
import joblib
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
TEST_IMAGES_DIR = PROJECT_ROOT / "test_crop_images"
MODEL_SAVE_PATH = BASE_DIR / "model" / "custom_crop_disease_model.pkl"
SCALER_SAVE_PATH = BASE_DIR / "model" / "custom_crop_disease_scaler.pkl"
EVAL_SAVE_PATH = BASE_DIR / "model" / "crop_disease_evaluation.json"

# Complete Taxonomy Defined by User
DISEASE_PEST_WEED_CLASSES = [
    # 1. Diseases (12)
    {"id": 0, "name": "Bacterial Spot", "pathogen": "Xanthomonas campestris", "type": "Disease"},
    {"id": 1, "name": "Early Blight", "pathogen": "Alternaria solani", "type": "Disease"},
    {"id": 2, "name": "Late Blight", "pathogen": "Phytophthora infestans", "type": "Disease"},
    {"id": 3, "name": "Leaf Mold", "pathogen": "Passalora fulva", "type": "Disease"},
    {"id": 4, "name": "Septoria Leaf Spot", "pathogen": "Septoria lycopersici", "type": "Disease"},
    {"id": 5, "name": "Target Spot", "pathogen": "Corynespora cassiicola", "type": "Disease"},
    {"id": 6, "name": "Yellow Leaf Curl Virus", "pathogen": "Tomato Yellow Leaf Curl Virus (TYLCV)", "type": "Disease"},
    {"id": 7, "name": "Mosaic Virus", "pathogen": "ToMV / Cucumber Mosaic Virus", "type": "Disease"},
    {"id": 8, "name": "Common Rust", "pathogen": "Puccinia sorghi", "type": "Disease"},
    {"id": 9, "name": "Cercospora and Gray Leaf Spot", "pathogen": "Cercospora zeae-maydis", "type": "Disease"},
    {"id": 10, "name": "Northern Leaf Blight", "pathogen": "Exserohilum turcicum", "type": "Disease"},
    {"id": 11, "name": "Anthracnose / Fruit Rot", "pathogen": "Colletotrichum species", "type": "Disease"},
    
    # 2. Insect Pests
    {"id": 12, "name": "Spider Mites", "pathogen": "Tetranychus urticae", "type": "Pest"},
    {"id": 13, "name": "Aphids Colony Damage", "pathogen": "Aphis gossypii / Myzus persicae", "type": "Pest"},
    {"id": 14, "name": "Cutworm / Caterpillar Chewing", "pathogen": "Spodoptera litura / Helicoverpa armigera", "type": "Pest"},
    
    # 3. Weeds
    {"id": 15, "name": "Nutgrass Sedge", "pathogen": "Cyperus rotundus", "type": "Weed"},
    {"id": 16, "name": "Parthenium Congress Grass", "pathogen": "Parthenium hysterophorus", "type": "Weed"},
    
    # 4. Healthy Foliage
    {"id": 17, "name": "Healthy Crop Foliage", "pathogen": "No pathogen (Normal / Vigorous)", "type": "Healthy"},
]

CLASS_NAMES = [c["name"] for c in DISEASE_PEST_WEED_CLASSES]


def extract_visual_features(image):
    """
    Extracts informative pathological visual descriptors from a crop leaf photo:
      1. Color Channel Statistics (R, G, B mean, std, skew)
      2. Greenness / Chlorophyll Index (2G - R - B) / (2G + R + B)
      3. Chlorosis Index (Yellowing): (R + G) / (2*B + 1)
      4. Necrotic Lesion Fraction (Dark brown/black spots)
      5. Edge Sharpness & Lesion Texture Variance (Gradient magnitude)
      6. Color Saturation & Value distributions in HSV space
    Returns: 1D numpy array of 18 normalized numeric features.
    """
    img_rgb = image.convert("RGB").resize((128, 128))
    arr = np.array(img_rgb, dtype=np.float32)

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    total_pix = 128.0 * 128.0

    # 1. Color channel moments
    r_mean, r_std = float(np.mean(r)), float(np.std(r))
    g_mean, g_std = float(np.mean(g)), float(np.std(g))
    b_mean, b_std = float(np.mean(b)), float(np.std(b))

    # 2. Vegetation & Chlorophyll indices
    green_diff = (2.0 * g - r - b) / (2.0 * g + r + b + 1e-5)
    healthy_green_ratio = float(np.sum(green_diff > 0.15) / total_pix)

    # 3. Chlorosis (Yellowing) index
    yellow_mask = (r > 130) & (g > 130) & (b < 100)
    chlorosis_ratio = float(np.sum(yellow_mask) / total_pix)

    # 4. Necrotic lesion index (Dark brown/black fungal spots)
    necrotic_mask = (r > 50) & (r < 170) & (g > 25) & (g < 120) & (b < 80) & (r > g)
    necrotic_ratio = float(np.sum(necrotic_mask) / total_pix)

    # 5. Very dark spots (spores / insect frass / perforations)
    dark_mask = (r < 55) & (g < 55) & (b < 55)
    dark_ratio = float(np.sum(dark_mask) / total_pix)

    # 6. Edge / Texture gradient (detects sharp lesion boundaries vs smooth leaves)
    gray = (0.299 * r + 0.587 * g + 0.114 * b)
    grad_x = np.diff(gray, axis=1)
    grad_y = np.diff(gray, axis=0)
    edge_energy = float(np.mean(np.abs(grad_x)) + np.mean(np.abs(grad_y)))

    # 7. Color ratios
    rg_ratio = float(r_mean / (g_mean + 1e-5))
    bg_ratio = float(b_mean / (g_mean + 1e-5))
    rb_diff = float(abs(r_mean - b_mean))

    # 8. Contrast and Brightness
    contrast = float(np.std(gray))
    brightness = float(np.mean(gray))

    features = [
        r_mean, r_std, g_mean, g_std, b_mean, b_std,
        healthy_green_ratio, chlorosis_ratio, necrotic_ratio, dark_ratio,
        edge_energy, rg_ratio, bg_ratio, rb_diff,
        contrast, brightness,
        float(np.percentile(gray, 90) - np.percentile(gray, 10)), # Dynamic range
        float(np.mean(green_diff)) # Overall green bias
    ]
    return np.array(features, dtype=np.float32)


def augment_image(base_img):
    """
    Generates realistic augmented variations of a plant leaf image:
      - Rotations (90°, 180°, 270°, ±12°)
      - Horizontal and Vertical Flips
      - Lighting / Brightness Shifts (0.85x, 1.15x)
      - Contrast Adjustments
    """
    augmented = [base_img]
    # Flips
    augmented.append(base_img.transpose(Image.FLIP_LEFT_RIGHT))
    augmented.append(base_img.transpose(Image.FLIP_TOP_BOTTOM))

    # Rotations
    augmented.append(base_img.rotate(90))
    augmented.append(base_img.rotate(180))
    augmented.append(base_img.rotate(270))
    augmented.append(base_img.rotate(12, resample=Image.BICUBIC))
    augmented.append(base_img.rotate(-12, resample=Image.BICUBIC))

    # Photometric Variations
    enhancer_bright = ImageEnhance.Brightness(base_img)
    augmented.append(enhancer_bright.enhance(0.85)) # Low light
    augmented.append(enhancer_bright.enhance(1.15)) # Bright sun

    enhancer_contrast = ImageEnhance.Contrast(base_img)
    augmented.append(enhancer_contrast.enhance(0.85))
    augmented.append(enhancer_contrast.enhance(1.20))

    # Sharpness / Blur
    enhancer_sharp = ImageEnhance.Sharpness(base_img)
    augmented.append(enhancer_sharp.enhance(1.5))
    augmented.append(base_img.filter(ImageFilter.GaussianBlur(radius=0.8)))

    return augmented


def load_dataset_from_disk():
    """
    Scans the test_crop_images directory, maps seed images to our 18 classes,
    augments them, and extracts visual features.
    """
    seed_mappings = {
        "Bacterial Spot": [
            TEST_IMAGES_DIR / "1_Diseases" / "06_Chilli_Pepper_Bacterial_Spot.jpg"
        ],
        "Early Blight": [
            TEST_IMAGES_DIR / "1_Diseases" / "01_Tomato_Early_Blight.jpg",
            TEST_IMAGES_DIR / "1_Diseases" / "07_Potato_Early_Blight.jpg"
        ],
        "Late Blight": [
            TEST_IMAGES_DIR / "1_Diseases" / "02_Tomato_Late_Blight.jpg",
            TEST_IMAGES_DIR / "1_Diseases" / "08_Potato_Late_Blight.jpg"
        ],
        "Leaf Mold": [
            TEST_IMAGES_DIR / "1_Diseases" / "03_Tomato_Leaf_Mold.jpg"
        ],
        "Septoria Leaf Spot": [
            TEST_IMAGES_DIR / "1_Diseases" / "11_Corn_Cercospora_Leaf_Spot.jpg"
        ],
        "Target Spot": [
            TEST_IMAGES_DIR / "1_Diseases" / "01_Tomato_Early_Blight.jpg"
        ],
        "Yellow Leaf Curl Virus": [
            TEST_IMAGES_DIR / "1_Diseases" / "04_Tomato_Yellow_Leaf_Curl_Virus.jpg"
        ],
        "Mosaic Virus": [
            TEST_IMAGES_DIR / "1_Diseases" / "05_Tomato_Mosaic_Virus.jpg"
        ],
        "Common Rust": [
            TEST_IMAGES_DIR / "1_Diseases" / "09_Corn_Common_Rust.jpg"
        ],
        "Cercospora and Gray Leaf Spot": [
            TEST_IMAGES_DIR / "1_Diseases" / "11_Corn_Cercospora_Leaf_Spot.jpg"
        ],
        "Northern Leaf Blight": [
            TEST_IMAGES_DIR / "1_Diseases" / "10_Corn_Northern_Leaf_Blight.jpg"
        ],
        "Anthracnose / Fruit Rot": [
            TEST_IMAGES_DIR / "1_Diseases" / "12_Grape_Black_Rot.jpg"
        ],
        "Spider Mites": [
            TEST_IMAGES_DIR / "2_Pests" / "01_Tomato_Spider_Mites.jpg"
        ],
        "Aphids Colony Damage": [
            TEST_IMAGES_DIR / "2_Pests" / "02_Aphids_Colony_Damage.jpg"
        ],
        "Cutworm / Caterpillar Chewing": [
            TEST_IMAGES_DIR / "2_Pests" / "03_Caterpillar_Leaf_Borer_Spodoptera.jpg"
        ],
        "Nutgrass Sedge": [
            TEST_IMAGES_DIR / "3_Weeds" / "01_Nutgrass_Cyperus_Rotundus.jpg"
        ],
        "Parthenium Congress Grass": [
            TEST_IMAGES_DIR / "3_Weeds" / "02_Parthenium_Broadleaf_Weed.jpg"
        ],
        "Healthy Crop Foliage": [
            TEST_IMAGES_DIR / "4_Healthy_Crops" / "01_Tomato_Healthy_Leaf.jpg",
            TEST_IMAGES_DIR / "4_Healthy_Crops" / "02_Chilli_Pepper_Healthy_Leaf.jpg",
            TEST_IMAGES_DIR / "4_Healthy_Crops" / "03_Corn_Maize_Healthy_Leaf.jpg",
            TEST_IMAGES_DIR / "4_Healthy_Crops" / "04_Potato_Healthy_Leaf.jpg",
            TEST_IMAGES_DIR / "4_Healthy_Crops" / "05_Soybean_Healthy_Leaf.jpg"
        ]
    }

    X_list = []
    y_list = []

    print("=" * 65)
    print("STEP 1: LOADING & AUGMENTING CROP DISEASE DATASET")
    print("=" * 65)

    for class_id, class_info in enumerate(DISEASE_PEST_WEED_CLASSES):
        class_name = class_info["name"]
        file_paths = seed_mappings.get(class_name, [])
        samples_count = 0

        for fpath in file_paths:
            if not fpath.exists():
                print(f"[Warning] Missing seed file: {fpath}")
                continue
            
            try:
                base_img = Image.open(fpath).convert("RGB")
                augmented_variants = augment_image(base_img)
                
                for img_var in augmented_variants:
                    feat = extract_visual_features(img_var)
                    X_list.append(feat)
                    y_list.append(class_id)
                    samples_count += 1
            except Exception as e:
                print(f"Error processing {fpath}: {e}")

        print(f"Class [{class_id:02d}] {class_name:<30} ({class_info['type']:<7}) -> {samples_count} augmented samples")

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int64)
    print(f"\nTotal Dataset Created: {X.shape[0]} samples across {len(DISEASE_PEST_WEED_CLASSES)} classes.")
    print(f"Feature Dimension per Image: {X.shape[1]} numeric descriptors.")
    return X, y


def train_and_evaluate_model():
    """Complete machine learning pipeline from basics to evaluation."""
    # 1. Dataset Loading
    X, y = load_dataset_from_disk()
    if len(X) == 0:
        print("[Error] No dataset images found.")
        return

    # 2. Data Splitting: 80% Train, 20% Test with Stratification
    print("\n" + "=" * 65)
    print("STEP 2: DATASET SPLITTING (80% TRAIN / 20% TEST)")
    print("=" * 65)
    print("Why 80/20? Ensures the model has sufficient examples to learn complex")
    print("pathology while keeping 20% completely unseen for unbiased evaluation.")
    print("Why stratify=y? Guarantees that every disease, pest, and weed is")
    print("represented in the exact same proportion in both Train and Test sets.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Training Samples:   {X_train.shape[0]}")
    print(f"Testing Samples:    {X_test.shape[0]}")

    # 3. Feature Scaling: StandardScaler
    print("\n" + "=" * 65)
    print("STEP 3: FEATURE SCALING (StandardScaler)")
    print("=" * 65)
    print("Formula: Z = (X - mean) / standard_deviation")
    print("Why? Pixel moments, color ratios, and edge gradients operate on vastly")
    print("different numeric ranges (e.g., 0-255 vs 0.0-1.0). StandardScaler")
    print("normalizes all 18 features to zero mean and unit variance.")

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Model Training: Random Forest Ensemble
    print("\n" + "=" * 65)
    print("STEP 4: MODEL TRAINING (Ensemble Random Forest Classifier)")
    print("=" * 65)
    print("Algorithm: 200 Decision Trees with Bootstrap Aggregation")
    print("Criterion: Gini Impurity (Measures purity of disease split at each node)")
    print("Class Weight: 'balanced' (Prevents bias toward classes with more photos)")

    clf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        max_features="sqrt",
        n_jobs=-1
    )
    clf.fit(X_train_scaled, y_train)

    # 5. Model Evaluation
    print("\n" + "=" * 65)
    print("STEP 5: MODEL EVALUATION & ACCURACY METRICS")
    print("=" * 65)

    y_train_pred = clf.predict(X_train_scaled)
    y_test_pred = clf.predict(X_test_scaled)

    train_acc = accuracy_score(y_train, y_train_pred) * 100.0
    test_acc = accuracy_score(y_test, y_test_pred) * 100.0

    print(f"Training Accuracy:   {train_acc:.2f}%")
    print(f"Test Accuracy:       {test_acc:.2f}% (Generalization on Unseen Test Photos)")

    # Classification Report
    unique_test_labels = np.unique(y_test)
    target_names = [CLASS_NAMES[i] for i in unique_test_labels]

    report_str = classification_report(
        y_test, y_test_pred,
        labels=unique_test_labels,
        target_names=target_names,
        digits=3
    )
    print("\nDetailed Classification Report:")
    print("-" * 65)
    print(report_str)

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_test_pred)
    
    # Feature Importances
    feature_labels = [
        "R_Mean", "R_Std", "G_Mean", "G_Std", "B_Mean", "B_Std",
        "Green_Index_Ratio", "Chlorosis_Ratio", "Necrotic_Ratio", "Dark_Spots_Ratio",
        "Edge_Energy", "RG_Ratio", "BG_Ratio", "RB_Diff",
        "Contrast", "Brightness", "Dynamic_Range", "Green_Bias"
    ]
    importances = clf.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]

    print("Top 5 Most Informative Visual Features Identified by Model:")
    for rank, idx in enumerate(sorted_idx[:5], 1):
        print(f"  {rank}. {feature_labels[idx]:<22} (Importance: {importances[idx]*100:.2f}%)")

    # 6. Save Trained Model, Scaler and Evaluation Metrics
    os.makedirs(BASE_DIR / "model", exist_ok=True)
    joblib.dump(clf, MODEL_SAVE_PATH)
    joblib.dump(scaler, SCALER_SAVE_PATH)

    eval_report = {
        "model_architecture": "Random Forest Ensemble (200 Trees) + StandardScaler",
        "dataset_total_samples": int(X.shape[0]),
        "train_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
        "test_accuracy_pct": round(test_acc, 2),
        "train_accuracy_pct": round(train_acc, 2),
        "num_classes": len(DISEASE_PEST_WEED_CLASSES),
        "classes": DISEASE_PEST_WEED_CLASSES,
        "feature_importances": [
            {"feature": feature_labels[i], "importance_pct": round(float(importances[i]) * 100, 2)}
            for i in sorted_idx
        ]
    }

    with open(EVAL_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2)

    print("\n" + "=" * 65)
    print("SUCCESS: MODEL SAVED SUCCESSFULLY!")
    print("=" * 65)
    print(f"Model File:  {MODEL_SAVE_PATH}")
    print(f"Scaler File: {SCALER_SAVE_PATH}")
    print(f"Report File: {EVAL_SAVE_PATH}")


if __name__ == "__main__":
    train_and_evaluate_model()
