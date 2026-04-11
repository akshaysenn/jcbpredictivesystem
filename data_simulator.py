"""
data_simulator.py — Synthetic sensor data generator for JCB Predictive Maintenance.

Normal operating ranges:
  temperature:    60–90 °C
  vibration:       1–4 mm/s
  engine_load:    40–70 %
  operating_hours: monotonically increasing

Anomaly (pre-failure) patterns:
  temperature:    95–120 °C  (overheating)
  vibration:       6–15 mm/s (bearing wear)
  engine_load:    80–100 %   (overloaded)
"""

import random
import time
import numpy as np
import pandas as pd

# ── In-process state (used by the background thread in app.py) ───────────────
_operating_hours = random.uniform(100, 500)  # start mid-life
_tick_lock_hours = 0.0  # hours accrued per tick (≈ 0.001 of a real hour)

def _normal_reading():
    return {
        "temperature":    round(random.uniform(60, 90), 2),
        "vibration":      round(random.uniform(1.0, 4.0), 2),
        "engine_load":    round(random.uniform(40, 70), 2),
    }

def _anomaly_reading():
    return {
        "temperature":    round(random.uniform(95, 120), 2),
        "vibration":      round(random.uniform(6.0, 15.0), 2),
        "engine_load":    round(random.uniform(80, 100), 2),
    }


def get_current_reading(anomaly_prob: float = 0.20) -> dict:
    """Return one live sensor tick (used by Flask /stream endpoint)."""
    global _operating_hours
    _operating_hours += random.uniform(0.001, 0.005)  # tiny increment per tick

    is_anomaly = random.random() < anomaly_prob
    reading = _anomaly_reading() if is_anomaly else _normal_reading()
    reading["operating_hours"] = round(_operating_hours, 2)
    reading["label"] = 1 if is_anomaly else 0
    return reading


# ── Training dataset ─────────────────────────────────────────────────────────

def generate_dataset(n: int = 1000, anomaly_ratio: float = 0.20) -> pd.DataFrame:
    """Generate labelled training data for ML training."""
    rows = []
    hours = random.uniform(100, 500)
    n_anomaly = int(n * anomaly_ratio)
    anomaly_indices = set(random.sample(range(n), n_anomaly))

    for i in range(n):
        hours += random.uniform(0.001, 0.01)
        if i in anomaly_indices:
            row = _anomaly_reading()
            row["failure"] = 1
        else:
            row = _normal_reading()
            row["failure"] = 0
        row["operating_hours"] = round(hours, 2)
        rows.append(row)

    return pd.DataFrame(rows)
