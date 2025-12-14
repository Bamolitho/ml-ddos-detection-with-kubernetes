#!/bin/bash

# ====================================
# Script de déploiement Kubernetes
# Usage: ./run_system.sh [--dev|--prod]
# Par défaut: dev
# ====================================

set -e  # Arrête le script en cas d'erreur

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="flask-hello"
IMAGE_TAG="1.0"
IMAGE="${APP_NAME}:${IMAGE_TAG}"

# Détermine l'environnement (dev par défaut)
ENV="dev"
if [[ "$1" == "--prod" ]]; then
    ENV="prod"
elif [[ "$1" == "--dev" ]] || [[ -z "$1" ]]; then
    ENV="dev"
else
    echo -e "${RED}Usage: $0 [--dev|--prod]${NC}"
    echo "Par défaut: dev"
    exit 1
fi

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}Déploiement en environnement: ${ENV^^}${NC}"
echo -e "${BLUE}==========================================${NC}"

# 1. Démarrer Minikube si pas déjà démarré
echo ""
echo -e "${YELLOW}[1/6] Vérification de Minikube...${NC}"
if ! minikube status &> /dev/null; then
    echo "Démarrage de Minikube..."
    minikube start --driver=virtualbox
    echo -e "${GREEN}✓ Minikube démarré${NC}"
else
    echo -e "${GREEN}✓ Minikube déjà démarré${NC}"
fi

# 2. Configurer Docker pour utiliser Minikube
echo ""
echo -e "${YELLOW}[2/6] Configuration de Docker pour Minikube...${NC}"
eval $(minikube docker-env)

# Vérifier que Docker pointe sur Minikube
DOCKER_NAME=$(docker info 2>/dev/null | grep "Name:" | awk '{print $2}')
if [[ "$DOCKER_NAME" == "minikube" ]]; then
    echo -e "${GREEN}✓ Docker pointe sur: ${DOCKER_NAME}${NC}"
else
    echo -e "${RED}⚠ Docker ne pointe pas sur Minikube (${DOCKER_NAME})${NC}"
    echo "Exécutez: eval \$(minikube docker-env)"
    exit 1
fi

# 3. Builder l'image dans Minikube (seulement si nécessaire)
echo ""
echo -e "${YELLOW}[3/6] Build de l'image Docker...${NC}"

# Vérifier si l'image existe déjà
if docker images | grep -q "${APP_NAME}.*${IMAGE_TAG}"; then
    echo -e "${GREEN}✓ Image ${IMAGE} existe déjà, skip du build${NC}"
else
    echo "Build de l'image..."
    if docker build -t ${IMAGE} .; then
        echo -e "${GREEN}✓ Image buildée avec succès${NC}"
    else
        echo -e "${RED}⚠ Erreur de build (problème réseau?)${NC}"
        echo "Vérification si l'image existe quand même..."
        if docker images | grep -q ${APP_NAME}; then
            echo -e "${YELLOW}✓ Image trouvée, on continue${NC}"
        else
            echo -e "${RED}✗ Image introuvable, abandon${NC}"
            exit 1
        fi
    fi
fi

# Vérifier que l'image existe
if docker images | grep -q ${APP_NAME}; then
    echo -e "${GREEN}✓ Image ${IMAGE} disponible${NC}"
else
    echo -e "${RED}✗ Erreur: image non disponible${NC}"
    exit 1
fi

# 4. Supprimer les anciennes ressources (si elles existent)
echo ""
echo -e "${YELLOW}[4/6] Nettoyage des anciennes ressources...${NC}"
if kubectl delete -k k8s/overlays/${ENV}/ 2>/dev/null; then
    echo -e "${GREEN}✓ Ressources ${ENV} supprimées${NC}"
else
    echo "Aucune ressource à supprimer"
fi

# Supprimer aussi les services créés manuellement (si existants)
if kubectl delete service flask-deployment 2>/dev/null; then
    echo -e "${GREEN}✓ Service manuel flask-deployment supprimé${NC}"
fi

# Attendre un peu pour la suppression
sleep 2

# 5. Déployer avec Kustomize
echo ""
echo -e "${YELLOW}[5/6] Déploiement Kubernetes (${ENV})...${NC}"
kubectl apply -k k8s/overlays/${ENV}/

# Attendre que les pods soient prêts
echo "Attente du démarrage des pods..."
if kubectl wait --for=condition=ready pod -l app=flask-app --timeout=60s 2>/dev/null; then
    echo -e "${GREEN}✓ Pods prêts${NC}"
else
    echo -e "${YELLOW}⚠ Timeout ou pods pas encore prêts, vérifiez avec 'kubectl get pods'${NC}"
fi

# 6. Afficher l'état et l'URL
echo ""
echo -e "${YELLOW}[6/6] État du déploiement:${NC}"
echo "=========================="
kubectl get pods
echo ""
kubectl get svc | grep -E "NAME|flask"
echo ""

# Récupérer l'URL du service
echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}✓ Application déployée avec succès!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${BLUE}URL d'accès:${NC}"
URL=$(minikube service flask-service --url)
echo -e "${GREEN}${URL}${NC}"
echo ""
echo -e "${BLUE}Commandes utiles:${NC}"
echo "  minikube service flask-service      # Ouvrir dans le navigateur"
echo "  kubectl logs -l app=flask-app       # Voir les logs"
echo "  kubectl get all                     # Voir toutes les ressources"
echo "  make delete-${ENV}                  # Nettoyer"
echo -e "${BLUE}==========================================${NC}"