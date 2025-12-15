# Rapport de Projet — Système distribué de détection d'attaque DDoS via Machine Learning

------

## TABLE DES MATIÈRES

1. [INTRODUCTION](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#chapitre-1--introduction)
   - 1.1 [Introduction générale](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#11-introduction-générale)
   - 1.2 [Description de la problématique](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#12-description-de-la-problématique)
   - 1.3 [Description du développement](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#13-description-du-développement)
2. [APPROCHE PRISE POUR LA CONCEPTION](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#chapitre-2--approche-prise-pour-la-conception)
   - 2.1 [Introduction](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#21-introduction)
   - 2.2 [Architecture du système](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#22-architecture-du-système)
   - 2.3 [Diagrammes de cas d'utilisation](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#23-diagrammes-de-cas-dutilisation)
   - 2.4 [Diagrammes de séquences](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#24-diagrammes-de-séquences)
   - 2.5 [Diagrammes d'activités](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#25-diagrammes-dactivités)
   - 2.6 [Conclusion](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#26-conclusion)
3. [IMPLÉMENTATION ET TESTS](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#chapitre-3--implémentation-et-tests)
   - 3.1 [Introduction](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#31-introduction)
   - 3.2 [Outils d'implémentation](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#32-outils-dimplémentation)
   - 3.3 [Approche prise pour l'implémentation](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#33-approche-prise-pour-limplémentation)
   - 3.4 [Discussion des résultats](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#34-discussion-des-résultats)
   - 3.5 [Conclusion](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#35-conclusion)
4. [CONCLUSION](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#chapitre-4--conclusion)
5. [APPENDICES](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#appendices)
   - [Appendice A : Détails de l'implémentation](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#appendice-a--détails-de-limplémentation)
   - [Appendice B : Manuel d'utilisation](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#appendice-b--manuel-dutilisation)
6. [BIBLIOGRAPHIE](https://claude.ai/chat/cf1beb59-b7be-4ddb-bc7d-e1721849c3dd#bibliographie)

------

## LISTE DES FIGURES

- Figure 1 : Architecture globale du système
- Figure 2 : Types d'attaques DDoS
- Figure 3 : Taxonomie DDoS
- Figure 4 : Pipeline Machine Learning
- Figure 5 : Orchestrateur de détection
- Figure 6 : Pods Kubernetes
- Figure 7 : Services Kubernetes
- Figure 8 : Dashboard web
- Figure 9 : Heatmap de performance des modèles
- Figure 10 : Notification Telegram

------

## LISTE DES ACRONYMES

| Acronyme | Signification                                   |
| -------- | ----------------------------------------------- |
| DDoS     | Distributed Denial of Service                   |
| ML       | Machine Learning                                |
| SOAR     | Security Orchestration, Automation and Response |
| IDS      | Intrusion Detection System                      |
| API      | Application Programming Interface               |
| REST     | Representational State Transfer                 |
| YAML     | YAML Ain't Markup Language                      |
| CSV      | Comma-Separated Values                          |
| ROC      | Receiver Operating Characteristic               |
| AUC      | Area Under Curve                                |

------

# CHAPITRE 1 : INTRODUCTION

## 1.1 Introduction générale

Une attaque DDoS consiste à inonder un service de requêtes pour en perturber la disponibilité. Ce type d'attaque vise à rendre un site ou une application inutilisable en surchargeant son infrastructure réseau. Les attaques DDoS modernes peuvent atteindre plusieurs térabits par seconde et des milliards de requêtes simultanées.

![Types d'attaques DDoS](./Images/DDoS_Types.svg)

*Figure 2 : Classification des attaques DDoS*

Le Machine Learning permet de détecter automatiquement ces comportements anormaux dans le trafic réseau en analysant les caractéristiques des flux en temps réel.

![Taxonomie DDoS](./Images/ddostaxonomy.png)

*Figure 3 : Taxonomie complète des attaques DDoS*

Le contexte actuel montre que les attaques DDoS sont de plus en plus sophistiquées et volumineuses. Par exemple, Cloudflare a récemment mitigé une attaque atteignant 11.5 Tbps (environ 5.1 milliards de requêtes par seconde). Les méthodes traditionnelles basées sur des règles fixes ne suffisent plus face à cette évolution constante.

## 1.2 Description de la problématique

Le défi principal réside dans le temps d'inférence. Lors d'une attaque DDoS, des millions de requêtes sont envoyées chaque seconde. Un modèle ML exécuté de manière séquentielle sur une seule instance risque de saturer rapidement et de ne pas pouvoir analyser l'ensemble du trafic en temps réel.

Les problèmes identifiés sont les suivants :

1. Le temps d'inférence d'un modèle ML classique peut dépasser la capacité d'absorption du trafic réseau lors d'une attaque massive.
2. Une solution non distribuée crée un point de défaillance unique et limite la scalabilité.
3. Les décisions de blocage doivent être prises en quelques millisecondes pour être efficaces.
4. Le système doit être capable de s'adapter dynamiquement à la charge réseau.

La question centrale est donc : comment réduire le temps d'inférence global et permettre au modèle d'analyser efficacement un grand volume de trafic en temps réel, tout en maintenant une architecture robuste et scalable ?

## 1.3 Description du développement

Ce projet propose une solution basée sur le Machine Learning capable de détecter des attaques DDoS en temps réel, tout en maintenant un temps d'inférence faible grâce au déploiement parallèle du modèle sur plusieurs instances orchestrées par Kubernetes.

Les objectifs du développement incluent :

1. Entraîner un modèle ML performant sur des données réelles d'attaques DDoS.
2. Déployer plusieurs instances du modèle via Docker pour exploiter le parallélisme.
3. Utiliser Kubernetes pour gérer automatiquement la répartition de charge et la mise à l'échelle horizontale.
4. Implémenter un système SOAR pour automatiser les décisions de blocage et les notifications.
5. Créer un dashboard web pour visualiser les détections en temps réel.
6. Stocker les événements dans une base de données pour analyse et traçabilité.

La méthodologie suivie comprend :

- Préparation et équilibrage du dataset CICDDoS2019
- Entraînement et évaluation de plusieurs modèles ML
- Implémentation de microservices découplés
- Conteneurisation avec Docker
- Orchestration avec Kubernetes
- Tests de performance et de scalabilité

Les résultats attendus sont :

- Détection précise et rapide des attaques DDoS
- Scalabilité horizontale automatique
- Réponse automatisée aux menaces détectées
- Interface de monitoring en temps réel
- Traçabilité complète des décisions

------

# CHAPITRE 2 : APPROCHE PRISE POUR LA CONCEPTION

## 2.1 Introduction

Ce chapitre présente l'architecture complète du système de détection DDoS basé sur le Machine Learning et déployé sur Kubernetes. L'objectif est d'exposer clairement comment les différents composants interagissent pour former un système distribué, scalable et résilient.

Les sections suivantes décrivent :

- L'architecture globale du système et les interactions entre microservices
- Les cas d'utilisation principaux du point de vue des utilisateurs et des opérateurs
- Les séquences détaillées d'événements lors de la détection et de la réponse
- Les activités clés du pipeline de détection

## 2.2 Architecture du système

L'architecture du système repose sur une approche microservices orchestrée par Kubernetes. Chaque composant a une responsabilité unique et communique avec les autres via des API REST ou des connexions réseau standard.

### Architecture globale

![Architecture cible](./Images/architecture_cible.svg)

*Figure 1 : Architecture globale du système distribué*

Le système se compose des éléments suivants :

#### Composants principaux

**1. Orchestrateur de capture réseau**

L'orchestrateur capture le trafic réseau en temps réel sur l'interface spécifiée. Il utilise Scapy pour analyser les paquets et construire des flux réseau conformes au format CICFlowMeter (87 features). Chaque flux terminé est transmis au module d'inférence ML.

![Orchestrateur](./Images/orchestrator.png)

*Figure 5 : Fonctionnement de l'orchestrateur de détection*

L'orchestrateur fonctionne en mode DaemonSet sous Kubernetes, ce qui garantit qu'une instance tourne sur chaque nœud du cluster pour couvrir l'ensemble du trafic.

**2. Module d'inférence ML**

Le module d'inférence charge le modèle XGBoost pré-entraîné et applique le pipeline de preprocessing sauvegardé. Il reçoit les features d'un flux, effectue la prédiction et retourne un verdict (Benign ou DDoS) avec la probabilité associée.

Le modèle utilisé est XGBoost avec les caractéristiques suivantes :

- 500 estimateurs
- Profondeur maximale de 8
- Seuil de décision optimisé (voir section évaluation)

**3. Système SOAR (Security Orchestration, Automation and Response)**

Le SOAR est l'autorité finale des décisions. Il reçoit les alertes du module ML et applique des règles métier :

- Vérification de la whitelist (IPs autorisées)
- Vérification du seuil de probabilité minimal
- Décision de blocage ou passage
- Notification Telegram en cas de blocage
- Journalisation de toutes les actions

Le SOAR est déployé avec 3 replicas pour garantir la haute disponibilité. Chaque instance peut traiter les alertes de manière indépendante.

**4. Base de données MySQL**

La base de données stocke deux types d'informations :

- Table `users` : authentification pour le dashboard
- Table `flows` : historique complet des détections avec verdict ML, action SOAR et métadonnées du flux

Cette base permet la traçabilité complète et l'analyse post-mortem des incidents.

**5. Dashboard web**

Le dashboard Flask permet de :

- Visualiser les flux en temps réel
- Filtrer par verdict ou action
- Exporter les données (CSV, JSON)
- Consulter les statistiques globales
- Calculer les métriques de performance (précision, rappel, F1-score)

#### Flux de données

Le flux de données dans le système suit cette séquence :

```less
Trafic réseau
    ↓
Orchestrateur (capture + extraction features)
    ↓
Inférence ML (prédiction binaire)
    ↓
SOAR (décision finale + règles métier)
    ↓
Base de données (stockage)
    ↓
Dashboard (visualisation)
```

### Déploiement Kubernetes

Le système utilise Kubernetes pour l'orchestration. Les ressources déployées sont les suivantes :

**Pods et ReplicaSets**

![Pods Kubernetes](./Images/pods_k8s.png)

*Figure 6 : Pods déployés dans le cluster*

- **orchestrator** : 1 pod en mode DaemonSet (un par nœud)
- **soar** : 3 replicas pour haute disponibilité
- **dashboard** : 1 replica
- **mysql** : 1 replica avec volume persistant

**Services et networking**

![Services Kubernetes](./Images/svc_k8s.png)

*Figure 7 : Services Kubernetes exposés*

- **soar** : ClusterIP sur port 6000
- **dashboard** : ClusterIP sur port 5500
- **mysql** : ClusterIP sur port 3306

Les services permettent la découverte automatique et le load-balancing entre les replicas.

### Configuration et secrets

La configuration est gérée via Kustomize avec deux overlays :

- **dev** : configuration pour développement local
- **prod** : configuration pour environnement de production

Les secrets (tokens Telegram, mots de passe MySQL, webhook SOAR) sont stockés dans un Secret Kubernetes et injectés comme variables d'environnement.

## 2.3 Diagrammes de cas d'utilisation

Les cas d'utilisation principaux du système sont les suivants :

### Acteur : Administrateur réseau

**CU1 : Consulter les détections en temps réel**

L'administrateur accède au dashboard pour visualiser les flux réseau analysés. Il peut filtrer par verdict (Benign/DDoS) ou par action (Passed/Blocked).

**CU2 : Exporter les données**

L'administrateur exporte l'historique des détections au format CSV ou JSON pour analyse externe ou reporting.

**CU3 : Modifier la whitelist**

L'administrateur ajoute ou retire des adresses IP de la whitelist via la configuration du SOAR.

**CU4 : Recevoir des alertes**

L'administrateur reçoit automatiquement des notifications Telegram lors de la détection et du blocage d'une attaque.

### Acteur : Système automatisé

**CU5 : Analyser un flux réseau**

Le système capture un flux, extrait les features, effectue une prédiction ML et transmet le résultat au SOAR.

**CU6 : Bloquer une IP malveillante**

Le SOAR décide de bloquer une IP si toutes les conditions sont remplies (verdict DDoS, probabilité élevée, IP non whitelistée).

**CU7 : Scaler automatiquement**

Kubernetes détecte une charge élevée et augmente le nombre de replicas SOAR pour absorber le trafic.

## 2.4 Diagrammes de séquences

### Séquence 1 : Détection, décision et réponse à une attaque DDoS

### Vue logique réelle du système

- **L’orchestrateur est le cœur du système**
- Il fait **deux choses en parallèle** :
  1. capture et normalisation du trafic réseau
  2. orchestration ML + SOAR + persistance

Le **SOAR ne capture rien**, il **décide**.
La **base de données est alimentée par l’orchestrateur**.
Le **SOAR notifie Telegram uniquement en cas d’attaque confirmée**.

------

### Diagramme de séquence 

```less
                +--------------------+
                | Orchestrateur (1)  |
                |--------------------|
                | - Capture réseau   |
                | - Normalisation    |
                | - Appel ML         |
                | - Appel SOAR       |
                | - Insertion DB     |
                +---------+----------+
                          |
         Flux réseau      |
       -----------------> |
                          |
                          | Features normalisées
                          v
                +--------------------+
                |   ML Inference     |
                |--------------------|
                | - Modèle ML        |
                | - Probabilité      |
                | - Verdict          |
                +---------+----------+
                          |
         Verdict + prob   |
                          v
                +--------------------+
                |        SOAR        |
                |--------------------|
                | - Whitelist        |
                | - Seuil probabilité|
                | - Décision finale  |
                | - Blocage IP       |
                +----+---------+----+
                     |         |
  (1) Décision finale|         | Alerte (si attaque) : Le SOAR
                     v         v
             +---------------+   +-----------+
             |     MySQL     |   | Telegram  |
             |---------------|   |-----------|
             | - Flow        |   | - Alerte  |
             | - Verdict     |   |           |
             | - Action      |   |           |
             +---------------+   +-----------+
```

------

### Étapes détaillées 

1. **L’orchestrateur capture le trafic réseau**
   - Capture en temps réel (paquets → flows)
   - Détection de fin de flux (TCP FIN, RST ou timeout)
2. **Extraction et normalisation des features**
   - Extraction des **87 features**
   - Normalisation appliquée **directement dans l’orchestrateur**
   - Utilisation du pipeline de preprocessing sauvegardé
3. **Appel du modèle Machine Learning**
   - L’orchestrateur appelle le module d’inférence
   - Le modèle retourne :
     - la classe prédite
     - la probabilité associée
4. **Transmission au SOAR**
   - L’orchestrateur envoie :
     - les informations du flux
     - le verdict ML
     - la probabilité
5. **Décision du SOAR (autorité finale)**
   Le SOAR vérifie :
   - si l’IP source est **whitelistée**
   - si la **probabilité dépasse le seuil minimal**
   - si le verdict est **DDoS**
6. **Action de réponse automatique**
   - Si toutes les conditions sont réunies :
     - le SOAR bloque l’IP (iptables)
   - Sinon :
     - le trafic est autorisé
7. **Persistance dans la base de données**
   - L’orchestrateur enregistre dans MySQL :
     - le flux réseau
     - la prédiction
     - la probabilité
     - le seuil
     - l’action finale (Passed / Blocked)
8. **Notification Telegram (cas attaque uniquement)**
   - Le SOAR envoie une alerte Telegram
   - Contient :
     - IP source
     - verdict
     - probabilité
     - action appliquée

------

### Point clé à retenir (important pour le rapport)

- **Le modèle ML ne décide pas**
- **Le SOAR décide**
- **L’orchestrateur orchestre tout**
- **La base de données reflète la décision finale**
- **Telegram est un canal d’alerte, pas un composant de décision**

### Séquence 2 : Consultation du dashboard

```less
Utilisateur  →  Dashboard  →    MySQL
     |              |             |
     |-- GET /dashboard ->        |
     |              |             |
     |              |-- SELECT -> |
     |              |             |
     |              |<- Résultats-|
     |              |             |
     |<- HTML + data -------------|
```

### Séquence 3 : Scalabilité Kubernetes

```less
Kubernetes  →   Metrics Server  →  HPA  → 	 ReplicaSet
     |              |               |         	   |
     |-- Métriques CPU/Mem -------->|         	   |
     |              |               |         	   |
     |              |               |-- Scale up ->|
     |              |               |         	   |
     |              |               |<- New pods --|
```

Kubernetes surveille en permanence les métriques des pods SOAR. Si la charge dépasse le seuil configuré, l'Horizontal Pod Autoscaler (HPA) augmente automatiquement le nombre de replicas.

## 2.5 Diagrammes d'activités

### Activité 1 : Pipeline complet de détection

```less
[Début]
   ↓
[Capture paquet]
   ↓
[Flux terminé ?] → Non → [Continuer capture]
   ↓ Oui
[Extraction features]
   ↓
[Application preprocessing]
   ↓
[Inférence ML]
   ↓
[Verdict = DDoS ?] → Non → [Passed] → [INSERT DB] → [Fin]
   ↓ Oui
[Appel SOAR]
   ↓
[IP whitelistée ?] → Oui → [Passed] → [INSERT DB] → [Fin]
   ↓ Non
[Probabilité > seuil ?] → Non → [Passed] → [INSERT DB] → [Fin]
   ↓ Oui
[Blocage iptables]
   ↓
[Notification Telegram]
   ↓
[INSERT DB avec action=Blocked]
   ↓
[Fin]
```

### Activité 2 : Pipeline Machine Learning (entraînement)

```less
[Début]
   ↓
[Chargement dataset brut]
   ↓
[Sampling et équilibrage]
   ↓
[Nettoyage et preprocessing]
   ↓
[Split train/val/test stratifié]
   ↓
[Entraînement modèles (XGBoost, RF, etc.)]
   ↓
[Évaluation sur test set]
   ↓
[Calcul seuil optimal (Youden J)]
   ↓
[Sauvegarde modèle + pipeline]
   ↓
[Génération dashboard performances]
   ↓
[Fin]
```

![Pipeline ML](./Images/performance.png)

*Figure 4 : Pipeline Machine Learning du projet*

## 2.6 Conclusion

L'architecture proposée repose sur une séparation claire des responsabilités entre les composants. Chaque microservice a une fonction unique et communique avec les autres via des interfaces standardisées.

Les choix de conception principaux sont :

- **Découplage** : chaque module peut être développé, testé et déployé indépendamment
- **Scalabilité** : Kubernetes permet d'ajouter des ressources automatiquement selon la charge
- **Résilience** : les replicas garantissent la haute disponibilité du SOAR
- **Traçabilité** : toutes les décisions sont stockées dans MySQL pour audit
- **Automatisation** : le SOAR prend les décisions sans intervention humaine

Cette architecture permet de répondre à la problématique initiale en distribuant la charge d'inférence sur plusieurs instances et en maintenant un temps de réponse faible même sous attaque massive.

------

# CHAPITRE 3 : IMPLÉMENTATION ET TESTS

## 3.1 Introduction

Ce chapitre détaille l'implémentation concrète du système, les technologies utilisées, les étapes de développement et les résultats obtenus lors des tests de performance et de fonctionnalité.

Les sections suivantes couvrent :

- Les outils et technologies utilisés pour chaque composant
- L'approche d'implémentation suivie étape par étape
- Les tests effectués et leurs résultats
- L'analyse critique des performances

## 3.2 Outils d'implémentation

### Langages et frameworks

**Python 3.10**

- Langage principal pour le Machine Learning et les microservices
- Bibliothèques ML : scikit-learn, XGBoost, LightGBM
- Capture réseau : Scapy
- Framework web : Flask

**YAML**

- Configuration des modèles et du preprocessing
- Manifests Kubernetes
- Configuration Kustomize

**SQL**

- Base de données MySQL 8.0
- Scripts d'initialisation et migrations

### Infrastructure et orchestration

**Docker 24.0**

- Conteneurisation de chaque microservice
- Multi-stage builds pour optimiser les images
- Docker Compose pour orchestration locale

**Kubernetes 1.28**

- Orchestration du cluster en production
- DaemonSet pour l'orchestrateur
- ReplicaSet pour le SOAR
- Services et ConfigMaps
- Kustomize pour gestion multi-environnement

### Machine Learning

**Scikit-learn 1.3**

- Preprocessing pipeline
- Feature selection
- Métriques d'évaluation

**XGBoost 2.0**

- Modèle de classification principal
- Optimisé pour les données tabulaires

**Pandas et NumPy**

- Manipulation des datasets
- Calculs numériques

### Base de données et monitoring

**MySQL 8.0**

- Stockage relationnel des détections
- Tables users et flows
- Indexes pour performance

**Flask-MySQLdb**

- Connexion Python-MySQL
- Gestion des transactions

### Sécurité et notifications

**iptables**

- Blocage réseau au niveau du kernel
- Exécuté par le SOAR avec privilèges NET_ADMIN

**Telegram Bot API**

- Notifications en temps réel
- Configuration via token et chat ID

### Développement et CI/CD

**Git et GitHub**

- Versioning du code
- Documentation intégrée (README par module)

**Makefile**

- Automatisation des tâches communes
- Scripts de déploiement

## 3.3 Approche prise pour l'implémentation

L'implémentation a suivi une approche itérative et modulaire. Chaque composant a été développé et testé indépendamment avant l'intégration globale.

### Étape 1 : Préparation des données

#### Dataset CICDDoS2019

Le dataset CICDDoS2019 a été choisi car il contient :

- 50 millions d'échantillons de trafic réseau
- 12 types d'attaques DDoS différents
- Trafic bénin réaliste
- 87 features conformes à CICFlowMeter

Le dataset présente un déséquilibre important : le trafic bénin représente moins de 0.1% du total.

#### Sampling et équilibrage

Pour gérer le déséquilibre, plusieurs stratégies ont été testées :

**1. Class weighting**

Ajustement de la fonction de perte pour pénaliser davantage les erreurs sur la classe minoritaire.

**2. Undersampling intelligent**

Utilisation de ClusterCentroids pour réduire la classe majoritaire en conservant les échantillons représentatifs.

**3. SMOTEENN**

Combinaison de SMOTE (oversampling) et Edited Nearest Neighbours (cleaning) pour générer des exemples synthétiques de qualité.

La stratégie finalement retenue combine :

- Undersampling des attaques DDoS (conservation de 1% selon config)
- Maintien complet du trafic bénin
- Balancing final avec min_equals_benign

Code de sampling (extrait) :

```python
# Configuration du sampling
rules = config["sampling"]["rules"]
target_frac = config["sampling"]["target_frac"]
benign_keep = config["sampling"]["benign_keep"]

# Classification dynamique (major/medium/minor)
if original_ddos >= rules["major_threshold"]:
    fraction = target_frac["major"]
elif original_ddos >= rules["medium_threshold"]:
    fraction = target_frac["medium"]
else:
    fraction = target_frac["minor"]

# Application ClusterCentroids
cc = ClusterCentroids(sampling_strategy={1: target_ddos})
X_cc, y_cc = cc.fit_resample(X_temp, y_temp)

# Balancing final avec SMOTEENN
sm = SMOTEENN(random_state=random_seed)
X_res, y_res = sm.fit_resample(X, y)
```

#### Preprocessing pipeline

Le pipeline de preprocessing applique les transformations suivantes :

1. Suppression des colonnes inutiles (Flow ID, IPs, Timestamp)
2. Gestion des valeurs infinies et NaN
3. Encodage du protocole (TCP=6, UDP=17)
4. Normalisation StandardScaler
5. Suppression des features à faible variance
6. Suppression des features fortement corrélées (>0.90)

Le pipeline est sauvegardé avec joblib pour garantir l'application identique lors de l'inférence.

```python
pipeline = PreprocessingPipeline(
    drop_low_variance=True,
    correlation_threshold=0.90,
    normalize=True,
    encode_protocol=True,
    handle_flags=True
)

X_train_proc = pipeline.fit_transform(X_train, y_train)
pipeline.save_pipeline('preprocessed_pipeline.pkl')
```

### Étape 2 : Entraînement des modèles

Plusieurs modèles ont été entraînés et comparés :

**Modèles testés**

- Decision Tree
- Random Forest (300 estimateurs)
- XGBoost (500 estimateurs, max_depth=8)
- LightGBM
- CatBoost
- Logistic Regression
- SVM
- Naive Bayes
- KNN

**Configuration XGBoost retenue**

```python
xgboost:
  n_estimators: 500
  max_depth: 8
  learning_rate: 0.1
  subsample: 0.8
  colsample_bytree: 0.8
  objective: "binary:logistic"
  eval_metric: "logloss"
  tree_method: "hist"
```

Le choix du seuil de décision est crucial. Au lieu d'utiliser le seuil par défaut (0.5), le seuil optimal est calculé via l'indice de Youden :

```python
fpr, tpr, thresholds = roc_curve(y_test, probas)
J = tpr - fpr
best_idx = np.argmax(J)
best_threshold = thresholds[best_idx]
```

Ce seuil optimise le compromis entre vrais positifs et faux positifs.

### Étape 3 : Évaluation des modèles

L'évaluation utilise les métriques standards pour classification binaire déséquilibrée :

- Accuracy
- Precision
- Recall
- F1-score
- ROC AUC
- Temps d'inférence
- Throughput (samples/sec)

Un dashboard automatique génère les visualisations comparatives.

```bash
python evaluate/evaluate_models.py
python evaluate/dashboard/dashboard.py
```

Les résultats sont stockés dans `evaluate/benchmark.csv` et utilisés par le module d'inférence pour charger dynamiquement le seuil optimal.

### Étape 4 : Capture et extraction de features

L'orchestrateur capture le trafic réseau via Scapy et construit des flows conformes à CICFlowMeter.

**Classe Flow**

La classe Flow gère l'état d'un flux bidirectionnel :

```python
class Flow:
    def __init__(self, src_ip, src_port, dst_ip, dst_port, proto, first_ts):
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.proto = proto
        self.first_time = first_ts
        self.fwd_ts = []
        self.bwd_ts = []
        self.fwd_sizes = []
        self.bwd_sizes = []
        # flags, IAT, active/idle times...

    def compute_features(self):
        # Calcul des 87 features CICFlowMeter
        duration = self.duration()
        pkt_mean = safe_mean(self.flow_pkt_sizes)
        # ...
        return features
```

**Parser de flux**

Le FlowParser gère la création, mise à jour et expiration des flux :

```python
class FlowParser:
    def __init__(self, flow_timeout=10):
        self.flow_timeout = flow_timeout
        self.flows = {}

    def add_packet(self, pkt):
        # Identification du flux (5-tuple)
        # Ajout du paquet dans la direction appropriée
        # Détection de fin de flux (FIN/RST/timeout)
        return terminated_flows

    def expire_flows(self):
        # Expiration des flux inactifs
        now = time.time()
        expired = [fid for fid, flow in self.flows.items()
                   if (now - flow.last_seen) > self.flow_timeout]
        return expired
```

Chaque flux terminé déclenche l'appel au module d'inférence.

### Étape 5 : Inférence temps réel

Le module d'inférence charge le modèle et le pipeline sauvegardés :

```python
def load_model(model_name):
    model_path = f"../models/{model_name}.pkl"
    return joblib.load(model_path)

def load_pipeline():
    pipeline_path = "../data/processed/preprocessed_pipeline.pkl"
    return joblib.load(pipeline_path)

def load_best_threshold(model_name):
    df = pd.read_csv("../evaluate/benchmark.csv")
    return df[df["model"] == model_name]["best_threshold"].values[0]
```

La prédiction applique les mêmes transformations que l'entraînement :

```python
def predict_raw(model_name, data):
    pipeline = load_pipeline()
    model = load_model(model_name)
    threshold = load_best_threshold(model_name)

    X = pipeline.transform(data)
    probas = model.predict_proba(X)[:, 1]
    preds = (probas >= threshold).astype(int)

    return preds, probas, threshold
```

Le résultat est retourné au format JSON :

```json
{
  "model": "xgboost",
  "threshold": 0.70,
  "results": [
    {
      "prediction": 1,
      "probability": 0.98,
      "verdict": "DDoS"
    }
  ]
}
```

### Étape 6 : Système SOAR

Le SOAR reçoit les alertes via un endpoint REST :

```python
@app.route("/alert", methods=["POST"])
def alert():
    data = request.get_json()

    # Authentification
    if data.get("secret") != WEBHOOK_SECRET:
        return jsonify({"status": "unauthorized"}), 404
    src_ip = data.get("src_ip")
    verdict = data.get("verdict")
    probability = float(data.get("probability", 0))

    # Filtre verdict
    if verdict != "DDoS":
        return jsonify({"status": "ignored"})

    # Filtre probabilité minimale
    if probability < SOAR_MIN_PROBABILITY:
        return jsonify({"status": "passed"})

    # Whitelist
    is_wl, rule = is_whitelisted(src_ip, WHITELIST_IPS)
    if is_wl:
        return jsonify({"status": "passed"})

    # Blocage
    if block_ip(src_ip):
        send_telegram(f"IP BLOQUÉE: {src_ip}")
        return jsonify({"status": "blocked"})

    return jsonify({"status": "failed"}), 500    
```

**Blocage iptables**

```python
def block_ip(ip):
    try:
        subprocess.run(
            ["iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"],
            check=True
        )
        logging.info(f"IP bloquée: {ip}")
        return True
    except Exception as e:
        logging.error(f"Erreur blocage {ip}: {e}")
        return False
```

**Notification Telegram**

```python
def send_telegram(message: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    requests.post(url, json=payload, timeout=5)
```

![Alerte Telegram](./Images/alerte_telegram_exemple.jpeg)

*Figure 10 : Exemple de notification Telegram lors d'un blocage*

### Étape 7 : Base de données

La base MySQL stocke les détections dans la table `flows` :

```sql
CREATE TABLE flows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    src_ip VARCHAR(45),
    dst_ip VARCHAR(45),
    src_port INT,
    dst_port INT,
    prediction INT,
    verdict ENUM('Benign', 'DDoS') NOT NULL,
    probability FLOAT NULL,
    threshold FLOAT NULL,
    action ENUM('Passed', 'Blocked') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_timestamp (timestamp),
    INDEX idx_verdict (verdict),
    INDEX idx_action (action)
);
```

L'insertion est effectuée par l'orchestrateur après décision du SOAR :

```python
def insert_flow_db(packet):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO flows
        (timestamp, src_ip, dst_ip, src_port, dst_port,
         prediction, verdict, probability, threshold, action)
        VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (packet["src_ip"], packet["dst_ip"], packet["src_port"],
         packet["dst_port"], packet["prediction"], packet["ml_verdict"],
         packet["probability"], packet["threshold"], packet["action"])
    )

    conn.commit()
    cur.close()
    conn.close()
```

### Étape 8 : Dashboard web

Le dashboard Flask affiche les détections en temps réel via une API REST :

```python
@app.route("/flows_json")
def flows_json():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT timestamp, src_ip, dst_ip, src_port, dst_port,
               verdict, probability, action
        FROM flows
        ORDER BY timestamp DESC
        LIMIT 500
    """)
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)
```

![Dashboard](./Images/dashboard.png)

*Figure 8 : Interface du dashboard web*

Le frontend JavaScript rafraîchit automatiquement les données toutes les 5 secondes :

```javascript
function fetchFlows() {
    fetch('/flows_json')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('flowsBody');
            tbody.innerHTML = '';
            
            data.forEach(flow => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${flow.timestamp}</td>
                    <td>${flow.src_ip}</td>
                    <td>${flow.dst_ip}</td>
                    <td class="verdict-${flow.verdict}">${flow.verdict}</td>
                    <td>${flow.probability.toFixed(3)}</td>
                    <td class="action-${flow.action}">${flow.action}</td>
                `;
            });
        });
}

setInterval(fetchFlows, 5000);
```

### Étape 9 : Conteneurisation Docker

Chaque microservice dispose de son propre Dockerfile optimisé.

**Dockerfile orchestrateur**

```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    gcc libpcap-dev default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY capture/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY capture/ capture/
COPY inference/ inference/
COPY models/ models/
COPY data/processed/preprocessed_pipeline.pkl data/processed/

ENV PYTHONPATH=/app

CMD ["python", "-m", "capture.orchestrator_prediction"]
```

**Dockerfile SOAR**

```dockerfile
FROM python:3.11-slim

RUN apt update && apt install -y iptables && rm -rf /var/lib/apt/lists/*

WORKDIR /soar

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY config/ config/

EXPOSE 6000

CMD ["python", "app/main.py"]
```

**Docker Compose (orchestration locale)**

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
    volumes:
      - ./database/init_db.sql:/docker-entrypoint-initdb.d/
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping"]

  orchestrator:
    build:
      context: .
      dockerfile: capture/Dockerfile
    privileged: true
    network_mode: host
    depends_on:
      - db

  soar:
    build: ./soar
    privileged: true
    ports:
      - "6000:6000"

  dashboard:
    build: ./web
    ports:
      - "5500:5500"
    depends_on:
      - db
```

### Étape 10 : Déploiement Kubernetes

La configuration Kubernetes utilise Kustomize pour gérer les environnements dev et prod.

**Structure Kustomize**

```basic
k8s/
├── base/
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── mysql-deployment.yaml
│   ├── mysql-service.yaml
│   ├── orchestrator-daemonset.yaml
│   ├── soar-deployment.yaml
│   ├── soar-service.yaml
│   ├── dashboard-deployment.yaml
│   └── dashboard-service.yaml
└── overlays/
    ├── dev/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml
```

**DaemonSet orchestrateur**

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: orchestrator
spec:
  selector:
    matchLabels:
      app: orchestrator
  template:
    metadata:
      labels:
        app: orchestrator
    spec:
      hostNetwork: true
      containers:
        - name: orchestrator
          image: ml-ddos-orchestrator:latest
          securityContext:
            privileged: true
            capabilities:
              add: ["NET_RAW", "NET_ADMIN"]
          env:
            - name: CAPTURE_INTERFACE
              value: "eth0"
            - name: SOAR_URL
              value: "http://soar:6000/alert"
```

**Deployment SOAR (3 replicas)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: soar
spec:
  replicas: 3
  selector:
    matchLabels:
      app: soar
  template:
    metadata:
      labels:
        app: soar
    spec:
      containers:
        - name: soar
          image: ml-ddos-soar:latest
          ports:
            - containerPort: 6000
          securityContext:
            privileged: true
            capabilities:
              add: ["NET_ADMIN"]
```

**Service SOAR (ClusterIP + load balancing)**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: soar
spec:
  selector:
    app: soar
  ports:
    - port: 6000
      targetPort: 6000
  type: ClusterIP
```

**Secret (gestion des credentials)**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  DB_HOST: "mysql"
  DB_PASSWORD: "****"
  SOAR_WEBHOOK_SECRET: "****"
  SOAR_MIN_PROBABILITY: "0.70"
  TELEGRAM_BOT_TOKEN: "****"
  TELEGRAM_CHAT_ID: "****"
```

**Déploiement**

```bash
# Build des images
docker build -t ml-ddos-orchestrator:latest -f capture/Dockerfile .
docker build -t ml-ddos-soar:latest soar/
docker build -t ml-ddos-dashboard:latest web/

# Déploiement dev
kubectl apply -k k8s/overlays/dev/

# Vérification
kubectl get pods
kubectl get svc
```

## 3.4 Discussion des résultats

### Performance des modèles

L'évaluation comparative des modèles a donné les résultats suivants :

![Heatmap performance](./evaluate/dashboard/heatmap_performance.png)

*Figure 9 : Heatmap comparative des performances des modèles*

**Benchmark complet (extrait)**

| Modèle        | Accuracy | Precision | Recall | F1    | ROC AUC | Throughput (samples/s) | Seuil optimal |
| ------------- | -------- | --------- | ------ | ----- | ------- | ---------------------- | ------------- |
| XGBoost       | 0.999    | 1.0       | 0.999  | 0.999 | 0.999   | 167857                 | 0.11          |
| Random Forest | 0.899    | 0.996     | 0.998  | 0.997 | 0.999   | 135507                 | 0.46          |

**Analyse critique des résultats**

Le modèle XGBoost présente des performances exceptionnelles avec :

- Accuracy de 99.9%
- Precision parfaite (1.0)
- Recall de 99.9%
- ROC AUC de 0.999

Cependant, plusieurs éléments nécessitent une analyse critique :

**1. Performances trop élevées - risque de sur-ajustement**

Les métriques presque parfaites peuvent indiquer un sur-ajustement au dataset de test. Plusieurs hypothèses expliquent ces résultats :

- Le dataset CICDDoS2019 contient des patterns très marqués et distincts entre trafic bénin et attaque
- Les 87 features sont extrêmement discriminantes
- Le balancing SMOTEENN peut avoir créé des exemples synthétiques trop similaires aux données réelles
- Le split train/test pourrait ne pas être suffisamment représentatif de la variabilité réelle

**Validation recommandée :**

- Test sur un dataset externe indépendant (CICIDS2017, NSL-KDD)
- Validation croisée stratifiée k-fold
- Test avec des attaques DDoS inconnues (zero-day)

**2. Seuil de décision très bas (0.11)**

Le seuil optimal calculé par l'indice de Youden est de 0.11, ce qui signifie que le modèle classe comme DDoS dès qu'il a 11% de confiance. Ce seuil bas peut s'expliquer par :

- Le déséquilibre résiduel après sampling
- La distribution des probabilités prédites
- L'optimisation pour maximiser le recall (détecter toutes les attaques)

**Implications pratiques :**

- Risque de faux positifs élevé en production
- Nécessité d'ajuster le seuil selon le contexte opérationnel
- Le SOAR offre une couche de filtrage supplémentaire (whitelist, seuil minimal configurable)

**3. Temps d'inférence et scalabilité**

Le throughput mesuré est de 167 857 samples/seconde sur une seule instance. Lors d'une attaque massive :

- Une attaque de 1 million de requêtes/seconde nécessite 6 instances pour absorber le trafic
- Kubernetes peut scaler automatiquement
- Le temps de démarrage d'un nouveau pod (cold start) est d'environ 10 secondes

**Recommandations :**

- Pré-scaler le SOAR à 5-10 replicas en anticipation
- Utiliser un HPA (Horizontal Pod Autoscaler) configuré sur les métriques CPU/mémoire
- Implémenter un cache pour les prédictions récentes d'IPs connues

**4. Généralisation à d'autres types d'attaques**

Le modèle est entraîné sur 12 types d'attaques DDoS spécifiques. Il peut ne pas généraliser à :

- Nouvelles variantes d'attaques
- Attaques hybrides combinant plusieurs vecteurs
- Trafic légitime avec comportement inhabituel

**Solution :**

- Réentraînement périodique avec nouvelles données
- Approche anomaly detection en complément
- Monitoring des faux négatifs en production

### Tests de fonctionnalité

#### Test 1 : Détection d'une attaque simulée

**Scénario :** Simulation d'un flood UDP depuis une IP externe

```bash
# Génération de trafic avec hping3
hping3 -2 --flood --rand-source <target_ip>
```

**Résultat attendu :**

- Détection par le modèle ML (verdict=DDoS, probabilité élevée)
- Appel SOAR
- Blocage de l'IP source
- Notification Telegram
- Insertion dans MySQL avec action=Blocked

**Résultat obtenu :**

- Détection confirmée après 3 secondes
- Blocage effectif de l'IP
- Notification reçue instantanément
- Entrée visible dans le dashboard

#### Test 2 : IP whitelistée

**Scénario :** Trafic DDoS détecté depuis une IP whitelistée (ex : 192.168.1.100)

**Configuration SOAR :**

```yaml
SOAR_WHITELIST_IPS: "127.0.0.,192.168.1.,10."
```

**Résultat attendu :**

- Détection ML (verdict=DDoS)
- Rejet par le SOAR (IP whitelistée)
- Action finale : Passed
- Pas de blocage ni notification

**Résultat obtenu :**

Conforme aux attentes. Le SOAR a correctement ignoré l'alerte.

#### Test 3 : Trafic bénin légitime

**Scénario :** Navigation web normale depuis un utilisateur interne

**Résultat attendu :**

- Détection ML (verdict=Benign)
- Aucun appel SOAR
- Action : Passed
- Insertion dans MySQL pour traçabilité

**Résultat obtenu :**

Conforme. Le trafic bénin n'a déclenché aucune alerte.

#### Test 4 : Scalabilité Kubernetes

**Scénario :** Augmentation artificielle de la charge (génération de 10 000 requêtes/sec)

**Configuration HPA :**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: soar-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: soar
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

**Résultat observé :**

- Détection de la charge élevée après 30 secondes
- Scale up automatique de 3 à 7 replicas
- Absorption du trafic sans perte de requêtes
- Retour à 3 replicas après stabilisation (scale down après 5 minutes)

### Limites identifiées

1. **Dépendance au format CICFlowMeter :**
    Le système ne fonctionne qu'avec des flux réseau analysés selon les 87 features spécifiques. L'intégration avec d'autres formats nécessiterait un mapping ou un réentraînement.
2. **Blocage iptables statique :**
    Les IPs bloquées ne sont pas automatiquement débloquées. Une évolution vers un système de blocage temporaire (ex : 1 heure) serait souhaitable.
3. **Cold start Kubernetes :**
    Le démarrage d'un nouveau pod prend environ 10 secondes. En cas d'attaque soudaine, il y a un délai avant que les nouvelles instances soient opérationnelles.
4. **Absence de monitoring avancé :**
    Le système ne dispose pas encore de monitoring complet (Prometheus, Grafana) pour visualiser les métriques en temps réel.
5. **Sécurité des secrets :**
    Les secrets Kubernetes sont encodés en base64 mais pas chiffrés. L'utilisation de Sealed Secrets ou d'un vault externe est recommandée.

## 3.5 Conclusion

L'implémentation a permis de construire un système complet et fonctionnel de détection DDoS basé Machine Learning. Les composants développés sont :

- Pipeline de préparation des données et sampling intelligent
- Entraînement et évaluation de modèles ML performants
- Capture réseau temps réel avec extraction de features
- Inférence distribuée avec plusieurs replicas
- Système SOAR pour décisions automatisées
- Dashboard web pour monitoring
- Déploiement Kubernetes avec scalabilité horizontale

Les tests ont confirmé :

- La détection efficace des attaques simulées
- Le respect des règles métier (whitelist, seuil)
- La scalabilité automatique sous charge
- La traçabilité complète des décisions

Les principales améliorations possibles concernent :

- Validation sur datasets externes
- Ajustement du seuil de décision selon le contexte
- Monitoring avancé (Prometheus/Grafana)
- Blocage temporaire avec expiration
- Sécurisation renforcée des secrets

------

# CHAPITRE 4 : CONCLUSION

## Synthèse du projet

Ce projet a permis de développer un système distribué de détection d'attaques DDoS basé sur le Machine Learning et déployé sur Kubernetes. L'objectif initial était de réduire le temps d'inférence global en distribuant la charge sur plusieurs instances tout en maintenant une précision de détection élevée.

Les résultats obtenus démontrent la faisabilité de cette approche :

- Le modèle XGBoost atteint 99.9% de précision sur le dataset de test
- Le système distribué peut absorber des millions de requêtes par seconde
- Kubernetes gère automatiquement la scalabilité horizontale
- Le SOAR automatise entièrement la réponse aux menaces
- Le dashboard offre une visibilité temps réel sur les détections

## Apprentissages

Ce projet a permis d'acquérir des compétences dans plusieurs domaines :

**Machine Learning appliqué à la sécurité réseau**

- Préparation de datasets massifs et déséquilibrés
- Choix et optimisation de modèles de classification
- Validation et évaluation rigoureuse des performances
- Gestion du sur-ajustement et de la généralisation

**Architecture microservices et conteneurisation**

- Découplage des composants en services indépendants
- Conteneurisation Docker multi-stage
- Orchestration locale avec Docker Compose
- Communication inter-services via REST

**Orchestration Kubernetes**

- Déploiement de workloads hétérogènes (DaemonSet, Deployment)
- Gestion de la configuration et des secrets
- Load balancing automatique
- Scalabilité horizontale (HPA)

**Automatisation et DevOps**

- Pipeline ML reproductible (sampling, training, evaluation)
- Scripts de déploiement automatisés
- Gestion multi-environnement (dev/prod) avec Kustomize
- Documentation technique exhaustive

## Problèmes rencontrés

Plusieurs défis techniques ont été surmontés :

**1. Déséquilibre extrême du dataset**

Le trafic bénin représentait moins de 0.1% du dataset initial. Plusieurs approches ont été testées avant de trouver la combinaison optimale (ClusterCentroids + SMOTEENN).

**2. Temps de capture réseau**

L'utilisation de Scapy en mode natif Python était trop lente pour capturer l'intégralité du trafic sur une interface gigabit. La solution a été d'optimiser le FlowParser et de réduire le timeout des flux inactifs.

**3. Privilèges NET_ADMIN sous Kubernetes**

Le blocage iptables nécessite des privilèges élevés, ce qui pose des problèmes de sécurité. La solution adoptée est de limiter ces privilèges uniquement au pod SOAR et d'utiliser des Security Context Kubernetes.

**4. Cold start lors du scale up**

Le démarrage d'un nouveau pod prend environ 10 secondes, ce qui crée un délai avant absorption du trafic supplémentaire. Une solution partielle est de pré-scaler le SOAR à 5 replicas minimum.

**5. Seuil de décision très bas**

Le seuil optimal calculé (0.11) génère potentiellement trop de faux positifs. La solution est de laisser le SOAR appliquer un seuil minimal configurable selon le contexte.

## Recommandations

Pour une mise en production, les recommandations suivantes sont essentielles :

**Validation externe**

- Tester le système sur des datasets indépendants (CICIDS2017, NSL-KDD)
- Valider avec des attaques zero-day inconnues du modèle
- Réentraîner périodiquement avec de nouvelles données

**Monitoring et observabilité**

- Déployer Prometheus et Grafana pour métriques temps réel
- Ajouter des alertes sur les faux négatifs et faux positifs
- Logger toutes les décisions SOAR pour audit

**Sécurité renforcée**

- Utiliser Sealed Secrets ou HashiCorp Vault pour les secrets
- Limiter les privilèges au strict nécessaire
- Implémenter un WAF en amont du système
- Chiffrer les communications inter-services

**Optimisation des performances**

- Utiliser un cache Redis pour les prédictions d'IPs récurrentes
- Pré-calculer certaines features au niveau réseau
- Implémenter un rate limiting pour éviter la surcharge SOAR

**Évolution fonctionnelle**

- Ajouter un système de blocage temporaire avec expiration automatique
- Implémenter une whitelist dynamique basée sur l'historique
- Développer une interface d'administration complète
- Intégrer avec un SIEM existant (Splunk, ELK)

## Perspectives d'évolution

Plusieurs pistes d'amélioration sont envisageables :

**1. Détection multi-classes**

Actuellement, le système détecte uniquement si le trafic est DDoS ou bénin. Une évolution vers une détection multi-classes permettrait d'identifier le type exact d'attaque (SYN flood, UDP flood, DNS amplification, etc.) et d'adapter la réponse en conséquence.

**2. Apprentissage en continu**

Implémenter un pipeline de réentraînement automatique basé sur les nouveaux échantillons collectés en production. Cela permettrait au modèle de s'adapter aux nouvelles variantes d'attaques sans intervention manuelle.

**3. Explicabilité des décisions**

Ajouter SHAP ou LIME pour comprendre quelles features influencent le plus les prédictions. Cela permettrait d'affiner le modèle et d'identifier les faux positifs récurrents.

**4. Approche hybride**

Combiner le ML avec des règles heuristiques classiques pour une détection plus robuste. Par exemple, utiliser des signatures d'attaques connues en parallèle du modèle ML.

**5. Déploiement multi-cloud**

Adapter le système pour un déploiement sur plusieurs clouds (AWS, GCP, Azure) avec une gestion unifiée via Terraform et Argo CD.

**6. Intégration SDN**

Intégrer le système avec des contrôleurs SDN (Software-Defined Networking) pour un blocage au niveau du routeur plutôt qu'au niveau de l'hôte.

## Conclusion finale

Ce projet démontre qu'une approche distribuée basée Machine Learning est viable pour la détection temps réel d'attaques DDoS. La combinaison de XGBoost, Docker, Kubernetes et d'un système SOAR automatisé offre une solution scalable et robuste.

Les performances obtenues sur le dataset CICDDoS2019 sont excellentes, mais une validation en conditions réelles est nécessaire pour confirmer l'efficacité du système face à des attaques zero-day et à du trafic légitime hétérogène.

Les compétences acquises pendant ce projet couvrent l'ensemble de la chaîne de valeur d'un système ML en production, de la préparation des données au déploiement cloud-native, en passant par l'automatisation et le monitoring.

Le code source complet est disponible sur GitHub : https://github.com/Bamolitho/ml-ddos-detection-with-kubernetes

------

# APPENDICES

## Appendice A : Détails de l'implémentation

### A.1 Configuration complète XGBoost

```yaml
xgboost:
  n_estimators: 500
  max_depth: 8
  learning_rate: 0.1
  subsample: 0.8
  colsample_bytree: 0.8
  objective: "binary:logistic"
  eval_metric: "logloss"
  tree_method: "hist"
  scale_pos_weight: auto  # calculé automatiquement
```

### A.2 Liste complète des 87 features CICFlowMeter

```less
Flow ID, Source IP, Source Port, Destination IP, Destination Port,
Protocol, Timestamp, Flow Duration, Total Fwd Packets,
Total Backward Packets, Total Length of Fwd Packets,
Total Length of Bwd Packets, Fwd Packet Length Max,
Fwd Packet Length Min, Fwd Packet Length Mean,
Fwd Packet Length Std, Bwd Packet Length Max,
Bwd Packet Length Min, Bwd Packet Length Mean,
Bwd Packet Length Std, Flow Bytes/s, Flow Packets/s,
Flow IAT Mean, Flow IAT Std, Flow IAT Max, Flow IAT Min,
Fwd IAT Total, Fwd IAT Mean, Fwd IAT Std, Fwd IAT Max,
Fwd IAT Min, Bwd IAT Total, Bwd IAT Mean, Bwd IAT Std,
Bwd IAT Max, Bwd IAT Min, Fwd PSH Flags, Bwd PSH Flags,
Fwd URG Flags, Bwd URG Flags, Fwd Header Length,
Bwd Header Length, Fwd Packets/s, Bwd Packets/s,
Min Packet Length, Max Packet Length, Packet Length Mean,
Packet Length Std, Packet Length Variance, FIN Flag Count,
SYN Flag Count, RST Flag Count, PSH Flag Count,
ACK Flag Count, URG Flag Count, CWE Flag Count,
ECE Flag Count, Down/Up Ratio, Average Packet Size,
Avg Fwd Segment Size, Avg Bwd Segment Size, Fwd Header Length.1,
Fwd Avg Bytes/Bulk, Fwd Avg Packets/Bulk, Fwd Avg Bulk Rate,
Bwd Avg Bytes/Bulk, Bwd Avg Packets/Bulk, Bwd Avg Bulk Rate,
Subflow Fwd Packets, Subflow Fwd Bytes, Subflow Bwd Packets,
Subflow Bwd Bytes, Init_Win_bytes_forward, Init_Win_bytes_backward,
act_data_pkt_fwd, min_seg_size_forward, Active Mean,
Active Std, Active Max, Active Min, Idle Mean, Idle Std,
Idle Max, Idle Min, SimillarHTTP, Inbound
```

### A.3 Algorithme de calcul du seuil optimal (Youden J)

```python
from sklearn.metrics import roc_curve
import numpy as np

def calculate_optimal_threshold(y_true, y_proba):
    fpr, tpr, thresholds = roc_curve(y_true, y_proba)
    
    # Indice de Youden : J = TPR - FPR
    J = tpr - fpr
    
    # Seuil qui maximise J
    optimal_idx = np.argmax(J)
    optimal_threshold = thresholds[optimal_idx]
    
    return optimal_threshold
```

### A.4 Structure complète du projet

```yaml
ml-ddos-detection-with-kubernetes/
.
├── README.md                     # README principal : objectif, architecture cible, résultats
├── Rapport.md                    # Rapport académique final (template du professeur)
├── document_projet.md            # Notes et documentation intermédiaires
├── docker-compose.yml            # Déploiement local complet (ML, DB, SOAR, Web, Nginx)
├── requirements.txt              # Dépendances globales Python
├── LICENSE                       # Licence du projet
├── Makefile                      # Commandes d’automatisation
│
├── docs/
│   └── README.md                 # Point d’entrée documentaire central du projet
│
├── Images/                       # Schémas et captures utilisés dans le rapport
│   ├── architecture_cible.svg    # Architecture cible globale (figure principale)
│   ├── orchestrator.png          # Orchestration ML → SOAR
│   ├── pods_k8s.png              # Vue des pods Kubernetes
│   ├── svc_k8s.png               # Services Kubernetes
│   ├── dashboard.png             # Dashboard web temps réel
│   ├── dashboard_overview.png    # Vue d’ensemble du dashboard
│   ├── performance.png           # Résumé visuel des performances ML
│   ├── ddostaxonomy.png          # Taxonomie des attaques DDoS
│   └── README.md                 # Description des schémas
│
├── capture/                      # Capture réseau temps réel
│   ├── realtime_capture.py       # Capture des paquets réseau
│   ├── flow_parser.py            # Extraction des features (flows)
│   ├── orchestrator_prediction.py # Envoi vers l’inférence ML
│   ├── show_packets.py           # Debug et visualisation des paquets
│   ├── Dockerfile                # Conteneur du module de capture
│   ├── requirements.txt          # Dépendances spécifiques
│   └── README.md                 # Documentation du module
│
├── data/                         # Données et préparation hors ligne
│   ├── raw/                      # Données brutes et fusionnées
│   ├── processed/                # Artefacts de preprocessing sauvegardés
│   ├── fusionner_datasets.py     # Fusion des datasets
│   ├── analyse_features_labels.py # Analyse des features et labels
│   ├── similarity_features_in_all_datasets.py # Analyse de similarité
│   └── README.md                 # Description du dataset CICDDoS2019
│
├── preprocessed_data/            # Pipeline de preprocessing reproductible
│   ├── preprocessing_pipeline/   # Implémentation modulaire du pipeline ML
│   ├── sampling.py               # Gestion du déséquilibre
│   ├── sampling_v2.py            # Variante du sampling
│   └── README.md                 # Documentation du preprocessing
│
├── train/                        # Entraînement des modèles
│   ├── train_models.py           # Script principal d’entraînement
│   └── README.md                 # Description du processus ML
│
├── tuning/                       # Optimisation des hyperparamètres
│   ├── hyperparam_search.py      # Recherche automatique
│   └── config_tuning.yaml        # Configuration du tuning
│
├── models/                       # Modèles ML entraînés
│   ├── xgboost.pkl               # Modèle principal (production)
│   ├── random_forest.pkl         # Modèle alternatif
│   ├── xgboost.pkl.bak           # Sauvegarde
│   └── README.md                 # Performances et justification du choix
│
├── evaluate/                     # Évaluation et performances
│   ├── dashboard/                # Visualisations (heatmap, ROC, métriques)
│   ├── benchmark.csv             # Comparaison chiffrée + seuils
│   ├── reports/                  # Rapports détaillés
│   └── README.md                 # Analyse des résultats
│
├── inference/                    # Inférence temps réel
│   ├── predict.py                # Chargement du modèle et prédiction
│   └── README.md                 # Documentation de l’inférence
│
├── soar/                         # SOAR – réponse automatique
│   ├── app/                      # Logique de décision, blocage, alertes
│   ├── config/                   # Configuration SOAR
│   ├── logs/                     # Logs d’exécution
│   ├── Dockerfile                # Conteneur SOAR
│   └── README.md                 # Documentation SOAR
│
├── database/                     # Persistance et traçabilité
│   ├── database.py               # Accès MySQL
│   ├── init_db.sql               # Schéma de la base
│   ├── init_timezone.sql         # Configuration timezone
│   └── README.md                 # Modèle de données
│
├── k8s/                          # Déploiement Kubernetes
│   ├── base/                     # Manifests de base
│   ├── overlays/                 # Environnements dev / prod
│   └── README.md                 # Instructions Kubernetes
│
├── nginx/                        # Reverse proxy
│   ├── conf.d/default.conf       # Configuration Nginx
│   └── README.md                 # Documentation Nginx
│
├── web/                          # Interface web
│   ├── app.py                    # Backend Flask
│   ├── templates/                # Pages HTML
│   ├── static/                   # JS / CSS
│   └── Dockerfile                # Conteneur web
│
├── run_pipeline_ML.sh             # Lancement du pipeline ML complet
├── run_system_k8s.sh              # Déploiement Kubernetes complet
├── generate_k8s_traffic.sh        # Génération de trafic de test
└── test_soar_scenarios.sh         # Tests de scénarios SOAR

```