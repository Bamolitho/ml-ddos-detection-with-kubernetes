import pandas as pd
import os
from glob import glob

"""
Script de fusion optimisée des fichiers CSV
-------------------------------------------
1. Détecte tous les fichiers CSV du dossier courant.
2. Conserve l'ordre des colonnes du PREMIER fichier.
3. Ajoute uniquement les colonnes manquantes à la fin.
4. Lit chaque fichier en streaming (chunks de 100k).
5. Unifie les colonnes dans le même ordre pour tous les fichiers.
6. Concatène sans jamais saturer la RAM.
7. Fournit un résumé final (rows, features, labels).
"""

# --- Définition des chemins ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.normpath(os.path.join(BASE_DIR, "."))

csv_files = glob(os.path.join(data_path, "*.csv"))
output_file = os.path.join(data_path, "merged_dataset.csv")

if not csv_files:
    print("Aucun fichier CSV trouvé.")
    exit()

print(f"{len(csv_files)} fichiers trouvés :")
for f in csv_files:
    print(" -", os.path.basename(f))

# --------------------------------------------------------------------------
# 1. Détection de l'ordre des colonnes du premier fichier
# --------------------------------------------------------------------------

print("\nLecture du premier fichier pour définir l'ordre des colonnes...")

first_file = csv_files[0]
df_first = pd.read_csv(first_file, nrows=5, low_memory=False)
all_columns = list(df_first.columns)  # ordre préservé

print("Colonnes détectées dans le premier fichier :", len(all_columns))

# --------------------------------------------------------------------------
# 2. Ajout des nouvelles colonnes venant des autres fichiers
# --------------------------------------------------------------------------

print("\nAnalyse des autres fichiers pour détecter les colonnes manquantes...")

for file in csv_files[1:]:
    df_head = pd.read_csv(file, nrows=5, low_memory=False)
    for col in df_head.columns:
        if col not in all_columns:
            all_columns.append(col)  # ajout en fin → ordre stable

print("Nombre total de colonnes unifiées :", len(all_columns))

# --------------------------------------------------------------------------
# 3. Fusion en streaming
# --------------------------------------------------------------------------

print("\nDébut de la fusion en streaming...")

first_write = True
total_rows = 0
label_counts = {}

for file in csv_files:
    print(f"\nFusion de : {os.path.basename(file)}")

    for chunk in pd.read_csv(file, chunksize=100_000, low_memory=False):

        # Ajout des colonnes manquantes dans ce chunk
        for col in all_columns:
            if col not in chunk:
                chunk[col] = None

        # Réordonner
        chunk = chunk[all_columns]

        # Mise à jour stats : Label
        if "Label" in chunk.columns:
            for lbl, count in chunk["Label"].value_counts().items():
                label_counts[lbl] = label_counts.get(lbl, 0) + count

        # Mise à jour du total
        total_rows += len(chunk)

        # Écriture sur disque
        chunk.to_csv(
            output_file,
            mode=("w" if first_write else "a"),
            header=first_write,
            index=False
        )

        first_write = False

# --------------------------------------------------------------------------
# 4. Statistiques finales
# --------------------------------------------------------------------------

print("\n=== Fusion terminée avec succès ===\n")
print("Nombre total d’échantillons :", total_rows)

if "Label" in all_columns:
    print("Nombre total de features :", len(all_columns) - 1)
else:
    print("Nombre total de features :", len(all_columns))

if label_counts:
    print("\nCatégories dans Label :")
    for lbl, count in label_counts.items():
        print(f" - {lbl} : {count}")

print(f"\nDataset fusionné sauvegardé sous : {output_file}")
