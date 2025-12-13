Le SOAR est l’autorité des notifications et des actions (passed/blocked/whitelist)

# 1️⃣ Vue d’ensemble de l’architecture

```bash
.
.
.
├── capture/                  # service actuel (Flask / ML / DB)
│   ├── app.py
│   ├── inference/
│   ├── models/
│   ├── templates/
│   ├── Dockerfile
│   └── ...
│
├── database/
│   └── ...
│
├── soar/                     # 🆕 micro-service SOAR
│   ├── app/
│   │   ├── main.py           # API SOAR (webhook)
│   │   ├── blocker.py        # logique blocage IP
│   │   ├── telegram.py       # notifications
│   │   ├── whitelist.py
│   │   └── rate_limit.py
│   │
│   ├── config/
│   │   └── config.json
│   │
│   ├── logs/
│   │   └── soar.log
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
└── .env
```

------

# 2️⃣ Rôle du micro-service SOAR

**Responsabilités uniques :**

- recevoir un événement DDoS
- vérifier whitelist / rate-limit
- bloquer l’IP (iptables / ipset)
- notifier Telegram
- journaliser

**Ce qu’il ne fait PAS :**

- ML
- UI
- accès DB applicative
- auth utilisateur

------

# 3️⃣ API SOAR 

### Endpoint unique

```
POST /alert
```

### Payload envoyé par Flask

```json
{
  "secret": "WEBHOOK_SECRET",
  "src_ip": "104.18.32.47",
  "verdict": "DDoS",
  "probability": 0.38,
  "flow_id": 164,
  "timestamp": "2025-12-13 11:24:58"
}
```

------

# 4️⃣ Code SOAR – structure interne

## `soar/app/main.py`

```python
from flask import Flask, request, jsonify
from blocker import block_ip
from telegram import send_telegram
from whitelist import is_whitelisted
import json, os

app = Flask(__name__)

CONFIG_PATH = "/soar/config/config.json"
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

@app.route("/alert", methods=["POST"])
def alert():
    data = request.json

    if not data or data.get("secret") != CONFIG["security"]["webhook_secret"]:
        return jsonify({"error": "unauthorized"}), 401

    src_ip = data.get("src_ip")
    verdict = data.get("verdict")

    if verdict != "DDoS" or not src_ip:
        return jsonify({"status": "ignored"})

    wl, rule = is_whitelisted(src_ip, CONFIG["security"]["whitelist_ips"])
    if wl:
        send_telegram(f"IP {src_ip} whitelistée ({rule}) – pas de blocage", CONFIG)
        return jsonify({"status": "whitelisted"})

    if block_ip(src_ip):
        send_telegram(
            f"🚨 IP BLOQUÉE\nIP: {src_ip}\nProb: {data.get('probability')}",
            CONFIG
        )
        return jsonify({"status": "blocked"})

    return jsonify({"status": "failed"}), 500
```

------

## `soar/app/blocker.py`

```python
import subprocess
import logging

def block_ip(ip):
    try:
        subprocess.run(
            ["iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"],
            check=True
        )
        logging.info(f"IP bloquée: {ip}")
        return True
    except Exception as e:
        logging.error(f"Erreur blocage {ip}: {e}")
        return False
```

------

## `soar/app/telegram.py`

```python
import requests

def send_telegram(msg, config):
    token = config["telegram"]["bot_token"]
    chat_id = config["telegram"]["chat_id"]

    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": msg},
        timeout=10
    )
```

------

## `soar/app/whitelist.py`

```python
def is_whitelisted(ip, whitelist):
    for w in whitelist:
        if ip.startswith(w.rstrip(".")):
            return True, w
    return False, None
```

------

# 5️⃣ Dockerfile SOAR

## `soar/Dockerfile`

```dockerfile
FROM python:3.11-slim

RUN apt update && apt install -y iptables && rm -rf /var/lib/apt/lists/*

WORKDIR /soar

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY config/ config/

EXPOSE 6000

CMD ["python", "app/main.py"]
```

------

## `soar/requirements.txt`

```
flask
requests
```

------

# 6️⃣ docker-compose.yml

```yaml
services:
  web:
    build: ./capture
    ports:
      - "5500:5500"
    depends_on:
      - db
      - soar

  soar:
    build: ./soar
    container_name: soar
    privileged: true
    ports:
      - "6000:6000"
    volumes:
      - ./soar/logs:/var/log/soar

  db:
    image: mysql:8
    ...
```

⚠️ `privileged: true` **uniquement pour SOAR**
Jamais pour Flask.

------

# 7️⃣ Changement côté Flask (1 seul endroit)

Dans l'orchestrateur / insertion flow :

```python
import requests

def notify_soar(flow):
    if flow["verdict"] != "DDoS":
        return

    requests.post(
        "http://soar:6000/alert",
        json={
            "secret": os.getenv("SOAR_SECRET"),
            "src_ip": flow["src_ip"],
            "verdict": flow["verdict"],
            "probability": flow["probability"],
            "flow_id": flow["id"],
            "timestamp": flow["timestamp"]
        },
        timeout=2
    )
```

Appelé **après insertion DB**, jamais avant.

------

# 8️⃣ Pourquoi cette architecture est solide

- isolation des privilèges
- SOAR redémarrable indépendamment
- facile à tester (`curl`)
- évolutif vers ipset / nftables
- compatible ElastAlert2 plus tard
- production-ready

------

# 9️⃣ 

**Notes :** 

| Élément          | Où                  |
| ---------------- | ------------------- |
| Telegram token   | `.env`              |
| Telegram chat id | `.env`              |
| Webhook secret   | `.env`              |
| Whitelist IPs    | `.env`              |
| Mode de blocage  | `config.json`       |
| Secrets          | **JAMAIS dans Git** |



## Pour vérifier que ce micro-service fonctionne : 

docker build -t soar .

docker run -d \
  -p 6000:6000 \
  --name soar \
  --env-file ../.env \
  --cap-add NET_ADMIN \
  soar



## Étape suivante immédiate : tester le SOAR pour de vrai

### 1️⃣ Vérifie que le port écoute

Sur la machine hôte :

```bash
ss -tulpen | grep 6000
```

Tu dois voir Flask écouter sur `0.0.0.0:6000`.

------

### 2️⃣ Test du webhook (le plus important)

Depuis ta machine hôte :

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

### Résultat attendu

```bash
{"status":"blocked"}
```

Et dans les logs :

```bash
docker logs -f soar
```

Tu dois voir :

- message de blocage
- tentative iptables
- envoi Telegram

------

## Vérifier que l’IP est réellement bloquée

Dans le conteneur :

```bash
docker exec -it soar sh
iptables -L INPUT -n --line-numbers
```

Tu dois voir une règle :

```less
Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination         
1    DROP       all  --  8.8.8.8              0.0.0.0/0 
```

------

## Tester la whitelist

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

```less
{"status":"whitelisted"}
```

Et **aucune règle iptables ajoutée**.



```pgsql
[ Orchestrator ]
   |
   |  POST /alert (JSON + secret)
   v
[ SOAR Service ]  --> iptables / ipset
        |
        +--> Telegram

```

```yaml
ML → verdict = DDoS ?
        |
        v
     SOAR
        |
        v
Décision finale (Blocked / Passed / Whitelisted)
        |
        v
Insertion DB

```

```pgsql
┌──────────────┐
│ Realtime Cap │
└──────┬───────┘
       │
       v
┌──────────────┐
│ Orchestrator │  (ML only)
│  - capture   │
│  - inference │
└──────┬───────┘
       │ POST /alert
       v
┌──────────────┐
│     SOAR     │  (Decision engine)
│ - whitelist  │
│ - block IP   │
│ - notify     │
└──────┬───────┘
       │ JSON response
       v
┌──────────────┐
│   Database   │  (truth)
└──────────────┘
```



```less
PACKET
  ↓
ML verdict = DDoS
  ↓
CALL SOAR
  ↓
SOAR:
  - whitelist ?
  - block ?
  ↓
decision = Blocked | Passed
  ↓
INSERT INTO flows (action = decision)

```

```objective-c
CAPTURE → ML → ORCHESTRATEUR → SOAR → ACTION → DB
```

