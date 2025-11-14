"""
Script de tuning automatique :
- GridSearchCV
- RandomizedSearchCV
- Sauvegarde du meilleur modèle
- Sauvegarde du meilleur score
"""

import os
import pandas as pd
import joblib
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = os.path.dirname(__file__)
processed_dir = os.path.normpath(os.path.join(BASE_DIR, "../data/processed"))

# Charger les données preprocessées
X_train = pd.read_csv(os.path.join(processed_dir, "train_processed.csv"))
y_train = pd.read_csv(os.path.join(processed_dir, "train_labels.csv")).values.ravel()

# Dossier pour sauvegarde
tuning_dir = os.path.normpath(os.path.join(BASE_DIR, "../tuning"))
os.makedirs(tuning_dir, exist_ok=True)


def run_grid_search(model, params, model_name):
    print(f"Running GridSearch for {model_name}...")

    search = GridSearchCV(
        model,
        params,
        cv=5,
        scoring="f1",
        n_jobs=-1
    )

    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    best_score = search.best_score_

    joblib.dump(best_model, os.path.join(tuning_dir, f"{model_name}_best_grid.pkl"))

    print(f"[OK] GridSearch {model_name}")
    print("Best Score:", best_score)
    print("Best Params:", search.best_params_)

    return best_model, best_score


def run_random_search(model, params, model_name):
    print(f"Running RandomSearch for {model_name}...")

    search = RandomizedSearchCV(
        model,
        params,
        cv=5,
        scoring="f1",
        n_jobs=-1,
        n_iter=20,
        random_state=42
    )

    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    best_score = search.best_score_

    joblib.dump(best_model, os.path.join(tuning_dir, f"{model_name}_best_random.pkl"))

    print(f"[OK] RandomSearch {model_name}")
    print("Best Score:", best_score)
    print("Best Params:", search.best_params_)

    return best_model, best_score


if __name__ == "__main__":
    # === Decision Tree ===
    dt_params = {
        "criterion": ["gini", "entropy"],
        "max_depth": [None, 10, 20, 40],
        "min_samples_split": [2, 10, 20],
        "min_samples_leaf": [1, 5, 10]
    }

    run_grid_search(DecisionTreeClassifier(random_state=42), dt_params, "decision_tree")
    run_random_search(DecisionTreeClassifier(random_state=42), dt_params, "decision_tree")

    # === Random Forest ===
    rf_params = {
        "n_estimators": [100, 200, 300],
        "max_depth": [None, 20, 40],
        "min_samples_split": [2, 10],
        "min_samples_leaf": [1, 5],
        "bootstrap": [True, False]
    }

    run_grid_search(RandomForestClassifier(random_state=42, n_jobs=-1), rf_params, "random_forest")
    run_random_search(RandomForestClassifier(random_state=42, n_jobs=-1), rf_params, "random_forest")

