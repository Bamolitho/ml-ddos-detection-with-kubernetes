"""
Advanced evaluation for ALL models automatically.
Generates:
- Accuracy, Precision, Recall, F1
- ROC AUC + ROC Curve
- Inference time + throughput
- Best threshold (Youden J)
- Detailed reports
- Global benchmark
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
from sklearn.exceptions import NotFittedError

# ============================================================
# 1. Load Data
# ============================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
processed_dir = os.path.normpath(os.path.join(BASE_DIR, "../data/processed"))

X_test = pd.read_csv(os.path.join(processed_dir, "test_processed.csv"))
y_test = pd.read_csv(os.path.join(processed_dir, "test_labels.csv")).values.ravel()

print("============================================================")
print("[INFO] Loading processed test dataset...")
print("============================================================")
print(f"[INFO] Test shape: {X_test.shape}")
print("[OK] Data loaded successfully.\n")


# ============================================================
# 2. Directory Structure
# ============================================================

eval_dir = os.path.normpath(os.path.join(BASE_DIR, "../evaluate"))
plots_dir = os.path.join(eval_dir, "plots")
reports_dir = os.path.join(eval_dir, "reports")

os.makedirs(eval_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)


# ============================================================
# 3. Load ALL models
# ============================================================

models_dir = os.path.normpath(os.path.join(BASE_DIR, "../models"))
model_files = [f for f in os.listdir(models_dir) if f.endswith(".pkl")]

results = []

print("============================================================")
print("[INFO] Evaluating models...")
print("============================================================")


# ============================================================
#  UTIL: fallback if model has no predict_proba
# ============================================================

def safe_predict_proba(model, X):
    """Handles models without predict_proba (e.g., SVM/Linear models)."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-12)
        return scores
    preds = model.predict(X)
    return preds.astype(float)


# ============================================================
# 4. Evaluation loop
# ============================================================

for file in model_files:
    model_path = os.path.join(models_dir, file)
    name = file.replace(".pkl", "")

    print("------------------------------------------------------------")
    print(f"[INFO] Evaluating model: {name}")
    print("------------------------------------------------------------")

    try:
        model = joblib.load(model_path)
    except:
        print("[ERROR] Could not load model, skipping.")
        continue

    try:
        # Inference timing
        start = time.time()
        probas = safe_predict_proba(model, X_test)
        end = time.time()
    except NotFittedError:
        print("[ERROR] Model not fitted, skipping.")
        continue

    inference_time = end - start
    throughput = len(X_test) / inference_time

    # Default threshold
    preds = (probas >= 0.5).astype(int)

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    roc_auc = roc_auc_score(y_test, probas)

    fpr, tpr, thresholds = roc_curve(y_test, probas)

    # Best threshold (Youden J)
    J = tpr - fpr
    best_idx = np.argmax(J)
    best_threshold = thresholds[best_idx]

    # ROC Curve
    plt.figure()
    plt.plot(fpr, tpr)
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC Curve - {name}")

    plot_path = os.path.join(plots_dir, f"{name}_roc.png")
    plt.savefig(plot_path)
    plt.close()

    # Detailed report
    report_path = os.path.join(reports_dir, f"{name}_report.txt")
    with open(report_path, "w") as f:
        f.write(f"""
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

""")

    print("[OK] Report saved:", report_path)

    results.append({
        "model": name,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": roc_auc,
        "inference_time": inference_time,
        "throughput": throughput,
        "best_threshold": best_threshold
    })


# ============================================================
# 5. Final benchmark
# ============================================================

df = pd.DataFrame(results).sort_values(by="roc_auc", ascending=False)
bench_path = os.path.join(eval_dir, "benchmark.csv")
df.to_csv(bench_path, index=False)

print("\n============================================================")
print("[OK] EVALUATION COMPLETE")
print("[INFO] Benchmark saved to:", bench_path)
print("============================================================")
