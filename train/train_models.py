"""
Script d'entraînement des modèles supervisés :
- Chargement des données preprocessées
- Entraînement : Decision Tree + Random Forest
- Sauvegarde des modèles entraînés
"""

import pandas as pd
import os
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


# ==========================
# 1. Chargement des données
# ==========================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
processed_dir = os.path.normpath(os.path.join(BASE_DIR, "../data/processed"))

print("============================================================")
print("[INFO] Loading processed datasets...")
print("============================================================")

X_train = pd.read_csv(os.path.join(processed_dir, "train_processed.csv"))
X_val   = pd.read_csv(os.path.join(processed_dir, "val_processed.csv"))
X_test  = pd.read_csv(os.path.join(processed_dir, "test_processed.csv"))

y_train = pd.read_csv(os.path.join(processed_dir, "train_labels.csv")).values.ravel()
y_val   = pd.read_csv(os.path.join(processed_dir, "val_labels.csv")).values.ravel()
y_test  = pd.read_csv(os.path.join(processed_dir, "test_labels.csv")).values.ravel()

print("[OK] Data loaded successfully.\n")


# ==========================
# 2. Modèles supervisés
# ==========================

dt_model = DecisionTreeClassifier(
    criterion="gini",
    max_depth=None,
    random_state=42
)

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    n_jobs=-1,
    random_state=42
)

models = {
    "decision_tree": dt_model,
    "random_forest": rf_model
}


# ==========================
# 3. Entraînement + sauvegarde
# ==========================

models_dir = os.path.normpath(os.path.join(BASE_DIR, "../models"))
os.makedirs(models_dir, exist_ok=True)

for name, model in models.items():
    print("============================================================")
    print(f"[INFO] Training model: {name}")
    print("============================================================")

    model.fit(X_train, y_train)

    save_path = os.path.join(models_dir, f"{name}.pkl")
    joblib.dump(model, save_path)

    print(f"[OK] {name} saved to {save_path}\n")

print("============================================================")
print("[OK] TRAINING COMPLETED")
print("============================================================")
