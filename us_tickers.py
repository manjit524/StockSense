"""
================================================================================
 US_TICKERS.PY — real S&P 500 constituent list, fetched live and cached
================================================================================
Pulls the current S&P 500 list from a real, public, actively-maintained
dataset (https://github.com/datasets/s-and-p-500-companies) instead of a
hand-typed list — hand-typed ticker lists are easy to get subtly wrong
(delisted tickers, typos), which matters if this project gets published.

Cached to disk for a day so repeated runs don't re-fetch every time. Falls
back to a small, verified list if the fetch ever fails (no internet, dataset
moved, etc.) so the app still runs.
================================================================================
"""

import os
import io
import json
import time
import requests
import pandas as pd

CACHE_PATH = "sp500_tickers_cache.json"
CACHE_MAX_AGE_HOURS = 24
CSV_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"

FALLBACK_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    "JPM", "V", "JNJ", "WMT", "PG", "DIS", "NFLX", "AMD",
]


def _fetch_sp500_tickers():
    resp = requests.get(CSV_URL, timeout=15)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))
    tickers = df["Symbol"].astype(str).str.strip().str.upper().tolist()
    # yfinance/Twelve Data use '-' for share classes where this dataset uses '.'
    # (e.g. BRK.B -> BRK-B)
    tickers = [t.replace(".", "-") for t in tickers]
    return sorted(set(tickers))


def get_sp500_tickers(force_refresh=False):
    if not force_refresh and os.path.exists(CACHE_PATH):
        age_hours = (time.time() - os.path.getmtime(CACHE_PATH)) / 3600
        if age_hours < CACHE_MAX_AGE_HOURS:
            try:
                with open(CACHE_PATH) as f:
                    cached = json.load(f)
                if cached:
                    return cached
            except Exception:
                pass

    try:
        tickers = _fetch_sp500_tickers()
        if tickers:
            with open(CACHE_PATH, "w") as f:
                json.dump(tickers, f)
            return tickers
    except Exception as e:
        print(f"⚠️ Could not fetch the live S&P 500 list ({e}) — using the fallback list.")

    return FALLBACK_TICKERS


SP500_TICKERS = get_sp500_tickers()
