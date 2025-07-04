import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import numpy as np

# Load dataset
df = pd.read_csv('filled_season_color_dataset.csv')

# Use correct column names (case-sensitive)
X = df[['Hair_L', 'Hair_A', 'Hair_B', 'Skin_L', 'Skin_A', 'Skin_B', 'Eye_L', 'Eye_A', 'Eye_B']]
y = df['Season']

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
print(f"\nAccuracy: {model.score(X_test, y_test)*100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
labels = sorted(y.unique())

print("Confusion Matrix:")
print(pd.DataFrame(cm, index=labels, columns=labels))

# Correct predictions per season
correct_counts = dict(zip(labels, cm.diagonal()))
print("\nCorrect predictions per season:")
for season, count in correct_counts.items():
    print(f"{season}: {count}")

# Save model
joblib.dump(model, 'season_classifier.pkl')
