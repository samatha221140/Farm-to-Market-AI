import pandas as pd
import joblib

# Load trained model
model = joblib.load("../model/crop_model.pkl")

# Load label encoder
encoder = joblib.load("../model/label_encoder.pkl")


# Farmer input
data = pd.DataFrame([{
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.8,
    "humidity": 82,
    "ph": 6.5,
    "rainfall": 202
}])


# Get prediction probabilities
probabilities = model.predict_proba(data)[0]


# Get top 10 predictions
top_10_indices = probabilities.argsort()[-10:][::-1]


print()
print("🌱 TOP 10 CROP RECOMMENDATIONS")
print("--------------------------------")

for rank, index in enumerate(top_10_indices, start=1):

    crop = encoder.inverse_transform([index])[0]

    probability = probabilities[index] * 100

    print(f"{rank}. {crop} - {probability:.2f}%")