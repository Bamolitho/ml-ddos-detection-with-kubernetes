# ==============================
# CONFIGURATION DU PROJET
# ==============================

PYTHON = python3
VENV = amomo_venv

# Répertoires importants
DATA_DIR = data
PREP_DIR = preprocessed_data
MODELS_DIR = models
EVAL_DIR = evaluate
DASHBOARD_DIR = evaluate/dashboard
TUNING_DIR = tuning

# ==============================
# (0) INSTALLATION ENV
# ==============================

install:
	$(PYTHON) -m pip install -r requirements.txt

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Active ton venv avec: source $(VENV)/bin/activate"

# ==============================
# (1) PRÉPROCESSING
# ==============================

preprocess:
	$(PYTHON) train/preprocess.py

# ==============================
# (2) TRAINING
# ==============================

train:
	$(PYTHON) train/train.py

# ==============================
# (3) TUNING
# ==============================

tune:
	$(PYTHON) tuning/tuning.py

# ==============================
# (4) EVALUATION
# ==============================

evaluate:
	$(PYTHON) evaluate/evaluate_models.py

dashboard:
	$(PYTHON) evaluate/dashboard.py
	@echo "Dashboard généré dans $(DASHBOARD_DIR)"

# ==============================
# (5) INFERENCE
# ==============================

inference:
	$(PYTHON) inference/inference.py

# ==============================
# (6) PIPELINE COMPLET
# ==============================

pipeline:
	chmod +x run_pipeline.sh
	./run_pipeline.sh

# ==============================
# (7) NETTOYAGE
# ==============================

## Nettoyage simple
clean:
	rm -rf $(MODELS_DIR)/*.pkl || true
	rm -rf $(EVAL_DIR)/reports/* || true
	rm -rf $(EVAL_DIR)/plots/* || true
	rm -rf $(DASHBOARD_DIR)/*.png || true
	rm -rf $(DASHBOARD_DIR)/*.html || true
	rm -rf $(PREP_DIR)/* || true

## Nettoyage complet
purge: clean
	rm -rf __pycache__ **/__pycache__ || true
	rm -rf *.pyc **/*.pyc || true
	rm -rf $(VENV) || true

# ==============================
# (8) OUTILS
# ==============================

tree:
	@echo "Structure du projet:"
	tree -I '__pycache__|*.pyc|$(VENV)' -L 5

help:
	@echo "Commandes disponibles :"
	@echo ""
	@echo "  make install        - Installer dépendances"
	@echo "  make venv           - Créer un environnement virtuel"
	@echo ""
	@echo "  make preprocess     - Lancer preprocessing"
	@echo "  make train          - Entraîner modèles"
	@echo "  make tune           - Tuning hyperparamètres"
	@echo "  make evaluate       - Évaluation modèles"
	@echo "  make dashboard      - Générer dashboard"
	@echo "  make inference      - Lancer inference"
	@echo ""
	@echo "  make pipeline       - Lancer run_pipeline.sh"
	@echo ""
	@echo "  make clean          - Nettoyage fichiers générés"
	@echo "  make purge          - Nettoyage total + venv"
	@echo "  make tree           - Afficher structure du projet"

