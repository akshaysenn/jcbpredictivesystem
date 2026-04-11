"""
main.py — Single entry point for JCB Predictive Maintenance System.

Usage:
    python main.py

Steps:
  1. Install deps reminder (user runs pip install -r requirements.txt)
  2. Train model if model.joblib is missing
  3. Start Flask on http://localhost:5000
"""

import os
import webbrowser
import threading
import time

MODEL_PATH = "model.joblib"


def main():
    # ── Train if model missing ────────────────────────────────────────────────
    if not os.path.exists(MODEL_PATH):
        print("[*] No model found - training now ...")
        from train_model import train
        train()
    else:
        print(f"[OK] Model found at {MODEL_PATH} - skipping training.")

    # ── Launch Flask ──────────────────────────────────────────────────────────
    print("\n[*] Starting JCB Maintenance Dashboard ...")
    print("    Open: http://localhost:5000\n")

    # Auto-open browser after a short delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:5000")

    threading.Thread(target=open_browser, daemon=True).start()

    from app import app
    app.run(debug=False, port=5000, use_reloader=False)


if __name__ == "__main__":
    main()
