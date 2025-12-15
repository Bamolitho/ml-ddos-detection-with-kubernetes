# train — Entraînement des modèles de détection DDoS

Ce répertoire contient **la logique d’entraînement des modèles de machine learning** à partir des données prétraitées.

Objectifs :
- charger les données préparées (`data/processed`)
- gérer le fort déséquilibre des classes
- entraîner plusieurs familles de modèles
- sauvegarder les modèles entraînés
- permettre des expérimentations contrôlées via configuration

---

## Structure du répertoire

```
train/
├── __init__.py
└── train_models.py
```

---

## Vue d’ensemble du workflow

1. Chargement de la configuration (`config/config_train.yaml`)
2. Chargement des données préprocessées
3. Gestion du déséquilibre des classes
4. Construction des modèles selon la configuration
5. Entraînement des modèles activés
6. Sauvegarde des modèles entraînés

---

## Données utilisées

Les données sont chargées depuis :

```
data/processed/
├── train_processed.csv
└── train_labels.csv
```

Caractéristiques :
- données déjà nettoyées
- mêmes transformations que celles utilisées en inférence
- labels binaires :
  - `0` → BENIGN
  - `1` → DDoS

⚠️ **Aucune transformation de features n’est refaite ici**  
Tout le preprocessing est figé en amont.

---

## Gestion du déséquilibre des classes

Le script gère explicitement le **déséquilibre extrême** du dataset DDoS.

La stratégie est définie dans le fichier de configuration.

### Stratégies supportées

| Stratégie      | Description                         |
| -------------- | ----------------------------------- |
| `none`         | aucune correction                   |
| `class_weight` | pondération automatique des classes |
| `oversample`   | sur-échantillonnage                 |
| `undersample`  | sous-échantillonnage                |
| `smote`        | SMOTE explicite                     |
| `hybrid`       | oversampling + undersampling        |

Les bibliothèques `imbalanced-learn` sont utilisées **si disponibles**, avec fallback gracieux.

---

### Pondération automatique des classes

Lorsque `class_weight` est activé :
- calcul automatique via `compute_class_weight`
- adaptation spécifique selon le modèle :
  - **XGBoost** → `scale_pos_weight`
  - **LightGBM** → `class_weight`
  - **CatBoost** → `class_weights`
  - **Scikit-learn** → `class_weight` standard

👉 Cela permet une **gestion cohérente du déséquilibre**, quel que soit le framework.

---

## Modèles supportés

Le script supporte plusieurs familles de modèles.

### Modèles classiques (scikit-learn)

- Decision Tree
- Random Forest
- Gradient Boosting
- AdaBoost
- Logistic Regression
- SVM
- Naive Bayes
- KNN

---

### Modèles boosting avancés (optionnels)

- XGBoost
- LightGBM
- CatBoost

Ces modèles sont chargés **uniquement s’ils sont installés**.  
Sinon, ils sont ignorés sans casser le pipeline.

---

## Configuration par fichier YAML

Le comportement du script est entièrement piloté par :

config/config_train.yaml

Il permet de définir :
- les modèles activés / désactivés
- les hyperparamètres de chaque modèle
- la stratégie de gestion du déséquilibre
- les ratios de sampling

👉 Aucun paramètre critique n’est codé en dur.

---

## Boucle d’entraînement

Pour chaque modèle activé :

1. construction du modèle avec hyperparamètres
2. injection des poids de classes si nécessaire
3. entraînement sur le dataset complet
4. mesure du temps d’entraînement
5. sauvegarde du modèle

Les modèles sont sauvegardés dans :

```
models/
├── decision_tree.pkl
├── random_forest.pkl
├── xgboost.pkl
└── ...
```



---

## Bonnes pratiques appliquées

- séparation claire preprocessing / entraînement
- gestion robuste du déséquilibre
- fallback automatique si librairies absentes
- configuration centralisée
- sauvegarde systématique des modèles
- reproductibilité des expériences

---

## Quand utiliser ce dossier

- entraînement initial des modèles
- comparaison de plusieurs algorithmes
- tuning d’hyperparamètres
- tests de stratégies de déséquilibre
- génération des modèles pour l’inférence

---

## Perspectives d’évolution

- cross-validation stratifiée
- early stopping pour les boosters
- suivi des expériences (MLflow)
- sélection automatique du meilleur modèle
- entraînement distribué

---

## Résumé

Le dossier `train/` fournit un **pipeline d’entraînement flexible, robuste et extensible**, capable de gérer :
- des datasets massifs
- un déséquilibre sévère
- plusieurs frameworks ML
- des contraintes réalistes de production