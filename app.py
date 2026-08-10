"""
================================================================================
 APP.PY — Flask website wrapping the multi-exchange advisor + intraday scanner
================================================================================
Run with: python app.py
Then open http://127.0.0.1:5000

The long-term advisor's model trains ONCE at startup (see initialize_engine())
and is cached in memory — individual page requests just query the cached
results, they don't retrain anything. The intraday scanner runs live on each
request since it's meant to reflect the current session.
================================================================================
"""

from flask import Flask, render_template, request, jsonify, Response
import threading
import time
import pandas as pd
import yfinance as yf
import advisor_engine
import intraday_engine
import markets_data
import reports_data
import etf_tickers
import us_tickers

app = Flask(__name__)

MASTER_DF = pd.DataFrame()
ENGINE_STATUS = {"ready": False, "message": "Starting up — loading the advisor engine..."}


def to_yf_symbol(symbol, exchange):
    """Converts a plain symbol + exchange into the ticker format yfinance expects."""
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol
    if exchange == "NSE":
        return f"{symbol}.NS"
    if exchange == "BSE":
        return f"{symbol}.BO"
    return symbol  # US tickers need no suffix


def _load_engine_in_background():
    global MASTER_DF, ENGINE_STATUS
    ENGINE_STATUS["message"] = "Loading model and evaluating tickers — this can take a minute or two on CPU..."
    df = advisor_engine.initialize_engine()
    MASTER_DF = df
    ENGINE_STATUS["ready"] = True
    ENGINE_STATUS["message"] = (
        f"Ready — {len(df)} tickers loaded." if not df.empty
        else "No ticker data found. Check your NSE_FOLDER / BSE_FOLDER / US_FOLDER paths."
    )
    print(f"✅ {ENGINE_STATUS['message']}")


# Runs in the background so the Flask server starts responding right away —
# the browser gets a loading page instead of hanging on a blank screen.
threading.Thread(target=_load_engine_in_background, daemon=True).start()


# Static base data for the landing page's "today's tape" section — price and
# change here are just the initial values shown before the first live poll;
# /api/live-quotes overwrites them in the browser a moment after page load.
TREND_STOCKS = [
    {"symbol": "RELIANCE", "exchange": "NSE", "price": 2948.10, "change": 1.24, "spark": "0,20 15,18 30,14 45,16 60,10 75,8 100,4"},
    {"symbol": "TCS", "exchange": "NSE", "price": 3812.55, "change": -0.62, "spark": "0,8 15,10 30,9 45,14 60,16 75,20 100,22"},
    {"symbol": "HDFCBANK", "exchange": "BSE", "price": 1712.85, "change": 0.87, "spark": "0,18 15,16 30,17 45,12 60,13 75,9 100,7"},
    {"symbol": "ICICIBANK", "exchange": "BSE", "price": 1284.40, "change": -0.35, "spark": "0,10 15,12 30,11 45,15 60,14 75,18 100,19"},
    {"symbol": "AAPL", "exchange": "US", "price": 231.18, "change": 2.10, "spark": "0,22 15,18 30,15 45,13 60,9 75,6 100,3"},
    {"symbol": "MSFT", "exchange": "US", "price": 468.02, "change": -1.05, "spark": "0,6 15,9 30,10 45,13 60,17 75,19 100,21"},
    {"symbol": "NVDA", "exchange": "US", "price": 142.66, "change": 3.42, "spark": "0,24 15,19 30,16 45,11 60,7 75,5 100,2"},
    {"symbol": "TITAN", "exchange": "NSE", "price": 3402.75, "change": 0.44, "spark": "0,16 15,15 30,14 45,13 60,12 75,10 100,9"},
    {"symbol": "SBIN", "exchange": "BSE", "price": 812.40, "change": -0.28, "spark": "0,9 15,11 30,10 45,13 60,12 75,15 100,16"},
]
for _s in TREND_STOCKS:
    _s["yf_symbol"] = to_yf_symbol(_s["symbol"], _s["exchange"])


@app.route("/api/live-quotes")
def live_quotes():
    """
    Returns {symbol: {price, change}} for a comma-separated list of yfinance
    tickers passed as ?tickers=RELIANCE.NS,TCS.NS,AAPL
    Batches everything into one yfinance call to keep this fast and to avoid
    hammering the data source with one request per stock.
    """
    tickers_param = request.args.get("tickers", "")
    tickers = sorted(set(t.strip() for t in tickers_param.split(",") if t.strip()))
    if not tickers:
        return jsonify({})

    results = {}
    try:
        data = yf.download(
            tickers=tickers, period="1d", interval="1m",
            group_by="ticker", progress=False, threads=True,
        )
    except Exception:
        return jsonify({})

    for t in tickers:
        try:
            df = data[t] if len(tickers) > 1 else data
            df = df.dropna()
            if df.empty:
                continue
            last_close = float(df["Close"].iloc[-1])
            first_open = float(df["Open"].iloc[0])
            change_pct = ((last_close - first_open) / first_open) * 100 if first_open else 0.0
            results[t] = {"price": round(last_close, 2), "change": round(change_pct, 2)}
        except Exception:
            continue

    return jsonify(results)


@app.route("/")
def landing():
    return render_template("landing.html", active="landing", trend_stocks=TREND_STOCKS)


@app.route("/about")
def about():
    return render_template("about.html", active="about")


@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html", active="contact")


@app.route("/login")
def login():
    return render_template("login.html", active="login")


@app.route("/get-advice")
def get_advice():
    if not ENGINE_STATUS["ready"]:
        return render_template("loading.html", message=ENGINE_STATUS["message"])
    return render_template("input.html", active="advice")


# ==============================================================================
# MARKETS HUB — ETFs, Crypto, Commodities (all reuse /api/live-quotes since
# they're plain tradeable tickers) + Mutual Funds, Bonds, IPO, Derivatives
# (each with their own genuinely different data source, see markets_data.py)
# ==============================================================================

TRACKED_ETFS = etf_tickers.TRACKED_ETFS

TRACKED_CRYPTO = [
    {"symbol": "BTC", "yf_symbol": "BTC-USD", "label": "Bitcoin"},
    {"symbol": "ETH", "yf_symbol": "ETH-USD", "label": "Ethereum"},
    {"symbol": "SOL", "yf_symbol": "SOL-USD", "label": "Solana"},
    {"symbol": "BNB", "yf_symbol": "BNB-USD", "label": "BNB"},
    {"symbol": "XRP", "yf_symbol": "XRP-USD", "label": "XRP"},
]

TRACKED_COMMODITIES = [
    {"symbol": "GOLD", "yf_symbol": "GC=F", "label": "Gold (USD/oz)"},
    {"symbol": "SILVER", "yf_symbol": "SI=F", "label": "Silver (USD/oz)"},
    {"symbol": "CRUDE", "yf_symbol": "CL=F", "label": "Crude Oil (USD/bbl)"},
]

for _e in TRACKED_ETFS:
    _e["yf_symbol"] = to_yf_symbol(_e["symbol"], _e["exchange"])


# ==============================================================================
# MARKETS CACHE — refreshed in the background so /markets never blocks on
# slow external calls (100 mutual fund NAVs, NSE's IPO/option-chain scrapes).
# The route just reads whatever's currently cached — instant, even if a
# refresh is still in progress underneath.
# ==============================================================================
MARKETS_CACHE = {
    "mutual_funds": [],
    "ipos": [],
    "options_summary": None,
    "indian_bonds": markets_data.get_indian_bond_yields(),  # static, no need to refresh on a timer
    "us_bonds": [],
    "ready": False,
    "message": "Loading market data for the first time — this can take a moment...",
}

MARKETS_REFRESH_SECONDS = 15 * 60  # 15 minutes — fine for daily NAV and event-calendar data


def _refresh_markets_cache():
    while True:
        try:
            MARKETS_CACHE["mutual_funds"] = markets_data.get_default_mutual_funds()
            MARKETS_CACHE["ipos"] = markets_data.get_ipo_calendar()
            MARKETS_CACHE["options_summary"] = markets_data.get_option_chain_summary("NIFTY")
            MARKETS_CACHE["us_bonds"] = markets_data.get_us_treasury_yields()
            MARKETS_CACHE["ready"] = True
            MARKETS_CACHE["message"] = "Ready"
            print("✅ Markets cache refreshed.")
        except Exception as e:
            print(f"⚠️ Markets cache refresh failed: {e}")
        time.sleep(MARKETS_REFRESH_SECONDS)


threading.Thread(target=_refresh_markets_cache, daemon=True).start()


@app.route("/markets")
def markets():
    return render_template(
        "markets.html",
        active="markets",
        etfs=TRACKED_ETFS,
        crypto=TRACKED_CRYPTO,
        commodities=TRACKED_COMMODITIES,
        mutual_funds=MARKETS_CACHE["mutual_funds"],
        indian_bonds=MARKETS_CACHE["indian_bonds"],
        us_bonds=MARKETS_CACHE["us_bonds"],
        ipos=MARKETS_CACHE["ipos"],
        options_summary=MARKETS_CACHE["options_summary"],
        markets_ready=MARKETS_CACHE["ready"],
        markets_message=MARKETS_CACHE["message"],
    )


@app.route("/api/mutual-fund-navs")
def api_mutual_fund_navs():
    return jsonify(MARKETS_CACHE["mutual_funds"])


@app.route("/api/mutual-funds/search")
def api_mutual_funds_search():
    query = request.args.get("q", "")
    return jsonify(markets_data.search_mutual_funds(query))


@app.route("/api/ipo-calendar")
def api_ipo_calendar():
    return jsonify(MARKETS_CACHE["ipos"])


@app.route("/api/option-chain-summary")
def api_option_chain_summary():
    symbol = request.args.get("symbol", "NIFTY")
    if symbol == "NIFTY":
        return jsonify(MARKETS_CACHE["options_summary"] or {})
    summary = markets_data.get_option_chain_summary(symbol)
    return jsonify(summary or {})


# ==============================================================================
# REPORTS — growth report for any tracked symbol over a chosen period
# ==============================================================================

@app.route("/api/search-tickers")
def api_search_tickers():
    """Powers the symbol search box on the Reports page. Searches stocks
    (from the loaded advisor engine), ETFs, and crypto in one place."""
    query = request.args.get("q", "").strip().upper()
    if len(query) < 1:
        return jsonify([])

    results = []

    if not MASTER_DF.empty:
        matches = MASTER_DF[MASTER_DF["symbol"].str.upper().str.contains(query, na=False)].head(15)
        for _, row in matches.iterrows():
            results.append({"symbol": row["symbol"], "exchange": row["exchange"], "label": row["symbol"]})

    for e in TRACKED_ETFS:
        if query in e["symbol"].upper() and len(results) < 25:
            results.append({"symbol": e["symbol"], "exchange": e["exchange"], "label": f"{e['symbol']} (ETF)"})

    for c in TRACKED_CRYPTO:
        if query in c["symbol"].upper() and len(results) < 30:
            results.append({"symbol": c["yf_symbol"], "exchange": "RAW", "label": f"{c['label']} ({c['symbol']})"})

    return jsonify(results[:30])


@app.route("/reports")
def reports():
    return render_template("reports.html", active="reports", period_options=reports_data.PERIOD_OPTIONS, report=None)


@app.route("/reports/growth", methods=["POST"])
def reports_growth():
    symbol = request.form.get("symbol", "").strip().upper()
    exchange = request.form.get("exchange", "NSE").strip()
    period_days = request.form.get("period_days", "30")
    custom_days = request.form.get("custom_days", "").strip()

    if period_days == "custom" and custom_days.isdigit():
        period_days = custom_days
    elif not str(period_days).isdigit():
        period_days = "30"

    report = None
    error = None
    if symbol:
        report = reports_data.generate_growth_report(symbol, exchange, period_days)
        if report is None:
            # The typed exchange might be a guess (e.g. defaulted to NSE) —
            # retry against whatever the advisor registry actually has this
            # symbol under before giving up.
            if not MASTER_DF.empty:
                match = MASTER_DF[MASTER_DF["symbol"].str.upper() == symbol]
                if not match.empty:
                    real_exchange = match.iloc[0]["exchange"]
                    if real_exchange != exchange:
                        report = reports_data.generate_growth_report(symbol, real_exchange, period_days)
                        exchange = real_exchange
            if report is None:
                error = f"Couldn't fetch price history for {symbol} — check the symbol/exchange, or try a shorter period."
    else:
        error = "Type a symbol and pick it from the dropdown (or just type it and hit Generate)."

    return render_template(
        "reports.html",
        active="reports",
        period_options=reports_data.PERIOD_OPTIONS,
        report=report,
        error=error,
        submitted_symbol=symbol,
        submitted_exchange=exchange,
    )


def _regenerate_report_from_query():
    symbol = request.args.get("symbol", "").strip().upper()
    exchange = request.args.get("exchange", "NSE").strip()
    period_days = request.args.get("period_days", "30")
    if not symbol:
        return None, None
    return reports_data.generate_growth_report(symbol, exchange, period_days), symbol


@app.route("/reports/export/pdf")
def reports_export_pdf():
    report, symbol = _regenerate_report_from_query()
    if report is None:
        return "Report unavailable — generate it on the Reports page first, then download.", 404
    buffer = reports_data.build_pdf_report(report)
    return Response(
        buffer.read(),
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={symbol}_growth_report.pdf"},
    )


@app.route("/reports/export/excel")
def reports_export_excel():
    report, symbol = _regenerate_report_from_query()
    if report is None:
        return "Report unavailable — generate it on the Reports page first, then download.", 404
    buffer = reports_data.build_excel_report(report)
    return Response(
        buffer.read(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={symbol}_growth_report.xlsx"},
    )


@app.route("/advisor/results", methods=["POST"])
def advisor_results():
    if not ENGINE_STATUS["ready"]:
        return render_template("loading.html", message=ENGINE_STATUS["message"])

    exchange_choice = request.form.get("exchange_choice", "nse_bse")
    try:
        capital = float(request.form.get("capital", 50000))
    except ValueError:
        capital = 50000.0
    try:
        years = float(request.form.get("years", 5))
    except ValueError:
        years = 5.0

    if MASTER_DF.empty:
        result = {'label': 'No Data', 'mixed_currency': False,
                  'buckets': {'Low Risk': [], 'Medium Risk': [], 'High Risk': []}}
    else:
        result = advisor_engine.get_recommendations(MASTER_DF, exchange_choice, capital, years)
        for bucket in result['buckets'].values():
            for item in bucket:
                item['yf_symbol'] = to_yf_symbol(item['symbol'], item['exchange'])

    return render_template(
        "output.html",
        mode="advisor",
        query_label=result['label'],
        capital=capital,
        years=years,
        mixed_currency=result['mixed_currency'],
        buckets=result['buckets'],
        has_data=not MASTER_DF.empty,
    )


@app.route("/intraday/results", methods=["POST"])
def intraday_results():
    try:
        capital = float(request.form.get("capital", 20000))
    except ValueError:
        capital = 20000.0

    risk_choice = request.form.get("risk_choice", "all")
    risk_map = {
        "low": ["Low Risk"],
        "medium": ["Medium Risk"],
        "high": ["High Risk"],
        "all": ["Low Risk", "Medium Risk", "High Risk"],
    }
    risk_filter = risk_map.get(risk_choice, risk_map["all"])

    snapshot = intraday_engine.build_intraday_snapshot()
    buckets = intraday_engine.get_intraday_recommendations(snapshot, capital, risk_filter)
    for bucket in buckets.values():
        if bucket:
            for item in bucket:
                item['yf_symbol'] = item['symbol']  # intraday tickers are already yfinance-ready (e.g. RELIANCE.NS)

    return render_template(
        "output.html",
        mode="intraday",
        query_label="Intraday Scan — NSE",
        capital=capital,
        years=None,
        mixed_currency=False,
        buckets=buckets,
        has_data=not snapshot.empty,
    )


if __name__ == "__main__":
    # use_reloader=False is important here — the reloader spawns a second
    # process that would duplicate the background model-loading thread and
    # double your CPU load on startup.
    app.run(debug=True, use_reloader=False)
