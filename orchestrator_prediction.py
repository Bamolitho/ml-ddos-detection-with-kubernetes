#!/usr/bin/env python3
import subprocess
import json
import sys
from capture.realtime_capture import RealtimeCapture


# ======================================================================
# LISTE DES FEATURES CICFlowMeter (87 colonnes)
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
# NORMALISATION
# ======================================================================
def normalize_flow_dict(flow):
    return {col: flow.get(col, 0) for col in CICFLOWMETER_FEATURES}


# ======================================================================
# ORCHESTRATEUR 
# ======================================================================
class OrchestratorPredictionV2:

    def __init__(self, interface="wlp2s0"):
        self.interface = interface
        self.capture = RealtimeCapture(interface=self.interface)
        self.capture.flow_callback = self.handle_flow

    # ------------------------------------------------------------------
    def handle_flow(self, flow_features):

        normalized = normalize_flow_dict(flow_features)
        json_input = json.dumps(normalized)

        # cmd = [
        #     "/home/ing/amomo_venv/bin/python3",
        #     "inference/predict.py",
        #     "--json", json_input
        # ]
        cmd = [
            sys.executable,
            "inference/predict.py",
            "--json", json_input
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

            threshold = prediction_json.get("threshold", None)

            pred_entry = prediction_json["results"][0]

            verdict = pred_entry["verdict"]
            probability = pred_entry["probability"]
            pred_int = pred_entry["prediction"]

            # Action dictée par le modèle (pas ton orchestrateur)
            action = "Blocked" if pred_int == 1 else "Passed"

            packet_web_ready = {
                "src_ip": flow_features.get("Source IP"),
                "dst_ip": flow_features.get("Destination IP"),
                "src_port": flow_features.get("Source Port"),
                "dst_port": flow_features.get("Destination Port"),
                "prediction": pred_int,
                "verdict": verdict,
                "probability": probability,
                "threshold": threshold,
                "action": action
            }

            print("\n=== PACKET ===")
            print(json.dumps(packet_web_ready, indent=4))

            # --- Enregistrement DB ---
            try:
                from database.database import insert_flow
                insert_flow(packet_web_ready)
                print("[DB] Flow enregistré en base.")
            except Exception as e:
                print(f"[DB ERROR] Impossible d'enregistrer le flow : {e}")

            # print("\n=== UI OUTPUT ===")
            # print(json.dumps({
            #     "source_ip": packet_web_ready["source_ip"],
            #     "destination_ip": packet_web_ready["destination_ip"],
            #     "source_port": packet_web_ready["source_port"],
            #     "destination_port": packet_web_ready["destination_port"],
            #     "verdict": verdict,
            #     "probability": probability,
            #     "action": action
            # }, indent=2))

        except Exception as e:
            print("ERREUR lors de l'appel predict.py:", e)

    # ------------------------------------------------------------------
    def start(self):
        print(f"--- ORCHESTRATEUR V2 EN MARCHE SUR : {self.interface} ---")
        self.capture.start()


# ======================================================================
# MAIN
# ======================================================================
if __name__ == "__main__":
    orch = OrchestratorPredictionV2("wlp2s0")
    orch.start()
