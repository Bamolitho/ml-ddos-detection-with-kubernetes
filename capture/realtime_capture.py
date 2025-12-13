#!/usr/bin/env python3
import time
from scapy.all import sniff, IP, TCP, UDP
from capture.flow_parser import FlowParser

class RealtimeCapture:

    def __init__(self, interface="eth0", flow_timeout=10):
        self.interface = interface
        self.flow_timeout = flow_timeout
        self.parser = FlowParser(flow_timeout=flow_timeout)

        # === callback externe (orchestrateur) ===
        self.flow_callback = None

    def parse_packet(self, pkt):
        if IP not in pkt:
            return None

        ip = pkt[IP]
        transport = None
        proto = None

        if TCP in pkt:
            transport = pkt[TCP]
            proto = 6
        elif UDP in pkt:
            transport = pkt[UDP]
            proto = 17
        else:
            return None

        flags = {"fin": 0, "syn": 0, "rst": 0, "psh": 0, "ack": 0, "urg": 0}
        if proto == 6 and hasattr(transport, "flags"):
            f = transport.flags
            flags["fin"] = int("F" in str(f))
            flags["syn"] = int("S" in str(f))
            flags["rst"] = int("R" in str(f))
            flags["psh"] = int("P" in str(f))
            flags["ack"] = int("A" in str(f))
            flags["urg"] = int("U" in str(f))

        return {
            "timestamp": getattr(pkt, "time", time.time()),
            "src_ip": ip.src,
            "dst_ip": ip.dst,
            "src_port": int(getattr(transport, "sport", 0)),
            "dst_port": int(getattr(transport, "dport", 0)),
            "protocol": int(proto),
            "length": len(pkt),
            "flags": flags
        }

    def process_packet(self, pkt):
        parsed = self.parse_packet(pkt)
        if parsed is None:
            return

        terminated_by_packet = self.parser.add_packet(parsed) or []
        terminated_by_timeout = self.parser.expire_flows() or []
        terminated_flows = list(set(terminated_by_packet + terminated_by_timeout))

        for fid in terminated_flows:
            features = self.parser.finalize_flow(fid)
            if features is None:
                continue

            print("\n=== FLOW TERMINÉ ===")
            # for k, v in features.items():
            #     print(f"{k} : {v}")

            # === NOTIFICATION A L’ORCHESTRATEUR ===
            if self.flow_callback:
                self.flow_callback(features)

            self.parser.delete_flow(fid)

    def start(self):
        print(f"--- Capture temps réel sur interface : {self.interface} ---")
        sniff(
            iface=self.interface,
            prn=self.process_packet,
            store=False
        )

if __name__ == "__main__":
    cap = RealtimeCapture(interface="wlp2s0", flow_timeout=10)
    cap.start()
