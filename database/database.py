import MySQLdb.cursors
import os

mysql_instance = None

def init_mysql(mysql):
    """Initialise la connexion MySQL depuis Flask"""
    global mysql_instance
    mysql_instance = mysql


def get_db_connection():
    """Retourne la connexion MySQL depuis Flask-MySQLdb"""
    if mysql_instance is None:
        raise RuntimeError("MySQL n'est pas initialisé.")
    return mysql_instance.connection


def init_db():
    """Création de la table flows pour le projet DDoS detection"""
    try:
        cur = mysql_instance.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS flows (
                id INT AUTO_INCREMENT PRIMARY KEY,
                src_ip VARCHAR(45),
                dst_ip VARCHAR(45),
                src_port INT,
                dst_port INT,
                prediction INT,
                verdict ENUM('Benign', 'DDoS') NOT NULL,
                probability FLOAT NULL,
                threshold FLOAT NULL,
                action ENUM('Passed', 'Blocked') NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                INDEX idx_timestamp (timestamp),
                INDEX idx_verdict (verdict),
                INDEX idx_action (action)
            ) ENGINE=InnoDB 
              DEFAULT CHARSET=utf8mb4 
              COLLATE=utf8mb4_unicode_ci
        ''')
        
        mysql_instance.connection.commit()
        cur.close()
        print("[DB] Table 'flows' créée ou déjà existante.")
    except Exception as e:
        print(f"[DB ERROR] Erreur lors de la création de la table flows : {e}")


def execute_query(query, params=(), fetch=False):
    """Exécute une requête SQL générique"""
    if mysql_instance is None:
        print("[DB ERROR] MySQL n'est pas initialisé.")
        return [] if fetch else None
    
    try:
        cur = mysql_instance.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(query, params)
        mysql_instance.connection.commit()

        if fetch:
            result = cur.fetchall()
            cur.close()
            return result
        
        cur.close()
    except Exception as e:
        print(f"[DB ERROR] Erreur requête SQL : {e}")
        return [] if fetch else None


def insert_flow(flow):
    """
    Insère dans la DB un flow venant de l'orchestrateur :
    {
        "src_ip": "192.168.1.81",
        "dst_ip": "142.250.69.106",
        "src_port": 42800,
        "dst_port": 443,
        "prediction": 0,
        "verdict": "Benign",
        "probability": 0.0002854558697436005,
        "threshold": 0.11374477,
        "action": "Passed"
    }
    """
    query = '''
        INSERT INTO flows (src_ip, dst_ip, src_port, dst_port, prediction, verdict, probability, threshold, action)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    params = (
        flow.get("src_ip"),
        flow.get("dst_ip"),
        flow.get("src_port"),
        flow.get("dst_port"),
        flow.get("prediction"),
        flow.get("verdict"),
        flow.get("probability"),
        flow.get("threshold"),
        flow.get("action"), 
    )
    try:
        execute_query(query, params)
        print(f"[DB] Flow enregistré: {flow.get('src_ip')} → {flow.get('dst_ip')} ({flow.get('verdict')})")
    except Exception as e:
        print(f"[DB ERROR] Erreur insertion flow : {e}")
        print(f"[DB ERROR] Flow problématique : {flow}")


def get_last_flows(limit=100):
    """Retourne les derniers flows pour l'interface web"""
    query = "SELECT * FROM flows ORDER BY timestamp DESC LIMIT %s"
    return execute_query(query, (limit,), fetch=True)


def ensure_db_initialized():
    """Initialisation automatique"""
    if mysql_instance is not None:
        init_db()
    else:
        print("[DB WARNING] MySQL instance non disponible pour l'initialisation.")