# Capture & Orchestrator — Détection DDoS en temps réel

Cette partie du projet correspond au **cœur temps réel** du système :
- capture du trafic réseau
- reconstruction des flux
- extraction de features
- inférence ML
- décision SOAR
- persistance en base

Elle fonctionne **en continu**, au niveau réseau, et alimente tout le reste du système.

---

## Rôle global

Le module `capture` agit comme un **orchestrateur intelligent** entre :

1. le trafic réseau réel
2. le moteur de features (CICFlowMeter-like)
3. le modèle ML
4. le SOAR
5. la base de données

Il ne décide jamais seul :  
👉 **il observe, analyse, prédit, transmet, applique la décision.**

---

## Point d’entrée principal

```bash
python -m capture.orchestrator_prediction
```

C’est aussi la commande utilisée dans le Dockerfile.

------

## Structure des fichiers

```
capture/
├── orchestrator_prediction.py   # Orchestrateur principal
├── realtime_capture.py          # Capture réseau live (Scapy)
├── flow_parser.py               # Reconstruction des flows + features
└── requirements.txt
```

------

## Dockerfile (vue d’ensemble)

Le conteneur est construit pour :

- capturer du trafic réel
- exécuter du ML
- accéder à MySQL
- communiquer avec le SOAR

Fonctionnalités clés :

- Scapy + libpcap
- MySQL client
- outils réseau (`iproute2`, `net-tools`)
- modèle ML + pipeline préchargés

Commande finale :

```dockerfile
CMD ["python", "-m", "capture.orchestrator_prediction"]
```

------

## 1. RealtimeCapture — Capture réseau

**Fichier :** `realtime_capture.py`

### Rôle

- écouter le trafic réseau en temps réel
- parser les paquets IP / TCP / UDP
- transmettre les paquets au FlowParser

### Choix techniques

- Scapy (`sniff`)
- capture directe sur interface réseau
- compatible Kubernetes (DaemonSet + hostNetwork)

### Variables importantes

- `interface` : interface réseau à écouter (ex: `eth0`)
- `flow_timeout` : expiration d’un flow inactif

------

## 2. FlowParser — Reconstruction des flux

**Fichier :** `flow_parser.py`

### Rôle

- regrouper les paquets en flows (5-tuple)
- gérer les directions (forward / backward)
- détecter la fin des flows (FIN / RST / timeout)
- calculer les statistiques réseau

### Fonctionnement

- un flow est identifié par :

```
src_ip:src_port → dst_ip:dst_port + protocole
```

- un flow est terminé quand :
  - FIN ou RST TCP
  - ou inactivité > timeout

------

## 3. Extraction des features

Les features générées sont **alignées avec CICFlowMeter**.

Catégories principales :

- durée du flow
- tailles de paquets
- inter-arrival times (IAT)
- statistiques forward / backward
- flags TCP
- taux (packets/s, bytes/s)
- activité / inactivité

👉 Le dictionnaire final contient **toutes les features nécessaires au modèle ML**, même si certaines sont mises à `0` pour rester compatibles.

------

## 4. OrchestratorPrediction — Cerveau du module

**Fichier :** `orchestrator_prediction.py`

### Rôle central

- reçoit les features d’un flow terminé
- normalise les données
- lance l’inférence ML
- appelle le SOAR si nécessaire
- écrit le résultat en base

------

## 5. Pipeline ML

### Étapes

1. features du flow → JSON
2. appel du script d’inférence :

```bash
python inference/predict.py --json "<features>"
```

1. récupération :
   - prediction (0 / 1)
   - verdict (Benign / DDoS)
   - probabilité
   - seuil

------

## 6. Intégration SOAR

### Quand le SOAR est appelé ?

Uniquement si :

```
verdict == "DDoS"
```

### Données envoyées

```json
{
  "secret": "...",
  "src_ip": "...",
  "verdict": "DDoS",
  "probability": 0.92
}
```

### Réponse possible du SOAR

- `blocked` → action = Blocked
- `passed` → action = Passed
- erreur → Passed par sécurité

👉 **Le SOAR est l’unique autorité de blocage.**

------

## 7. Insertion en base MySQL

Chaque flow analysé est stocké avec :

- IP source / destination
- ports
- verdict ML
- probabilité
- action finale (Passed / Blocked)
- timestamp

Table ciblée :

```
flows
```

Cela permet :

- audit
- visualisation
- analyse post-incident

------

## Variables d’environnement utilisées

| Variable            | Rôle                  |
| ------------------- | --------------------- |
| CAPTURE_INTERFACE   | Interface réseau      |
| SOAR_URL            | Endpoint SOAR         |
| SOAR_WEBHOOK_SECRET | Authentification SOAR |
| DB_HOST             | Hôte MySQL            |
| DB_PORT             | Port MySQL            |
| DB_USER             | Utilisateur           |
| DB_PASSWORD         | Mot de passe          |
| DB_DATABASE         | Base de données       |

------

## Choix d’architecture assumés

- Capture réseau bas niveau (Scapy)
- DaemonSet Kubernetes
- Séparation claire :
  - capture
  - features
  - ML
  - décision
- Aucun blocage direct depuis l’orchestrator
- Tout est traçable en base

------

## Limites actuelles

- Pas de buffering distribué
- Un modèle ML unique
- Pas de batching des flows
- Pas de persistance locale en cas de crash

------

## Perspectives d’évolution

- Support multi-modèles
- Feature selection dynamique
- Envoi asynchrone vers le SOAR
- File de messages (Kafka / Redis)
- Enrichissement GeoIP / ASN
- Optimisation perf (Cython / Rust)

------

## Résumé

Ce module est **le lien vital** entre :

- le réseau réel
- l’intelligence artificielle
- la réponse automatique

Sans lui :
👉 pas de détection temps réel
👉 pas de décision
👉 pas de SOAR

C’est le **nerf du système**.

