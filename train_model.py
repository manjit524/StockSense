"""
================================================================================
 TRAIN_MODEL.PY — trains the GRU advisor model and saves it as a .keras file
================================================================================
Run this whenever you want to (re)train the model, e.g. after refreshing your
NSE/BSE/US data with a backfill:

    python train_model.py

It writes advisor_model.keras to this folder. app.py / advisor_engine.py will
automatically load that file on the next startup instead of retraining.
================================================================================
"""

import advisor_engine

registry = advisor_engine.load_registry()

if not registry:
    print("❌ No ticker data found — check NSE_FOLDER / BSE_FOLDER / US_FOLDER "
          "paths in advisor_engine.py.")
else:
    print(f"🔄 Training on {len(registry)} tickers...")
    model = advisor_engine.train_model(registry)
    advisor_engine.save_model(model)
    print(f"✅ Saved trained model to {advisor_engine.MODEL_PATH}")
