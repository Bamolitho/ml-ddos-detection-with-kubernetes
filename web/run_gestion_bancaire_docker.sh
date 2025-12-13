#!/bin/bash

# ============================================================
# Script : run_gestion_bancaire.sh
# Description : Construit l'image Docker, lance le conteneur,
#               et ouvre automatiquement le navigateur.
# ============================================================

# --- Étape 1 : Variables globales ---
IMAGE_NAME="gestion_bancaire:1.0"
CONTAINER_NAME="gestion_bancaire"
HOST_PORT=7000
CONTAINER_PORT=6000
URL="http://localhost:${HOST_PORT}/login"

# --- Étape 2 : Vérification de l'existence de l'image ---
echo "[INFO] Vérification de l'image Docker..."
if ! sudo docker images | grep -q "$IMAGE_NAME"; then
    echo "[INFO] Image non trouvée, création en cours..."
    sudo docker build -t "$IMAGE_NAME" .
    if [ $? -ne 0 ]; then
        echo "[ERREUR] Échec de la création de l'image. Vérifiez Dockerfile."
        exit 1
    fi
    echo "[OK] Image créée avec succès."
else
    echo "[OK] Image déjà présente localement."
fi

# --- Étape 3 : Vérification du conteneur existant ---
echo "[INFO] Vérification du conteneur existant..."
if sudo docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "[INFO] Suppression de l'ancien conteneur..."
    sudo docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1
    echo "[OK] Ancien conteneur supprimé."
fi

# --- Étape 4 : Lancement du nouveau conteneur ---
echo "[INFO] Lancement du conteneur Docker..."
sudo docker run -d -p ${HOST_PORT}:${CONTAINER_PORT} --name "$CONTAINER_NAME" "$IMAGE_NAME"
if [ $? -ne 0 ]; then
    echo "[ERREUR] Impossible de démarrer le conteneur."
    exit 1
fi
echo "[OK] Conteneur lancé avec succès."

# --- Étape 5 : Attente du démarrage complet ---
echo "[INFO] Attente du démarrage de l'application (5 secondes)..."
sleep 5

# --- Étape 6 : Test de santé du conteneur ---
HEALTH=$(sudo docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null)
if [ "$HEALTH" = "healthy" ]; then
    echo "[OK] L'application est en bon état (healthy)."
else
    echo "[AVERTISSEMENT] L'état de santé est : $HEALTH"
fi

# --- Étape 7 : Ouverture du navigateur ---
echo "[INFO] Ouverture du navigateur sur $URL ..."
if command -v xdg-open &> /dev/null; then
    xdg-open "$URL" >/dev/null 2>&1 &
else
    echo "[AVERTISSEMENT] Impossible d'ouvrir automatiquement le navigateur."
fi

echo "[OK] Système bancaire prêt à l'emploi."