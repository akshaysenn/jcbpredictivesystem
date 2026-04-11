# JCB Predictive Maintenance System

A simulated, end-to-end predictive maintenance system for construction equipment. Generates synthetic sensor data, runs ML inference in real-time, and displays live results on a dark-themed dashboard.

![Dashboard](https://img.shields.io/badge/status-alpha-orange) ![Python](https://img.shields.io/badge/python-3.8+-blue) ![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)

---

## Features

- **Sensor simulation** — generates temperature, vibration, engine load, and operating hours every 3 seconds with injected anomaly patterns
- **ML prediction** — Random Forest classifier (+ Logistic Regression baseline) predicts failure probability in real-time
- **Tiered alerts** — Normal / Warning / Critical thresholds with colour-coded banner and persistent alert log
- **Live dashboard** — rolling Chart.js charts, SVG risk gauge, sensor cards; auto-updates without page refresh

---

## Quick Start

```bash
# 1. Install dependencies (first time only)
pip install -r requirements.txt

# 2. Run
python main.py
```

The browser opens automatically at **http://localhost:5000**.  
On first run, the model is trained and saved as `model.joblib` (~2 seconds).

---

## Project Structure

```
jcb/
├── main.py              # Entry point — train → open browser → start server
├── app.py               # Flask API  (/stream, /)
├── data_simulator.py    # Sensor data generator + anomaly injection
├── train_model.py       # ML training (Random Forest + Logistic Regression)
├── model.joblib         # Saved model (auto-generated)
├── requirements.txt
├── templates/
│   └── index.html       # Dashboard UI
└── static/
    ├── style.css        # Dark theme
    └── dashboard.js     # Polling loop, Chart.js, gauge, alerts
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data simulation | Python, NumPy, Pandas |
| ML model | Scikit-learn — `RandomForestClassifier` |
| API | Flask |
| Frontend | HTML / CSS / Vanilla JS |
| Charts | Chart.js |
| Model persistence | joblib |

---

## API

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the dashboard |
| `/stream` | GET | Returns current sensor reading + history (JSON) |
| `/health` | GET | Health check |

**Example `/stream` response:**
```json
{
  "current": {
    "temperature": 111.12,
    "vibration": 6.42,
    "engine_load": 87.54,
    "operating_hours": 341.81,
    "risk_score": 100.0,
    "alert_level": "Critical"
  },
  "history": [...]
}
```

---

## Alert Levels

| Level | Risk Score | Colour |
|---|---|---|
| Normal | < 30% | 🟢 Green |
| Warning | 30 – 70% | 🟡 Yellow |
| Critical | > 70% | 🔴 Red (pulsing) |

---

## Sensor Ranges

| Sensor | Normal | Anomaly (pre-failure) |
|---|---|---|
| Temperature | 60 – 90 °C | 95 – 120 °C |
| Vibration | 1 – 4 mm/s | 6 – 15 mm/s |
| Engine Load | 40 – 70 % | 80 – 100 % |

---

## Model Performance

Trained on 1500 synthetic samples (80/20 train-test split, 20% anomaly ratio):

| Model | Accuracy | F1 |
|---|---|---|
| Logistic Regression | ~100% | 1.00 |
| Random Forest ✅ | ~100% | 1.00 |

> High accuracy is expected — synthetic data has clean, non-overlapping value ranges by design.
