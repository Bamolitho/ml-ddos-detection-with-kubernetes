# SOAR — Security Orchestration, Automation and Response

## Rôle du SOAR

Le SOAR est **l’autorité finale des décisions de sécurité** du système de détection DDoS.

Il reçoit des alertes du moteur de détection (ML / orchestrateur),  
évalue la situation,  
et décide de l’action à appliquer :

- Passed
- Whitelisted
- Blocked

➡️ **Aucune décision de blocage n’est prise ailleurs que dans le SOAR.**

---

## Position dans l’architecture globale

CAPTURE → ML → ORCHESTRATEUR → SOAR → ACTION → DATABASE

- Le ML **détecte**
- L’orchestrateur **transmet**
- Le SOAR **décide et agit**
- La base de données **enregistre la vérité finale**

Le SOAR est volontairement isolé :
- pas de ML
- pas d’UI
- pas d’accès à la base applicative

---

## Responsabilités du SOAR

### Ce qu’il fait

- reçoit un événement DDoS
- vérifie l’authenticité (secret partagé)
- applique un seuil de confiance
- vérifie la whitelist
- bloque l’IP si nécessaire
- notifie via Telegram
- journalise chaque décision

### Ce qu’il ne fait pas

- Machine Learning
- Interface utilisateur
- Authentification utilisateur
- Gestion de base de données métier

---

## Architecture du répertoire

```bash
soar/
├── app/
│ ├── main.py # API Flask + logique de décision
│ ├── blocker.py # Blocage IP (iptables)
│ ├── whitelist.py # Gestion whitelist (préfixes IP)
│ └── telegram.py # Notifications Telegram
│
├── config/
│ └── config.json # Mode de blocage (log / iptables)
│
├── logs/
│ └── soar.log # Journal des actions
│
├── Dockerfile # Image Docker du SOAR
├── requirements.txt # Dépendances Python
└── README.md
```



---

## API SOAR

### Endpoint unique

POST /alert

### Payload attendu

```json
{
  "secret": "shared-secret",
  "src_ip": "1.2.3.4",
  "verdict": "DDoS",
  "probability": 0.92
}
```

- `secret` : authentification du webhook
- `src_ip` : IP source suspecte
- `verdict` : doit être `DDoS`
- `probability` : score ML

------

## Fonctionnement détaillé

### 1. Authentification

Si le secret est incorrect :
➡️ requête rejetée (`401 unauthorized`)

------

### 2. Filtrage initial

Une alerte est ignorée si :

- verdict ≠ `DDoS`
- IP absente
- probabilité < seuil

------

### 3. Seuil de confiance

Défini par variable d’environnement :

```less
SOAR_MIN_PROBABILITY=0.8
```

En dessous :
➡️ l’alerte est acceptée mais **aucune action** n’est prise.

------

### 4. Whitelist IP

Définie par variable d’environnement :

```less
SOAR_WHITELIST_IPS=127.0.0.1,192.168.1.,10.
```

- support des **préfixes IP**
- exemple : `192.168.1.` autorise tout le sous-réseau

Si whitelistée :
➡️ action = `Passed`

------

### 5. Mode de blocage

Configuré dans :

```less
config/config.json
{
  "blocking": {
    "method": "log"
  }
}
```

Modes disponibles :

- `iptables` : blocage réel
- `log` : mode développement (aucune règle appliquée)

------

### 6. Blocage réseau

En mode `iptables` :

```less
iptables -I INPUT -s <IP> -j DROP
```

- règle appliquée immédiatement
- action journalisée
- notification Telegram envoyée

------

### 7. Notifications Telegram

Chaque blocage génère un message contenant :

- IP bloquée
- probabilité
- méthode utilisée

Variables requises :

```less
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

------

### 8. Logs

Tous les événements sont écrits dans :

```less
logs/soar.log
```

Les logs servent :

- d’audit
- de preuve de décision
- de support au debug

------

## Dépendances

- Python 3
- Flask
- Requests
- iptables (si blocage réel)

------

## Tests manuels

### Test du webhook

```bash
curl -X POST http://localhost:6000/alert \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "super-long-secret-random-64chars",
    "src_ip": "8.8.8.8",
    "verdict": "DDoS",
    "probability": 0.98
  }'
```

Réponse attendue :

```json
{"status":"blocked"}
```

------

### Vérification iptables

Dans le conteneur :

```bash
iptables -L INPUT -n --line-numbers
```

------

### Test whitelist

```bash
curl -X POST http://localhost:6000/alert \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "super-long-secret-random-64chars",
    "src_ip": "192.168.1.55",
    "verdict": "DDoS"
  }'
```

Résultat attendu :

```json
{"status":"passed"}
```

Aucune règle iptables ajoutée.

------

## Sécurité

- Secret partagé obligatoire
- Whitelist réseau
- Seuil de confiance configurable
- Journalisation complète
- Privilèges élevés **uniquement** pour ce service

------

## Perspectives d’évolution

- Blocage temporaire avec expiration
- Support ipset / nftables
- Corrélation multi-alertes
- Stockage des décisions en base dédiée
- Interface d’administration SOAR
- Intégration SIEM / SOAR externe

------

## Résumé

Le SOAR est le **cerveau décisionnel** du projet.

Il transforme une prédiction ML en **action réelle, traçable et sécurisée**.

Simple, isolé, et conçu pour évoluer vers un environnement professionnel.