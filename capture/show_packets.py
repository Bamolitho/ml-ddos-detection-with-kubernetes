from realtime_capture import RealtimeCapture

def callback_dummy(features):
    print("=== Flow terminé, features générées ===")
    print(features)
    print("=======================================\n")

if __name__ == "__main__":
    print("--- Capture en temps réel ---")
    capture = RealtimeCapture(
        interfaces=["wlp2s0"],   # Change selon ton interface
        bpf="ip"
    )
    capture.run(callback_dummy)
