"""
Script de preprocessing des données :
- Lancement automatique du script de sampling (équilibrage binaire)
- Chargement du dataset équilibré
- Nettoyage et suppression des colonnes inutiles
- Division en train, validation et test (splits figés et reproductibles)
- Fit du pipeline uniquement sur l'ensemble train
- Transformation de validation et test avec le même pipeline
- Sauvegarde des splits et des versions preprocessées
- Sauvegarde du pipeline de preprocessing
"""

import subprocess
from preprocessing_pipeline.preprocessing_pipeline import PreprocessingPipeline

from sklearn.model_selection import train_test_split
import pandas as pd
import os
import numpy as np

# --------------------------------------------------------
# 1. Lancement du script de sampling avant tout
# --------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sampling_script = os.path.normpath(os.path.join(BASE_DIR, "sampling.py"))

print("[INFO] Running sampling script...")
# subprocess.run(["python", sampling_script], check=True)
print("[INFO] Sampling script finished.\n")

# --------------------------------------------------------
# 2. Chargement du dataset équilibré
# --------------------------------------------------------
balanced_path = os.path.normpath(os.path.join(BASE_DIR, "../data/raw/merged_balanced.csv"))
df = pd.read_csv(balanced_path, low_memory=False)

print("Labels BEFORE preprocessing:", df['Label'].value_counts())

# --------------------------------------------------------
# 3. Nettoyage brut
# --------------------------------------------------------
df = df.replace([np.inf, -np.inf], np.nan)
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# --------------------------------------------------------
# 4. Suppression des colonnes inutiles
# --------------------------------------------------------
cols_to_drop = ["Unnamed: 0", "Flow ID", "Source IP", "Destination IP", "Timestamp", "SimillarHTTP"]
df = df.drop(columns=cols_to_drop, errors="ignore")

# --------------------------------------------------------
# 5. Features / Labels
# --------------------------------------------------------
X = df.drop(columns=["Label"])
y = df["Label"]  # déjà 0 (benign) et 1 (ddos)

df_X = pd.DataFrame(X)
df_y = pd.DataFrame(y)

print("Aperçu des features :")
print(df_X.head(), "\n")

print("Aperçu des Labels :")
print(df_y.head(), "\n")

# --------------------------------------------------------
# 6. Splits stratifiés
# --------------------------------------------------------
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
)

del X_temp, y_temp

print(f"Taille train : {len(X_train)} | Taille test : {len(X_test)} | Taille val : {len(X_val)}\n")

# --------------------------------------------------------
# 7. Instance du pipeline maison
# --------------------------------------------------------
pipeline = PreprocessingPipeline(
    drop_low_variance=True,
    correlation_threshold=0.90,
    normalize=True,
    encode_protocol=True,
    handle_flags=True
)

# --------------------------------------------------------
# 8. Suppression des doublons dans TRAIN
# --------------------------------------------------------
df_no_dup = pd.concat([X_train, y_train], axis=1).drop_duplicates()
X_train = df_no_dup.drop(columns=["Label"])
y_train = df_no_dup["Label"]

# --------------------------------------------------------
# 9. Fit seulement sur TRAIN
# --------------------------------------------------------
X_train_proc = pipeline.fit_transform(X_train, y_train)
if isinstance(X_train_proc, tuple):
    X_train_proc = X_train_proc[0]

# --------------------------------------------------------
# 10. Transform VAL / TEST
# --------------------------------------------------------
X_val_proc = pipeline.transform(X_val)
if isinstance(X_val_proc, tuple):
    X_val_proc = X_val_proc[0]

X_test_proc = pipeline.transform(X_test)
if isinstance(X_test_proc, tuple):
    X_test_proc = X_test_proc[0]

# --------------------------------------------------------
# 11. Sauvegarde
# --------------------------------------------------------
output_dir = os.path.normpath(os.path.join(BASE_DIR, "../data/processed"))
os.makedirs(output_dir, exist_ok=True)

pipeline.save_pipeline(os.path.join(output_dir, 'preprocessed_pipeline.pkl'))

# RAW
pd.DataFrame(X_train).to_csv(os.path.join(output_dir, "train.csv"), index=False)
pd.DataFrame(y_train).to_csv(os.path.join(output_dir, "train_labels.csv"), index=False)

pd.DataFrame(X_val).to_csv(os.path.join(output_dir, "val.csv"), index=False)
pd.DataFrame(y_val).to_csv(os.path.join(output_dir, "val_labels.csv"), index=False)

pd.DataFrame(X_test).to_csv(os.path.join(output_dir, "test.csv"), index=False)
pd.DataFrame(y_test).to_csv(os.path.join(output_dir, "test_labels.csv"), index=False)

# PROCESSED
pd.DataFrame(X_train_proc).to_csv(os.path.join(output_dir, "train_processed.csv"), index=False)
pd.DataFrame(X_val_proc).to_csv(os.path.join(output_dir, "val_processed.csv"), index=False)
pd.DataFrame(X_test_proc).to_csv(os.path.join(output_dir, "test_processed.csv"), index=False)

print("Préprocessing terminé et sauvegardé.")
