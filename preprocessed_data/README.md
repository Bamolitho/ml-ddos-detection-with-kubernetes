# preprocessed_data — Préprocessing et équilibrage des données

Ce répertoire contient **toute la logique de préparation des données avant l’entraînement ML**.

Objectifs principaux :
- transformer le dataset brut en données exploitables
- équilibrer le dataset DDoS / BENIGN
- supprimer les informations inutiles ou dangereuses
- produire des splits reproductibles
- sauvegarder un pipeline de preprocessing réutilisable en production

C’est une **brique critique du pipeline ML**.

---

## Structure du répertoire

```bash
preprocessed_data/
├── __init__.py
├── preprocessed_data.py
├── sampling.py
├── sampling_v2.py
├── preprocessing_pipeline/
│ ├── preprocessing_pipeline.py
│ ├── config.yaml
│ ├── main.py
│ ├── README.md
│ └── requirements.txt
└── README.md
```

---

## Vue d’ensemble du pipeline

1. Chargement du dataset brut
2. Conversion en classification **binaire** (BENIGN / DDoS)
3. Équilibrage du dataset
4. Nettoyage des colonnes
5. Splits train / validation / test
6. Fit du preprocessing **uniquement sur train**
7. Transformation cohérente de val et test
8. Sauvegarde :
   - des datasets
   - du pipeline de preprocessing

---

## Choix fondamentaux de conception

### Classification binaire

- **0** → trafic BENIGN  
- **1** → trafic DDoS (toutes attaques confondues)

Raison :
- plus robuste
- plus simple à déployer
- plus réaliste en production

Un IDS orienté DDoS doit répondre à **une seule question** :

> *Ce trafic est-il normal ou malveillant ?*

---

## Politique de gestion des colonnes

### Colonnes supprimées volontairement

| Colonne          | Décision  | Raison                                  |
| ---------------- | --------- | --------------------------------------- |
| `Flow ID`        | supprimée | Identifiant sans valeur ML              |
| `Source IP`      | supprimée | Apprentissage biaisé, non généralisable |
| `Destination IP` | supprimée | Même raison                             |
| `Timestamp`      | supprimée | Date brute non exploitable              |
| `Unnamed: 0`     | supprimée | Index pandas                            |
| `SimillarHTTP`   | supprimée | Bruit et faible valeur                  |

### Colonnes conservées

- durées de flux
- tailles de paquets
- IAT
- compteurs
- flags TCP
- statistiques (mean, std, variance, max, min)

👉 Ce sont **les signaux clés en détection DDoS**.

---

## Scripts principaux

### preprocessed_data.py

Script central de preprocessing.

Responsabilités :
- chargement du dataset équilibré
- nettoyage brut (NaN, inf)
- suppression des colonnes inutiles
- splits stratifiés :
  - 60 % train
  - 20 % validation
  - 20 % test
- suppression des doublons **uniquement dans train**
- fit du pipeline uniquement sur train
- transformation cohérente de val et test
- sauvegarde des fichiers et du pipeline

Sorties générées dans `data/processed/` :
- `train.csv`, `val.csv`, `test.csv`
- `train_processed.csv`, `val_processed.csv`, `test_processed.csv`
- `train_labels.csv`, `val_labels.csv`, `test_labels.csv`
- `preprocessed_pipeline.pkl`

---

### sampling.py

Script avancé d’équilibrage du dataset.

Fonctionnement :
- lecture du dataset par chunks (RAM-safe)
- regroupement par type d’attaque
- conversion robuste en binaire
- sous-échantillonnage dynamique des attaques
- conservation contrôlée du trafic BENIGN
- équilibrage final via **SMOTEENN**
- gestion des cas extrêmes (classes rares)

Objectif :
- obtenir un dataset équilibré **sans déformer la distribution réelle**

---

### sampling_v2.py

Version alternative plus simple et plus rapide.

Approche :
- streaming du dataset
- conservation totale de BENIGN
- sous-échantillonnage aléatoire des DDoS
- équilibrage final par undersampling simple

Utilisation :
- tests rapides
- environnements contraints
- validation exploratoire

---

## preprocessing_pipeline/

Contient le **pipeline de transformation des features**.

### preprocessing_pipeline.py

Pipeline maison basé sur scikit-learn.

Fonctions principales :
- suppression des features à faible variance
- suppression des features trop corrélées
- encodage du protocole
- gestion des flags réseau
- normalisation des features numériques

---

### config.yaml

Fichier de configuration du preprocessing.

Permet d’activer/désactiver :
- normalisation
- encodage catégoriel
- filtrage statistique
- réduction de dimension
- sélection de features

Les paramètres sont **centralisés et reproductibles**.

---

## Bonnes pratiques appliquées

- aucun leakage train → val → test
- pipeline appris uniquement sur train
- mêmes transformations appliquées partout
- preprocessing sérialisé pour l’inférence
- scripts reproductibles
- gestion mémoire adaptée aux gros datasets

---

## Quand utiliser ce dossier

- préparation initiale des données
- re-génération des datasets
- changement de stratégie de sampling
- mise à jour du preprocessing
- alignement entraînement ↔ production

---

## Perspectives d’évolution

- automatisation du choix de sampling
- monitoring du déséquilibre réel en production
- détection de dérive des features
- feature selection adaptative
- intégration directe avec MLflow / DVC

---

## Résumé

Le dossier `preprocessed_data/` transforme un dataset réseau brut et massif en **données propres, équilibrées et exploitables**, prêtes pour l’entraînement et l’inférence d’un système de détection DDoS en production.
