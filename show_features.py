import sys
sys.path.append("preprocessed_data")  # IMPORTANT

import joblib

pipe = joblib.load("data/processed/preprocessed_pipeline.pkl")
#print(pipe)


print("\n=== FEATURES FINALES UTILISÉES PAR LE MODÈLE ===")
for f in pipe.final_columns:
    print(f)

print("\nTotal :", len(pipe.final_columns))
