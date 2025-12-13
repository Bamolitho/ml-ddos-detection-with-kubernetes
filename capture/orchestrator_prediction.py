#!/usr/bin/env python3
import subprocess
import json
import sys
import os
import mysql.connector
import requests

from capture.realtime_capture import RealtimeCapture

# ======================================================================
# MYSQL
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
# CICFLOWMETER FEATURES (STRICT ORDER)
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

def normalize_flow_dict(flow):
    return {col: flow.get(col, 0) for col in CICFLOWMETER_FEATURES}

# ======================================================================
# ORCHESTRATOR
# ======================================================================

class OrchestratorPrediction:

    def __init__(self, interface="wlp2s0"):
        self.interface = interface
        self.capture = RealtimeCapture(interface=self.interface)
        self.capture.flow_callback = self.handle_flow

        self.soar_url = os.getenv("SOAR_URL", "http://127.0.0.1:6000/alert")
        self.soar_secret = os.getenv("SOAR_WEBHOOK_SECRET")

        if not self.soar_secret:
            raise RuntimeError("SOAR_WEBHOOK_SECRET missing")

        print("[OK] Orchestrator ready")
        print("[OK] Interface :", self.interface)
        print("[OK] SOAR URL  :", self.soar_url)

    # ------------------------------------------------------------------
    def call_soar(self, packet):
        try:
            resp = requests.post(
                self.soar_url,
                json={
                    "secret": self.soar_secret,
                    "src_ip": packet["src_ip"],
                    "verdict": packet["ml_verdict"],
                    "probability": packet["probability"]
                },
                timeout=3
            )

            if resp.status_code != 200:
                return "Passed", "soar_http_error"

            status = resp.json().get("status", "ignored")

            if status == "blocked":
                return "Blocked", "soar_blocked"

            return "Passed", "soar_passed"

        except Exception:
            return "Passed", "soar_unreachable"

    # ------------------------------------------------------------------
    def handle_flow(self, flow_features):

        normalized = normalize_flow_dict(flow_features)
        json_input = json.dumps(normalized)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cmd = [
            sys.executable,
            os.path.join(base_dir, "inference/predict.py"),
            "--json",
            json_input
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if not result.stdout.strip():
            return

        prediction_json = json.loads(result.stdout)
        pred = prediction_json["results"][0]

        packet = {
            "src_ip": flow_features.get("Source IP"),
            "dst_ip": flow_features.get("Destination IP"),
            "src_port": flow_features.get("Source Port"),
            "dst_port": flow_features.get("Destination Port"),

            # ML output (IMMUTABLE)
            "prediction": pred["prediction"],
            "ml_verdict": pred["verdict"],
            "probability": pred["probability"],
            "threshold": prediction_json.get("threshold"),

            # SOAR decision
            "action": "Passed",
            "decision_source": "ml_only"
        }

        # ==============================================================
        # SOAR DECISION
        # ==============================================================

        if packet["ml_verdict"] == "DDoS":
            action, source = self.call_soar(packet)
            packet["action"] = action
            packet["decision_source"] = source

        print("\n=== FLOW FINAL ===")
        print(json.dumps(packet, indent=4))

        self.insert_flow_db(packet)

    # ------------------------------------------------------------------
    def insert_flow_db(self, packet):
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO flows
                (timestamp, src_ip, dst_ip, src_port, dst_port,
                 prediction, verdict, probability, threshold,
                 action)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    packet["src_ip"],
                    packet["dst_ip"],
                    packet["src_port"],
                    packet["dst_port"],
                    packet["prediction"],
                    packet["ml_verdict"],
                    packet["probability"],
                    packet["threshold"],
                    packet["action"]
                )
            )

            cur.close()
            conn.close()

        except Exception as e:
            print("[DB ERROR]", e)

    # ------------------------------------------------------------------
    def start(self):
        print(f"\n--- ORCHESTRATOR ACTIVE ON {self.interface} ---\n")
        self.capture.start()

# ======================================================================
# MAIN
# ======================================================================

if __name__ == "__main__":
    orch = OrchestratorPrediction(interface="wlp2s0")
    orch.start()
