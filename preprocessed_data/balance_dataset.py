import pandas as pd
import yaml
from pathlib import Path
import os

def classify_class(size, major_th, medium_th):
    if size >= major_th:
        return "major"
    elif size >= medium_th:
        return "medium"
    else:
        return "minor"

def main():
    # Load config

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    CONFIG_PATH = os.path.normpath(os.path.join(BASE_DIR, "../config/config_sampling.yaml"))

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    input_path = Path(config["dataset"]["input_path"])
    output_path = Path(config["dataset"]["output_path"])
    chunk_size = config["dataset"]["chunk_size"]
    random_seed = config["dataset"]["random_seed"]

    benign_keep = config["sampling"]["benign_keep"]
    major_th = config["sampling"]["rules"]["major_threshold"]
    medium_th = config["sampling"]["rules"]["medium_threshold"]
    target_frac = config["sampling"]["target_frac"]
    enforce_min_benign = config["sampling"]["min_equals_benign"]

    print("[INFO] Loading dataset by chunks...")
    buffers = {}

    # Phase 1 — lecture par chunks
    for chunk in pd.read_csv(input_path, chunksize=chunk_size):

        # Strip des noms de colonnes pour éviter ' Label'
        fixed_cols = {c: c.strip() for c in chunk.columns}
        chunk = chunk.rename(columns=fixed_cols)

        # Affichage des colonnes une fois (avec noms propres)
        print(chunk.columns.tolist())

        for label, part in chunk.groupby("Label"):
            if label not in buffers:
                buffers[label] = []
            buffers[label].append(part)

    # Phase 2 — concaténation
    full = {label: pd.concat(parts, ignore_index=True) for label, parts in buffers.items()}

    print("\n[INFO] Dataset class sizes:")
    for label, df in full.items():
        print(f"  - {label}: {len(df)} rows")

    # Phase 3 — identification automatique des catégories
    class_info = {}
    for label, df in full.items():
        if label == "BENIGN":
            class_info[label] = ("benign", 1.0)
            continue
        
        size = len(df)
        category = classify_class(size, major_th, medium_th)
        frac = target_frac[category]
        class_info[label] = (category, frac)

    print("\n[INFO] Classification by category:")
    for label, (cat, frac) in class_info.items():
        print(f"  - {label}: {cat}, target fraction = {frac}")

    # Phase 4 — sampling
    benign_df = full["BENIGN"]
    sampled = [benign_df.sample(frac=benign_keep, random_state=random_seed)]

    benign_count = len(benign_df)

    print("\n[INFO] Sampling each attack class...")
    for label, df in full.items():
        if label == "BENIGN":
            continue
        
        category, frac = class_info[label]
        target_n = int(len(df) * frac)

        if enforce_min_benign:
            target_n = max(target_n, benign_count)

        print(f"  - {label}: keeping {target_n} samples out of {len(df)} ({category})")
        sampled.append(df.sample(n=target_n, random_state=random_seed))

    # Phase 5 — dataset final
    final_df = pd.concat(sampled, ignore_index=True)

    print("\n[INFO] Saving output dataset...")
    final_df.to_csv(output_path, index=False)

    print(f"[DONE] Final dataset saved at: {output_path}")
    print(f"[INFO] Final size: {len(final_df):,} rows")

if __name__ == "__main__":
    main()
