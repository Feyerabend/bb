import xgboost as xgb
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from PIL import Image, ImageDraw, ImageFont
import os

# Load Titanic dataset
titanic = sns.load_dataset('titanic')

# Select features and target
features = ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked']
X = titanic[features]
y = titanic['survived']

# Preprocess data
# Handle missing values
X['age'].fillna(X['age'].median(), inplace=True)
X['embarked'].fillna(X['embarked'].mode()[0], inplace=True)

# Encode categorical variables
le = LabelEncoder()
X['sex'] = le.fit_transform(X['sex'])  # Male=1, Female=0
X['embarked'] = le.fit_transform(X['embarked'])  # C=0, Q=1, S=2

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create XGBoost model
model = xgb.XGBClassifier(random_state=42)

# Perform 5-fold cross-validation
cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
print(f"Cross-validation accuracy: {np.mean(cv_scores):.2f} (+/- {np.std(cv_scores) * 2:.2f})")

# Simple grid search for hyperparameter tuning
param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [3, 5],
    'learning_rate': [0.01, 0.1]
}
grid_search = GridSearchCV(model, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train, y_train)

# Best model from grid search
best_model = grid_search.best_estimator_
print(f"Best parameters: {grid_search.best_params_}")

# Train best model
best_model.fit(X_train, y_train)

# Make predictions
y_pred = best_model.predict(X_test)

# Evaluate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Test accuracy: {accuracy:.2f}")

# Get feature importance (using 'gain')
feature_importance = best_model.get_booster().get_score(importance_type='gain')
feature_names = X.columns
importance_scores = [feature_importance.get(f"f{i}", 0) for i in range(len(feature_names))]

# Normalize importance scores for visualization (scale to max bar length)
max_length = 400  # Maximum bar length in pixels
max_importance = max(importance_scores)
if max_importance > 0:
    importance_scores = [score / max_importance * max_length for score in importance_scores]

# Create image with Pillow
image_width = 600
image_height = len(features) * 50 + 100  # 50px per feature + padding
image = Image.new('RGB', (image_width, image_height), 'white')
draw = ImageDraw.Draw(image)

# Try to load a font (use default if not available)
try:
    font = ImageFont.truetype("arial.ttf", 20)
except:
    font = ImageFont.load_default()

# Draw title
draw.text((10, 10), "Feature Importance (Gain)", fill='black', font=font)

# Draw bars and labels
bar_height = 30
y_offset = 50
for i, (feature, score) in enumerate(zip(feature_names, importance_scores)):
    # Draw bar
    draw.rectangle(
        [(100, y_offset + i * 50), (100 + score, y_offset + i * 50 + bar_height)],
        fill='blue'
    )
    # Draw feature name
    draw.text((10, y_offset + i * 50 + 5), feature, fill='black', font=font)
    # Draw importance value
    draw.text((110 + score, y_offset + i * 50 + 5), f"{score/max_length*max_importance:.2f}", fill='black', font=font)

# Save and display image
image.save('feature_importance.png')
image.show()  # Opens the image using the default image viewer
print("Feature importance image saved as 'feature_importance.png'")