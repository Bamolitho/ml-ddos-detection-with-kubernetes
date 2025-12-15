# data — Datasets et préparation des données

Ce répertoire regroupe **l’ensemble du travail lié aux données** du projet de détection DDoS :
- collecte et description du dataset
- analyse des features et des labels
- fusion et harmonisation des fichiers
- gestion du déséquilibre
- préparation des données pour l’entraînement et l’inférence

Il constitue la **fondation du pipeline Machine Learning**.

---

## Dataset utilisé

Le jeu de données utilisé est **CICDDoS2019**.  
Il provient du site officiel de l’Université du New Brunswick :

- Présentation : https://www.unb.ca/cic/datasets/ddos-2019.html  
- Dataset : http://cicresearch.ca/CICDataset/CICDDoS2019/Dataset/

Téléchargement :

```bash
wget http://cicresearch.ca/CICDataset/CICDDoS2019/Dataset/CSVs/CSV-01-12.zip
# ou
curl -O http://cicresearch.ca/CICDataset/CICDDoS2019/Dataset/CSVs/CSV-01-12.zip
```

Ce dataset couvre les **deux grandes familles d’attaques DDoS** :

- Reflection-based attacks
- Exploitation-based attacks

------

## Contenu du dataset

Le fichier `CSV-01-12.zip` contient **11 fichiers CSV**, chacun correspondant à un type d’attaque spécifique.

Tous les fichiers partagent :

- une colonne cible unique : **Label**
- une structure commune de **87 features + Label**

### Résumé des fichiers

| Fichier CSV       | Total échantillons | Labels                   |
| ----------------- | ------------------ | ------------------------ |
| TFTP.csv          | 20,107,827         | TFTP, BENIGN             |
| DrDoS_NetBIOS.csv | 4,094,986          | DrDoS_NetBIOS, BENIGN    |
| DrDoS_SSDP.csv    | 2,611,374          | DrDoS_SSDP, BENIGN       |
| DrDoS_DNS.csv     | 5,074,413          | DrDoS_DNS, BENIGN        |
| Syn.csv           | 1,582,681          | Syn, BENIGN              |
| DrDoS_SNMP.csv    | 5,161,377          | DrDoS_SNMP, BENIGN       |
| UDPLag.csv        | 370,605            | UDP-lag, BENIGN, WebDDoS |
| DrDoS_MSSQL.csv   | 4,524,498          | DrDoS_MSSQL, BENIGN      |
| DrDoS_UDP.csv     | 3,136,802          | DrDoS_UDP, BENIGN        |
| DrDoS_LDAP.csv    | 2,181,542          | DrDoS_LDAP, BENIGN       |
| DrDoS_NTP.csv     | 1,217,007          | DrDoS_NTP, BENIGN        |

Total : **50 063 112 flux réseau**

------

## Features

Chaque fichier contient **87 features réseau**, décrivant les flux :

- informations d’en-tête (IP, ports, protocole)
- statistiques de paquets (min, max, moyenne, écart-type)
- caractéristiques temporelles (durée, IAT, débit)
- flags TCP (SYN, ACK, FIN…)
- activité et inactivité des flux

La colonne **Label** indique le type de trafic (Benign ou attaque).

------

## Déséquilibre du dataset

Le trafic **Benign est très largement minoritaire** par rapport aux attaques.
Ce déséquilibre peut biaiser fortement l’apprentissage si aucune stratégie adaptée n’est appliquée.

### Problèmes induits

- accuracy trompeuse
- sur-apprentissage des classes majoritaires
- mauvaise détection du trafic légitime

------

## Stratégies envisagées

### 1. Rééchantillonnage

- oversampling (ex. SMOTE)
- undersampling des classes majoritaires

### 2. Pondération des classes

- `class_weight='balanced'`
- pondération spécifique pour XGBoost / LightGBM

### 3. Métriques adaptées

- F1-score
- Precision / Recall
- AUC-ROC
- AUC-PR
- matrice de confusion

### 4. Validation stratifiée

- `train_test_split(..., stratify=...)`
- `StratifiedKFold`

### 5. Modèles robustes

- XGBoost
- LightGBM
- Random Forest avec pondération

------

## Approche retenue

**Class Weighting + Modèles Boostés**

Cette combinaison est la plus robuste pour :

- datasets massifs
- déséquilibre extrême
- diversité des attaques
- contraintes de performance

En pratique :

- XGBoost : `scale_pos_weight`
- LightGBM : `is_unbalance` ou `class_weight`
- modèles sklearn : `class_weight='balanced'`

------

## Structure du répertoire

```bash
data/
├── raw/                          # Datasets bruts
├── processed/
│   └── preprocessed_pipeline.pkl # Pipeline de preprocessing sérialisé
├── splits/                       # Jeux train / val / test (si générés)
├── analyse_features_labels.py
├── fusionner_datasets.py
├── fusionner_datasets_version_HPC.py
├── similarity_features_in_all_datasets.py
└── README.md
```

------

## Rôle des scripts

- **fusionner_datasets.py**
  - fusion des CSV
  - harmonisation des colonnes et labels
- **fusionner_datasets_version_HPC.py**
  - version optimisée pour très grands volumes
  - traitement par chunks
- **analyse_features_labels.py**
  - analyse des distributions
  - détection d’anomalies et déséquilibres
- **similarity_features_in_all_datasets.py**
  - comparaison des features entre fichiers
  - vérification de compatibilité avant fusion

------

## processed/

- contient les données prêtes pour le ML
- `preprocessed_pipeline.pkl` est utilisé **à l’identique en entraînement et en inférence**
- garantit la cohérence du pipeline de bout en bout

------

## Bonnes pratiques

- ne jamais modifier `raw/`
- versionner les pipelines
- relancer l’analyse à chaque nouvelle source
- conserver des scripts reproductibles

------

## Perspectives

- data versioning (DVC, MLflow)
- génération automatique des splits
- détection de dérive des données
- ingestion streaming temps réel
- validation automatique des datasets entrants

