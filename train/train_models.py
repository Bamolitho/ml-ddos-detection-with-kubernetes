import os
import yaml
import time
import joblib
import pandas as pd
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

# Tree-based
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier

# Linear
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

# Simple
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier

# Try optional boosters (graceful fallback)
try:
    from xgboost import XGBClassifier
except ImportError:
    print("[INFO] xgboost non installé")
    XGBClassifier = None

try:
    from lightgbm import LGBMClassifier
except ImportError:
    print("[INFO] lightgbm non installé")
    LGBMClassifier = None

try:
    from catboost import CatBoostClassifier
except ImportError:
    print("[INFO] catboost non installé")
    CatBoostClassifier = None

# Try resampling libs (graceful fallback)
try:
    from imblearn.over_sampling import RandomOverSampler, SMOTE
    from imblearn.under_sampling import RandomUnderSampler
    IMBLEARN_AVAILABLE = True
except Exception:
    print("[INFO] IMBLEARN_AVAILABLE = False")
    IMBLEARN_AVAILABLE = False

# ============================================================
# Load CONFIG
# ============================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.normpath(os.path.join(BASE_DIR, "../config/config_train.yaml"))

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

model_flags = config.get("models", {})
hyper = config.get("hyperparameters", {})
imbalance_cfg = config.get("imbalance", {})

print("============================================================")
print("[INFO] Configuration loaded.")
print("============================================================\n")


# ============================================================
# Load DATA
# ============================================================

processed_dir = os.path.normpath(os.path.join(BASE_DIR, "../data/processed"))
X_train = pd.read_csv(os.path.join(processed_dir, "train_processed.csv"))
y_train = pd.read_csv(os.path.join(processed_dir, "train_labels.csv")).values.ravel()

print("[INFO] Training shape:", X_train.shape)


# ============================================================
# Handle IMBALANCE (none | oversample | undersample | smote | class_weight | hybrid)
# ============================================================

strategy = imbalance_cfg.get("strategy", "class_weight")
oversample_method = imbalance_cfg.get("oversample_method", "random")
undersample_method = imbalance_cfg.get("undersample_method", "random")
undersample_ratio = float(imbalance_cfg.get("undersample_ratio", 0.5))
oversample_ratio = float(imbalance_cfg.get("oversample_ratio", 1.0))
auto_class_weight = bool(imbalance_cfg.get("auto_class_weight", True))

print("============================================================")
print(f"[INFO] Imbalance strategy: {strategy}")
print("============================================================")

# compute class_weight mapping if requested
class_weight_map = None
if strategy == "class_weight" and auto_class_weight:
    classes = np.unique(y_train)
    cw = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
    class_weight_map = {cls: float(w) for cls, w in zip(classes, cw)}
    print("[INFO] Computed class weights:", class_weight_map)

# apply resampling if needed
if strategy in ("oversample", "undersample", "smote", "hybrid"):
    if not IMBLEARN_AVAILABLE:
        print("[WARN] imbalanced-learn not installed — skipping sampling step.")
    else:
        if strategy == "oversample":
            if oversample_method == "random":
                sampler = RandomOverSampler(sampling_strategy=oversample_ratio)
                X_train, y_train = sampler.fit_resample(X_train, y_train)
                print(f"[INFO] Random oversampling applied, new shape: {X_train.shape}")
            elif oversample_method == "smote":
                sampler = SMOTE(sampling_strategy=oversample_ratio, n_jobs=-1)
                X_train, y_train = sampler.fit_resample(X_train, y_train)
                print(f"[INFO] SMOTE oversampling applied, new shape: {X_train.shape}")
            else:
                print(f"[WARN] Unknown oversample_method: {oversample_method} — skipping.")

        elif strategy == "undersample":
            if undersample_method == "random":
                sampler = RandomUnderSampler(sampling_strategy=undersample_ratio)
                X_train, y_train = sampler.fit_resample(X_train, y_train)
                print(f"[INFO] Random undersampling applied, new shape: {X_train.shape}")
            else:
                print(f"[WARN] Unknown undersample_method: {undersample_method} — skipping.")

        elif strategy == "smote":
            # explicit SMOTE
            sampler = SMOTE(sampling_strategy=oversample_ratio, n_jobs=-1)
            X_train, y_train = sampler.fit_resample(X_train, y_train)
            print(f"[INFO] SMOTE applied, new shape: {X_train.shape}")

        elif strategy == "hybrid":
            # hybrid: oversample then undersample
            if oversample_method == "smote":
                over = SMOTE(sampling_strategy=oversample_ratio, n_jobs=-1)
            else:
                over = RandomOverSampler(sampling_strategy=oversample_ratio)
            X_train, y_train = over.fit_resample(X_train, y_train)
            if undersample_method == "random":
                under = RandomUnderSampler(sampling_strategy=undersample_ratio)
                X_train, y_train = under.fit_resample(X_train, y_train)
            print(f"[INFO] Hybrid sampling applied, new shape: {X_train.shape}")


# ============================================================
# Utility: prepare model params and class-weight conversion
# ============================================================

def apply_class_weight_to_params(model_name, params, cw_map):
    """
    Modify / inject parameters for models that don't accept sklearn-style class_weight.
    Returns a copy of params (dict).
    """
    p = dict(params) if params else {}
    if not cw_map:
        return p

    # compute pos/neg ratio for scale_pos_weight (XGBoost)
    # assume binary labels 0/1
    # scale_pos_weight = negatives / positives
    counts = np.bincount(y_train.astype(int))
    if len(counts) < 2:
        neg, pos = counts[0], 0
    else:
        neg, pos = counts[0], counts[1]
    scale_pos_weight = float(neg) / float(pos + 1e-12)

    if model_name == "xgboost":
        # XGBoost uses scale_pos_weight
        p["scale_pos_weight"] = scale_pos_weight
    elif model_name == "lightgbm":
        # LightGBM accepts class_weight param (can be "balanced" or dict)
        # supply dict mapping class->weight if available
        p["class_weight"] = cw_map
    elif model_name == "catboost":
        # CatBoost expects a list of weights per class ordered by class label
        # build list from cw_map
        # If classes are not 0/1, we map them by sorted order
        classes_sorted = sorted(list(cw_map.keys()))
        weights_list = [float(cw_map[c]) for c in classes_sorted]
        p["class_weights"] = weights_list
    else:
        # sklearn models generally accept class_weight parameter directly
        if "class_weight" in p:
            p["class_weight"] = cw_map
    return p


# ============================================================
# Model Builders (reads hyperparameters from config)
# ============================================================

def build_model(name):
    p = hyper.get(name, {}) or {}

    # ensure we don't pass null (None) values where constructors break;
    # leave as-is and rely on scikit/XG/LGB/Cat to handle None where supported.
    p = dict(p)

    # inject class-weight adapted params if needed
    if class_weight_map is not None:
        p = apply_class_weight_to_params(name, p, class_weight_map)

    # instantiate, handling missing optional libs gracefully
    if name == "decision_tree":
        return DecisionTreeClassifier(**p)

    if name == "random_forest":
        return RandomForestClassifier(**p)

    if name == "gradient_boosting":
        return GradientBoostingClassifier(**p)

    if name == "adaboost":
        return AdaBoostClassifier(**p)

    if name == "xgboost":
        if XGBClassifier is None:
            print("[WARN] xgboost not installed — skipping xgboost.")
            return None
        return XGBClassifier(**p)

    if name == "lightgbm":
        if LGBMClassifier is None:
            print("[WARN] lightgbm not installed — skipping lightgbm.")
            return None
        return LGBMClassifier(**p)

    if name == "catboost":
        if CatBoostClassifier is None:
            print("[WARN] catboost not installed — skipping catboost.")
            return None
        return CatBoostClassifier(**p)

    if name == "logistic_regression":
        return LogisticRegression(**p)

    if name == "svm":
        return SVC(**p)

    if name == "naive_bayes":
        return GaussianNB(**p)

    if name == "knn":
        return KNeighborsClassifier(**p)

    raise ValueError(f"Unknown model: {name}")


# ============================================================
# Training Loop
# ============================================================

models_dir = os.path.normpath(os.path.join(BASE_DIR, "../models"))
os.makedirs(models_dir, exist_ok=True)

for model_name, active in model_flags.items():
    if not active:
        continue

    print("------------------------------------------------------------")
    print(f"[INFO] Training model: {model_name}")
    print("------------------------------------------------------------")

    model = build_model(model_name)
    if model is None:
        print(f"[WARN] Model {model_name} not available — skipped.")
        continue

    # Some estimators (like XGBoost LGBM) accept class weights via params already.
    # For sklearn estimators that accept attribute 'class_weight' but didn't receive it via params,
    # set it here.
    if class_weight_map is not None and hasattr(model, "class_weight") and not getattr(model, "class_weight", None):
        try:
            model.class_weight = class_weight_map
        except Exception:
            # ignore if not assignable
            pass

    # Fit
    print("Labels in training:", np.unique(y_train, return_counts=True))
    # print("Labels in test:", np.unique(y_test, return_counts=True))
    # print("Labels in val:", np.unique(y_val, return_counts=True))

    start = time.time()
    model.fit(X_train, y_train)
    end = time.time()

    print(f"[OK] Training finished in {end - start:.2f} sec.")

    # Save
    out = os.path.join(models_dir, f"{model_name}.pkl")
    joblib.dump(model, out)
    print("[OK] Saved model:", out)


print("\n============================================================")
print("[OK] TRAINING COMPLETE")
print("============================================================")
