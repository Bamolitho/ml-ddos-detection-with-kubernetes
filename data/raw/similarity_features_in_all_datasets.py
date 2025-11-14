import pandas as pd
import glob

# Liste tous les fichiers CSV du dossier courant
csv_files = glob.glob("*.csv")

features_dict = {}

for file in csv_files:
    cols = pd.read_csv(file, nrows=0).columns.tolist()
    features_dict[file] = cols

# Comparaison
reference = features_dict[csv_files[0]]
print(f"Fichier de référence : {csv_files[0]}")
print(f"Nombre de features : {len(reference)}\n")

for file, cols in features_dict.items():
    if cols != reference:
        print(f"⚠️  Différences détectées dans {file} ({len(cols)} colonnes)")
        diff1 = set(reference) - set(cols)
        diff2 = set(cols) - set(reference)
        if diff1:
            print(f"  - Colonnes manquantes : {diff1}")
        if diff2:
            print(f"  - Colonnes supplémentaires : {diff2}")
        print()
    else:
        print(f"✅ {file} : mêmes features\n")
