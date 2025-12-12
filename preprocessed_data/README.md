# 1 — Colonne par colonne : garder, transformer ou supprimer ?

## **1.1 Flow ID → À SUPPRIMER**

Flow ID est juste une chaîne qui concatène IP + ports + timestamp.
 Le modèle ne peut rien apprendre dessus.
 Ça ne porte aucune information exploitable sous cette forme.

Donc, tu supprimes.
 Tu as déjà toutes les infos utiles dans les colonnes séparées.

------

## **1.2 Source IP / Destinati**"""
Script d'entraînement des modèles supervisés :

- Chargement des données preprocessées
- Entraînement : Decision Tree + Random Forest
- Sauvegarde des modèles entraînés
"""

import pandas as pd
import os
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


# ==========================
# 1. Chargement des données
# ==========================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
processed_dir = os.path.normpath(os.path.join(BASE_DIR, "../data/processed"))

print("============================================================")
print("[INFO] Loading processed datasets...")
print("============================================================")

X_train = pd.read_csv(os.path.join(processed_dir, "train_processed.csv"))
X_val   = pd.read_csv(os.path.join(processed_dir, "val_processed.csv"))
X_test  = pd.read_csv(os.path.join(processed_dir, "test_processed.csv"))

y_train = pd.read_csv(os.path.join(processed_dir, "train_labels.csv")).values.ravel()
y_val   = pd.read_csv(os.path.join(processed_dir, "val_labels.csv")).values.ravel()
y_test  = pd.read_csv(os.path.join(processed_dir, "test_labels.csv")).values.ravel()

print("[OK] Data loaded successfully.\n")


# ==========================
# 2. Modèles supervisés
# ==========================

dt_model = DecisionTreeClassifier(
    criterion="gini",
    max_depth=None,
    random_state=42
)

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    n_jobs=-1,
    random_state=42
)

models = {
    "decision_tree": dt_model,
    "random_forest": rf_model
}


# ==========================
# 3. Entraînement + sauvegarde
# ==========================

models_dir = os.path.normpath(os.path.join(BASE_DIR, "../models"))
os.makedirs(models_dir, exist_ok=True)

for name, model in models.items():
    print("============================================================")
    print(f"[INFO] Training model: {name}")
    print("============================================================")

    model.fit(X_train, y_train)
    
    save_path = os.path.join(models_dir, f"{name}.pkl")
    joblib.dump(model, save_path)
    
    print(f"[OK] {name} saved to {save_path}\n")

print("============================================================")
print("[OK] TRAINING COMPLETED")
print("============================================================")**on IP → DÉCISION IMPORTANTE**

### Options possibles :

1. **Tu gardes et tu les transformes en numérique**
   - Ex : 192.168.1.1 → 3232235777
   - Ça peut avoir un impact si certaines IP attaquent plus que d’autres.
2. **Tu supprimes**
   - Si ton modèle doit généraliser à d’autres réseaux, garder les IP risque d’apprendre des patterns spécifiques, pas des comportements réseau.

### ***Mon opinion ferme pour un vrai système de détection en production :***

Tu supprimes **les adresses IP**.

Pourquoi ?
 Parce qu’en production, l’IP change tout le temps, et il est dangereux que ton modèle apprenne à détecter « l’IP du botnet du dataset » au lieu de comprendre **les caractéristiques du trafic**.

Bonne pratique :
 → Garde *les ports*, mais enlève *les IP*.

------

## **1.3 Unnamed: 0 → À SUPPRIMER**

C’est un index pandas exporté.
 Complètement inutile.
 On supprime sans réfléchir.

------

## **1.4 Timestamp → À SUPPRIMER**

Le modèle ne comprend rien à une date brute.
 Une date en tant que string n’a aucun sens pour un modèle ML.

Tu pourrais l’exploiter si tu convertissais en :

- heure de la journée
- jour de semaine
- durée inter-flux

… mais ce n’est **pas utile pour détecter du DDoS**, car l’heure d’attaque n’est pas systématique : un botnet attaque n’importe quand.

Donc on supprime.

------

## **1.5 Flow Duration → À GARDER**

Très important.
 Durée du flux = un des indicateurs clés dans DDoS.

------

## **1.6 Toutes les variables IAT, lengths, counts, flags → À GARDER**

Ce sont les variables **les plus importantes** en détection DDoS :

- nombre de paquets
- taux de paquets
- taux d’octets
- flag SYN, ACK…
- tailles
- variances

Garde tout ça.
 Tu ne peux pas mieux espérer pour ce type de modèle.

------

# 2 — Classification binaire ou multiclasses ?

### **Option A : Multiclasse**

Classes possibles :

- TFTP
- DNS
- UDP
- ACK
- NTP
- LDAP
- NETBIOS
- PortMap
- Benign
- etc.

### Problèmes :

- beaucoup plus complexe
- difficile à équilibrer
- certains types DDoS se ressemblent
- risque d'erreur élevé
- **pas utile en déploiement réel**

------

### **Option B : Binaire**

On regroupe :

- toutes les attaques DDoS → 1
- tout le trafic normal → 0

### Avantages :

- bien plus robuste
- performances plus élevées
- ré-entraînement plus facile
- déploiement production très simple

### ***Et dans un vrai environnement réseau ?***

Dans un vrai IDS orienté DDoS, **on ne cherche pas le type exact**.

Ce qu’on veut :
 → savoir si ton serveur se fait inonder ou pas.

Point.

Ce que tu fais après :

- tu détectes “attaque”
- puis tu fais une analyse secondaire pour deviner le vecteur (UDP / NTP / DNS), mais ça n’a rien à faire dans le modèle ML.

***Un détecteur ML doit répondre à une seule question :
 “Cette connexion est-elle normale ou pas ?”***

Donc je te recommande fortement :

➡️ **classification binaire**
➡️ toutes attaques → 1
➡️ bénin → 0

C’est la meilleure option pour un premier modèle, et même en production.

------

## Pipeline Steps

### Visual Flow

```less
┌─────────────────────────────────────┐
│  [1] DATA CLEANING                  │
│  - Remove duplicates                │
│  - Handle outliers (IQR/Z-score)    │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  [2] MISSING VALUES HANDLING        │
│  - Numerical imputation             │
│  - Categorical imputation           │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  [3] COLUMN TYPE IDENTIFICATION     │
│  - Identify numerical columns       │
│  - Identify categorical columns     │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  [4] CATEGORICAL ENCODING           │
│  - One-Hot Encoding                 │
│  - Label Encoding                   │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  [5] STATISTICAL FILTERING          │
│  - Remove low variance features     │
│  - Remove correlated features       │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  [6] SCALING/NORMALIZATION          │
│  - StandardScaler (z-score)         │
│  - MinMaxScaler (0-1 range)         │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  [7] DIMENSIONALITY REDUCTION       │
│  - PCA (variance maximization)      │
│  - ICA (independent sources)        │
│  - LDA (class separation)           │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  [8] FEATURE SELECTION              │
│  - Statistical tests (F-test, χ²)   │
│  - Information theory (MI)          │
│  - Model-based (Random Forest)      │
└─────────────────────────────────────┘
```

---

## Configuration

### Configuration File Structure (config.yaml)

```yaml
preprocessing:
  # Data Cleaning
  remove_duplicates: true
  handle_outliers: false
  outlier_method: 'iqr'  # or 'zscore'
  
  # Missing Values
  handle_missing: true
  missing_numerical_strategy: 'mean'  # 'mean', 'median', 'most_frequent'
  missing_categorical_strategy: 'most_frequent'
  
  # Categorical Encoding
  encode_categorical: true
  categorical_encoding_method: 'onehot'  # 'onehot' or 'label'
  
  # Statistical Filtering
  remove_low_variance: true
  variance_threshold: 0.01
  remove_correlated: true
  correlation_threshold: 0.95
  
  # Scaling
  use_scaler: true
  scaling_method: 'standard'  # 'standard' or 'minmax'
  
  # Dimensionality Reduction (choose ONE)
  use_pca: false
  n_components: 10
  use_ica: false
  ica_components: 10
  use_lda: false
  lda_components: 'auto'
  
  # Feature Selection
  feature_selection: false
  selection_method: 'auto'  # 'auto', 'f_test', 'mutual_info', 'chi2', 'random_forest'
  k_best: 10
  problem_type: 'auto'  # 'classification', 'regression', or 'auto'
```

### Key Configuration Parameters

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `remove_duplicates` | bool | true/false | Remove duplicate rows |
| `handle_outliers` | bool | true/false | Detect and remove outliers |
| `outlier_method` | str | 'iqr', 'zscore' | Method for outlier detection |
| `handle_missing` | bool | true/false | Impute missing values |
| `missing_numerical_strategy` | str | 'mean', 'median', 'most_frequent' | Strategy for numerical columns |
| `use_scaler` | bool | true/false | Apply feature scaling |
| `scaling_method` | str | 'standard', 'minmax' | Scaling algorithm |
| `use_pca` | bool | true/false | Apply PCA |
| `n_components` | int/str | integer or 'auto' | Number of PCA components |
| `feature_selection` | bool | true/false | Enable feature selection |
| `selection_method` | str | 'auto', 'f_test', etc. | Feature selection method |

preprocessing:

```yaml
use_scaler: false  # Trees are scale-invariant

  encode_categorical: true

  categorical_encoding_method: 'label'  # Label encoding is sufficient

  remove_correlated: false  # Trees handle correlation naturally

  feature_selection: false  # Trees perform implicit feature selection
```

