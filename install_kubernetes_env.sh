#!/bin/bash

# Script d'installation de l'environnement Kubernetes avec Minikube
# Ce script vérifie si les composants sont déjà installés avant de les installer

echo "=== Installation de l'environnement Kubernetes ==="
echo ""

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Installation de Docker
echo "--- Vérification de Docker ---"
if command_exists docker; then
    echo "Docker est déjà installé : $(docker --version)"
else
    echo "Installation de Docker..."
    sudo apt update
    sudo apt install docker.io -y
    sudo systemctl enable docker
    sudo systemctl start docker
    echo "Docker installé : $(docker --version)"
fi
echo ""

# 2. Installation de kubectl
echo "--- Vérification de kubectl ---"
if command_exists kubectl; then
    echo "kubectl est déjà installé : $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
else
    echo "Installation de kubectl..."
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl gpg
    sudo mkdir -p -m 755 /etc/apt/keyrings
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt-get update
    sudo apt-get install -y kubectl
    echo "kubectl installé : $(kubectl version --client)"
fi
echo ""

# 3. Vérification de VirtualBox
echo "--- Vérification de VirtualBox ---"
if command_exists vboxmanage; then
    echo "VirtualBox est déjà installé : $(vboxmanage --version)"
    echo "Aucune installation nécessaire"
else
    echo "VirtualBox n'est pas installé"
    echo "ATTENTION : Installez VirtualBox manuellement depuis le site officiel d'Oracle"
    echo "pour éviter les problèmes de compatibilité avec les dépôts Ubuntu"
    echo "Site : https://www.virtualbox.org/wiki/Linux_Downloads"
fi
echo ""

# 4. Installation de Minikube
echo "--- Vérification de Minikube ---"
if command_exists minikube; then
    echo "Minikube est déjà installé : $(minikube version --short)"
else
    echo "Installation de Minikube..."
    sudo apt install -y curl apt-transport-https
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    rm minikube-linux-amd64
    echo "Minikube installé : $(minikube version --short)"
fi
echo ""

# 5. Résumé des installations
echo "=== Résumé des composants installés ==="
echo "Docker     : $(command_exists docker && echo "OK" || echo "NON INSTALLÉ")"
echo "kubectl    : $(command_exists kubectl && echo "OK" || echo "NON INSTALLÉ")"
echo "VirtualBox : $(command_exists vboxmanage && echo "OK" || echo "NON INSTALLÉ")"
echo "Minikube   : $(command_exists minikube && echo "OK" || echo "NON INSTALLÉ")"
echo ""

# 6. Instructions pour démarrer Minikube
echo "=== Prochaines étapes ==="
if command_exists minikube && command_exists vboxmanage; then
    echo "Pour démarrer votre cluster Kubernetes :"
    echo "  minikube start --driver=virtualbox"
    echo ""
    echo "Pour vérifier que tout fonctionne :"
    echo "  kubectl get nodes"
else
    echo "Veuillez installer les composants manquants avant de démarrer Minikube"
fi
echo ""
echo "Installation terminée !"
