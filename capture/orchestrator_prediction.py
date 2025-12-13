#!/usr/bin/env python3
import subprocess
import json
import sys
import os
import mysql.connector
from capture.realtime_capture import RealtimeCapture

# ======================================================================
# CONFIGURATION MYSQL (SANS FLASK)
# ======================================================================

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_DATABASE", "ddos_detection"),
        autocommit=True
    )

# ======================================================================
# FEATURES CICFlowMeter (DOIT MATCHER LE MODELE)
# ======================================================================

CICFLOWMETER_FEATURES = [
    "Unnamed: 0","Flow ID","Source IP","Source Port","Destination IP","Destination Port",
    "Protocol","Timestamp","Flow Duration","Total Fwd Packets","Total Backward Packets",
    "Total Length of Fwd Packets","Total Length of Bwd Packets","Fwd Packet Length Max",
    "Fwd Packet Length Min","Fwd Packet Length Mean","Fwd Packet Length Std",
    "Bwd Packet Length Max","Bwd Packet Length Min","Bwd Packet Length Mean",
    "Bwd Packet Length Std","Flow Bytes/s","Flow Packets/s","Flow IAT Mean","Flow IAT Std",
    "Flow IAT Max","Flow IAT Min","Fwd IAT Total","Fwd IAT Mean","Fwd IAT Std","Fwd IAT Max",
    "Fwd IAT Min","Bwd IAT Total","Bwd IAT Mean","Bwd IAT Std","Bwd IAT Max","Bwd IAT Min",
    "Fwd PSH Flags","Bwd PSH Flags","Fwd URG Flags","Bwd URG Flags","Fwd Header Length",
    "Bwd Header Length","Fwd Packets/s","Bwd Packets/s","Min Packet Length","Max Packet Length",
    "Packet Length Mean","Packet Length Std","Packet Length Variance","FIN Flag Count",
    "SYN Flag Count","RST Flag Count","PSH Flag Count","ACK Flag Count","URG Flag Count",
    "CWE Flag Count","ECE Flag Count","Down/Up Ratio","Average Packet Size",
    "Avg Fwd Segment Size","Avg Bwd Segment Size","Fwd Header Length.1","Fwd Avg Bytes/Bulk",
    "Fwd Avg Packets/Bulk","Fwd Avg Bulk Rate","Bwd Avg Bytes/Bulk","Bwd Avg Packets/Bulk",
    "Bwd Avg Bulk Rate","Subflow Fwd Packets","Subflow Fwd Bytes","Subflow Bwd Packets",
    "Subflow Bwd Bytes","Init_Win_bytes_forward","Init_Win_bytes_backward","act_data_pkt_fwd",
    "min_seg_size_forward","Active Mean","Active Std","Active Max","Active Min","Idle Mean",
    "Idle Std","Idle Max","Idle Min","SimillarHTTP","Inbound"
]

# ======================================================================
# NORMALISATION DES FEATURES
# ======================================================================

def normalize_flow_dict(flow):
    return {col: flow.get(col, 0) for col in CICFLOWMETER_FEATURES}

# ======================================================================
# ORCHESTRATEUR
# ======================================================================

class OrchestratorPrediction:

    def __init__(self, interface="wlp2s0"):
        self.interface = interface
        self.capture = RealtimeCapture(interface=self.interface)
        self.capture.flow_callback = self.handle_flow

        print("[OK] Orchestrateur initialisé")
        print(f"[OK] Interface réseau : {self.interface}")

    # ------------------------------------------------------------------
    def handle_flow(self, flow_features):

        normalized = normalize_flow_dict(flow_features)
        json_input = json.dumps(normalized)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        cmd = [
            sys.executable,
            os.path.join(BASE_DIR, "inference/predict.py"),
            "--json",
            json_input
        ]

        try:
            result = subprocess.run(
                cmd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.stderr:
                print("ERREUR predict.py :", result.stderr)

            if not result.stdout.strip():
                print("Aucune sortie JSON reçue.")
                return

            prediction_json = json.loads(result.stdout)

            pred_entry = prediction_json["results"][0]

            verdict = pred_entry["verdict"]
            probability = pred_entry["probability"]
            prediction = pred_entry["prediction"]
            threshold = prediction_json.get("threshold")

            action = "Blocked" if prediction == 1 else "Passed"

            packet = {
                "src_ip": flow_features.get("Source IP"),
                "dst_ip": flow_features.get("Destination IP"),
                "src_port": flow_features.get("Source Port"),
                "dst_port": flow_features.get("Destination Port"),
                "prediction": prediction,
                "verdict": verdict,
                "probability": probability,
                "threshold": threshold,
                "action": action
            }

            print("\n=== FLOW ===")
            print(json.dumps(packet, indent=4))

            self.insert_flow_db(packet)

        except Exception as e:
            print("ERREUR orchestrateur :", e)

    # ------------------------------------------------------------------
    def insert_flow_db(self, packet):

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO flows
                (timestamp, src_ip, dst_ip, src_port,
                 dst_port, prediction, verdict, probability, threshold, action)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    packet["src_ip"],
                    packet["dst_ip"],
                    packet["src_port"],
                    packet["dst_port"],
                    packet["prediction"],
                    packet["verdict"],
                    packet["probability"],
                    packet["threshold"],
                    packet["action"]
                )
            )

            cur.close()
            conn.close()

            print("[DB] Flow enregistré")

        except Exception as e:
            print("[DB ERROR]", e)

    # ------------------------------------------------------------------
    def start(self):
        print(f"\n--- ORCHESTRATEUR EN MARCHE SUR {self.interface} ---\n")
        self.capture.start()

# ======================================================================
# MAIN
# ======================================================================

if __name__ == "__main__":
    orch = OrchestratorPrediction(interface="wlp2s0")
    orch.start()
