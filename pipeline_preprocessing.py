# pipeline_preprocessing.py

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import PCA, FastICA
from sklearn.compose import ColumnTransformer
import joblib

# ===== 1) Charger un échantillon pour identifier les colonnes =====
df = pd.read_csv("merged_dataset.csv", nrows=50000)  # échantillon suffisant

# Détection auto des types
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

# On retire la colonne label si elle est détectée automatiquement
target_col = "Label"
if target_col in categorical_cols:
    categorical_cols.remove(target_col)
if target_col in numeric_cols:
    numeric_cols.remove(target_col)

print("Colonnes numériques :", len(numeric_cols))
print("Colonnes catégorielles :", len(categorical_cols))

# ===== 2) Préprocesseur pour les colonnes =====
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
    ]
)

# ===== 3) Pipeline complet =====
pipeline = Pipeline([
    ("preprocess", preprocessor),
    ("pca", PCA(n_components=50)),      # Ajuste si nécessaire
    ("ica", FastICA(n_components=20, max_iter=500))
])

# ===== 4) Fit du pipeline sur un échantillon =====
pipeline.fit(df.drop(columns=[target_col]))

# ===== 5) Sauvegarde =====
joblib.dump(pipeline, "pipeline_preprocessing.pkl")

print("Pipeline sauvegardé sous pipeline_preprocessing.pkl")
