from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import io
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecret"

# =============================
# CONFIG MYSQL
# =============================
app.config["MYSQL_HOST"] = "mysql_db"
app.config["MYSQL_USER"] = "bank_user"
app.config["MYSQL_PASSWORD"] = "ddos_detection_"
app.config["MYSQL_DB"] = "ddos_detection"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

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
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Identifiants incorrects")

    return render_template("login.html")

# =============================
# PAGE D’INSCRIPTION
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
        except:
            return render_template("register.html", error="Nom d’utilisateur déjà utilisé.")
        finally:
            cur.close()

        return redirect(url_for("login"))

    return render_template("register.html")

# =============================
# DASHBOARD PRINCIPAL
# =============================
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["username"])

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

        if not check_password_hash(user["password"], old):
            return render_template("changer_mot_de_passe.html", error="Ancien mot de passe incorrect.")

        cur.execute("UPDATE users SET password = %s WHERE id = %s",
                    (generate_password_hash(new), session["user_id"]))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("dashboard"))

    return render_template("changer_mot_de_passe.html")

# =============================
# SUPPRESSION DE COMPTE
# =============================
@app.route("/supprimer-compte", methods=["POST"])
def supprimer_compte():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (session["user_id"],))
    mysql.connection.commit()
    cur.close()

    session.clear()
    return redirect(url_for("register"))

# =============================
# API – DONNÉES DES FLOWS
# =============================
@app.route("/flows_json")
def flows_json():
    cur = mysql.connection.cursor(dictionary=True)
    cur.execute("SELECT * FROM flows ORDER BY timestamp DESC LIMIT 500")
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)

# =============================
# EXPORT CSV
# =============================
@app.route("/export_flows_csv")
def export_flows_csv():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM flows ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()

    proxy = io.StringIO()

    # Cas table vide
    if not rows:
        # Définis les colonnes manuellement
        fieldnames = [
            "timestamp",
            "source_ip",
            "destination_ip",
            "source_port",
            "destination_port",
            "verdict",
            "probability",
            "action"
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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM flows ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()

    mem = io.BytesIO(json.dumps(rows, indent=4).encode("utf-8"))
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name="flows.json", mimetype="application/json")

# =============================
# STATISTIQUES SIMPLES
# =============================
@app.route("/calculer_stats")
def calculer_stats():
    stats = {}

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM flows")
    stats["total"] = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS benign FROM flows WHERE verdict = 'Benign'")
    stats["benign"] = cur.fetchone()["benign"]

    cur.execute("SELECT COUNT(*) AS ddos FROM flows WHERE verdict = 'DDoS'")
    stats["ddos"] = cur.fetchone()["ddos"]

    cur.execute("SELECT COUNT(*) AS blocked FROM flows WHERE action = 'Blocked'")
    stats["blocked"] = cur.fetchone()["blocked"]

    cur.close()

    return render_template("stats.html", stats=stats)

# =============================
# LOGOUT
# =============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =============================
# MAIN
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500)
