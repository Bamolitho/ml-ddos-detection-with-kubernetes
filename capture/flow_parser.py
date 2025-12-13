#!/usr/bin/env python3
import time
from collections import deque
from statistics import mean, pstdev

# -----------------------------
# Helper: safe statistics
# -----------------------------
def safe_mean(xs):
    return mean(xs) if len(xs) > 0 else 0.0

def safe_std(xs):
    return pstdev(xs) if len(xs) > 1 else 0.0

# -----------------------------
# Flow object (simplifié mais complet)
# -----------------------------
class Flow:
    def __init__(self, src_ip, src_port, dst_ip, dst_port, proto, first_ts):
        # identifiers
        self.src_ip = src_ip
        self.src_port = int(src_port)
        self.dst_ip = dst_ip
        self.dst_port = int(dst_port)
        self.proto = int(proto)

        # timestamps and packet lists
        self.first_time = first_ts
        self.last_seen = first_ts
        self.fwd_ts = []
        self.bwd_ts = []
        self.fwd_sizes = []
        self.bwd_sizes = []

        # flags count (TCP)
        self.fin_count = 0
        self.syn_count = 0
        self.rst_count = 0
        self.psh_count = 0
        self.ack_count = 0
        self.urg_count = 0
        self.ece_count = 0
        self.cwr_count = 0

        # active/idle
        self.last_flow_time = None
        self.active_times = []
        self.idle_times = []

        # flow-level packet record (for some metrics)
        self.flow_pkt_ts = []
        self.flow_pkt_sizes = []

    def add_packet(self, pkt_dict, direction):
        ts = pkt_dict["timestamp"]
        size = int(pkt_dict["length"])
        flags = pkt_dict.get("flags", {})

        # update last seen
        self.last_seen = ts

        # active/idle tracking
        if self.last_flow_time is None:
            self.last_flow_time = ts
        else:
            delta = ts - self.last_flow_time
            if delta > 1.0:  # threshold for idle vs active (1s)
                self.idle_times.append(delta)
            else:
                self.active_times.append(delta)
            self.last_flow_time = ts

        # direction append
        if direction == "fwd":
            self.fwd_ts.append(ts)
            self.fwd_sizes.append(size)
        else:
            self.bwd_ts.append(ts)
            self.bwd_sizes.append(size)

        # flow aggregations
        self.flow_pkt_ts.append(ts)
        self.flow_pkt_sizes.append(size)

        # tcp flags
        if self.proto == 6 and flags:
            if flags.get("fin", 0): self.fin_count += 1
            if flags.get("syn", 0): self.syn_count += 1
            if flags.get("rst", 0): self.rst_count += 1
            if flags.get("psh", 0): self.psh_count += 1
            if flags.get("ack", 0): self.ack_count += 1
            if flags.get("urg", 0): self.urg_count += 1
            if flags.get("ece", 0): self.ece_count += 1
            if flags.get("cwr", 0): self.cwr_count += 1

    def duration(self):
        if len(self.flow_pkt_ts) < 2:
            return 0.0
        return max(self.flow_pkt_ts) - min(self.flow_pkt_ts)

    def compute_iat_stats(self, ts_list):
        if len(ts_list) < 2:
            return (0.0, 0.0, 0.0, 0.0)
        iats = [ts_list[i] - ts_list[i-1] for i in range(1, len(ts_list))]
        return (safe_mean(iats), safe_std(iats), max(iats), min(iats))

    def compute_features(self):
        # duration and counts
        duration = self.duration()
        total_fwd = len(self.fwd_sizes)
        total_bwd = len(self.bwd_sizes)
        total_flow_pkts = len(self.flow_pkt_sizes)
        total_flow_bytes = sum(self.flow_pkt_sizes)

        # packet length stats
        pkt_min = min(self.flow_pkt_sizes) if self.flow_pkt_sizes else 0
        pkt_max = max(self.flow_pkt_sizes) if self.flow_pkt_sizes else 0
        pkt_mean = safe_mean(self.flow_pkt_sizes)
        pkt_std = safe_std(self.flow_pkt_sizes)
        pkt_var = pkt_std ** 2

        # iat
        flow_iat_mean, flow_iat_std, flow_iat_max, flow_iat_min = self.compute_iat_stats(self.flow_pkt_ts)
        fwd_iat_mean, fwd_iat_std, fwd_iat_max, fwd_iat_min = self.compute_iat_stats(self.fwd_ts)
        bwd_iat_mean, bwd_iat_std, bwd_iat_max, bwd_iat_min = self.compute_iat_stats(self.bwd_ts)

        # rates
        bytes_per_s = total_flow_bytes / duration if duration > 0 else 0.0
        pkts_per_s = total_flow_pkts / duration if duration > 0 else 0.0
        fwd_pkts_per_s = total_fwd / duration if duration > 0 else 0.0
        bwd_pkts_per_s = total_bwd / duration if duration > 0 else 0.0

        # active/idle
        active_mean = safe_mean(self.active_times)
        active_std = safe_std(self.active_times)
        active_max = max(self.active_times) if self.active_times else 0.0
        active_min = min(self.active_times) if self.active_times else 0.0

        idle_mean = safe_mean(self.idle_times)
        idle_std = safe_std(self.idle_times)
        idle_max = max(self.idle_times) if self.idle_times else 0.0
        idle_min = min(self.idle_times) if self.idle_times else 0.0

        # Down/Up ratio
        down_up_ratio = (total_bwd / total_fwd) if total_fwd > 0 else 0.0

        # average sizes
        avg_pkt_size = pkt_mean
        avg_fwd_seg = safe_mean(self.fwd_sizes)
        avg_bwd_seg = safe_mean(self.bwd_sizes)

        # build dictionary with all 87-like features (names aligned with your earlier list)
        features = {
            # identifiers
            "Flow ID": f"{self.src_ip}-{self.src_port}_{self.dst_ip}-{self.dst_port}_{self.proto}",
            "Source IP": self.src_ip,
            "Destination IP": self.dst_ip,
            "Source Port": self.src_port,
            "Destination Port": self.dst_port,
            "Protocol": self.proto,
            "Timestamp": self.first_time,

            # basics
            "Flow Duration": duration,
            "Total Fwd Packets": total_fwd,
            "Total Backward Packets": total_bwd,
            "Total Length of Fwd Packets": sum(self.fwd_sizes),
            "Total Length of Bwd Packets": sum(self.bwd_sizes),

            # forward/backward packet length stats
            "Fwd Packet Length Max": max(self.fwd_sizes) if self.fwd_sizes else 0,
            "Fwd Packet Length Min": min(self.fwd_sizes) if self.fwd_sizes else 0,
            "Fwd Packet Length Mean": safe_mean(self.fwd_sizes),
            "Fwd Packet Length Std": safe_std(self.fwd_sizes),

            "Bwd Packet Length Max": max(self.bwd_sizes) if self.bwd_sizes else 0,
            "Bwd Packet Length Min": min(self.bwd_sizes) if self.bwd_sizes else 0,
            "Bwd Packet Length Mean": safe_mean(self.bwd_sizes),
            "Bwd Packet Length Std": safe_std(self.bwd_sizes),

            # IATs
            "Flow IAT Mean": flow_iat_mean,
            "Flow IAT Std": flow_iat_std,
            "Flow IAT Max": flow_iat_max,
            "Flow IAT Min": flow_iat_min,

            "Fwd IAT Total": sum(self.fwd_ts) if len(self.fwd_ts) > 1 else 0,
            "Fwd IAT Mean": fwd_iat_mean,
            "Fwd IAT Std": fwd_iat_std,
            "Fwd IAT Max": fwd_iat_max,
            "Fwd IAT Min": fwd_iat_min,

            "Bwd IAT Total": sum(self.bwd_ts) if len(self.bwd_ts) > 1 else 0,
            "Bwd IAT Mean": bwd_iat_mean,
            "Bwd IAT Std": bwd_iat_std,
            "Bwd IAT Max": bwd_iat_max,
            "Bwd IAT Min": bwd_iat_min,

            # flags
            "Fwd PSH Flags": self.psh_count if hasattr(self, "psh_count") else self.psh_count if 'psh_count' in dir(self) else self.psh_count if hasattr(self, 'psh_count') else 0,
            "Bwd PSH Flags": 0,
            "Fwd URG Flags": self.urg_count if hasattr(self, "urg_count") else 0,
            "Bwd URG Flags": 0,

            # rates
            "Flow Bytes/s": bytes_per_s,
            "Flow Packets/s": pkts_per_s,

            "Fwd Header Length": 0,
            "Bwd Header Length": 0,

            "Fwd Packets/s": fwd_pkts_per_s,
            "Bwd Packets/s": bwd_pkts_per_s,

            "Min Packet Length": pkt_min,
            "Max Packet Length": pkt_max,
            "Packet Length Mean": pkt_mean,
            "Packet Length Std": pkt_std,
            "Packet Length Variance": pkt_var,

            "FIN Flag Count": self.fin_count,
            "SYN Flag Count": self.syn_count,
            "RST Flag Count": self.rst_count,
            "PSH Flag Count": self.psh_count,
            "ACK Flag Count": self.ack_count,
            "URG Flag Count": self.urg_count,
            "CWE Flag Count": self.cwr_count if hasattr(self, "cwr_count") else 0,
            "ECE Flag Count": self.ece_count,

            "Down/Up Ratio": down_up_ratio,

            "Average Packet Size": avg_pkt_size,
            "Avg Fwd Segment Size": avg_fwd_seg,
            "Avg Bwd Segment Size": avg_bwd_seg,

            "Fwd Header Length.1": 0,

            "Fwd Avg Bytes/Bulk": 0,
            "Fwd Avg Packets/Bulk": 0,
            "Fwd Avg Bulk Rate": 0,

            "Bwd Avg Bytes/Bulk": 0,
            "Bwd Avg Packets/Bulk": 0,
            "Bwd Avg Bulk Rate": 0,

            "Subflow Fwd Packets": total_fwd,
            "Subflow Fwd Bytes": sum(self.fwd_sizes),
            "Subflow Bwd Packets": total_bwd,
            "Subflow Bwd Bytes": sum(self.bwd_sizes),

            "Init_Win_bytes_forward": 0,
            "Init_Win_bytes_backward": 0,

            "act_data_pkt_fwd": len([x for x in self.fwd_sizes if x > 0]),
            "min_seg_size_forward": min(self.fwd_sizes) if self.fwd_sizes else 0,

            "Active Mean": active_mean,
            "Active Std": active_std,
            "Active Max": active_max,
            "Active Min": active_min,

            "Idle Mean": idle_mean,
            "Idle Std": idle_std,
            "Idle Max": idle_max,
            "Idle Min": idle_min,

            "SimillarHTTP": 0,
            "Inbound": 0
        }

        # ensure all keys exist (to match exact ordering/names if required)
        return features

# -----------------------------
# FlowParser (interface simple)
# -----------------------------
class FlowParser:
    def __init__(self, flow_timeout=10):
        self.flow_timeout = float(flow_timeout)
        self.flows = {}  # fid -> Flow instance

    def _make_fid(self, src_ip, src_port, dst_ip, dst_port, proto):
        # canonical 5-tuple ordering: keep as src->dst seen
        return f"{src_ip}-{src_port}_{dst_ip}-{dst_port}_{proto}"

    def init_flow(self, pkt):
        fid = self._make_fid(pkt["src_ip"], pkt["src_port"], pkt["dst_ip"], pkt["dst_port"], pkt["protocol"])
        f = Flow(pkt["src_ip"], pkt["src_port"], pkt["dst_ip"], pkt["dst_port"], pkt["protocol"], pkt["timestamp"])
        self.flows[fid] = f
        return fid

    def add_packet(self, pkt):
        """
        Add packet in dict format. Returns list of flow ids that were terminated by this packet (FIN/RST).
        """
        src = pkt["src_ip"]
        dst = pkt["dst_ip"]
        sport = pkt["src_port"]
        dport = pkt["dst_port"]
        proto = pkt["protocol"]
        ts = pkt["timestamp"]

        fid = self._make_fid(src, sport, dst, dport, proto)
        rev_fid = self._make_fid(dst, dport, src, sport, proto)

        # determine which flow to attach
        if fid in self.flows:
            flow = self.flows[fid]
            direction = "fwd"
        elif rev_fid in self.flows:
            flow = self.flows[rev_fid]
            direction = "bwd"
        else:
            # create new flow with forward direction as seen
            fid = self.init_flow(pkt)
            flow = self.flows[fid]
            direction = "fwd"

        # add packet
        flow.add_packet(pkt, direction)

        terminated = []
        # terminate on TCP FIN/RST
        if proto == 6:
            flags = pkt.get("flags", {})
            if flags.get("fin", 0) or flags.get("rst", 0):
                terminated.append(fid)

        return terminated

    def expire_flows(self):
        """
        Return list of fids expired by timeout (inactivity > flow_timeout).
        """
        now = time.time()
        expired = []
        for fid, flow in list(self.flows.items()):
            # last seen = flow.last_seen
            last = getattr(flow, "last_seen", None)
            if last is None:
                continue
            if (now - last) > self.flow_timeout:
                expired.append(fid)
        return expired

    def finalize_flow(self, fid):
        """
        Compute features for a flow id and return a dict of features.
        """
        flow = self.flows.get(fid)
        if flow is None:
            return None
        feats = flow.compute_features()
        # attach proper Flow ID (consistent with earlier format)
        feats["Flow ID"] = fid
        return feats

    def delete_flow(self, fid):
        if fid in self.flows:
            del self.flows[fid]
