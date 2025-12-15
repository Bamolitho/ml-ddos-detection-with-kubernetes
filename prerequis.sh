#!/bin/bash

# ============================================================
# Script : prerequis.sh
# Objectif :
#   - Générer les fichiers sensibles nécessaires au projet
#   - .env (racine du projet)
#   - k8s/base/secret.yaml (Kubernetes)
#
# IMPORTANT :
#   Ces fichiers contiennent des SECRETS.
#   Ils doivent être MODIFIÉS avant un déploiement réel.
# ============================================================

set -e

PROJECT_ROOT="$(pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
K8S_SECRET_DIR="$PROJECT_ROOT/k8s/base"
K8S_SECRET_FILE="$K8S_SECRET_DIR/secret.yaml"

echo "Initialisation des prérequis du projet..."
echo "Racine du projet : $PROJECT_ROOT"
echo

# ------------------------------------------------------------
# Création du fichier .env
# ------------------------------------------------------------
if [ -f "$ENV_FILE" ]; then
  echo "[INFO] Le fichier .env existe déjà -> ignoré"
else
  echo "[INFO] Création du fichier .env"

  cat << 'EOF' > "$ENV_FILE"
# ============================================================
# Fichier .env
# ============================================================
# ATTENTION :
# - Ne jamais commit ce fichier
# - Changer toutes les valeurs par défaut en production
# ============================================================

# -------------------
# Configuration MySQL
# -------------------
DB_ROOT_PASSWORD=CHANGE_MOI_ROOT_PASSWORD
MYSQL_ROOT_PASSWORD=CHANGE_MOI_ROOT_PASSWORD
MYSQL_DATABASE=ddos_detection
MYSQL_USER=bank_user
MYSQL_PASSWORD=CHANGE_MOI_DB_PASSWORD

# -------------------
# Configuration Flask / Application
# -------------------
FLASK_ENV=production
DB_HOST=mysql_db
DB_PORT=3306
DB_NAME=ddos_detection
DB_DATABASE=ddos_detection
DB_USER=bank_user
DB_PASSWORD=CHANGE_MOI_DB_PASSWORD

# -------------------
# SOAR
# -------------------
SOAR_SECRET=CHANGE_MOI_SOAR_SECRET
SOAR_MIN_PROBABILITY=0.70

# -------------------
# TELEGRAM
# -------------------
TELEGRAM_BOT_TOKEN=CHANGE_MOI_TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=CHANGE_MOI_TELEGRAM_CHAT_ID

# -------------------
# WEBHOOK
# -------------------
SOAR_WEBHOOK_SECRET=CHANGE_MOI_WEBHOOK_SECRET_LONG_ET_RANDOM

# -------------------
# WHITELIST IP
# -------------------
SOAR_WHITELIST_IPS=127.0.0.,192.168.,10.,172.17.,172.18.,172.19.
EOF

  echo "[OK] .env créé"
fi

echo

# ------------------------------------------------------------
# Création du secret Kubernetes
# ------------------------------------------------------------
if [ -f "$K8S_SECRET_FILE" ]; then
  echo "[INFO] Le fichier k8s/base/secret.yaml existe déjà -> ignoré"
else
  echo "[INFO] Création de k8s/base/secret.yaml"
  mkdir -p "$K8S_SECRET_DIR"

  cat << 'EOF' > "$K8S_SECRET_FILE"
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:

  # ==========================================================
  # FLASK / APPLICATION
  # ==========================================================
  SECRET_KEY: "CHANGE_MOI_SECRET_KEY_FLASK"
  API_KEY: "CHANGE_MOI_API_KEY"

  # ==========================================================
  # DATABASE
  # ==========================================================
  DB_HOST: "mysql"
  DB_PORT: "3306"
  DB_NAME: "ddos_detection"
  DB_USER: "bank_user"
  DB_PASSWORD: "CHANGE_MOI_DB_PASSWORD"

  # ==========================================================
  # SOAR CORE
  # ==========================================================
  SOAR_WEBHOOK_SECRET: "CHANGE_MOI_WEBHOOK_SECRET_LONG_ET_RANDOM"
  SOAR_MIN_PROBABILITY: "0.70"
  SOAR_WHITELIST_IPS: "127.0.0.,192.168.,10.,172.17.,172.18.,172.19."

  # ==========================================================
  # TELEGRAM
  # ==========================================================
  TELEGRAM_BOT_TOKEN: "CHANGE_MOI_TELEGRAM_BOT_TOKEN"
  TELEGRAM_CHAT_ID: "CHANGE_MOI_TELEGRAM_CHAT_ID"
EOF

  echo "[OK] secret.yaml créé"
fi

echo
echo "============================================================"
echo "Préparation terminée."
echo
echo "ACTIONS OBLIGATOIRES AVANT DEPLOIEMENT :"
echo "1. Modifier le fichier .env"
echo "2. Modifier le fichier k8s/base/secret.yaml"
echo "3. NE PAS COMMIT ces fichiers"
echo "============================================================"
