import pandas as pd
import os
from glob import glob

"""
Ce que fait le script :
-----------------------
1. Parcourt automatiquement tous les fichiers .csv du dossier courant.
2. Lit chaque fichier par blocs de 100 000 lignes (pour éviter un plantage mémoire).
3. Vérifie que les colonnes correspondent avant de fusionner.
4. Concatène proprement toutes les lignes dans un seul grand DataFrame.
5. Affiche à la fin :
      - Le nombre total d’échantillons
      - Le nombre de features
      - Les différentes catégories présentes dans la colonne 'Label'
6. Sauvegarde le dataset fusionné sous 'merged_dataset.csv'
"""

# --- Définition du chemin du dossier contenant les CSV ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.normpath(os.path.join(BASE_DIR, "."))

# --- Recherche des fichiers CSV ---
csv_files = glob(os.path.join(data_path, "*.csv"))
output_file = os.path.join(data_path, "merged_dataset.csv")

if not csv_files:
    print("Aucun fichier CSV trouvé dans le dossier :", data_path)
    exit()

print(f"{len(csv_files)} fichiers trouvés :")
for file in csv_files:
    print(" -", os.path.basename(file))

# --- Fusion des fichiers ---
merged_df = None

for file in csv_files:
    print(f"\nLecture de {os.path.basename(file)} ...")
    chunks = pd.read_csv(file, chunksize=100000, low_memory=False)
    
    for chunk in chunks:
        if merged_df is None:
            merged_df = chunk
        else:
            # Fusion uniquement sur les colonnes communes
            common_cols = merged_df.columns.intersection(chunk.columns)
            merged_df = pd.concat([merged_df[common_cols], chunk[common_cols]], ignore_index=True)

print("\nFusion terminée avec succès !")

# --- Informations sur le dataset fusionné ---
if 'Label' in merged_df.columns:
    print("Nombre total d’échantillons :", len(merged_df))
    print("Nombre total de features :", len(merged_df.columns) - 1)
    print("Catégories uniques dans Label :", merged_df['Label'].unique())
else:
    print("[!]  Attention : la colonne 'Label' n’a pas été trouvée !")

# --- Sauvegarde du fichier fusionné ---
merged_df.to_csv(output_file, index=False)
print(f"\nFichier final sauvegardé sous : {output_file}")
