"""
tuning.py

Script de tuning automatique (échantillonnage + recherche d'hyperparamètres) :
- Lit un config YAML (config_tuning.yaml)
- Échantillonne automatiquement un pourcentage du dataset pour le tuning
- Pour chaque modèle activé dans la section `models:` :
    - lance GridSearchCV, RandomizedSearchCV ou HalvingGridSearchCV selon config.tuning.search_method
    - sauvegarde le meilleur estimateur (joblib)
    - sauvegarde un rapport (JSON + txt) et les cv_results (CSV)
- Génère des fichiers destinés au dashboard dans output.dashboard_dir
- Conçu pour être utilisable avec de grands datasets (on échantillonne avant tuning)
"""

import os
import yaml
import time
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, HalvingGridSearchCV
from sklearn.model_selection import StratifiedKFold

# modèles sklearn de base
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier

# tentative d'import des boosteurs facultatifs
XGBClassifier = None
LGBMClassifier = None
CatBoostClassifier = None

# We'll import conditionally later based on config, but do lightweight try here so errors are visible early
try:
    import xgboost as xgb  # we may use xgb.XGBClassifier
    from xgboost import XGBClassifier as _XGB
    XGBClassifier = _XGB
except Exception:
    XGBClassifier = None

try:
    import lightgbm as lgb
    from lightgbm import LGBMClassifier as _LGBM
    LGBMClassifier = _LGBM
except Exception:
    LGBMClassifier = None

try:
    from catboost import CatBoostClassifier as _CAT
    CatBoostClassifier = _CAT
except Exception:
    CatBoostClassifier = None

# resampling libs: optional (we only sample with pandas; imblearn not required here)
try:
    from imblearn.over_sampling import RandomOverSampler, SMOTE
    from imblearn.under_sampling import RandomUnderSampler
    IMBLEARN_AVAILABLE = True
except Exception:
    IMBLEARN_AVAILABLE = False

# -------------------------
# Helpers
# -------------------------

def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def now_str():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def save_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

def top_cv_results(cv_results, top_k=10):
    # returns a small dataframe with the top_k results sorted by rank_test_score
    df = pd.DataFrame(cv_results)
    cols = [c for c in df.columns if ("mean_test" in c or "std_test" in c or "param_" in c or "rank_test" in c)]
    if "rank_test_score" in df.columns:
        rank_col = "rank_test_score"
    else:
        # fallback: use mean_test_score if rank not present
        rank_col = [c for c in df.columns if c.startswith("mean_test")][0]
    if rank_col in df.columns:
        df_sorted = df.sort_values(by=rank_col)
    else:
        df_sorted = df
    return df_sorted.head(top_k)

# -------------------------
# Load config
# -------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config_tuning.yaml")
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

# dataset config
dataset_cfg = cfg.get("dataset", {})
dataset_path = dataset_cfg.get("path", "../data/dataset.csv")
sample_percent = float(dataset_cfg.get("sample_percent", 0.02))
random_seed = int(dataset_cfg.get("random_seed", 42))

# output config
output_cfg = cfg.get("output", {})
MODEL_DIR = os.path.normpath(os.path.join(BASE_DIR, output_cfg.get("model_dir", "../models/")))
REPORT_DIR = os.path.normpath(os.path.join(BASE_DIR, output_cfg.get("report_dir", "./tuning_results/")))
DASHBOARD_DIR = os.path.normpath(os.path.join(BASE_DIR, output_cfg.get("dashboard_dir", "./evaluate/dashboard/")))

safe_mkdir(MODEL_DIR)
safe_mkdir(REPORT_DIR)
safe_mkdir(DASHBOARD_DIR)

# tuning config
tuning_cfg = cfg.get("tuning", {})
search_method = tuning_cfg.get("search_method", "halving")  # grid | random | halving
cv_folds = int(tuning_cfg.get("cv", 3))
n_jobs = int(tuning_cfg.get("n_jobs", -1))
random_state = int(tuning_cfg.get("random_state", 42)) if tuning_cfg.get("random_state") is not None else 42
n_iter_random = int(tuning_cfg.get("n_iter_random", 20))

models_cfg = cfg.get("models", {})
grids = cfg.get("grids", {})

print("============================================================")
print("[INFO] Tuning configuration loaded.")
print(f"[INFO] dataset: {dataset_path} | sample_percent: {sample_percent} | seed: {random_seed}")
print(f"[INFO] search_method: {search_method} | cv: {cv_folds} | n_jobs: {n_jobs}")
print("============================================================\n")

# -------------------------
# Load dataset (and sample)
# -------------------------
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

print("[INFO] Reading dataset (this may take some time for very large files)...")
df = pd.read_csv(dataset_path)
print(f"[INFO] Full dataset shape: {df.shape}")

# assume label column named 'Label' or 'label' — try to detect
label_col = None
for candidate in ("Label", "label", "target", "y"):
    if candidate in df.columns:
        label_col = candidate
        break
if label_col is None:
    raise ValueError("No label column found. Expected one of: Label, label, target, y")

# sample
if sample_percent <= 0 or sample_percent > 1.0:
    raise ValueError("sample_percent must be in (0, 1].")
sample_n = max(1, int(len(df) * sample_percent))
print(f"[INFO] Sampling {sample_percent*100:.3f}% -> {sample_n} rows for tuning (seed={random_seed})")
df_sample = df.sample(n=sample_n, random_state=random_seed).reset_index(drop=True)

X = df_sample.drop(columns=[label_col])
y = df_sample[label_col].values

print("[INFO] Sample shape:", X.shape, y.shape)

# Stratified CV
cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_seed)

# -------------------------
# Model registry builder
# -------------------------
def get_estimator_by_name(name):
    """Return an instantiated estimator (unfitted) for a given model name.
       The hyperparameter search will override parameters from the grid.
    """
    name = name.lower()
    if name == "decision_tree":
        return DecisionTreeClassifier(random_state=random_state)
    if name == "random_forest":
        return RandomForestClassifier(random_state=random_state, n_jobs=1)
    if name == "gradient_boosting":
        return GradientBoostingClassifier(random_state=random_state)
    if name == "adaboost":
        return AdaBoostClassifier(random_state=random_state)
    if name == "logistic_regression":
        return LogisticRegression(max_iter=1000, random_state=random_state)
    if name == "svm":
        return SVC(probability=True, random_state=random_state)
    if name == "naive_bayes":
        return GaussianNB()
    if name == "knn":
        return KNeighborsClassifier()
    if name == "xgboost":
        if XGBClassifier is None:
            print("[WARN] xgboost requested but not installed. Skipping XGBoost.")
            return None
        return XGBClassifier(random_state=random_state, n_jobs=1, use_label_encoder=False, verbosity=0)
    if name == "lightgbm":
        if LGBMClassifier is None:
            print("[WARN] lightgbm requested but not installed. Skipping LightGBM.")
            return None
        return LGBMClassifier(n_jobs=1, random_state=random_state)
    if name == "catboost":
        if CatBoostClassifier is None:
            print("[WARN] catboost requested but not installed. Skipping CatBoost.")
            return None
        return CatBoostClassifier(iterations=100, verbose=0, random_seed=random_state)
    print(f"[WARN] Unknown model requested: {name} -> skipping")
    return None

# -------------------------
# Search runner
# -------------------------
def run_search(estimator, param_grid, model_name):
    """Run the selected hyperparameter search and return the fitted search object."""
    if estimator is None:
        return None

    method = search_method.lower()
    searcher = None

    if method == "grid":
        searcher = GridSearchCV(
            estimator,
            param_grid,
            cv=cv,
            scoring="f1",
            n_jobs=n_jobs,
            verbose=1
        )
    elif method == "random":
        searcher = RandomizedSearchCV(
            estimator,
            param_grid,
            cv=cv,
            scoring="f1",
            n_jobs=n_jobs,
            n_iter=n_iter_random,
            random_state=random_state,
            verbose=1
        )
    elif method == "halving":
        # HalvingGridSearchCV is a good option for large datasets
        try:
            searcher = HalvingGridSearchCV(
                estimator,
                param_grid,
                cv=cv,
                scoring="f1",
                factor=3,
                resource='n_samples',
                max_resources=None,
                n_jobs=n_jobs,
                verbose=1
            )
        except Exception:
            # fallback to GridSearch if halving not available
            print("[WARN] HalvingGridSearchCV not available, falling back to GridSearchCV.")
            searcher = GridSearchCV(estimator, param_grid, cv=cv, scoring="f1", n_jobs=n_jobs, verbose=1)
    else:
        raise ValueError(f"Unknown search_method: {search_method}")

    # run search (safe)
    start = time.time()
    try:
        searcher.fit(X, y)
    except Exception as e:
        print(f"[ERROR] Search for {model_name} failed: {e}")
        return None
    end = time.time()
    print(f"[OK] Search for {model_name} finished in {end-start:.2f}s")
    return searcher

# -------------------------
# Main loop over models
# -------------------------
results_summary = []

for model_name, enabled in models_cfg.items():
    if not enabled:
        continue

    model_name_lower = model_name.lower()
    print("------------------------------------------------------------")
    print(f"[INFO] Tuning model: {model_name}")
    print("------------------------------------------------------------")

    estimator = get_estimator_by_name(model_name_lower)
    if estimator is None:
        print(f"[SKIP] Estimator for {model_name} unavailable. Skipping.")
        continue

    param_grid = grids.get(model_name_lower, None)
    if not param_grid:
        print(f"[WARN] No grid found for {model_name} in config; skipping.")
        continue

    # run the search
    search = run_search(estimator, param_grid, model_name)
    if search is None:
        print(f"[WARN] Search failed or returned None for {model_name}.")
        continue

    # collect results & save best model
    best_est = search.best_estimator_
    best_score = float(search.best_score_) if hasattr(search, "best_score_") else None
    best_params = search.best_params_ if hasattr(search, "best_params_") else {}

    timestamp = now_str()
    model_fname = f"{model_name}_{timestamp}_best.pkl"
    model_path = os.path.join(MODEL_DIR, model_fname)
    joblib.dump(best_est, model_path)
    print(f"[OK] Saved best model to: {model_path}")

    # save report (json + txt)
    rep = {
        "model": model_name,
        "timestamp": timestamp,
        "best_score": best_score,
        "best_params": best_params,
        "sample_used": sample_n,
        "search_method": search_method,
        "cv": cv_folds
    }
    rep_json_path = os.path.join(REPORT_DIR, f"{model_name}_{timestamp}_report.json")
    save_json(rep_json_path, rep)

    rep_txt_path = os.path.join(REPORT_DIR, f"{model_name}_{timestamp}_report.txt")
    with open(rep_txt_path, "w") as f:
        f.write(json.dumps(rep, indent=2))

    # save top cv_results
    try:
        top_df = top_cv_results(search.cv_results_, top_k=20)
        cv_csv_path = os.path.join(REPORT_DIR, f"{model_name}_{timestamp}_cv_results_top.csv")
        top_df.to_csv(cv_csv_path, index=False)
    except Exception:
        pass

    # record for summary
    results_summary.append(rep)

    # copy info to dashboard dir for quick viewing (small artifacts)
    try:
        # save best params as a small text file in dashboard dir
        dash_params_path = os.path.join(DASHBOARD_DIR, f"{model_name}_{timestamp}_best_params.txt")
        with open(dash_params_path, "w") as f:
            f.write(json.dumps(best_params, indent=2))
    except Exception:
        pass

# -------------------------
# Final summary save
# -------------------------
summary_path = os.path.join(REPORT_DIR, f"tuning_summary_{now_str()}.json")
save_json(summary_path, results_summary)
print("\n============================================================")
print("[OK] TUNING COMPLETE")
print("[INFO] Reports saved to:", REPORT_DIR)
print("[INFO] Models saved to:", MODEL_DIR)
print("============================================================")
