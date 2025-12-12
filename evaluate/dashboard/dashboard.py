"""
Dashboard automatique des performances :
- Charge evaluate/benchmark.csv
- Génère :
    - Bar charts
    - Comparaison F1/Recall/Precision/Accuracy/ROC-AUC
    - Heatmap des performances
    - ROC Curves des modèles
- Génère un rapport HTML avec toutes les images dans l'ordre
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def dashboard():
    base_dir = os.path.dirname(__file__)
    evaluate_dir = os.path.normpath(os.path.join(base_dir, "../"))

    # Charger benchmark
    bench_path = os.path.join(evaluate_dir, "benchmark.csv")
    df = pd.read_csv(bench_path)

    # Dossiers
    plots_dir = base_dir
    os.makedirs(plots_dir, exist_ok=True)

    # ===== Bar charts des métriques =====
    metrics = ["accuracy", "precision", "recall", "f1", "roc_auc", "throughput"]

    generated_images = []  # liste pour le futur rapport HTML

    for metric in metrics:
        plt.figure(figsize=(8, 5))
        sns.barplot(data=df, x="model", y=metric)
        plt.title(f"{metric.upper()} comparison")
        plt.tight_layout()

        out = os.path.join(plots_dir, f"{metric}.png")
        plt.savefig(out)
        plt.close()

        generated_images.append((f"Comparaison {metric.upper()}", out))

    # ===== Heatmap des performances =====
    plt.figure(figsize=(8, 6))
    sns.heatmap(df.set_index("model")[metrics], annot=True, fmt=".3f", cmap="Blues")
    plt.title("Model Performance Heatmap")
    plt.tight_layout()

    heatmap_path = os.path.join(plots_dir, "heatmap_performance.png")
    plt.savefig(heatmap_path)
    plt.close()

    generated_images.append(("Heatmap des performances", heatmap_path))

    # ===== ROC Curves =====
    roc_folder = os.path.join(evaluate_dir, "plots")
    roc_files = sorted([f for f in os.listdir(roc_folder) if f.endswith(".png")])

    for roc in roc_files:
        src = os.path.join(roc_folder, roc)
        dst = os.path.join(plots_dir, roc)
        os.system(f"cp '{src}' '{dst}'")

        generated_images.append((f"Courbe ROC – {roc.replace('.png','')}", dst))

    # ============================================================
    # Génération du mini-rapport HTML
    # ============================================================

    html_path = os.path.join(plots_dir, "dashboard_report.html")

    with open(html_path, "w") as f:
        f.write("<html><head><title>Dashboard Performance</title></head><body>")
        f.write("<h1>Dashboard automatique – Résultats des modèles</h1>")

        for title, img_path in generated_images:
            file_name = os.path.basename(img_path)
            f.write(f"<h2>{title}</h2>")
            f.write(f"<img src='{file_name}' style='max-width:800px;'><hr>")

        f.write("</body></html>")

    print("[OK] Dashboard generated in /evaluate/dashboard")
    print("[OK] HTML report generated:", html_path)


if __name__ == "__main__":
    dashboard()
