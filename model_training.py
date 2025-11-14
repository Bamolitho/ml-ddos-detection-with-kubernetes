# model_training.py

import pandas as pd
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

"""
Ce script :
    charge ton pipeline .pkl
    transforme les données ENTIEREMENT
    applique un Decision Tree avec class_weight='balanced'
    sauvegarde le modèle .pkl
"""

# ===== 1) Charger les données =====
df = pd.read_csv("merged_dataset.csv")

X = df.drop(columns=["Label"])
y = df["Label"]

# ===== 2) Charger le pipeline =====
pipeline = joblib.load("pipeline_preprocessing.pkl")

# ===== 3) Transformation complète =====
print("Transformation des données...")
X_transformed = pipeline.transform(X)

# ===== 4) Split stratifié =====
X_train, X_test, y_train, y_test = train_test_split(
    X_transformed, y, test_size=0.2, random_state=42, stratify=y
)

# ===== 5) Modèle Decision Tree avec correction du déséquilibre =====
model = DecisionTreeClassifier(
    class_weight="balanced",
    max_depth=None,
    random_state=42
)

print("Entraînement du modèle...")
model.fit(X_train, y_train)

# ===== 6) Évaluation =====
y_pred = model.predict(X_test)
print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred))

# ===== 7) Sauvegarde =====
joblib.dump(model, "decision_tree_balanced.pkl")

print("Modèle sauvegardé sous decision_tree_balanced.pkl")
