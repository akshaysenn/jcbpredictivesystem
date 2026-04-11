"""
train_model.py — Train Random Forest (primary) + Logistic Regression (baseline).
Saves best model as model.joblib.  Run standalone or called from main.py.
"""

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from data_simulator import generate_dataset

FEATURES = ["temperature", "vibration", "engine_load", "operating_hours"]
MODEL_PATH = "model.joblib"


def train():
    print("[*] Generating training data ...")
    df = generate_dataset(n=1500, anomaly_ratio=0.20)

    X = df[FEATURES].values
    y = df["failure"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── Logistic Regression baseline ─────────────────────────────────────────
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    lr = LogisticRegression(max_iter=500, random_state=42)
    lr.fit(X_train_s, y_train)
    lr_pred = lr.predict(X_test_s)
    lr_acc  = accuracy_score(y_test, lr_pred)
    lr_f1   = f1_score(y_test, lr_pred)
    print(f"[LR]  Logistic Regression  -> accuracy: {lr_acc:.2%}  F1: {lr_f1:.2f}")

    # ── Random Forest (primary) ───────────────────────────────────────────────
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_acc  = accuracy_score(y_test, rf_pred)
    rf_f1   = f1_score(y_test, rf_pred)
    print(f"[RF]  Random Forest        -> accuracy: {rf_acc:.2%}  F1: {rf_f1:.2f}")

    if rf_acc < 0.80:
        print("[WARN] Random Forest accuracy below 80% - check dataset balance.")

    # ── Persist ───────────────────────────────────────────────────────────────
    joblib.dump(rf, MODEL_PATH)
    print(f"[OK]  Model saved -> {MODEL_PATH}")
    return rf


if __name__ == "__main__":
    train()
