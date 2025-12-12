"""
Script de preprocessing des données :
- Chargement du dataset brut
- Nettoyage et suppression des colonnes inutiles
- Division en train, validation et test (splits figés et reproductibles)
- Fit du pipeline uniquement sur l'ensemble train
- Transformation de validation et test avec le même pipeline
- Sauvegarde des splits et de leurs versions preprocessées
- Sauvegarde du pipeline de preprocessing
"""

from preprocessing_pipeline.preprocessing_pipeline import PreprocessingPipeline

from sklearn.model_selection import train_test_split
import pandas as pd
import os
import numpy as np

# Load data
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
full_path = os.path.normpath(os.path.join(BASE_DIR, "../data/raw/merged_balanced.csv"))

# df = pd.read_csv(full_path)
df = pd.read_csv(full_path, low_memory=False)

print("Labels BEFORE preprocessing:", df['Label'].value_counts())

# Nettoyage brut avant le pipeline
df = df.replace([np.inf, -np.inf], np.nan)
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Suppression colonnes inutiles
cols_to_drop = ["Unnamed: 0", "Flow ID", "Source IP", "Destination IP", "Timestamp", "SimillarHTTP"]
df = df.drop(columns=cols_to_drop, errors="ignore")

# Extraction features / labels
X = df.drop(columns=["Label"])
y = df["Label"].apply(lambda x: 0 if str(x).lower() in ["benign", "normal"] else 1)

df_X = pd.DataFrame(X)
df_y = pd.DataFrame(y)

print("Aperçu des features :")
print(df_X.head(), "\n")

print("Aperçu des Labels :")
print(df_y.head(), "\n")

# Splits
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
)

del X_temp, y_temp

print(f"Taille train : {len(X_train)} | Taille test : {len(X_test)} | Taille val : {len(X_val)}\n")

# Instance du pipeline
pipeline = PreprocessingPipeline(
    drop_low_variance=True,
    correlation_threshold=0.90,
    normalize=True,
    encode_protocol=True,
    handle_flags=True
)

# Suppression des doublons dans TRAIN
df_no_dup = pd.concat([X_train, y_train], axis=1).drop_duplicates()
X_train = df_no_dup.drop(columns=["Label"])
y_train = df_no_dup["Label"]

# Fit seulement sur TRAIN
X_train_proc = pipeline.fit_transform(X_train, y_train)
if isinstance(X_train_proc, tuple):
    X_train_proc = X_train_proc[0]

# Transform validation / test
X_val_proc = pipeline.transform(X_val)
if isinstance(X_val_proc, tuple):
    X_val_proc = X_val_proc[0]

X_test_proc = pipeline.transform(X_test)
if isinstance(X_test_proc, tuple):
    X_test_proc = X_test_proc[0]

# Output directory
output_dir = os.path.normpath(os.path.join(BASE_DIR, "../data/processed"))
os.makedirs(output_dir, exist_ok=True)

# Save pipeline
pipeline.save_pipeline(os.path.join(output_dir, 'preprocessed_pipeline.pkl'))

# Save RAW splits
pd.DataFrame(X_train).to_csv(os.path.join(output_dir, "train.csv"), index=False)
pd.DataFrame(y_train).to_csv(os.path.join(output_dir, "train_labels.csv"), index=False)

pd.DataFrame(X_val).to_csv(os.path.join(output_dir, "val.csv"), index=False)
pd.DataFrame(y_val).to_csv(os.path.join(output_dir, "val_labels.csv"), index=False)

pd.DataFrame(X_test).to_csv(os.path.join(output_dir, "test.csv"), index=False)
pd.DataFrame(y_test).to_csv(os.path.join(output_dir, "test_labels.csv"), index=False)

# Save PREPROCESSED splits
pd.DataFrame(X_train_proc).to_csv(os.path.join(output_dir, "train_processed.csv"), index=False)
pd.DataFrame(X_val_proc).to_csv(os.path.join(output_dir, "val_processed.csv"), index=False)
pd.DataFrame(X_test_proc).to_csv(os.path.join(output_dir, "test_processed.csv"), index=False)

print("Préprocessing terminé et sauvegardé.")
