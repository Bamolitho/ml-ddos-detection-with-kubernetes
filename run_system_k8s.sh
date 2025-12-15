#!/bin/bash
set -e

# ===============================
# COLORS
# ===============================
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
RESET="\033[0m"

ENV="dev"
[[ "$1" == "--prod" ]] && ENV="prod"

DASHBOARD_PORT=5500
LOCAL_PORT=8080

clear
echo -e "${CYAN}"
echo "=============================================="
echo "   ML DDoS Detection — Kubernetes Launcher"
echo "=============================================="
echo -e "${RESET}"

echo -e "${BLUE}➜ Environment:${RESET} ${YELLOW}${ENV}${RESET}"

# ------------------------------------------------
# Minikube
# ------------------------------------------------
echo -e "${BLUE}➜ Checking Minikube...${RESET}"
if ! minikube status &>/dev/null; then
    echo -e "${YELLOW}➜ Starting Minikube${RESET}"
    minikube start
fi

# ------------------------------------------------
# Docker env
# ------------------------------------------------
eval $(minikube docker-env)
echo -e "${GREEN}✓ Docker connected to Minikube${RESET}"

# ------------------------------------------------
# Build images
# ------------------------------------------------
echo -e "${BLUE}➜ Building images${RESET}"

echo -e "${CYAN}[BUILD] Dashboard${RESET}"
docker build -t ml-ddos-dashboard:latest -f web/Dockerfile .

echo -e "${CYAN}[BUILD] Orchestrator${RESET}"
docker build -t ml-ddos-orchestrator:latest -f capture/Dockerfile .

echo -e "${CYAN}[BUILD] SOAR${RESET}"
docker build -t ml-ddos-soar:latest ./soar

# ------------------------------------------------
# Cleanup
# ------------------------------------------------
echo -e "${BLUE}➜ Cleaning previous deployment${RESET}"
kubectl delete -k k8s/overlays/${ENV} --ignore-not-found
sleep 5

# ------------------------------------------------
# Deploy
# ------------------------------------------------
echo -e "${BLUE}➜ Deploying Kubernetes resources${RESET}"
kubectl apply -k k8s/overlays/${ENV}

# ------------------------------------------------
# Wait
# ------------------------------------------------
echo -e "${BLUE}➜ Waiting for components${RESET}"

kubectl wait --for=condition=ready pod -l app=mysql --timeout=120s
kubectl wait --for=condition=ready pod -l app=soar --timeout=120s
kubectl wait --for=condition=ready pod -l app=dashboard --timeout=120s

echo -e "${GREEN}✓ All components ready${RESET}"

# ------------------------------------------------
# Port-forward Dashboard
# ------------------------------------------------
echo -e "${BLUE}➜ Starting port-forward${RESET}"

kubectl port-forward svc/dashboard ${LOCAL_PORT}:${DASHBOARD_PORT} >/tmp/dashboard_pf.log 2>&1 &
PF_PID=$!

trap "echo -e '${RED}Stopping port-forward${RESET}'; kill $PF_PID" EXIT

sleep 3

URL="http://localhost:${LOCAL_PORT}"
echo -e "${GREEN}✓ Dashboard available at:${RESET} ${YELLOW}${URL}${RESET}"

# ------------------------------------------------
# Open browser
# ------------------------------------------------
if command -v xdg-open &>/dev/null; then
    xdg-open "${URL}" &>/dev/null
elif command -v open &>/dev/null; then
    open "${URL}"
fi

# ------------------------------------------------
# Summary
# ------------------------------------------------
echo -e "${CYAN}"
kubectl get pods
echo ""
kubectl get svc
echo -e "${RESET}"

echo -e "${GREEN}System fully operational.${RESET}"
echo -e "${BLUE}Press Ctrl+C to stop port-forward.${RESET}"

wait
