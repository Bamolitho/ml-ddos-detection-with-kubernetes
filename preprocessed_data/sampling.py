"""
Sampling script for binary DDoS vs BENIGN dataset creation.

Pipeline:
1. Load the raw dataset chunk by chunk (RAM-safe).
2. Group samples by original attack class.
3. Apply dynamic rules from config_sampling.yaml:
      - major / medium / minor classification
      - target_frac thresholds
      - min_equals_benign constraint
4. Undersample DDoS using ClusterCentroids.
5. Subsample BENIGN according to benign_keep.
6. Final balancing with SMOTEENN (when applicable).
7. Save the final balanced binary dataset.

This file is defensive:
 - preserves the Label column when cleaning,
 - drops non-numeric features before using imblearn,
 - handles tiny-class edge cases gracefully.
"""

import pandas as pd
import yaml
from pathlib import Path
import os
import numpy as np
from imblearn.under_sampling import ClusterCentroids
from imblearn.combine import SMOTEENN


def main():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    CONFIG_PATH = os.path.normpath(os.path.join(BASE_DIR, "../config/config_sampling.yaml"))

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    input_path = Path(config["dataset"]["input_path"])
    output_path = Path(config["dataset"]["output_path"])
    chunk_size = config["dataset"]["chunk_size"]
    random_seed = config["dataset"]["random_seed"]

    rules = config["sampling"]["rules"]
    target_frac = config["sampling"]["target_frac"]
    benign_keep = config["sampling"]["benign_keep"]
    enforce_min_benign = config["sampling"]["min_equals_benign"]

    print("[INFO] Loading dataset by chunks...")
    buffers = {}

    # -----------------------
    # Phase 1 — chunk loading
    # -----------------------
    for chunk in pd.read_csv(input_path, chunksize=chunk_size, low_memory=False):
        # fix column names
        fixed_cols = {c: c.strip() for c in chunk.columns}
        chunk = chunk.rename(columns=fixed_cols)

        for label, part in chunk.groupby("Label"):
            buffers.setdefault(label, []).append(part)

    # -----------------------
    # Phase 2 — concat
    # -----------------------
    full = {lab: pd.concat(parts, ignore_index=True) for lab, parts in buffers.items()}

    print("\n[INFO] Class sizes before sampling:")
    for lab, df in full.items():
        print(f"  - {lab}: {len(df)} rows")

    # -----------------------
    # Phase 3 — make binary
    # -----------------------
    df_all = pd.concat(full.values(), ignore_index=True)

    # Keep original counts BEFORE cleaning
    orig_counts = df_all["Label"].value_counts().to_dict()
    orig_benign = orig_counts.get("BENIGN", orig_counts.get("Benign", 0)) \
                  or orig_counts.get("benign", 0) \
                  or (df_all[df_all["Label"] == 0].shape[0] if 0 in df_all["Label"].unique() else 0)

    # Convert labels robustly to binary 0/1
    df_all["Label"] = df_all["Label"].apply(lambda x: 0 if str(x).lower() == "benign" else 1)
    df_all["Label"] = df_all["Label"].astype(int)

    benign_df = df_all[df_all["Label"] == 0].copy()
    ddos_df = df_all[df_all["Label"] == 1].copy()

    print(f"\n[INFO] BENIGN count: {len(benign_df)}")
    print(f"[INFO] DDoS count:   {len(ddos_df)}")

    # -----------------------
    # Phase 3.5 — DROP NON-NUMERIC COLUMNS FOR SAMPLING (but protect Label)
    # -----------------------
    cols_to_drop = ["Unnamed: 0", "Flow ID", "Source IP", "Destination IP", "Timestamp", "SimillarHTTP"]

    for col in cols_to_drop:
        if col in ddos_df.columns:
            ddos_df = ddos_df.drop(columns=[col])
        if col in benign_df.columns:
            benign_df = benign_df.drop(columns=[col])

    # Dynamically drop all non-numeric columns EXCEPT Label
    def drop_non_numeric_but_keep_label(df, df_name="df"):
        non_numeric = [c for c in df.select_dtypes(exclude=["number"]).columns.tolist() if c != "Label"]
        if non_numeric:
            print(f"[INFO] Dropping non-numeric columns from {df_name}: {non_numeric}")
            df = df.drop(columns=non_numeric, errors="ignore")
        return df

    ddos_df = drop_non_numeric_but_keep_label(ddos_df, "ddos_df")
    benign_df = drop_non_numeric_but_keep_label(benign_df, "benign_df")

    # After forced drops, coerce any remaining object columns to numeric where possible,
    # then drop columns that are still non-numeric.
    for df_name, df in [("ddos_df", ddos_df), ("benign_df", benign_df)]:
        for col in df.columns:
            if df[col].dtype == object and col != "Label":
                df[col] = pd.to_numeric(df[col], errors="coerce")
        # drop any columns that remain non-numeric (safety)
        non_numeric_after = [c for c in df.select_dtypes(exclude=["number"]).columns.tolist() if c != "Label"]
        if non_numeric_after:
            print(f"[WARN] Columns still non-numeric in {df_name} after coercion, dropping: {non_numeric_after}")
            df = df.drop(columns=non_numeric_after, errors="ignore")

        if df_name == "ddos_df":
            ddos_df = df
        else:
            benign_df = df

    # Remove rows with NaN introduced by coercion
    ddos_df = ddos_df.replace([np.inf, -np.inf], np.nan).dropna()
    benign_df = benign_df.replace([np.inf, -np.inf], np.nan).dropna()

    # -----------------------
    # Phase 4 — dynamic undersampling target calculation
    # -----------------------
    original_ddos = len(ddos_df)
    original_benign = len(benign_df)

    if original_ddos >= rules["major_threshold"]:
        fraction = target_frac["major"]
        scale_type = "MAJOR"
    elif original_ddos >= rules["medium_threshold"]:
        fraction = target_frac["medium"]
        scale_type = "MEDIUM"
    else:
        fraction = target_frac["minor"]
        scale_type = "MINOR"

    # target number of DDoS rows after undersampling
    target_ddos = max(1, int(original_ddos * fraction))

    if enforce_min_benign:
        target_ddos = max(target_ddos, original_benign)

    print(f"\n[INFO] DDoS class scale: {scale_type}")
    print(f"[INFO] Undersampling target for DDoS → {target_ddos:,}")

    # If ddos is already small or target >= current size, skip CC
    if original_ddos <= 2 or target_ddos >= original_ddos:
        print("[INFO] Skipping ClusterCentroids undersampling (dataset too small or target >= original).")
        # Prepare X_ddos_under/y_ddos_under directly from ddos_df
        X_ddos_under = ddos_df.drop(columns=["Label"])
        y_ddos_under = ddos_df["Label"].values
    else:
        # -----------------------
        # ClusterCentroids requires BOTH classes (0 and 1) in y.
        # We create a tiny benign placeholder so CC sees 2 classes, then remove placeholder rows.
        # -----------------------
        print("\n[INFO] Preparing data for ClusterCentroids...")

        # choose a single benign sample as placeholder (or create synthetic if none exist)
        if len(benign_df) >= 1:
            benign_placeholder = benign_df.sample(n=1, random_state=random_seed)
        else:
            # create a minimal benign placeholder by taking mean of ddos features (rare case)
            print("[WARN] No benign rows available for placeholder; creating a synthetic benign placeholder.")
            placeholder_values = ddos_df.drop(columns=["Label"]).mean(axis=0).to_frame().T
            benign_placeholder = placeholder_values.copy()
            benign_placeholder["Label"] = 0

        temp_df = pd.concat([ddos_df, benign_placeholder], ignore_index=True)

        X_temp = temp_df.drop(columns=["Label"])
        y_temp = temp_df["Label"].values

        cc = ClusterCentroids(sampling_strategy={1: target_ddos}, random_state=random_seed)

        X_cc, y_cc = cc.fit_resample(X_temp, y_temp)

        # Keep only resampled DDoS rows (y_cc == 1)
        mask_ddos = (y_cc == 1)
        X_ddos_under = X_cc[mask_ddos]
        y_ddos_under = y_cc[mask_ddos]

        # If result is numpy 2D array, convert to DataFrame matching X_temp columns
        if not isinstance(X_ddos_under, pd.DataFrame):
            X_ddos_under = pd.DataFrame(X_ddos_under, columns=X_temp.columns)

        print(f"[INFO] DDoS after ClusterCentroids: {len(X_ddos_under)} rows")

    # -----------------------
    # Phase 5 — BENIGN sampling (subsample according to benign_keep)
    # -----------------------
    target_benign = max(1, int(original_benign * benign_keep)) if original_benign > 0 else 0
    print(f"\n[INFO] Selecting BENIGN → {target_benign:,}")

    if target_benign == 0:
        print("[WARN] No benign samples available to include. Continuing with DDoS-only dataset (not ideal).")
        benign_sampled = pd.DataFrame(columns=ddos_df.drop(columns=["Label"]).columns).astype(float)
        benign_sampled["Label"] = pd.Series(dtype=int)
    else:
        # sample up to available benign rows
        n_ben = min(len(benign_df), target_benign)
        benign_sampled = benign_df.sample(n=n_ben, replace=False, random_state=random_seed)

    # Combine before SMOTEENN
    X = pd.concat([X_ddos_under.reset_index(drop=True), benign_sampled.drop(columns=["Label"]).reset_index(drop=True)],
                  ignore_index=True)
    y = pd.concat([pd.Series(y_ddos_under).reset_index(drop=True), benign_sampled["Label"].reset_index(drop=True)],
                  ignore_index=True)

    # -----------------------
    # Phase 6 — SMOTEENN (only if both classes present)
    # -----------------------
    unique_labels = set(y.tolist())
    if len(unique_labels) < 2:
        print("[WARN] Not enough classes to run SMOTEENN. Skipping SMOTEENN step.")
        X_res = X
        y_res = y
    else:
        print("\n[INFO] Running SMOTEENN...")
        sm = SMOTEENN(random_state=random_seed)
        X_res, y_res = sm.fit_resample(X, y)

        # convert to DataFrame if needed
        if not isinstance(X_res, pd.DataFrame):
            X_res = pd.DataFrame(X_res, columns=X.columns)

    # -----------------------
    # Phase 7 — save final file
    # -----------------------
    final_df = pd.concat([X_res.reset_index(drop=True), pd.Series(y_res, name="Label").reset_index(drop=True)], axis=1)

    print("\n[INFO] Final dataset distribution:")
    print(final_df["Label"].value_counts())

    # Ensure parent folder exists and write CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)

    print(f"\n[DONE] Saved at: {output_path}")
    print(f"[SIZE] {len(final_df):,} rows")


if __name__ == "__main__":
    main()
