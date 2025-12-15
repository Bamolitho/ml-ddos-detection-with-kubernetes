from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import io
import json
#import sys
import os
import requests
from datetime import datetime

# Import du module database
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
from database.database import init_mysql, ensure_db_initialized

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret')

# =============================
# CONFIG MYSQL
# =============================
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'db')
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('DB_NAME', 'ddos_detection')
app.config['MYSQL_CHARSET'] = 'utf8mb4'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', '3306'))

mysql = MySQL(app)

# Initialiser le module database avec l'instance MySQL
with app.app_context():
    try:
        init_mysql(mysql)
        ensure_db_initialized()
    except Exception as e:
        print("[DB DISABLED]", e)

    # init_mysql(mysql)
    # ensure_db_initialized()

# =============================
# PAGE DE LOGIN
# =============================
@app.route("/", methods=["GET"])
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            session["user_id"] = user["id"]
            flash("Connexion réussie !", "success")
            return redirect(url_for("dashboard"))

        flash("Identifiants incorrects", "error")
        return render_template("login.html")

    return render_template("login.html")

# =============================
# PAGE D'INSCRIPTION
# =============================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for("login"))
        except:
            flash("Nom d'utilisateur déjà utilisé.", "error")
            return render_template("register.html")
        finally:
            cur.close()

    return render_template("register.html")

# =============================
# DASHBOARD PRINCIPAL
# =============================
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

# =============================
# CHANGER MOT DE PASSE
# =============================
@app.route("/changer-mot-de-passe", methods=["GET", "POST"])
def changer_mot_de_passe():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        old = request.form["old_password"]
        new = request.form["new_password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE id = %s", (session["user_id"],))
        user = cur.fetchone()

        if not user or not check_password_hash(user["password"], old):
            flash("Ancien mot de passe incorrect.", "error")
            cur.close()
            return render_template("changer_mot_de_passe.html")

        cur.execute("UPDATE users SET password = %s WHERE id = %s",
                    (generate_password_hash(new), session["user_id"]))
        mysql.connection.commit()
        cur.close()

        flash("Mot de passe modifié avec succès !", "success")
        return redirect(url_for("dashboard"))

    return render_template("changer_mot_de_passe.html")

# =============================
# SUPPRESSION DE COMPTE
# =============================
@app.route("/supprimer-compte", methods=["POST"])
def supprimer_compte():
    if "user_id" not in session:
        return redirect(url_for("login"))

    password = request.form.get("password")
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()
    
    if not user or not check_password_hash(user["password"], password):
        flash("Mot de passe incorrect.", "error")
        cur.close()
        return redirect(url_for("dashboard"))
    
    cur.execute("DELETE FROM users WHERE id = %s", (session["user_id"],))
    mysql.connection.commit()
    cur.close()

    session.clear()
    flash("Votre compte a été supprimé.", "success")
    return redirect(url_for("register"))

# =============================
# API – DONNÉES DES FLOWS
# =============================
@app.route("/flows_json")
def flows_json():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT
                DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') AS timestamp,
                src_ip,
                dst_ip,
                src_port,
                dst_port,
                verdict,
                probability,
                action
            FROM flows
            ORDER BY timestamp DESC
            LIMIT 500
        """)
        rows = cur.fetchall()
        cur.close()
        
        print(f"[OK] API /flows_json : {len(rows)} flows retournés")
        return jsonify(rows)
    except Exception as e:
        print(f"[FAILED] Erreur API /flows_json: {e}")
        return jsonify({"error": str(e)}), 500

# =============================
# EXPORT CSV
# =============================
@app.route("/export_flows_csv")
def export_flows_csv():
    if "user_id" not in session:
        flash("Connexion requise.", "error")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM flows ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()

    proxy = io.StringIO()

    if not rows:
        fieldnames = [
            "timestamp", "src_ip", "dst_ip", "src_port",
            "dst_port", "verdict", "probability", "action"
        ]
        writer = csv.DictWriter(proxy, fieldnames=fieldnames)
        writer.writeheader()
    else:
        writer = csv.DictWriter(proxy, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode("utf-8"))
    mem.seek(0)
    proxy.close()

    return send_file(
        mem,
        as_attachment=True,
        download_name="flows.csv",
        mimetype="text/csv"
    )

# =============================
# EXPORT JSON
# =============================
@app.route("/export_flows_json")
def export_flows_json():
    if "user_id" not in session:
        flash("Connexion requise.", "error")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM flows ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()

    # Convertir les datetime en string
    for row in rows:
        if 'timestamp' in row and isinstance(row['timestamp'], datetime):
            row['timestamp'] = row['timestamp'].isoformat()

    mem = io.BytesIO(json.dumps(rows, indent=4, default=str).encode("utf-8"))
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name="flows.json", mimetype="application/json")

# =============================
# STATISTIQUES - PAGE HTML
# =============================
@app.route("/calculer_stats")
def calculer_stats():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    return render_template("stats.html")

# =============================
# STATISTIQUES - API JSON (temps réel)
# =============================
@app.route("/stats_json")
def stats_json():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        cur = mysql.connection.cursor()

        # Total
        cur.execute("SELECT COUNT(*) AS total FROM flows")
        total = cur.fetchone()["total"]

        # Benign
        cur.execute("SELECT COUNT(*) AS benign FROM flows WHERE verdict = 'Benign'")
        benign = cur.fetchone()["benign"]

        # DDoS
        cur.execute("SELECT COUNT(*) AS ddos FROM flows WHERE verdict = 'DDoS'")
        ddos = cur.fetchone()["ddos"]

        # Bloqués
        cur.execute("SELECT COUNT(*) AS blocked FROM flows WHERE action = 'Blocked'")
        blocked = cur.fetchone()["blocked"]

        # Vrai Positif : DDoS + Blocked
        cur.execute("SELECT COUNT(*) AS ddos_blocked FROM flows WHERE verdict = 'DDoS' AND action = 'Blocked'")
        ddos_blocked = cur.fetchone()["ddos_blocked"]

        # Faux Positif : DDoS + Passed (DDoS NON bloqué - détection ratée)
        cur.execute("SELECT COUNT(*) AS ddos_passed FROM flows WHERE verdict = 'DDoS' AND action = 'Passed'")
        ddos_passed = cur.fetchone()["ddos_passed"]

        # Vrai Négatif : Benign + Passed
        cur.execute("SELECT COUNT(*) AS benign_passed FROM flows WHERE verdict = 'Benign' AND action = 'Passed'")
        benign_passed = cur.fetchone()["benign_passed"]

        # Faux Négatif : Benign + Blocked (trafic légitime bloqué à tort)
        cur.execute("SELECT COUNT(*) AS benign_blocked FROM flows WHERE verdict = 'Benign' AND action = 'Blocked'")
        benign_blocked = cur.fetchone()["benign_blocked"]

        cur.close()

        stats = {
            "total": total,
            "benign": benign,
            "ddos": ddos,
            "blocked": blocked,
            "ddos_blocked": ddos_blocked,    # Vrai Positif (VP)
            "ddos_passed": ddos_passed,      # Faux Positif (FP) - DDoS non bloqué
            "benign_passed": benign_passed,  # Vrai Négatif (VN)
            "benign_blocked": benign_blocked # Faux Négatif (FN) - Benign bloqué
        }

        print(f"[OK] API /stats_json : {stats}")
        return jsonify(stats)
    except Exception as e:
        print(f"[FAILED] Erreur API /stats_json: {e}")
        return jsonify({"error": str(e)}), 500

# =============================
# LOGOUT
# =============================
@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnexion réussie.", "success")
    return redirect(url_for("login"))

# =============================
# SOAR UTILITIES
# =============================
def notify_soar(flow):
    """Notifie le système SOAR en cas de détection DDoS"""
    if flow["verdict"] != "DDoS":
        return

    try:
        response = requests.post(
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
        print(f"[SOAR] Notification envoyée : {response.status_code}")
    except Exception as e:
        print(f"[SOAR] Erreur notification: {e}")

# =============================
# HEALTH CHECK
# =============================
@app.route("/health")
def health():
    return "ok", 200

# =============================
# MAIN
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)