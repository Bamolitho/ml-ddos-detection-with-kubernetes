# Config — Configuration centrale du pipeline ML

Ce répertoire contient **toute la configuration du projet** sous forme de fichiers YAML.

Il permet de :
- piloter les expériences sans modifier le code
- standardiser l’entraînement, l’échantillonnage et l’inférence
- garantir la reproductibilité
- centraliser les paramètres critiques

Aucun traitement n’est effectué ici :  
ce dossier **décrit ce que font les autres modules**.

---

## Structure du répertoire

```bash
config/
├── config_train.yaml # Entraînement des modèles
├── config_sampling.yaml # Échantillonnage et équilibrage des données
└── config_inference.yaml # Configuration de l’inférence
```

Chaque fichier correspond à **une phase précise du pipeline**.

---

## config_inference.yaml

Contrôle le comportement du module d’inférence.

### Rôle

- définir la source des données de prédiction
- choisir le modèle utilisé
- activer ou non l’évaluation avec labels

### Sections principales

#### Activation globale
```yaml
enable_config: true
```

Permet d’activer ou ignorer complètement la configuration YAML.

#### Données d’entrée

```yaml
use_static_input_file: true
input_file: "data/processed/test.csv"
```

- true : fichier statique utilisé
- false : fallback automatique vers un fichier par défaut

#### Labels (optionnels)

```yaml
use_static_label_file: true
label_file: "data/processed/test_labels.csv"
```

Utilisés uniquement pour évaluer les performances.

#### Modèle par défaut

```yaml
model_name: "xgboost"
use_static_model_name: xgboost
```

Permet de forcer un modèle sans passer par la CLI.

------

## config_sampling.yaml

Gère l’échantillonnage du dataset brut.

### Rôle

- réduire les volumes massifs
- conserver la diversité des attaques
- préparer des datasets exploitables

### Paramètres clés

#### Dataset

```yaml
input_path: "../data/raw/merged_datasets.csv"
output_path: "../data/raw/merged_balanced.csv"
chunk_size: 100000
random_seed: 42
```

#### Stratégie d’échantillonnage

```yaml
benign_keep: 1.0
ddos_keep_prob: 0.01
```

- 100% des flux bénins conservés
- ~1% des attaques DDoS conservées (streaming)

#### Règles dynamiques par taille de classe

```yaml
rules:
  major_threshold: 5_000_000
  medium_threshold: 500_000
```

#### Fractions cibles

```yaml
target_frac:
  major: 0.01
  medium: 0.02
  minor: 0.05
```

#### Sécurité statistique

```yaml
min_equals_benign: true
```

Empêche de créer des classes trop petites.

------

## config_train.yaml

Pilote **l’ensemble des expériences d’entraînement**.

### Sélection des modèles

```yaml
models:
  xgboost: true
  lightgbm: true
  random_forest: false
  ...
```

Seuls les modèles à `true` sont entraînés.

------

## Hyperparamètres

Chaque modèle possède sa propre section.

Exemples :

- `xgboost`
- `lightgbm`
- `random_forest`
- `logistic_regression`
- `svm`
- `knn`

Tous les paramètres sont :

- explicitement nommés
- commentés
- modifiables sans toucher au code

------

## Gestion du déséquilibre

```yaml
imbalance:
  strategy: "class_weight"
  auto_class_weight: true
```

Stratégies disponibles :

- none
- oversample
- undersample
- smote
- class_weight
- hybrid

Objectif :

> améliorer la détection DDoS sans exploser les faux positifs.

------

## Qui fait quoi

- **config_sampling.yaml**
  → Prépare les données exploitables
- **config_train.yaml**
  → Définit les expériences ML
- **config_inference.yaml**
  → Pilote la prédiction en production ou en test

------

## Pourquoi ce design

- séparation claire des responsabilités
- pas de valeurs magiques dans le code
- adaptation rapide à d’autres datasets
- exécution reproductible

------

## Perspectives d’évolution

- validation automatique des YAML
- profils de configuration (dev / prod)
- override via variables d’environnement
- versionnement des configs
- génération automatique de rapports de config

------

## Résumé

Le dossier `config/` est **le cerveau décisionnel du pipeline**.

Il permet de :

- comprendre le comportement du système
- modifier une expérience en quelques secondes
- garder un projet propre, maintenable et professionnel

