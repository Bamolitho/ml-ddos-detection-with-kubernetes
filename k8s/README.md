# Kubernetes — Déploiement du système ML DDoS Detection

Ce répertoire contient **l’ensemble des manifests Kubernetes** permettant de déployer le système complet de détection et de réponse DDoS.

Le déploiement est basé sur **Kustomize**, avec :
- une base commune (`base/`)
- des overlays par environnement (`dev/`, `prod/`)

---

## Objectif de cette couche Kubernetes

Cette couche est responsable de :

- déployer tous les micro-services
- gérer la configuration et les secrets
- assurer la communication inter-services
- permettre une exécution reproductible (dev / prod)
- capturer le trafic réseau réel du cluster

---

## Vue d’ensemble des composants déployés

| Composant    | Type Kubernetes | Rôle                              |
| ------------ | --------------- | --------------------------------- |
| Dashboard    | Deployment      | Interface web de visualisation    |
| Orchestrator | DaemonSet       | Capture réseau + ML en temps réel |
| SOAR         | Deployment      | Décision et réponse automatique   |
| MySQL        | Deployment      | Stockage des flux et verdicts     |
| ConfigMap    | ConfigMap       | Configuration applicative         |
| Secrets      | Secret          | Données sensibles                 |
| Services     | ClusterIP       | Communication interne             |

---

## Structure du répertoirek8s/

```basic
├── base/
│ ├── configmap.yaml
│ ├── secret.yaml
│ ├── dashboard-deployment.yaml
│ ├── dashboard-service.yaml
│ ├── orchestrator-daemonset.yaml
│ ├── soar-deployment.yaml
│ ├── soar-service.yaml
│ ├── mysql-deployment.yaml
│ ├── mysql-service.yaml
│ ├── mysql-init-configmap.yaml
│ └── kustomization.yaml
│
├── overlays/
│ ├── dev/
│ │ └── kustomization.yaml
│ └── prod/
│ └── kustomization.yaml
│
└── README.md
```



---

## Kustomize

### Base

Le dossier `base/` contient **tous les manifests communs**, indépendants de l’environnement.

Il définit :
- les images Docker
- les ports
- les rôles des pods
- la topologie du système

### Overlays

Les overlays permettent d’adapter le déploiement selon l’environnement :

```less
k8s/overlays/dev
k8s/overlays/prod
```

Chaque overlay référence simplement la base :

```yaml
resources:
  - ../../base
```

Cela permet :

- d’ajouter des patches plus tard
- de séparer dev / prod proprement
- d’éviter la duplication de manifests

------

## Description des manifests principaux

### Dashboard

**Type :** Deployment + Service
**Rôle :** interface web de visualisation des flux et alertes

- Port exposé : `5500`
- Healthchecks :
  - readinessProbe
  - livenessProbe
- Configuration via :
  - ConfigMap (`app-config`)
  - Secret (`app-secrets`)

------

### Orchestrator

**Type :** DaemonSet
**Rôle :** capture réseau + prédiction ML en temps réel

Pourquoi un DaemonSet :

- un pod par nœud
- visibilité complète du trafic
- capture au plus près du réseau

Spécificités importantes :

- `hostNetwork: true`
- accès direct à l’interface réseau du nœud
- privilèges élevés (`NET_RAW`, `NET_ADMIN`)

Variables clés :

```
CAPTURE_INTERFACE=eth0
SOAR_URL=http://soar:6000/alert
```

------

### SOAR

**Type :** Deployment + Service
**Rôle :** moteur de décision et de réponse automatique

- Réplicas : 3
- Port : `6000`
- Accès privilégié pour iptables
- Reçoit les alertes de l’orchestrator
- Applique les décisions (block / pass / whitelist)

------

### MySQL

**Type :** Deployment + Service
**Rôle :** stockage des flux réseau analysés

Initialisation automatique via ConfigMap :

- création de la base `ddos_detection`
- création des tables `users` et `flows`
- index pour les performances

Le script est injecté au démarrage via :

```
/docker-entrypoint-initdb.d
```

------

## Configuration (ConfigMap)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  ENV: "base"
  DEBUG: "false"
```

Utilisé pour :

- définir l’environnement
- activer / désactiver le debug

------

## Secrets

Les secrets sont centralisés dans `secret.yaml`.

Ils contiennent :

- identifiants MySQL
- secrets SOAR
- whitelist IP
- tokens Telegram

Exemples :

```
SOAR_WEBHOOK_SECRET
SOAR_MIN_PROBABILITY
SOAR_WHITELIST_IPS
TELEGRAM_BOT_TOKEN
```

⚠️ **Ces valeurs ne doivent jamais être versionnées en production.**

------

## Réseau et communication interne

Tous les services communiquent via des **Services ClusterIP** :

- `mysql:3306`
- `soar:6000`
- `dashboard:5500`

Aucun service n’est exposé publiquement par défaut.

------

## Déploiement

### Environnement de développement

```bash
kubectl apply -k k8s/overlays/dev
```

### Suppression

```bash
kubectl delete -k k8s/overlays/dev
```

------

## Vérifications utiles

### État des pods

```bash
kubectl get pods
```

### Logs SOAR

```bash
kubectl logs -l app=soar
```

### Accès à un pod

```bash
kubectl exec -it <pod> -- sh
```

------

## Choix d’architecture assumés

- DaemonSet pour la capture réseau
- SOAR isolé avec privilèges strictement nécessaires
- Secrets séparés de la configuration
- Kustomize pour la maintenabilité
- Pas d’exposition externe inutile

------

## Perspectives d’évolution

- Ajout de patches Kustomize (prod vs dev)
- Stockage persistant MySQL (PVC)
- NetworkPolicies Kubernetes
- HPA pour le SOAR
- Séparation des secrets par environnement
- Déploiement multi-cluster

------

## Résumé

Cette couche Kubernetes permet de déployer **un système complet, modulaire et réaliste** de détection et réponse DDoS.

Elle relie :

- la capture réseau
- le ML
- la décision
- l’action
- la persistance

➡️ Le tout de manière reproductible et professionnelle.

