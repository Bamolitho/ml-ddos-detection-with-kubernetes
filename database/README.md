# database — Persistance des données et historique des flux

Ce répertoire gère **toute la couche base de données** du projet :
- initialisation de la base MySQL
- création des tables
- insertion des flux analysés
- récupération de l’historique pour le dashboard

Il constitue la **mémoire persistante** du système de détection DDoS.

---

## Structure du répertoire

```
database/
├── __init__.py
├── database.py
├── init_db.sql
└── init_timezone.sql
```

---

## Rôle global

La base de données permet de :
- stocker les décisions prises par le moteur ML
- tracer chaque flux réseau analysé
- alimenter l’interface web (dashboard)
- conserver un historique exploitable (audit, analyse, tuning)

---

## Base de données utilisée

- **SGBD** : MySQL / MariaDB
- **Base** : `ddos_detection`
- **Encodage** : `utf8mb4`
- **Moteur** : InnoDB

---

## Tables principales

### Table `users`

Gère l’authentification des utilisateurs.

| Champ      | Type      | Description        |
| ---------- | --------- | ------------------ |
| id         | INT       | Identifiant unique |
| username   | VARCHAR   | Nom d’utilisateur  |
| password   | VARCHAR   | Mot de passe hashé |
| created_at | TIMESTAMP | Date de création   |

---

### Table `flows`

Stocke chaque flux réseau analysé par le système.

| Champ       | Type      | Description            |
| ----------- | --------- | ---------------------- |
| src_ip      | VARCHAR   | IP source              |
| dst_ip      | VARCHAR   | IP destination         |
| src_port    | INT       | Port source            |
| dst_port    | INT       | Port destination       |
| prediction  | INT       | Sortie brute du modèle |
| verdict     | ENUM      | Benign / DDoS          |
| probability | FLOAT     | Probabilité associée   |
| threshold   | FLOAT     | Seuil utilisé          |
| action      | ENUM      | Passed / Blocked       |
| timestamp   | TIMESTAMP | Date d’analyse         |

Indexes :
- `timestamp` → historique
- `verdict` → filtrage DDoS / Benign
- `action` → trafic bloqué ou autorisé

---

## Scripts SQL

### init_db.sql

- crée la base `ddos_detection`
- crée les tables `users` et `flows`
- applique les encodages et index
- affiche un message de succès

Utilisé pour une **initialisation manuelle ou automatisée**.

---

### init_timezone.sql

- définit le fuseau horaire global
- garantit la cohérence des timestamps entre services

---

## Module Python : `database.py`

Ce module est utilisé par l’application Flask.

### Responsabilités

- gérer la connexion MySQL
- créer les tables au démarrage
- exécuter des requêtes SQL
- enregistrer les flux analysés
- fournir l’historique au frontend

---

### Fonctions principales

#### `init_mysql(mysql)`
Initialise la connexion MySQL depuis Flask-MySQLdb.

---

#### `init_db()`
Crée automatiquement les tables si elles n’existent pas.

Appelée au démarrage de l’application.

---

#### `insert_flow(flow)`
Insère un flux analysé dans la table `flows`.

Utilisée par :
- le moteur d’inférence
- l’orchestrateur de décision

---

#### `get_last_flows(limit)`
Retourne les derniers flux pour l’interface web.

Utilisée par :
- dashboard
- pages d’historique

---

#### `execute_query(query, params, fetch)`
Fonction générique d’exécution SQL.

---

## Qui fait quoi

- **SQL**
  - structure de la base
  - création initiale
  - configuration globale

- **Python**
  - logique applicative
  - insertion dynamique
  - récupération des données

---

## Quand ce dossier est utilisé

- au démarrage de l’application Flask
- à chaque prédiction ML
- lors de l’affichage du dashboard
- pour analyser l’historique des attaques

---

## Bonnes pratiques appliquées

- séparation schéma / logique applicative
- création idempotente des tables
- indexation des champs critiques
- gestion d’erreurs explicite
- encodage et fuseau horaire cohérents

---

## Perspectives d’évolution

- rotation / purge automatique des flux anciens
- stockage des features complètes
- support multi-clients
- réplication / haute disponibilité
- export vers SIEM

---

## Résumé

Le dossier `database/` fournit une **couche de persistance fiable, claire et extensible**, essentielle pour :
- la traçabilité
- l’analyse post-incident
- la visualisation en temps réel
- la crédibilité du système

