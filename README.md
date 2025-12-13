💖 StyleMate – ML-Powered Personal Color & Style Recommender

A personalized color profiling and fashion recommendation system using machine learning and image processing.

📌 Overview

StyleMate is a web-based application that analyzes a user's skin, hair, and eye color from an uploaded photo to determine their seasonal color type (Spring, Summer, Autumn, Winter). Based on this analysis, it provides personalized recommendations for clothing colors, makeup tones, and suitable fabrics using machine learning.

With an accuracy of 93.75%, the system combines color theory with ML to make fashion and cosmetic choices more inclusive and data-driven.

🚀 Features

📷 Upload a photo and extract color features (skin, hair, eye).

🎨 Predict seasonal color type using LAB color values.

🤖 ML model trained with Random Forest Classifier.

💄 Style suggestions for makeup or gromming tips, outfits, and clothes.

🧠 Based on color theory + personalized ML logic.

🌐 Responsive UI for seamless experience across devices.

🛠️ Tech Stack

Frontend: HTML, CSS, JavaScript

Backend: Flask (Python)

ML Libraries: scikit-learn, OpenCV, NumPy, Pandas

Color Processing: LAB and HSV color space analysis

Model: RandomForestClassifier (Accuracy: 93.75%)

🧪 How It Works

User Photo ➡️ extract_colors.py ➡️ LAB Features ➡️ ML Model ➡️ Season Prediction ➡️ Load Palette ➡️ Display Result

📂 Project Structure

├── static/               # CSS, JS, and UI assets
├── templates/            # HTML templates (Flask Jinja)
├── extract_colors.py     # Feature extraction logic
├── model.pkl             # Trained ML model
├── app.py                # Flask application logic
└── README.md             # This file

🧑‍💻 Setup Instructions

Clone the repository

git clone https://github.com/samiya2804/Style-Mate-ML-Powered-Personal-Color-Style-Recommender-.git  

cd backend

Create virtual environment (optional but recommended)

python -m venv venv

source venv/bin/activate  # or venv\Scripts\activate on Windows

Install dependencies

pip install -r requirements.txt

Run the Flask app

python app.py

Open browser at http://127.0.0.1:5000

✨ Demo - Deployed link

https://style-mate-ml-powered-personal-color-muyw.onrender.com

🙌 Contributors

Samiya

