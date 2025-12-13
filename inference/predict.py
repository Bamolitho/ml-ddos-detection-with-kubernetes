#!/usr/bin/env python3
import os
import json
import pandas as pd
import joblib
import numpy as np
import yaml
from sklearn.metrics import classification_report

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

PREP_DIR = ROOT / "preprocessed_data"
sys.path.append(str(PREP_DIR))

PIPELINE_DIR = PREP_DIR / "preprocessing_pipeline"
sys.path.append(str(PIPELINE_DIR))


# ===============================================================
# Chargements
# ===============================================================

def load_best_threshold(model_name):
    evaluate_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "../evaluate"))
    bench_path = os.path.join(evaluate_dir, "benchmark.csv")

    if not os.path.exists(bench_path):
        raise FileNotFoundError("benchmark.csv introuvable. Lance evaluate_models.py.")

    df = pd.read_csv(bench_path)
    if model_name not in df["model"].values:
        raise ValueError(f"Le modèle {model_name} n'existe pas dans benchmark.csv")

    return df[df["model"] == model_name]["best_threshold"].values[0]


def load_model(model_name):
    models_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "../models"))
    model_path = os.path.join(models_dir, f"{model_name}.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modèle introuvable : {model_path}")

    return joblib.load(model_path)


def load_pipeline():
    pipeline_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../data/processed/preprocessed_pipeline.pkl"))
    if not os.path.exists(pipeline_path):
        raise FileNotFoundError("Pipeline preprocessé introuvable.")
    return joblib.load(pipeline_path)


# ===============================================================
# Prédiction finale
# ===============================================================

def predict_raw(model_name, data):
    if isinstance(data, dict):
        data = pd.DataFrame([data])
    elif not isinstance(data, pd.DataFrame):
        raise ValueError("Data doit être un dict ou un DataFrame.")

    pipeline = load_pipeline()
    model = load_model(model_name)
    threshold = load_best_threshold(model_name)

    X = pipeline.transform(data)
    if isinstance(X, tuple):
        X = X[0]

    probas = model.predict_proba(X)[:, 1]
    preds = (probas >= threshold).astype(int)

    return preds, probas, threshold


# ===============================================================
# CLI
# ===============================================================

def cli():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=str, help="JSON string contenant les features")
    parser.add_argument("--input", type=str, help="Chemin CSV à prédire")
    parser.add_argument("--model", type=str, help="Nom du modèle (override config)")
    args = parser.parse_args()

    # Charger config
    config_path = os.path.join(os.path.dirname(__file__), "../config/config_inference.yaml")
    cfg = {}

    if os.path.exists(config_path):
        cfg = yaml.safe_load(open(config_path))
        inf = cfg.get("inference", {})
    else:
        inf = {}
    enable_cfg = inf.get("enable_config", True)

    # Sélection du modèle
    if args.model:
        model_name = args.model
    elif enable_cfg and inf.get("use_static_model_name", False):
        model_name = inf.get("model_name", None)
        if not model_name:
            raise ValueError("Config : model_name manquant.")
    else:
        model_name = "xgboost"

    # Détermination des données
    input_path = None
    json_data = None
    label_path = None

    if args.json or args.input:
        json_data = args.json
        input_path = args.input
    else:
        if enable_cfg and inf.get("use_static_input_file", False):
            input_path = inf.get("input_file")
        if input_path is None:
            input_path = "data/processed/test.csv"

        if enable_cfg and inf.get("use_static_label_file", False):
            label_path = inf.get("label_file")

        if label_path is None:
            default_label = "data/processed/test_labels.csv"
            label_path = default_label if os.path.exists(default_label) else None

    # Chargement data
    if json_data:
        df = pd.DataFrame([json.loads(json_data)])
    else:
        df = pd.read_csv(input_path)

    # Chargement label
    y_true = None
    if label_path and os.path.exists(label_path):
        y_true = pd.read_csv(label_path)

    # Prédiction
    preds, probas, thr = predict_raw(model_name, df)

    # Formatage output final
    out = {
        "model": model_name,
        "threshold": float(thr),
        "results": []
    }

    for i in range(len(preds)):
        pred = int(preds[i])
        prob = float(probas[i])

        verdict = "DDoS" if pred == 1 else "Benign"

        entry = {
            "prediction": pred,
            "probability": prob,
            "verdict": verdict
        }
        out["results"].append(entry)

    # Ajouter rapport si labels fournis
    if y_true is not None:
        report = classification_report(y_true, preds, output_dict=True)
        out["metrics"] = report

    # Sortie JSON unique
    print(json.dumps(out, indent=2))


# ===============================================================
# Main
# ===============================================================

if __name__ == "__main__":
    cli()
