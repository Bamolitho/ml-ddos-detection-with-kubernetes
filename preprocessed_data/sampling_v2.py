import pandas as pd
import numpy as np
import yaml
import os
from pathlib import Path

def main():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    CONFIG_PATH = os.path.normpath(os.path.join(BASE_DIR, "../config/config_sampling.yaml"))

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    input_path = Path(config["dataset"]["input_path"])
    output_path = Path(config["dataset"]["output_path"])
    chunk_size = config["dataset"]["chunk_size"]
    random_seed = config["dataset"]["random_seed"]

    rng = np.random.default_rng(random_seed)

    tmp_benign = Path("tmp_benign.csv")
    tmp_ddos = Path("tmp_ddos.csv")

    # Remove temp files
    if tmp_benign.exists(): tmp_benign.unlink()
    if tmp_ddos.exists(): tmp_ddos.unlink()

    print("[INFO] Streaming dataset...")

    benign_count = 0
    ddos_count = 0

    # Probability for DDoS undersampling (keeps around ≈10%)
    DDOS_KEEP_PROB = config["sampling"].get("ddos_keep_prob", 0.1)

    for chunk in pd.read_csv(input_path, chunksize=chunk_size, low_memory=False):
        # Normalize columns
        chunk.columns = [c.strip() for c in chunk.columns]

        # Binary label
        chunk["Label"] = chunk["Label"].apply(lambda x: 0 if str(x).lower() == "benign" else 1).astype(int)

        # Separate
        benign = chunk[chunk["Label"] == 0]
        ddos = chunk[chunk["Label"] == 1]

        # Write BENIGN (keep everything)
        if not benign.empty:
            benign.to_csv(tmp_benign, mode="a", header=not tmp_benign.exists(), index=False)
            benign_count += len(benign)

        # Write sampled DDoS (random keep)
        if not ddos.empty:
            mask = rng.random(len(ddos)) < DDOS_KEEP_PROB
            ddos_sampled = ddos[mask]

            if not ddos_sampled.empty:
                ddos_sampled.to_csv(tmp_ddos, mode="a", header=not tmp_ddos.exists(), index=False)
                ddos_count += len(ddos_sampled)

        del chunk

        print(f"  Processed chunk – BENIGN={benign_count:,}, DDoS={ddos_count:,}")

    print("\n[INFO] Temp files ready:")
    print(f"  BENIGN stored: {benign_count:,}")
    print(f"  DDoS stored (sampled): {ddos_count:,}")

    # -------------------------------------------------
    # FINAL BALANCING (simple undersampling to match min class)
    # -------------------------------------------------

    df_b = pd.read_csv(tmp_benign)
    df_d = pd.read_csv(tmp_ddos)

    min_size = min(len(df_b), len(df_d))

    print(f"\n[INFO] Final balancing to {min_size:,} samples per class...")

    df_b = df_b.sample(min_size, random_state=random_seed)
    df_d = df_d.sample(min_size, random_state=random_seed)

    final_df = pd.concat([df_b, df_d], ignore_index=True)
    final_df = final_df.sample(frac=1, random_state=random_seed).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)

    print(f"\n[DONE] Final balanced dataset saved at: {output_path}")
    print(f"[SIZE] {len(final_df):,} rows")

if __name__ == "__main__":
    main()
