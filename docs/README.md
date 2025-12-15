# Documentation du projet

Ce répertoire centralise **toute la documentation fonctionnelle et technique** du projet **ML-based DDoS Detection with Kubernetes & SOAR**.

Il sert de **point d’entrée unique** pour comprendre :
- l’architecture globale
- le pipeline machine learning
- le déploiement Kubernetes
- la détection, la décision et la réponse automatique
- l’évaluation des performances

Chaque document pointe vers les README et ressources déjà présents dans le projet.

---

## Vue d’ensemble

- Architecture distribuée orientée microservices
- Détection DDoS basée Machine Learning
- Déploiement Kubernetes (Kustomize)
- SOAR pour la réponse automatique
- Dashboard web temps réel
- Traçabilité complète via base de données

---

## Navigation par thématique

### Architecture globale
📄 [`architecture.md`](architecture.md)

- Vue d’ensemble du système
- Flux de données
- Interaction entre services
- Schémas associés

Sources principales :
- [`Images/architecture_cible.svg`](../Images/architecture_cible.svg)
- [`Images/orchestrator.png`](../Images/orchestrator.png)
- [`k8s/README.md`](../k8s/README.md)

---

### Données & datasets
📄 [`data.md`](data.md)

- Dataset CICDDoS2019
- Préparation et fusion des données
- Gestion du déséquilibre
- Pipelines de preprocessing

Sources principales :
- [`data/README.md`](../data/README.md)
- [`preprocessed_data/README.md`](../preprocessed_data/README.md)

---

### Pipeline Machine Learning
📄 [`ml_pipeline.md`](ml_pipeline.md)

- Sampling
- Preprocessing
- Entraînement
- Tuning
- Sauvegarde des modèles

Sources principales :
- [`train/README.md`](../train/README.md)
- [`tuning/`](../tuning/)
- [`models/`](../models/)
- [`run_pipeline_ML.sh`](../run_pipeline_ML.sh)

---

### Inférence & prédiction
📄 [`inference.md`](inference.md)

- Chargement des modèles
- Application du pipeline de preprocessing
- Génération des prédictions
- Seuils et probabilités

Sources principales :
- [`inference/README.md`](../inference/README.md)
- [`capture/README.md`](../capture/README.md)

---

### SOAR — Réponse automatique
📄 [`soar.md`](soar.md)

- Logique de décision
- Blocage réseau
- Alertes (Telegram)
- Whitelist

Sources principales :
- [`soar/README.md`](../soar/README.md)
- [`test_soar_scenarios.sh`](../test_soar_scenarios.sh)

---

### Base de données
📄 [`database.md`](database.md)

- Modèle de données
- Tables users et flows
- Historique des décisions
- Intégration Flask

Sources principales :
- [`database/README.md`](../database/README.md)
- [`database/init_db.sql`](../database/init_db.sql)

---

### Kubernetes & déploiement
📄 [`kubernetes.md`](kubernetes.md)

- Manifests Kubernetes
- Kustomize (base / overlays)
- Services, pods, configmaps
- Déploiement dev / prod

Sources principales :
- [`k8s/README.md`](../k8s/README.md)
- [`run_system_k8s.sh`](../run_system_k8s.sh)
- [`docker-compose.yml`](../docker-compose.yml)

---

### Évaluation & performances
📄 [`evaluation.md`](evaluation.md)

- Benchmarks modèles
- Métriques ML
- Dashboards
- Visualisations

Sources principales :
- [`evaluate/README.md`](../evaluate/README.md)
- [`evaluate/dashboard/`](../evaluate/dashboard/)
- [`Images/performance.png`](../Images/performance.png)

---

### Sécurité & exploitation
📄 [`security.md`](security.md)

- Sécurité applicative
- Sécurité Kubernetes
- Gestion des secrets
- Bonnes pratiques opérationnelles

Sources principales :
- [`nginx/README.md`](../nginx/README.md)
- [`k8s/base/secret.yaml`](../k8s/base/secret.yaml)

---

### Références & annexes
📄 [`references.md`](references.md)

- Dataset CICDDoS2019
- Outils utilisés
- Publications associées
- Liens externes

---

## Public cible

- Étudiants / chercheurs
- Ingénieurs sécurité
- Ingénieurs ML
- DevOps / SRE
- Évaluateurs académiques

---

## Objectif du dossier `docs/`

- Offrir une **lecture guidée**
- Éviter la duplication
- Structurer un projet complexe
- Rendre le projet présentable académiquement et professionnellement
