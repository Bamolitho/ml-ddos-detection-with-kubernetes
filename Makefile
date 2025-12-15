# ============================================================
# MAKEFILE — ML DDoS Detection + Docker + Kubernetes
# ============================================================

# ============================================================
# (0) VARIABLES GLOBALES
# ============================================================

PYTHON      = python3
VENV        = amomo_venv

APP_NAME    = ml-ddos-detection
IMAGE_TAG   = latest

# Répertoires ML
DATA_DIR        = data
PREP_DIR        = preprocessed_data
MODELS_DIR      = models
EVAL_DIR        = evaluate
DASHBOARD_DIR   = evaluate/dashboard
TUNING_DIR      = tuning

# Kubernetes
K8S_BASE    = k8s/base
K8S_DEV     = k8s/overlays/dev
K8S_PROD    = k8s/overlays/prod


# ============================================================
# (1) ENVIRONNEMENT PYTHON
# ============================================================

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Active le venv avec : source $(VENV)/bin/activate"

install:
	$(PYTHON) -m pip install -r requirements.txt


# ============================================================
# (2) PIPELINE MACHINE LEARNING (RÉEL)
# ============================================================

preprocess:
	$(PYTHON) preprocessed_data/preprocessed_data.py

sampling:
	$(PYTHON) preprocessed_data/sampling.py

train:
	$(PYTHON) train/train_models.py

tune:
	$(PYTHON) tuning/hyperparam_search.py

evaluate:
	$(PYTHON) evaluate/evaluate_models.py

dashboard:
	$(PYTHON) evaluate/dashboard/dashboard.py
	@echo "Dashboard ML généré dans $(DASHBOARD_DIR)"

inference:
	$(PYTHON) inference/predict.py

pipeline-ml:
	chmod +x run_pipeline_ML.sh
	./run_pipeline_ML.sh


# ============================================================
# (3) CAPTURE & ORCHESTRATION TEMPS RÉEL
# ============================================================

capture:
	$(PYTHON) capture/realtime_capture.py

orchestrator:
	$(PYTHON) capture/orchestrator_prediction.py

show-packets:
	$(PYTHON) capture/show_packets.py


# ============================================================
# (4) DOCKER COMPOSE (SYSTÈME COMPLET)
# ============================================================

compose-up:
	docker compose up -d

compose-down:
	docker compose down -v

compose-logs:
	docker compose logs -f

compose-ps:
	docker ps


# ============================================================
# (5) KUBERNETES & MINIKUBE
# ============================================================

install-k8s-env:
	chmod +x install_kubernetes_env.sh
	./install_kubernetes_env.sh

start-minikube:
	minikube start
	minikube status
	kubectl get nodes

deploy-dev:
	kubectl apply -k $(K8S_DEV)
	kubectl get all

deploy-prod:
	kubectl apply -k $(K8S_PROD)
	kubectl get all

delete-dev:
	kubectl delete -k $(K8S_DEV) || true

delete-prod:
	kubectl delete -k $(K8S_PROD) || true

status:
	kubectl get pods,svc,configmap,secret

get-url:
	minikube service flask-service --url

open:
	minikube service flask-service


# ============================================================
# (6) AUTOMATION COMPLÈTE
# ============================================================

reset-dev:
	$(MAKE) compose-down
	$(MAKE) compose-up

auto-deploy-dev:
	chmod +x run_system_k8s.sh
	./run_system_k8s.sh --dev

auto-deploy-prod:
	chmod +x run_system_k8s.sh
	./run_system_k8s.sh --prod


# ============================================================
# (7) NETTOYAGE
# ============================================================

clean-ml:
	rm -rf $(MODELS_DIR)/*.pkl || true
	rm -rf $(EVAL_DIR)/reports/* || true
	rm -rf $(EVAL_DIR)/plots/* || true
	rm -rf $(DASHBOARD_DIR)/*.png || true
	rm -rf $(DASHBOARD_DIR)/*.html || true
	rm -rf $(PREP_DIR)/*.pkl || true

clean-py:
	rm -rf __pycache__ **/__pycache__ *.pyc **/*.pyc || true

purge:
	$(MAKE) clean-ml
	$(MAKE) clean-py
	rm -rf $(VENV) || true


# ============================================================
# (8) OUTILS
# ============================================================

tree:
	@echo "Structure du projet:"
	@tree -I '__pycache__|*.pyc|$(VENV)' -L 6 2>/dev/null || ls -R


# ============================================================
# (9) GIT
# ============================================================

github:
	git add .
	git commit -m "ml-ddos-detection-with-k8s"
	git push


# ============================================================
# (10) AIDE
# ============================================================

help:
	@echo ""
	@echo "ENV PYTHON"
	@echo "  make venv | make install"
	@echo ""
	@echo "PIPELINE ML"
	@echo "  make preprocess | sampling | train | tune"
	@echo "  make evaluate | dashboard | inference"
	@echo "  make pipeline-ml"
	@echo ""
	@echo "CAPTURE TEMPS RÉEL"
	@echo "  make capture | orchestrator"
	@echo ""
	@echo "DOCKER COMPOSE"
	@echo "  make compose-up | compose-down | compose-logs"
	@echo ""
	@echo "KUBERNETES"
	@echo "  make deploy-dev | deploy-prod"
	@echo "  make auto-deploy-dev | auto-deploy-prod"
	@echo ""
