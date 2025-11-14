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

# Load data
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
full_path = os.path.normpath(os.path.join(BASE_DIR, "../data/raw/merged_datasets.csv"))

df = pd.read_csv(full_path)

# === Suppression des colonnes inutiles ===
cols_to_drop = ["Unnamed: 0", "Flow ID", "Source IP", "Destination IP", "Timestamp"]
df = df.drop(columns=cols_to_drop, errors="ignore")

# === Extraction des features et des labels ===
X = df.drop(columns=["Label"])
y = df["Label"].apply(lambda x: 0 if str(x).lower() in ["benign", "normal"] else 1)  # conversion multi -> binaire

df_X = pd.DataFrame(X)
df_y = pd.DataFrame(y)

print("Aperçu des features :")
print(df_X.head(), "\n")

print("Aperçu des Labels :")
print(df_y.head(), "\n")

# === Split temp / test ===
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# === Split train / validation ===
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
)
del X_temp, y_temp

print(f"Taille train : {len(X_train)} | Taille test : {len(X_test)} | Taille val : {len(X_val)}\n")

# === Initialize preprocessing pipeline ===
config_path = os.path.normpath(os.path.join(BASE_DIR, "./preprocessing_pipeline/config.yaml"))
pipeline = PreprocessingPipeline(config_path=config_path)

# === Fit transform only on TRAIN ===
X_train_proc = pipeline.fit_transform(X_train, y_train)
if isinstance(X_train_proc, tuple):
    X_train_proc = X_train_proc[0]


# === Apply SAME transform on validation + test ===
X_val_proc = pipeline.transform(X_val)
if isinstance(X_val_proc, tuple):
    X_val_proc = X_val_proc[0]

X_test_proc = pipeline.transform(X_test)
if isinstance(X_test_proc, tuple):
    X_test_proc = X_test_proc[0]



# === Create output directory if needed ===
output_dir = os.path.normpath(os.path.join(BASE_DIR, "../data/processed"))
os.makedirs(output_dir, exist_ok=True)

# === Save pipeline ===
pipeline.save_pipeline(os.path.join(output_dir, 'preprocessed_pipeline.pkl'))

# === Save raw splits ===
pd.DataFrame(X_train).to_csv(os.path.join(output_dir, "train.csv"), index=False)
pd.DataFrame(y_train).to_csv(os.path.join(output_dir, "train_labels.csv"), index=False)

pd.DataFrame(X_val).to_csv(os.path.join(output_dir, "val.csv"), index=False)
pd.DataFrame(y_val).to_csv(os.path.join(output_dir, "val_labels.csv"), index=False)

pd.DataFrame(X_test).to_csv(os.path.join(output_dir, "test.csv"), index=False)
pd.DataFrame(y_test).to_csv(os.path.join(output_dir, "test_labels.csv"), index=False)

# === Save preprocessed versions ===
X_train_proc = pd.DataFrame(X_train_proc)
X_val_proc = pd.DataFrame(X_val_proc)
X_test_proc = pd.DataFrame(X_test_proc)

pd.DataFrame(X_train_proc).to_csv(os.path.join(output_dir, "train_processed.csv"), index=False)
pd.DataFrame(X_val_proc).to_csv(os.path.join(output_dir, "val_processed.csv"), index=False)
pd.DataFrame(X_test_proc).to_csv(os.path.join(output_dir, "test_processed.csv"), index=False)

