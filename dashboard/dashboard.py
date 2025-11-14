"""
Dashboard automatique des performances :
- Charge evaluate/benchmark.csv
- Génère :
    - Bar charts
    - Comparaison F1/Recall/Precision/Accuracy/ROC-AUC
    - Heatmap de performances
    - ROC Curves des modèles
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def dashboard():
    base_dir = os.path.dirname(__file__)
    evaluate_dir = os.path.normpath(os.path.join(base_dir, "../evaluate"))

    # Charger benchmark
    bench_path = os.path.join(evaluate_dir, "benchmark.csv")
    df = pd.read_csv(bench_path)

    plots_dir = os.path.join(evaluate_dir, "dashboard")
    os.makedirs(plots_dir, exist_ok=True)

    # ===== Bar charts des métriques =====
    metrics = ["accuracy", "precision", "recall", "f1", "roc_auc", "throughput"]

    for metric in metrics:
        plt.figure(figsize=(8, 5))
        sns.barplot(data=df, x="model", y=metric)
        plt.title(f"{metric.upper()} comparison")
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, f"{metric}.png"))
        plt.close()

    # ===== Heatmap des performances =====
    plt.figure(figsize=(8, 6))
    sns.heatmap(df.set_index("model")[metrics], annot=True, fmt=".3f", cmap="Blues")
    plt.title("Model Performance Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "heatmap_performance.png"))
    plt.close()

    # ===== ROC Curves =====
    roc_folder = os.path.join(evaluate_dir, "plots")
    roc_files = [f for f in os.listdir(roc_folder) if f.endswith(".png")]

    for roc in roc_files:
        os.system(f"cp {os.path.join(roc_folder, roc)} {os.path.join(plots_dir, roc)}")

    print("[OK] Dashboard generated in /evaluate/dashboard")


if __name__ == "__main__":
    dashboard()
