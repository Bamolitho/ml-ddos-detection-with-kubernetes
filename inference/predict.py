"""
Script d'inférence en production :
- Charge un modèle au choix
- Charge le pipeline preprocessé
- Récupère le meilleur threshold depuis evaluate/benchmark.csv
- Fait l'inférence sur une entrée ou un dataset
"""

import os
import pandas as pd
import joblib
import numpy as np

def load_best_threshold(model_name):
    evaluate_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "../evaluate"))
    bench_path = os.path.join(evaluate_dir, "benchmark.csv")

    if not os.path.exists(bench_path):
        raise FileNotFoundError("benchmark.csv introuvable. Lance evaluate_models.py d'abord.")

    df = pd.read_csv(bench_path)
    if model_name not in df["model"].values:
        raise ValueError(f"Le modèle {model_name} n'existe pas dans benchmark.csv")

    return df[df["model"] == model_name]["best_threshold"].values[0]


def load_model(model_name):
    models_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "../models"))
    model_path = os.path.join(models_dir, f"{model_name}.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modèle {model_path} introuvable.")

    return joblib.load(model_path)


def load_pipeline():
    pipeline_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../preprocessed_pipeline.pkl"))
    if not os.path.exists(pipeline_path):
        raise FileNotFoundError("Pipeline preprocessé introuvable.")
    return joblib.load(pipeline_path)


def predict(model_name, data):
    """
    data : pd.DataFrame ou un seul dictionnaire de features
    """

    if isinstance(data, dict):
        data = pd.DataFrame([data])
    elif not isinstance(data, pd.DataFrame):
        raise ValueError("Data doit être un dict ou un DataFrame.")

    # Charger pipeline + modèle + threshold
    pipeline = load_pipeline()
    model = load_model(model_name)
    threshold = load_best_threshold(model_name)

    # Preprocessing
    X = pipeline.transform(data)
    if isinstance(X, tuple):
        X = X[0]

    # Probabilités
    probas = model.predict_proba(X)[:, 1]

    # Conversion avec threshold optimal
    preds = (probas >= threshold).astype(int)

    return preds, probas, threshold


if __name__ == "__main__":
    # Exemple test
    sample = {
        "Source Port": 12345,
        "Destination Port": 80,
        "Protocol": 6,
        "Flow Duration": 123456,
        # ... ajouter toutes les colonnes !
    }

    preds, probas, thr = predict("random_forest", sample)

    print("Prediction :", preds)
    print("Probability :", probas)
    print("Threshold utilisé :", thr)
