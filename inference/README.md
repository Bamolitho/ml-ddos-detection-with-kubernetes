# Inference — Prédiction DDoS (ML)

Ce module est responsable de **l’inférence machine learning**.

Il prend des features réseau en entrée, applique le pipeline de prétraitement,
exécute le modèle ML, et retourne une décision exploitable par l’orchestrateur.

Il ne capture rien, ne bloque rien, ne stocke rien.
👉 Il **prédit uniquement**.

---

## Rôle du module

Le module `inference` a un seul objectif :

➡️ transformer des features réseau en **verdict ML fiable**.

Il fournit :
- une prédiction binaire (0 / 1)
- une probabilité
- un verdict lisible (`Benign` / `DDoS`)
- un seuil optimisé automatiquement

---

## Structure du répertoire

```bash
inference/
├── predict.py # Script principal d’inférence
├── __init__.py
└── README.md
```

---

## Point d’entrée principal

Le script est conçu pour être appelé :
- en **CLI**
- par un **autre module Python** (orchestrator)

Commande typique :

```bash
python inference/predict.py --json "<features_json>"
```

------

## Principe de fonctionnement

### 1. Chargement des composants

Au démarrage, le script charge dynamiquement :

- le **pipeline de prétraitement**
- le **modèle ML**
- le **seuil optimal** calculé lors de l’évaluation

Sources :

| Élément  | Emplacement                                |
| -------- | ------------------------------------------ |
| Modèle   | `models/<model_name>.pkl`                  |
| Pipeline | `data/processed/preprocessed_pipeline.pkl` |
| Seuil    | `evaluate/benchmark.csv`                   |

------

### 2. Gestion du seuil de décision

Le seuil n’est **pas codé en dur**.

Il est chargé depuis `benchmark.csv`, généré lors de la phase d’évaluation :

```
model,best_threshold
xgboost,0.11
```

➡️ Cela permet d’adapter la décision au modèle sans modifier le code.

------

### 3. Prétraitement des données

Les données d’entrée sont transformées via le pipeline :

```python
X = pipeline.transform(data)
```

Le pipeline garantit :

- ordre correct des features
- normalisation
- encodage
- compatibilité exacte avec l’entraînement

------

### 4. Prédiction

Pour chaque flow :

- calcul de la probabilité (`predict_proba`)
- comparaison avec le seuil optimal
- conversion en verdict final

Règle :

```
probability >= threshold → DDoS
sinon → Benign
```

------

## Formats d’entrée supportés

### 1. JSON (utilisé en production)

```bash
--json '{"Flow Duration":123,"Total Fwd Packets":10,...}'
```

C’est le mode utilisé par l’orchestrator Kubernetes.

------

### 2. CSV (tests / batch)

```bash
--input data/processed/test.csv
```

Optionnellement accompagné de labels pour l’évaluation.

------

## Format de sortie (JSON)

Sortie unique sur `stdout` :

```json
{
  "model": "xgboost",
  "threshold": 0.11,
  "results": [
    {
      "prediction": 1,
      "probability": 0.92,
      "verdict": "DDoS"
    }
  ]
}
```

Ce format est **consommé directement** par l’orchestrator.

------

## Support des métriques (optionnel)

Si un fichier de labels est fourni :

- le script génère automatiquement un `classification_report`
- les métriques sont ajoutées au JSON de sortie

Utile pour :

- validation
- tests hors production
- benchmark

------

## Sélection du modèle

Priorité de sélection :

1. `--model <nom>` (CLI)
2. `config/config_inference.yaml` (si activé)
3. modèle par défaut : `xgboost`

Aucun changement de code n’est nécessaire pour changer de modèle.

------

## Ce que ce module NE fait PAS

- pas de capture réseau
- pas de base de données
- pas de SOAR
- pas de règles de sécurité
- pas de logique métier

👉 Il reste **volontairement simple et isolé**.

------

## Intégration dans l’architecture globale

```
Features réseau
      ↓
Preprocessing pipeline
      ↓
Modèle ML
      ↓
Probabilité + verdict
      ↓
Orchestrator
```

------

## Avantages de cette approche

- découplage total du ML
- modèle interchangeable
- seuil ajustable sans code
- testable en standalone
- reproductible

------

## Perspectives d’évolution

- support multi-modèles simultanés
- ensemble learning
- calibration dynamique des seuils
- export ONNX
- accélération GPU
- détection multi-classes

------

## Résumé

Le module `inference` est le **moteur de décision statistique** du projet.

Il transforme des statistiques réseau en une **prédiction exploitable**,
sans dépendance au contexte réseau ou sécurité.

Simple, fiable, et prêt pour la production.