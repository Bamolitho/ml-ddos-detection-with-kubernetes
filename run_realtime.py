from capture.realtime_capture import RealtimeCapture
from inference.predict import predict_raw
import pandas as pd

def inference_callback(features):
    df = pd.DataFrame([features])
    pred, prob, thr = predict_raw("xgboost", df)
    print("RESULT:", pred[0], prob[0])

if __name__ == "__main__":
    r = RealtimeCapture(interfaces=["lo", "wlp2s0"])
    r.run(inference_callback)
