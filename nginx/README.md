# Nginx — Reverse Proxy du service d’inférence

Ce répertoire contient la configuration **Nginx utilisée comme reverse proxy** devant l’application Flask d’inférence.

Son rôle est de :
- exposer un point d’entrée HTTP unique
- relayer les requêtes vers l’API Flask
- gérer les headers, timeouts et erreurs
- préparer une intégration propre en environnement conteneurisé

---

## Structure du répertoire

```
nginx/
└── conf.d/
└── default.conf
```

---

## default.conf

Fichier principal de configuration Nginx.

### Rôle

- écouter les requêtes entrantes
- rediriger le trafic vers l’application Flask
- assurer la transmission correcte des métadonnées réseau

---

## Détails de configuration

### Upstream Flask

```nginx
upstream flask_app {
    server app:5500;
}
```

- `app` : nom du service (Docker / Kubernetes)
- `5500` : port exposé par Flask
- permet une abstraction du backend applicatif

------

### Serveur HTTP

```nginx
server {
    listen 7500;
    server_name localhost;
}
```

- Nginx écoute sur le port **7500**
- point d’entrée externe du service d’inférence

------

### Logs

```nginx
access_log /var/log/nginx/access.log;
error_log /var/log/nginx/error.log;
```

- traçabilité des requêtes
- diagnostic des erreurs proxy / backend

------

### Taille maximale des requêtes

```nginx
client_max_body_size 10M;
```

- autorise l’envoi de payloads JSON ou CSV
- protège contre les abus et erreurs client

------

### Proxy vers Flask

```nginx
location / {
    proxy_pass http://flask_app;
}
```

Headers transmis :

- `Host`
- `X-Real-IP`
- `X-Forwarded-For`
- `X-Forwarded-Proto`

Ces headers sont essentiels pour :

- le logging applicatif
- la traçabilité réseau
- l’intégration avec des outils de sécurité

------

### Timeouts

```nginx
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

- protège contre les requêtes bloquées
- adapté aux traitements ML plus longs

------

### Gestion des erreurs

```nginx
error_page 500 502 503 504 /50x.html;
```

- pages d’erreur standardisées
- meilleure lisibilité côté client

------

## Qui fait quoi

- **Nginx**
  - reçoit les requêtes HTTP
  - applique les règles réseau
  - relaie vers Flask
- **Flask**
  - exécute l’inférence ML
  - retourne les prédictions

------

## Pourquoi ce design

- séparation claire entre réseau et logique ML
- configuration simple et lisible
- compatible Docker et Kubernetes
- facile à étendre (HTTPS, auth, rate limiting)

------

## Perspectives d’évolution

- ajout HTTPS (TLS)
- rate limiting anti-abus
- headers de sécurité (HSTS, CSP)
- load balancing multi-replicas
- intégration WAF ou IDS réseau

------

## Résumé

Le dossier `nginx/` fournit une **couche réseau propre, stable et extensible** pour exposer l’API d’inférence ML en production.