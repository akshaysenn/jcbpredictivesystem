"""
app.py — Flask API for JCB Predictive Maintenance.

Routes:
  GET /          → serves the dashboard (index.html)
  GET /stream    → returns latest sensor reading + risk score + alert level (JSON)
  GET /health    → simple health check
"""

import os
import threading
import time
import joblib
import numpy as np
from flask import Flask, jsonify, render_template, send_from_directory
from data_simulator import get_current_reading

MODEL_PATH = "model.joblib"
FEATURES   = ["temperature", "vibration", "engine_load", "operating_hours"]
TICK_SEC   = 3       # seconds between simulator ticks
HISTORY_LEN = 60     # number of data points kept in memory

app = Flask(__name__, template_folder="templates", static_folder="static")

# ── Shared state (thread-safe read via GIL for simple dicts/lists) ────────────
_latest: dict = {}
_history: list = []
_lock = threading.Lock()

# ── Load ML model ─────────────────────────────────────────────────────────────
print("[*] Loading model ...")
model = joblib.load(MODEL_PATH)
print("[OK] Model loaded.")


def _alert_level(risk: float) -> str:
    if risk >= 0.70:
        return "Critical"
    elif risk >= 0.30:
        return "Warning"
    return "Normal"


def _simulator_loop():
    """Background thread: ticks every TICK_SEC, updates shared state."""
    while True:
        reading = get_current_reading(anomaly_prob=0.20)
        features = np.array([[reading[f] for f in FEATURES]])
        proba = model.predict_proba(features)[0]
        # class 1 = failure
        risk_score = float(proba[1]) if 1 in model.classes_ else float(proba[0])

        entry = {
            **reading,
            "risk_score":  round(risk_score * 100, 1),   # 0–100 %
            "alert_level": _alert_level(risk_score),
        }

        with _lock:
            _latest.clear()
            _latest.update(entry)
            _history.append(entry)
            if len(_history) > HISTORY_LEN:
                _history.pop(0)

        time.sleep(TICK_SEC)


# Start simulator thread on import (main.py does the startup sequence)
_thread = threading.Thread(target=_simulator_loop, daemon=True)
_thread.start()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stream")
def stream():
    with _lock:
        data = dict(_latest)
        hist = list(_history)
    return jsonify({"current": data, "history": hist})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
