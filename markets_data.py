"""
================================================================================
 MARKETS_DATA.PY — data sources for Mutual Funds, Bonds, IPOs, Derivatives
================================================================================
ETFs, Crypto, and Commodities are NOT here — they're plain tradeable tickers
(e.g. NIFTYBEES.NS, BTC-USD, GC=F) and reuse the existing /api/live-quotes
endpoint in app.py via yfinance. This file covers the four asset types that
need a genuinely different data source because they aren't priced the same
way stocks are.
================================================================================
"""

import time
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==============================================================================
# MUTUAL FUNDS — daily NAV via mfapi.in (free, wraps official AMFI data)
# ==============================================================================
# NAV updates once per trading day (usually published evening IST) — this is
# NOT live in the tick-by-tick sense, and the UI should label it "as of DATE",
# not with a live pulsing indicator.
#
# Rather than hand-typing 300-500 scheme codes (risking made-up/invalid ones),
# this pulls mfapi.in's own directory endpoint, which lists ALL ~40,000
# AMFI-registered schemes (just code + name, one lightweight call). That
# directory is cached and searchable. For the *default* view (no search
# typed yet), we show 100 real schemes pulled from that same directory —
# real codes guaranteed, since they came from the source itself — with their
# NAVs fetched in parallel so the page doesn't hang waiting on 100 sequential
# HTTP calls.

_MF_DIRECTORY_CACHE = {"data": [], "ts": 0}
_MF_DIRECTORY_TTL = 60 * 60 * 12  # the scheme list itself barely changes; refresh twice a day
_MF_NAV_CACHE = {}  # scheme_code -> {"data": {...}, "ts": ...}
_MF_NAV_TTL = 60 * 60 * 6  # NAV is daily data — no point refetching more than a few times a day
_mf_lock = threading.Lock()

DEFAULT_MF_COUNT = 100


def get_mf_directory():
    """Full list of {schemeCode, schemeName} for every AMFI-registered scheme. Cached."""
    now = time.time()
    with _mf_lock:
        if _MF_DIRECTORY_CACHE["data"] and (now - _MF_DIRECTORY_CACHE["ts"]) < _MF_DIRECTORY_TTL:
            return _MF_DIRECTORY_CACHE["data"]
    try:
        resp = requests.get("https://api.mfapi.in/mf", timeout=15)
        directory = resp.json()  # [{"schemeCode": 12345, "schemeName": "..."}, ...]
    except Exception:
        directory = []
    with _mf_lock:
        if directory:
            _MF_DIRECTORY_CACHE["data"] = directory
            _MF_DIRECTORY_CACHE["ts"] = now
    return _MF_DIRECTORY_CACHE["data"] or directory


def _fetch_single_nav(scheme_code, scheme_name):
    now = time.time()
    with _mf_lock:
        cached = _MF_NAV_CACHE.get(scheme_code)
        if cached and (now - cached["ts"]) < _MF_NAV_TTL:
            return cached["data"]
    try:
        resp = requests.get(f"https://api.mfapi.in/mf/{scheme_code}", timeout=8)
        data = resp.json()
        latest = data.get("data", [{}])[0]
        result = {
            "scheme_code": scheme_code,
            "name": scheme_name,
            "nav": float(latest.get("nav", 0)),
            "date": latest.get("date", "—"),
        }
    except Exception:
        result = {"scheme_code": scheme_code, "name": scheme_name, "nav": None, "date": "—"}
    with _mf_lock:
        _MF_NAV_CACHE[scheme_code] = {"data": result, "ts": now}
    return result


def get_mutual_fund_navs_parallel(schemes, max_workers=20):
    """
    schemes: list of (scheme_code, scheme_name) tuples.
    Fetches NAVs concurrently (I/O-bound HTTP calls) instead of one-by-one,
    so 100 funds takes roughly as long as the slowest single call, not the
    sum of all of them.
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_fetch_single_nav, code, name): code
            for code, name in schemes
        }
        for future in as_completed(futures):
            results.append(future.result())
    # Keep a stable order matching the input list
    order = {code: i for i, (code, _) in enumerate(schemes)}
    results.sort(key=lambda r: order.get(r["scheme_code"], 0))
    return results


def get_default_mutual_funds(count=DEFAULT_MF_COUNT):
    """A real, stable slice of the directory (not hand-picked) with NAVs attached."""
    directory = get_mf_directory()
    if not directory:
        return []
    schemes = [(str(row["schemeCode"]), row["schemeName"]) for row in directory[:count]]
    return get_mutual_fund_navs_parallel(schemes)


def search_mutual_funds(query, limit=30):
    """Case-insensitive substring search over the full ~40k scheme directory."""
    if not query or len(query.strip()) < 2:
        return []
    directory = get_mf_directory()
    query_lower = query.strip().lower()
    matches = [row for row in directory if query_lower in row["schemeName"].lower()][:limit]
    schemes = [(str(row["schemeCode"]), row["schemeName"]) for row in matches]
    return get_mutual_fund_navs_parallel(schemes)


# ==============================================================================
# BONDS — US Treasury yields (FRED, free, needs a free API key) +
#         Indian bond yields (no reliable free live source — manual table)
# ==============================================================================
# Sign up free at https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY = "abcdefghijklmnopqrstuvwxyz123456"

US_TREASURY_SERIES = {
    "DGS2": "US 2-Year Treasury",
    "DGS10": "US 10-Year Treasury",
    "DGS30": "US 30-Year Treasury",
}


def get_us_treasury_yields():
    """Returns a list of {name, yield_pct, date} for tracked US Treasury series."""
    if FRED_API_KEY == "YOUR_FRED_API_KEY_HERE":
        return []  # not configured yet — caller should handle the empty case

    results = []
    for series_id, name in US_TREASURY_SERIES.items():
        try:
            resp = requests.get(
                "https://api.stlouisfed.org/fred/series/observations",
                params={
                    "series_id": series_id,
                    "api_key": FRED_API_KEY,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 1,
                },
                timeout=8,
            )
            obs = resp.json().get("observations", [{}])[0]
            results.append({
                "name": name,
                "yield_pct": float(obs.get("value", 0)) if obs.get("value") not in (None, ".") else None,
                "date": obs.get("date", "—"),
            })
        except Exception:
            results.append({"name": name, "yield_pct": None, "date": "—"})
    return results


# Indian G-Sec / corporate bond yields: no free, reliable, live-updating
# public API found. Maintain this manually (e.g. weekly from RBI's site:
# https://www.rbi.org.in or NSE's bond platform) until a better free source
# turns up. Marked with a fixed "as of" date so the UI is honest about it.
INDIAN_BOND_YIELDS_MANUAL = [
    {"name": "India 10-Year G-Sec", "yield_pct": 7.05, "as_of": "2026-07-01 (manually updated)"},
    {"name": "India 5-Year G-Sec", "yield_pct": 6.85, "as_of": "2026-07-01 (manually updated)"},
]


def get_indian_bond_yields():
    return INDIAN_BOND_YIELDS_MANUAL


# ==============================================================================
# IPO CALENDAR — NSE's own unofficial "upcoming issues" endpoint
# ==============================================================================
# Same pattern as the Bhavcopy backfill: free, no key, but unofficial and can
# change format without notice.

def get_ipo_calendar():
    """Returns a list of upcoming/current NSE IPOs, or [] if unavailable."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        session.get("https://www.nseindia.com", timeout=10)
        resp = session.get(
            "https://www.nseindia.com/api/all-upcoming-issues?category=ipo", timeout=10
        )
        data = resp.json()
        results = []
        for row in data:
            results.append({
                "company": row.get("companyName", "—"),
                "open_date": row.get("issueStartDate", "—"),
                "close_date": row.get("issueEndDate", "—"),
                "price_band": row.get("issuePrice", "—"),
                "issue_size": row.get("issueSize", "—"),
            })
        return results
    except Exception:
        return []


def get_ipo_gmp(company_name):
    """
    Grey Market Premium — informal, unofficial, unregulated secondary-market
    number with no clean free API. This is a stub: no scrape target is wired
    in because none could be verified as reliable. If you want this live,
    plug in a specific source's response format here — and keep the UI label
    saying "unofficial" no matter what you connect.
    """
    return None


# ==============================================================================
# DERIVATIVES — NSE option chain (unofficial), info-only summary
# ==============================================================================

def get_option_chain_summary(symbol="NIFTY"):
    """
    Returns a small info-only summary: ATM strikes and put-call ratio for the
    given index. Intentionally NOT used to generate buy/sell suggestions —
    derivatives carry leverage risk that plain equity picks don't.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        session.get("https://www.nseindia.com", timeout=10)
        resp = session.get(
            f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}", timeout=10
        )
        data = resp.json()
        records = data.get("records", {})
        underlying = records.get("underlyingValue")
        rows = records.get("data", [])

        total_ce_oi = sum(r.get("CE", {}).get("openInterest", 0) for r in rows if "CE" in r)
        total_pe_oi = sum(r.get("PE", {}).get("openInterest", 0) for r in rows if "PE" in r)
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi else None

        # Nearest 5 strikes to the underlying value, for a compact display
        strikes = sorted(set(r.get("strikePrice") for r in rows if r.get("strikePrice")))
        if underlying and strikes:
            strikes = sorted(strikes, key=lambda s: abs(s - underlying))[:5]

        near_rows = [r for r in rows if r.get("strikePrice") in strikes]

        return {
            "symbol": symbol,
            "underlying_value": underlying,
            "put_call_ratio": pcr,
            "near_strikes": sorted(strikes) if strikes else [],
            "raw_near_rows": near_rows,
        }
    except Exception:
        return None
