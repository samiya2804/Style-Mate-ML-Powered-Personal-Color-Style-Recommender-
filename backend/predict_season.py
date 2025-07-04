from extract_colors import extract_colors_from_photo
import joblib
import pandas as pd

# Load the trained model
model = joblib.load("season_classifier.pkl")

def predict_season(photo_path):
    color_data = extract_colors_from_photo(photo_path)

    # Unpack LAB values
    hair_L, hair_A, hair_B = color_data['hair_lab']
    skin_L, skin_A, skin_B = color_data['skin_lab']
    eye_L, eye_A, eye_B = color_data['eye_lab']

    # Format for prediction
    features = pd.DataFrame([{
        "Hair_L": hair_L, "Hair_A": hair_A, "Hair_B": hair_B,
        "Skin_L": skin_L, "Skin_A": skin_A, "Skin_B": skin_B,
        "Eye_L": eye_L, "Eye_A": eye_A, "Eye_B": eye_B,
    }])

    # Predict
    return model.predict(features)[0]

# Run prediction
# photo = 'uploads/samiya-colored_20250627115237.jpg'  
# print("Predicted season:", predict_season(photo))

# Example:
# if __name__ == "__main__":
#     photo = "uploads/samiya-colored_20250627115237.jpg"  
#     if os.path.exists(photo):
#         print("Predicted season:", predict_season(photo))
#     else:
#         print("Photo not found:", photo)
