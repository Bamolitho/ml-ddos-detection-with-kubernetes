# Evaluate — Évaluation et Benchmark des modèles ML

Ce module est responsable de **l’évaluation automatique de tous les modèles ML entraînés**.

Il mesure leurs performances, compare leurs résultats, calcule les seuils optimaux
et génère les artefacts nécessaires à l’inférence en production.

---

## Rôle du module

Le module `evaluate` répond à une question simple :

➡️ **Quel est le meilleur modèle, avec quel seuil de décision ?**

Il produit :
- des métriques objectives
- des courbes ROC
- des rapports détaillés
- un benchmark global exploité par l’inférence

---

## Structure du répertoire

```bash
evaluate/
├── evaluate_models.py # Évaluation automatique des modèles
├── benchmark.csv # Résumé global des performances
├── plots/ # Courbes ROC
│ └── xgboost_roc.png
├── reports/ # Rapports détaillés par modèle
│ └── xgboost_report.txt
└── dashboard/
└── dashboard.py # Génération du dashboard visuel
```

---

## Données utilisées

Le module travaille **exclusivement sur des données déjà prétraitées** :

| Fichier                             | Description      |
| ----------------------------------- | ---------------- |
| `data/processed/test_processed.csv` | Features de test |
| `data/processed/test_labels.csv`    | Labels associés  |

Aucune transformation n’est effectuée ici.

---

## Évaluation automatique des modèles

### Script principal

```bash
python evaluate/evaluate_models.py
```

Ce script :

- charge **tous les modèles `.pkl`** présents dans `models/`
- les évalue sur le jeu de test
- génère automatiquement les métriques et graphiques

Aucun modèle n’est codé en dur.

------

## Métriques calculées

Pour chaque modèle :

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Temps d’inférence total
- Débit (samples / seconde)

------

## Gestion des probabilités

Le script est robuste :

- supporte les modèles avec `predict_proba`
- gère ceux avec `decision_function`
- normalise les scores si nécessaire

Cela garantit une comparaison équitable.

------

## Calcul du meilleur seuil

Le seuil optimal est calculé via **Youden’s J statistic** :

```
J = TPR - FPR
```

Le seuil maximisant `J` est retenu.

➡️ Ce seuil est **utilisé directement par le module d’inférence**.

------

## Courbes ROC

Pour chaque modèle :

- génération automatique de la courbe ROC
- sauvegarde dans `evaluate/plots/`

Exemple :

```
evaluate/plots/xgboost_roc.png
```

------

## Rapports détaillés

Un rapport texte est généré par modèle :

```
evaluate/reports/<model>_report.txt
```

Il contient :

- toutes les métriques
- le temps d’inférence
- le débit
- le seuil optimal
- le chemin vers la courbe ROC

------

## Benchmark global

Tous les résultats sont regroupés dans :

```
evaluate/benchmark.csv
```

Ce fichier contient :

- les métriques par modèle
- le seuil optimal
- les performances d’inférence

➡️ C’est la **source de vérité** pour la production.

------

## Génération du dashboard visuel

### Script dashboard

```bash
python evaluate/dashboard/dashboard.py
```

Ce script :

- charge `benchmark.csv`
- génère des graphiques comparatifs
- crée un rapport HTML statique

------

## Contenu du dashboard

Le dashboard inclut :

- Bar charts :
  - Accuracy
  - Precision
  - Recall
  - F1
  - ROC-AUC
  - Throughput
- Heatmap des performances
- Courbes ROC de tous les modèles
- Rapport HTML auto-généré

Fichier final :

```
evaluate/dashboard/dashboard_report.html
```

------

## Utilisation dans le projet

Le module `evaluate` est utilisé :

- après l’entraînement
- avant le déploiement
- pour décider :
  - du meilleur modèle
  - du seuil de décision

Il alimente directement :

- le module `inference`
- la configuration production

------

## Ce que ce module NE fait PAS

- pas d’entraînement
- pas d’inférence live
- pas de capture réseau
- pas de déploiement Kubernetes

Il est **hors chemin critique runtime**.

------

## Avantages de cette approche

- comparaison équitable multi-modèles
- seuils basés sur des données réelles
- reproductibilité totale
- décision objective et traçable
- séparation claire entraînement / évaluation / production

------

## Perspectives d’évolution

- ajout de métriques coûts (FP / FN)
- calibration avancée des probabilités
- validation croisée automatique
- suivi historique des benchmarks
- export des résultats vers la base de données
- intégration CI/CD (gating sur métriques)

------

## Résumé

Le module `evaluate` est le **pilier décisionnel ML** du projet.

Il transforme des modèles entraînés en **choix de production mesurés et justifiés**.