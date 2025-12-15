from flask import Flask, request, jsonify
import os
import json
import logging

from blocker import block_ip
from telegram import send_telegram
from whitelist import is_whitelisted

# =============================
# CONSTANTES SOAR
# =============================
SOAR_MIN_PROBABILITY = float(os.getenv("SOAR_MIN_PROBABILITY", 0.8))

# =============================
# ENV (SECRETS)
# =============================
WEBHOOK_SECRET = os.getenv("SOAR_WEBHOOK_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

WHITELIST_ENV = os.getenv("SOAR_WHITELIST_IPS", "")
WHITELIST_IPS = [ip.strip() for ip in WHITELIST_ENV.split(",") if ip.strip()]

if not WEBHOOK_SECRET:
    raise RuntimeError("Missing SOAR_WEBHOOK_SECRET")

# =============================
# PATHS
# =============================
CONFIG_PATH = "/soar/config/config.json"
LOG_DIR = "/var/log/soar"
LOG_FILE = f"{LOG_DIR}/soar.log"

# =============================
# LOGGING
# =============================
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("soar")
logger.info("SOAR service starting")

# =============================
# LOAD CONFIG
# =============================
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

BLOCKING_METHOD = CONFIG.get("blocking", {}).get("method", "iptables")
logger.info(f"Blocking method: {BLOCKING_METHOD}")
logger.info(f"SOAR min probability: {SOAR_MIN_PROBABILITY}")

# =============================
# FLASK APP
# =============================
app = Flask(__name__)

# =============================
# ROUTES
# =============================
@app.route("/alert", methods=["POST"])
def alert():
    data = request.get_json()
    if not data:
        return jsonify({"status": "invalid_payload"}), 400

    # --- AUTH ---
    if data.get("secret") != WEBHOOK_SECRET:
        logger.warning("Unauthorized webhook")
        return jsonify({"status": "unauthorized"}), 401

    src_ip = data.get("src_ip")
    verdict = data.get("verdict")
    probability = float(data.get("probability", 0))

    # --- SANITY ---
    if not src_ip or verdict != "DDoS":
        return jsonify({"status": "ignored"})

    # --- LOW CONFIDENCE ---
    if probability < SOAR_MIN_PROBABILITY:
        logger.info(
            f"Low confidence DDoS {src_ip} "
            f"(prob={probability}) → passed"
        )
        return jsonify({"status": "passed"})

    # --- WHITELIST ---
    is_wl, rule = is_whitelisted(src_ip, WHITELIST_IPS)
    if is_wl:
        logger.info(f"Whitelisted IP {src_ip} ({rule})")
        return jsonify({"status": "passed"})

    # --- BLOCKING ---
    if BLOCKING_METHOD == "iptables":
        success = block_ip(src_ip)
    elif BLOCKING_METHOD == "log":
        logger.warning(f"[DEV] DDoS détecté sur {src_ip}")
        success = True
    else:
        logger.error(f"Unknown blocking method: {BLOCKING_METHOD}")
        return jsonify({"status": "failed"}), 500
    
    if success:
        msg = (
            "🚨 IP BLOQUÉE 🚨\n\n"
            f"IP: {src_ip}\n"
            f"Probabilité: {probability}\n"
            f"Méthode: {BLOCKING_METHOD}"
        )
        logger.warning(msg)
        send_telegram(msg)
        return jsonify({"status": "blocked"})

    # --- FAILURE ---
    logger.error(f"Blocking failed for {src_ip}")
    send_telegram(f"⚠️ Blocage échoué pour {src_ip}")
    return jsonify({"status": "failed"}), 500


# =============================
# HEALTHCHECK
# =============================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# =============================
# MAIN
# =============================
if __name__ == "__main__":
    logger.info("SOAR service started on port 6000")
    app.run(host="0.0.0.0", port=6000)
