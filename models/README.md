# Modèles Machine Learning

Ce répertoire contient les **modèles Machine Learning entraînés** utilisés pour la **détection binaire DDoS vs Benign**.

Les modèles sont entraînés à partir de données **préprocessées de manière reproductible** et sont directement utilisés par le module d’**inférence temps réel**.

---

## Contenu du répertoire

| Fichier             | Description                            |
| ------------------- | -------------------------------------- |
| `xgboost.pkl`       | Modèle principal utilisé en production |
| `random_forest.pkl` | Modèle alternatif pour comparaison     |
| `xgboost.pkl.bak`   | Sauvegarde de sécurité                 |

---

## Modèle principal : XGBoost

Le modèle **XGBoost** est actuellement le **meilleur compromis** entre :
- performance de détection
- robustesse
- temps d’inférence
- capacité de généralisation

Il est donc utilisé par défaut pour :
- l’inférence temps réel
- l’orchestration SOAR
- le dashboard

---

## Performances et évaluation

Les performances des modèles sont évaluées dans le répertoire :

📁 [`evaluate/`](../evaluate)

---

### Heatmap de performance (comparaison globale)

Cette heatmap synthétise les **principales métriques** pour tous les modèles testés.

![Heatmap de performance des modèles ML](../evaluate/dashboard/heatmap_performance.png)

C’est la visualisation **la plus importante** pour justifier le choix du modèle final.

---

### Métriques détaillées (XGBoost)

**Accuracy**

![Accuracy XGBoost](../evaluate/dashboard/accuracy.png)

**Precision**

![Precision XGBoost](../evaluate/dashboard/precision.png)

**Recall**

![Recall XGBoost](../evaluate/dashboard/recall.png)

**F1-score**

![F1-score XGBoost](../evaluate/dashboard/f1.png)

**ROC AUC**

![ROC AUC XGBoost](../evaluate/dashboard/roc_auc.png)

**Courbe ROC spécifique XGBoost**

![Courbe ROC XGBoost](../evaluate/dashboard/xgboost_roc.png)

---

### Rapport complet

- Rapport HTML interactif  
  [`evaluate/dashboard/dashboard_report.html`](../evaluate/dashboard/dashboard_report.html)

- Rapport texte détaillé  
  [`evaluate/reports/xgboost_report.txt`](../evaluate/reports/xgboost_report.txt)

---

## Seuil de décision

Le seuil de classification utilisé par chaque modèle :
- n’est **pas fixe**
- est calculé automatiquement lors de l’évaluation
- est sauvegardé dans :

📄 [`evaluate/benchmark.csv`](../evaluate/benchmark.csv)

Ce seuil est ensuite chargé dynamiquement par le module d’inférence.

---

## Utilisation des modèles

Les modèles de ce répertoire sont utilisés par :

- le module d’inférence  
  📁 [`inference/`](../inference)

- l’orchestrateur SOAR  
  📁 [`soar/`](../soar)

- le dashboard web  
  📁 [`web/`](../web)

Aucun retraining n’est effectué en production.

---

## Bonnes pratiques

- Ne jamais modifier un `.pkl` en production
- Toujours régénérer les modèles via :
  - [`run_pipeline_ML.sh`](../run_pipeline_ML.sh)
- Toujours vérifier les performances avant remplacement
- Versionner les modèles importants

---

## Perspectives

- Ajout de modèles deep learning
- Détection multi-classes
- Apprentissage incrémental
- Sélection automatique du meilleur modèle en runtime
- Explicabilité (SHAP, feature importance avancée)

---

## Références

- Entraînement : [`train/`](../train)
- Évaluation : [`evaluate/`](../evaluate)
- Pipeline ML : [`docs/ml_pipeline.md`](../docs/ml_pipeline.md)