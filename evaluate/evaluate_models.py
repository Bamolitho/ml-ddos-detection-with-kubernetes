"""
Script d'évaluation avancée des modèles :
- Accuracy, Precision, Recall, F1
- ROC AUC + ROC Curve
- Temps d'inférence + Throughput
- Recherche du meilleur threshold
- Rapport détaillé + benchmark automatique
"""

import os
import time
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve
)
import matplotlib.pyplot as plt

# ==========================
# 1. Chargement des données
# ==========================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
processed_dir = os.path.normpath(os.path.join(BASE_DIR, "../data/processed"))

X_test = pd.read_csv(os.path.join(processed_dir, "test_processed.csv"))
y_test = pd.read_csv(os.path.join(processed_dir, "test_labels.csv")).values.ravel()

print("============================================================")
print("[INFO] Loading processed test dataset...")
print("============================================================")
print(f"[INFO] Test shape: {X_test.shape}")
print("[OK] Data loaded successfully.\n")


# ==========================
# 2. Structure des dossiers
# ==========================

eval_dir = os.path.normpath(os.path.join(BASE_DIR, "../evaluate"))
plots_dir = os.path.join(eval_dir, "plots")
reports_dir = os.path.join(eval_dir, "reports")

os.makedirs(eval_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)


# ==========================
# 3. Chargement des modèles
# ==========================

models_dir = os.path.normpath(os.path.join(BASE_DIR, "../models"))
model_files = [f for f in os.listdir(models_dir) if f.endswith(".pkl")]

results = []

print("============================================================")
print("[INFO] Evaluating models...")
print("============================================================")

for file in model_files:
    model_path = os.path.join(models_dir, file)
    model = joblib.load(model_path)
    name = file.replace(".pkl", "")

    print("------------------------------------------------------------")
    print(f"[INFO] Evaluating model: {name}")
    print("------------------------------------------------------------")

    # ======== Inférence + temps ========
    start = time.time()
    probas = model.predict_proba(X_test)[:, 1]
    end = time.time()

    inference_time = end - start
    throughput = len(X_test) / inference_time

    # ======== Metrics Threshold par défaut (0.5) ========
    preds = (probas >= 0.5).astype(int)

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds)
    rec = recall_score(y_test, preds)
    f1 = f1_score(y_test, preds)

    # ======== ROC AUC ========
    roc_auc = roc_auc_score(y_test, probas)
    fpr, tpr, thresholds = roc_curve(y_test, probas)

    # ======== Best threshold (Youden J) ========
    J = tpr - fpr
    best_idx = np.argmax(J)
    best_threshold = thresholds[best_idx]

    # ======== Sauvegarde ROC Curve ========
    plt.figure()
    plt.plot(fpr, tpr)
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.title(f"ROC Curve - {name}")

    plot_path = os.path.join(plots_dir, f"{name}_roc.png")
    plt.savefig(plot_path)
    plt.close()

    # ======== Rapport détaillé ========
    report_text = f"""
============================================================
DETAILED REPORT - {name}
============================================================

-> Accuracy      : {acc}
-> Precision     : {prec}
-> Recall        : {rec}
-> F1 Score      : {f1}
-> ROC AUC       : {roc_auc}

-> Inference Time (sec): {inference_time}
-> Throughput (samples/sec): {throughput}

-> Best Threshold: {best_threshold}

ROC Curve saved at: {plot_path}

"""

    report_file = os.path.join(reports_dir, f"{name}_report.txt")
    with open(report_file, "w") as f:
        f.write(report_text)

    print("[OK] Report saved:", report_file)

    # ======== Stocker les résultats pour benchmark ========
    results.append({
        "model": name,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": roc_auc,
        "inference_time_sec": inference_time,
        "throughput": throughput,
        "best_threshold": best_threshold
    })


# ==========================
# 4. Benchmark final
# ==========================

benchmark_df = pd.DataFrame(results)
bench_path = os.path.join(eval_dir, "benchmark.csv")
benchmark_df.to_csv(bench_path, index=False)

print("\n============================================================")
print("[OK] EVALUATION COMPLETED")
print("[INFO] Benchmark saved to:", bench_path)
print("============================================================")
