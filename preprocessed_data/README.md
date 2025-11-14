# 1 — Colonne par colonne : garder, transformer ou supprimer ?

## **1.1 Flow ID → À SUPPRIMER**

Flow ID est juste une chaîne qui concatène IP + ports + timestamp.
 Le modèle ne peut rien apprendre dessus.
 Ça ne porte aucune information exploitable sous cette forme.

Donc, tu supprimes.
 Tu as déjà toutes les infos utiles dans les colonnes séparées.

------

## **1.2 Source IP / Destination IP → DÉCISION IMPORTANTE**

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

C’est *LA* question stratégique.

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

Tu regroupes :

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

# 3 — Résumé décisionnel clair

| Colonne            | Action                | Pourquoi                           |
| ------------------ | --------------------- | ---------------------------------- |
| Flow ID            | Supprimer             | Non exploitable                    |
| Unnamed: 0         | Supprimer             | Index inutile                      |
| Timestamp          | Supprimer             | Pas pertinent pour DDoS            |
| Source IP          | Supprimer             | Trop spécifique, non généralisable |
| Destination IP     | Supprimer             | Même raison                        |
| Source Port        | Garder                | Caractéristique utile              |
| Destination Port   | Garder                | Idem                               |
| Flow Duration      | Garder                | Très utile                         |
| IAT, Length, Flags | Garder                | Les meilleures features            |
| Label              | Garder ou transformer | Pour binaire : DDoS=1, Benign=0    |

------





## Pipeline Steps

### Visual Flow

```
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

