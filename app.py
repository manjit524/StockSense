

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
    if symbol.endswith(".NS") or symbol.endswith(".BO") or "-USD" in symbol:
        return symbol
    if exchange == "CRYPTO":
        return f"{symbol}-USD"
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
    print(f"[OK] {ENGINE_STATUS['message']}")


# Runs in the background so the Flask server starts responding right away —
# the browser gets a loading page instead of hanging on a blank screen.
threading.Thread(target=_load_engine_in_background, daemon=True).start()


# Static base data for the landing page's "today's tape" section — price and
# change here are just the initial values shown before the first live poll;
# /api/live-quotes overwrites them in the browser a moment after page load.
TREND_STOCKS = [
    # --- Indian & US Stocks ---
    {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "exchange": "NSE", "category": "stocks", "price": 2948.10, "change": 1.24, "spark": "0,20 15,18 30,14 45,16 60,10 75,8 100,4"},
    {"symbol": "TCS", "name": "Tata Consultancy Services", "exchange": "NSE", "category": "stocks", "price": 3812.55, "change": -0.62, "spark": "0,8 15,10 30,9 45,14 60,16 75,20 100,22"},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "exchange": "BSE", "category": "stocks", "price": 1712.85, "change": 0.87, "spark": "0,18 15,16 30,17 45,12 60,13 75,9 100,7"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "exchange": "BSE", "category": "stocks", "price": 1284.40, "change": -0.35, "spark": "0,10 15,12 30,11 45,15 60,14 75,18 100,19"},
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "US", "category": "stocks", "price": 231.18, "change": 2.10, "spark": "0,22 15,18 30,15 45,13 60,9 75,6 100,3"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "US", "category": "stocks", "price": 468.02, "change": -1.05, "spark": "0,6 15,9 30,10 45,13 60,17 75,19 100,21"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "US", "category": "stocks", "price": 142.66, "change": 3.42, "spark": "0,24 15,19 30,16 45,11 60,7 75,5 100,2"},
    {"symbol": "TITAN", "name": "Titan Company Ltd", "exchange": "NSE", "category": "stocks", "price": 3402.75, "change": 0.44, "spark": "0,16 15,15 30,14 45,13 60,12 75,10 100,9"},
    {"symbol": "SBIN", "name": "State Bank of India", "exchange": "BSE", "category": "stocks", "price": 812.40, "change": -0.28, "spark": "0,9 15,11 30,10 45,13 60,12 75,15 100,16"},

    # --- Crypto Assets ---
    {"symbol": "BTC", "name": "Bitcoin (USD)", "exchange": "CRYPTO", "category": "crypto", "price": 89450.00, "change": 2.34, "spark": "0,22 15,19 30,17 45,12 60,9 75,6 100,2"},
    {"symbol": "ETH", "name": "Ethereum (USD)", "exchange": "CRYPTO", "category": "crypto", "price": 3310.40, "change": -0.78, "spark": "0,7 15,9 30,12 45,15 60,14 75,18 100,21"},
    {"symbol": "SOL", "name": "Solana (USD)", "exchange": "CRYPTO", "category": "crypto", "price": 184.25, "change": 4.15, "spark": "0,23 15,18 30,14 45,12 60,7 75,5 100,2"},
    {"symbol": "BNB", "name": "BNB (USD)", "exchange": "CRYPTO", "category": "crypto", "price": 638.10, "change": 0.85, "spark": "0,16 15,15 30,12 45,14 60,10 75,8 100,6"},
    {"symbol": "XRP", "name": "XRP (USD)", "exchange": "CRYPTO", "category": "crypto", "price": 2.24, "change": 1.45, "spark": "0,19 15,17 30,15 45,11 60,12 75,7 100,5"},

    # --- ETFs ---
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "exchange": "US", "category": "etfs", "price": 586.20, "change": 0.58, "spark": "0,18 15,16 30,15 45,13 60,11 75,9 100,6"},
    {"symbol": "QQQ", "name": "Invesco QQQ Trust (Nasdaq 100)", "exchange": "US", "category": "etfs", "price": 512.80, "change": 1.12, "spark": "0,21 15,17 30,14 45,12 60,8 75,6 100,3"},
    {"symbol": "NIFTYBEES", "name": "Nippon India Nifty 50 BeES", "exchange": "NSE", "category": "etfs", "price": 270.10, "change": 0.42, "spark": "0,17 15,16 30,14 45,13 60,11 75,9 100,8"},
    {"symbol": "GOLDBEES", "name": "Nippon India ETF Gold BeES", "exchange": "NSE", "category": "etfs", "price": 72.85, "change": 0.28, "spark": "0,15 15,14 30,13 45,12 60,11 75,9 100,7"},
    {"symbol": "BANKBEES", "name": "Nippon India Nifty Bank BeES", "exchange": "NSE", "category": "etfs", "price": 542.40, "change": -0.32, "spark": "0,9 15,11 30,10 45,14 60,15 75,17 100,19"}
]

for _s in TREND_STOCKS:
    _s["yf_symbol"] = to_yf_symbol(_s["symbol"], _s["exchange"])


@app.context_processor
def inject_global_data():
    return {"trend_stocks": TREND_STOCKS}


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


@app.route("/api/asset-chart")
def asset_chart():
    """
    Returns historical candlestick and closing price series with high/low/volume stats
    for the interactive Big Format Graph modal on the homepage.
    """
    ticker = request.args.get("ticker", "").strip()
    tf = request.args.get("tf", "1D").upper()
    if not ticker:
        return jsonify({"error": "No ticker specified"}), 400

    tf_map = {
        "1D": ("1d", "5m"),
        "1W": ("5d", "15m"),
        "1M": ("1mo", "1h"),
        "1Y": ("1y", "1d"),
        "ALL": ("5y", "1wk")
    }
    period, interval = tf_map.get(tf, ("1d", "5m"))

    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        if df is None or df.empty:
            return jsonify({"points": [], "stats": {}})

        df = df.dropna()
        points = []
        for idx, row in df.iterrows():
            if interval in ("5m", "15m"):
                t_str = idx.strftime("%H:%M")
            elif interval == "1h":
                t_str = idx.strftime("%d %b %H:%M")
            else:
                t_str = idx.strftime("%d %b '%y")

            c_val = round(float(row["Close"]), 2)
            o_val = round(float(row["Open"]), 2)
            h_val = round(float(row["High"]), 2)
            l_val = round(float(row["Low"]), 2)
            v_val = int(row["Volume"]) if ("Volume" in row and not pd.isna(row["Volume"])) else 0

            points.append({
                "time": t_str,
                "price": c_val,
                "open": o_val,
                "high": h_val,
                "low": l_val,
                "volume": v_val
            })

        if not points:
            return jsonify({"points": [], "stats": {}})

        first_open = points[0]["open"]
        last_price = points[-1]["price"]
        change_val = round(last_price - first_open, 2)
        change_pct = round(((last_price - first_open) / first_open) * 100, 2) if first_open else 0.0
        high_price = round(max(p["high"] for p in points), 2)
        low_price = round(min(p["low"] for p in points), 2)
        total_vol = sum(p["volume"] for p in points)

        return jsonify({
            "ticker": ticker,
            "tf": tf,
            "points": points,
            "current_price": last_price,
            "change_val": change_val,
            "change_pct": change_pct,
            "high": high_price,
            "low": low_price,
            "open": first_open,
            "volume": total_vol
        })
    except Exception as e:
        return jsonify({"error": str(e), "points": []})


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
    {"symbol": "BTC", "yf_symbol": "BTC-USD", "label": "Bitcoin", "category": "l1", "desc": "Decentralised Digital Gold"},
    {"symbol": "ETH", "yf_symbol": "ETH-USD", "label": "Ethereum", "category": "l1", "desc": "Smart Contract Platform"},
    {"symbol": "SOL", "yf_symbol": "SOL-USD", "label": "Solana", "category": "l1", "desc": "High-Throughput Layer 1"},
    {"symbol": "BNB", "yf_symbol": "BNB-USD", "label": "BNB (Binance)", "category": "l1", "desc": "BNB Chain Native Token"},
    {"symbol": "XRP", "yf_symbol": "XRP-USD", "label": "XRP (Ripple)", "category": "payments", "desc": "Cross-Border Settlement"},
    {"symbol": "ADA", "yf_symbol": "ADA-USD", "label": "Cardano", "category": "l1", "desc": "Proof-of-Stake Blockchain"},
    {"symbol": "AVAX", "yf_symbol": "AVAX-USD", "label": "Avalanche", "category": "l1", "desc": "Scalable Subnet Ecosystem"},
    {"symbol": "LINK", "yf_symbol": "LINK-USD", "label": "Chainlink", "category": "defi", "desc": "Decentralised Oracle Network"},
    {"symbol": "DOGE", "yf_symbol": "DOGE-USD", "label": "Dogecoin", "category": "payments", "desc": "Community Currency"},
]

TRACKED_COMMODITIES = [
    {"symbol": "GOLD", "yf_symbol": "GC=F", "label": "Gold Futures", "category": "precious", "unit": "USD/oz", "exchange": "COMEX"},
    {"symbol": "SILVER", "yf_symbol": "SI=F", "label": "Silver Futures", "category": "precious", "unit": "USD/oz", "exchange": "COMEX"},
    {"symbol": "PLATINUM", "yf_symbol": "PL=F", "label": "Platinum Futures", "category": "precious", "unit": "USD/oz", "exchange": "NYMEX"},
    {"symbol": "CRUDE", "yf_symbol": "CL=F", "label": "WTI Crude Oil", "category": "energy", "unit": "USD/bbl", "exchange": "NYMEX"},
    {"symbol": "BRENT", "yf_symbol": "BZ=F", "label": "Brent Crude Oil", "category": "energy", "unit": "USD/bbl", "exchange": "ICE"},
    {"symbol": "NATGAS", "yf_symbol": "NG=F", "label": "Natural Gas", "category": "energy", "unit": "USD/MMBtu", "exchange": "NYMEX"},
    {"symbol": "COPPER", "yf_symbol": "HG=F", "label": "Copper Futures", "category": "industrial", "unit": "USD/lb", "exchange": "COMEX"},
]

for _e in TRACKED_ETFS:
    _e["yf_symbol"] = to_yf_symbol(_e["symbol"], _e["exchange"])

US_STOCKS_LIST = [
    {"symbol": "AAPL", "yf_symbol": "AAPL", "label": "Apple Inc.", "exchange": "US", "sector": "Big Tech & AI", "category": "tech"},
    {"symbol": "MSFT", "yf_symbol": "MSFT", "label": "Microsoft Corp.", "exchange": "US", "sector": "Big Tech & AI", "category": "tech"},
    {"symbol": "NVDA", "yf_symbol": "NVDA", "label": "NVIDIA Corp.", "exchange": "US", "sector": "Semiconductors", "category": "semi"},
    {"symbol": "AMZN", "yf_symbol": "AMZN", "label": "Amazon.com Inc.", "exchange": "US", "sector": "Big Tech & AI", "category": "tech"},
    {"symbol": "GOOGL", "yf_symbol": "GOOGL", "label": "Alphabet Inc.", "exchange": "US", "sector": "Big Tech & AI", "category": "tech"},
    {"symbol": "META", "yf_symbol": "META", "label": "Meta Platforms Inc.", "exchange": "US", "sector": "Big Tech & AI", "category": "tech"},
    {"symbol": "TSLA", "yf_symbol": "TSLA", "label": "Tesla Inc.", "exchange": "US", "sector": "Auto & EV", "category": "tech"},
    {"symbol": "NFLX", "yf_symbol": "NFLX", "label": "Netflix Inc.", "exchange": "US", "sector": "Media & Tech", "category": "tech"},
    {"symbol": "AVGO", "yf_symbol": "AVGO", "label": "Broadcom Inc.", "exchange": "US", "sector": "Semiconductors", "category": "semi"},
    {"symbol": "AMD", "yf_symbol": "AMD", "label": "Advanced Micro Devices", "exchange": "US", "sector": "Semiconductors", "category": "semi"},
    {"symbol": "QCOM", "yf_symbol": "QCOM", "label": "Qualcomm Inc.", "exchange": "US", "sector": "Semiconductors", "category": "semi"},
    {"symbol": "INTC", "yf_symbol": "INTC", "label": "Intel Corp.", "exchange": "US", "sector": "Semiconductors", "category": "semi"},
    {"symbol": "TSM", "yf_symbol": "TSM", "label": "Taiwan Semiconductor", "exchange": "US", "sector": "Semiconductors", "category": "semi"},
    {"symbol": "JPM", "yf_symbol": "JPM", "label": "JPMorgan Chase & Co.", "exchange": "US", "sector": "Finance & Banking", "category": "finance"},
    {"symbol": "V", "yf_symbol": "V", "label": "Visa Inc.", "exchange": "US", "sector": "Finance & Payments", "category": "finance"},
    {"symbol": "MA", "yf_symbol": "MA", "label": "Mastercard Inc.", "exchange": "US", "sector": "Finance & Payments", "category": "finance"},
    {"symbol": "BAC", "yf_symbol": "BAC", "label": "Bank of America", "exchange": "US", "sector": "Finance & Banking", "category": "finance"},
    {"symbol": "GS", "yf_symbol": "GS", "label": "Goldman Sachs Group", "exchange": "US", "sector": "Finance & Investment", "category": "finance"},
    {"symbol": "BRK-B", "yf_symbol": "BRK-B", "label": "Berkshire Hathaway", "exchange": "US", "sector": "Finance & Conglomerate", "category": "finance"},
    {"symbol": "WMT", "yf_symbol": "WMT", "label": "Walmart Inc.", "exchange": "US", "sector": "Consumer & Retail", "category": "consumer"},
    {"symbol": "COST", "yf_symbol": "COST", "label": "Costco Wholesale", "exchange": "US", "sector": "Consumer & Retail", "category": "consumer"},
    {"symbol": "DIS", "yf_symbol": "DIS", "label": "Walt Disney Co.", "exchange": "US", "sector": "Entertainment", "category": "consumer"},
    {"symbol": "KO", "yf_symbol": "KO", "label": "Coca-Cola Co.", "exchange": "US", "sector": "Consumer Staples", "category": "consumer"},
    {"symbol": "PEP", "yf_symbol": "PEP", "label": "PepsiCo Inc.", "exchange": "US", "sector": "Consumer Staples", "category": "consumer"},
    {"symbol": "MCD", "yf_symbol": "MCD", "label": "McDonald's Corp.", "exchange": "US", "sector": "Consumer & Food", "category": "consumer"},
    {"symbol": "JNJ", "yf_symbol": "JNJ", "label": "Johnson & Johnson", "exchange": "US", "sector": "Healthcare & Pharma", "category": "healthcare"},
    {"symbol": "LLY", "yf_symbol": "LLY", "label": "Eli Lilly & Co.", "exchange": "US", "sector": "Healthcare & Pharma", "category": "healthcare"},
    {"symbol": "UNH", "yf_symbol": "UNH", "label": "UnitedHealth Group", "exchange": "US", "sector": "Healthcare Services", "category": "healthcare"},
    {"symbol": "PFE", "yf_symbol": "PFE", "label": "Pfizer Inc.", "exchange": "US", "sector": "Healthcare & Pharma", "category": "healthcare"},
    {"symbol": "BA", "yf_symbol": "BA", "label": "Boeing Co.", "exchange": "US", "sector": "Aerospace & Defence", "category": "industrial"},
]

INDIAN_STOCKS_LIST = [
    {"symbol": "RELIANCE", "yf_symbol": "RELIANCE.NS", "label": "Reliance Industries Ltd.", "exchange": "NSE", "sector": "Energy & Telecom", "category": "titans"},
    {"symbol": "TCS", "yf_symbol": "TCS.NS", "label": "Tata Consultancy Services", "exchange": "NSE", "sector": "IT & Tech Services", "category": "it"},
    {"symbol": "HDFCBANK", "yf_symbol": "HDFCBANK.NS", "label": "HDFC Bank Ltd.", "exchange": "NSE", "sector": "Banking & Financials", "category": "banking"},
    {"symbol": "INFY", "yf_symbol": "INFY.NS", "label": "Infosys Ltd.", "exchange": "NSE", "sector": "IT & Tech Services", "category": "it"},
    {"symbol": "ICICIBANK", "yf_symbol": "ICICIBANK.NS", "label": "ICICI Bank Ltd.", "exchange": "NSE", "sector": "Banking & Financials", "category": "banking"},
    {"symbol": "BHARTIARTL", "yf_symbol": "BHARTIARTL.NS", "label": "Bharti Airtel Ltd.", "exchange": "NSE", "sector": "Telecommunications", "category": "titans"},
    {"symbol": "SBIN", "yf_symbol": "SBIN.NS", "label": "State Bank of India", "exchange": "NSE", "sector": "Banking & PSU", "category": "banking"},
    {"symbol": "LT", "yf_symbol": "LT.NS", "label": "Larsen & Toubro Ltd.", "exchange": "NSE", "sector": "Infrastructure & Engg", "category": "titans"},
    {"symbol": "ITC", "yf_symbol": "ITC.NS", "label": "ITC Ltd.", "exchange": "NSE", "sector": "FMCG & Conglomerate", "category": "fmcg"},
    {"symbol": "HINDUNILVR", "yf_symbol": "HINDUNILVR.NS", "label": "Hindustan Unilever Ltd.", "exchange": "NSE", "sector": "FMCG & Consumer", "category": "fmcg"},
    {"symbol": "KOTAKBANK", "yf_symbol": "KOTAKBANK.NS", "label": "Kotak Mahindra Bank", "exchange": "NSE", "sector": "Banking & Financials", "category": "banking"},
    {"symbol": "AXISBANK", "yf_symbol": "AXISBANK.NS", "label": "Axis Bank Ltd.", "exchange": "NSE", "sector": "Banking & Financials", "category": "banking"},
    {"symbol": "BAJFINANCE", "yf_symbol": "BAJFINANCE.NS", "label": "Bajaj Finance Ltd.", "exchange": "NSE", "sector": "NBFC & Financials", "category": "banking"},
    {"symbol": "WIPRO", "yf_symbol": "WIPRO.NS", "label": "Wipro Ltd.", "exchange": "NSE", "sector": "IT & Tech Services", "category": "it"},
    {"symbol": "HCLTECH", "yf_symbol": "HCLTECH.NS", "label": "HCL Technologies Ltd.", "exchange": "NSE", "sector": "IT & Tech Services", "category": "it"},
    {"symbol": "TECHM", "yf_symbol": "TECHM.NS", "label": "Tech Mahindra Ltd.", "exchange": "NSE", "sector": "IT & Tech Services", "category": "it"},
    {"symbol": "TATAMOTORS", "yf_symbol": "TATAMOTORS.NS", "label": "Tata Motors Ltd.", "exchange": "NSE", "sector": "Automotive & EV", "category": "auto"},
    {"symbol": "MARUTI", "yf_symbol": "MARUTI.NS", "label": "Maruti Suzuki India", "exchange": "NSE", "sector": "Automotive", "category": "auto"},
    {"symbol": "M&M", "yf_symbol": "M&M.NS", "label": "Mahindra & Mahindra", "exchange": "NSE", "sector": "Auto & Farm Equip", "category": "auto"},
    {"symbol": "BAJAJ-AUTO", "yf_symbol": "BAJAJ-AUTO.NS", "label": "Bajaj Auto Ltd.", "exchange": "NSE", "sector": "2-Wheeler & Auto", "category": "auto"},
    {"symbol": "TITAN", "yf_symbol": "TITAN.NS", "label": "Titan Company Ltd.", "exchange": "NSE", "sector": "Consumer & Jewelry", "category": "fmcg"},
    {"symbol": "NESTLEIND", "yf_symbol": "NESTLEIND.NS", "label": "Nestle India Ltd.", "exchange": "NSE", "sector": "FMCG & Foods", "category": "fmcg"},
    {"symbol": "ASIANPAINT", "yf_symbol": "ASIANPAINT.NS", "label": "Asian Paints Ltd.", "exchange": "NSE", "sector": "Paints & Consumer", "category": "fmcg"},
    {"symbol": "SUNPHARMA", "yf_symbol": "SUNPHARMA.NS", "label": "Sun Pharma Industries", "exchange": "NSE", "sector": "Pharma & Healthcare", "category": "titans"},
    {"symbol": "TATASTEEL", "yf_symbol": "TATASTEEL.NS", "label": "Tata Steel Ltd.", "exchange": "NSE", "sector": "Metals & Mining", "category": "titans"},
    {"symbol": "POWERGRID", "yf_symbol": "POWERGRID.NS", "label": "Power Grid Corp of India", "exchange": "NSE", "sector": "Power Transmission", "category": "titans"},
    {"symbol": "NTPC", "yf_symbol": "NTPC.NS", "label": "NTPC Ltd.", "exchange": "NSE", "sector": "Power Generation", "category": "titans"},
]

CURATED_MUTUAL_FUNDS = [
    {"code": "120503", "name": "HDFC Top 100 Fund - Direct Plan - Growth", "category": "largecap", "cat_label": "Large Cap", "aum": "₹34,200 Cr", "rating": "5★", "risk": "Moderate"},
    {"code": "120586", "name": "ICICI Prudential Bluechip Fund - Direct Plan - Growth", "category": "largecap", "cat_label": "Large Cap", "aum": "₹55,100 Cr", "rating": "5★", "risk": "Moderate"},
    {"code": "119598", "name": "SBI Bluechip Fund - Direct Plan - Growth", "category": "largecap", "cat_label": "Large Cap", "aum": "₹46,800 Cr", "rating": "4★", "risk": "Moderate"},
    {"code": "122639", "name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth", "category": "flexicap", "cat_label": "Flexi Cap", "aum": "₹68,400 Cr", "rating": "5★", "risk": "Moderate-High"},
    {"code": "120847", "name": "Quant Flexi Cap Fund - Direct Plan - Growth", "category": "flexicap", "cat_label": "Flexi Cap", "aum": "₹6,300 Cr", "rating": "5★", "risk": "High"},
    {"code": "118778", "name": "HDFC Flexi Cap Fund - Direct Plan - Growth", "category": "flexicap", "cat_label": "Flexi Cap", "aum": "₹62,000 Cr", "rating": "5★", "risk": "Moderate-High"},
    {"code": "118768", "name": "Nippon India Small Cap Fund - Direct Plan - Growth", "category": "smallcap", "cat_label": "Small Cap", "aum": "₹58,900 Cr", "rating": "5★", "risk": "High"},
    {"code": "120828", "name": "Quant Mid Cap Fund - Direct Plan - Growth", "category": "smallcap", "cat_label": "Mid Cap", "aum": "₹12,400 Cr", "rating": "5★", "risk": "High"},
    {"code": "118989", "name": "HDFC Mid-Cap Opportunities Fund - Direct Plan - Growth", "category": "smallcap", "cat_label": "Mid Cap", "aum": "₹71,200 Cr", "rating": "5★", "risk": "High"},
    {"code": "128054", "name": "Mirae Asset ELSS Tax Saver Fund - Direct Plan - Growth", "category": "elss", "cat_label": "ELSS Tax Saver", "aum": "₹24,800 Cr", "rating": "5★", "risk": "Moderate-High"},
    {"code": "119718", "name": "SBI Long Term Equity Fund - Direct Plan - Growth", "category": "elss", "cat_label": "ELSS Tax Saver", "aum": "₹23,500 Cr", "rating": "5★", "risk": "Moderate-High"},
    {"code": "119102", "name": "HDFC Liquid Fund - Direct Plan - Growth", "category": "debt", "cat_label": "Liquid & Debt", "aum": "₹54,000 Cr", "rating": "5★", "risk": "Low"},
]

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
            print("[OK] Markets cache refreshed.")
        except Exception as e:
            print(f"[WARN] Markets cache refresh failed: {e}")
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


@app.route("/markets/<category_id>")
def market_category(category_id):
    if category_id == "etfs":
        top_equity = [e for e in TRACKED_ETFS if e["symbol"] in ["SPY", "QQQ", "NIFTYBEES", "BANKBEES"]]
        top_commodity = [e for e in TRACKED_ETFS if e["symbol"] in ["GLD", "GOLDBEES", "XLK", "MAFANG"]]
        return render_template(
            "etf_detail.html",
            active="markets",
            etfs=TRACKED_ETFS,
            top_equity=top_equity,
            top_commodity=top_commodity,
            markets_ready=MARKETS_CACHE["ready"],
            markets_message=MARKETS_CACHE["message"]
        )

    if category_id == "us-stocks":
        top_tech = [s for s in US_STOCKS_LIST if s["symbol"] in ["AAPL", "MSFT", "NVDA", "AMZN", "META", "TSLA"]]
        top_semi_bluechip = [s for s in US_STOCKS_LIST if s["symbol"] in ["AVGO", "AMD", "JPM", "WMT", "V", "LLY"]]
        return render_template(
            "us_stocks_detail.html",
            active="markets",
            stocks=US_STOCKS_LIST,
            top_tech=top_tech,
            top_semi_bluechip=top_semi_bluechip,
            markets_ready=MARKETS_CACHE["ready"],
            markets_message=MARKETS_CACHE["message"]
        )

    if category_id == "indian-stocks":
        top_titans = [s for s in INDIAN_STOCKS_LIST if s["symbol"] in ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "LT"]]
        top_growth_leaders = [s for s in INDIAN_STOCKS_LIST if s["symbol"] in ["TATAMOTORS", "BAJFINANCE", "TITAN", "SUNPHARMA", "ITC", "BHARTIARTL"]]
        return render_template(
            "indian_stocks_detail.html",
            active="markets",
            stocks=INDIAN_STOCKS_LIST,
            top_titans=top_titans,
            top_growth_leaders=top_growth_leaders,
            markets_ready=MARKETS_CACHE["ready"],
            markets_message=MARKETS_CACHE["message"]
        )

    if category_id == "mutual-funds":
        return render_template(
            "mf_detail.html",
            active="markets",
            curated_funds=CURATED_MUTUAL_FUNDS,
            all_funds=MARKETS_CACHE["mutual_funds"],
            markets_ready=MARKETS_CACHE["ready"],
            markets_message=MARKETS_CACHE["message"]
        )

    if category_id == "bonds":
        indian_bonds = MARKETS_CACHE["indian_bonds"] or [
            {"name": "India 10-Year Benchmark G-Sec", "yield_pct": 7.05, "as_of": "Daily RBI Benchmark"},
            {"name": "India 5-Year Sovereign G-Sec", "yield_pct": 6.85, "as_of": "Daily RBI Benchmark"},
            {"name": "India 91-Day Treasury Bill (T-Bill)", "yield_pct": 6.55, "as_of": "Weekly Auction"},
            {"name": "India 364-Day Treasury Bill (T-Bill)", "yield_pct": 6.75, "as_of": "Weekly Auction"},
            {"name": "India 10-Year State Dev Loan (SDL)", "yield_pct": 7.25, "as_of": "State Benchmark"},
        ]
        us_bonds = MARKETS_CACHE["us_bonds"] or [
            {"name": "US 10-Year Treasury Note", "yield_pct": 4.25, "date": "Federal Reserve (FRED)"},
            {"name": "US 2-Year Treasury Note", "yield_pct": 4.05, "date": "Federal Reserve (FRED)"},
            {"name": "US 30-Year Treasury Bond", "yield_pct": 4.50, "date": "Federal Reserve (FRED)"},
            {"name": "US 3-Month Treasury Bill", "yield_pct": 4.85, "date": "Federal Reserve (FRED)"},
        ]
        return render_template(
            "bonds_detail.html",
            active="markets",
            indian_bonds=indian_bonds,
            us_bonds=us_bonds,
            markets_ready=MARKETS_CACHE["ready"],
            markets_message=MARKETS_CACHE["message"]
        )

    if category_id == "commodities":
        top_precious = [c for c in TRACKED_COMMODITIES if c["category"] == "precious"]
        top_energy = [c for c in TRACKED_COMMODITIES if c["category"] == "energy" or c["category"] == "industrial"]
        return render_template(
            "commodities_detail.html",
            active="markets",
            commodities=TRACKED_COMMODITIES,
            top_precious=top_precious,
            top_energy=top_energy,
            gold_silver_ratio="82.4",
            markets_ready=MARKETS_CACHE["ready"],
            markets_message=MARKETS_CACHE["message"]
        )

    if category_id == "crypto" or category_id == "derivatives":
        top_crypto = [c for c in TRACKED_CRYPTO if c["symbol"] in ["BTC", "ETH", "SOL", "BNB", "XRP"]]
        options_summary = MARKETS_CACHE["options_summary"] or {
            "underlying_value": 24380.15,
            "put_call_ratio": 1.12,
            "near_strikes": [24100, 24200, 24300, 24400, 24500],
            "max_pain": 24300,
            "sentiment": "Mildly Bullish (Healthy PCR Support)"
        }
        return render_template(
            "crypto_detail.html",
            active="markets",
            crypto=TRACKED_CRYPTO,
            top_crypto=top_crypto,
            options_summary=options_summary,
            markets_ready=MARKETS_CACHE["ready"],
            markets_message=MARKETS_CACHE["message"]
        )

    if category_id == "ipos":
        enriched = []
        for ipo in MARKETS_CACHE["ipos"]:
            slug = _slugify(ipo.get("company", ""))
            enriched.append({**ipo, "slug": slug})
        return render_template(
            "ipos_hub.html",
            active="markets",
            ipos=enriched,
            markets_ready=MARKETS_CACHE["ready"],
            markets_message=MARKETS_CACHE["message"]
        )

    # Fallback to ETFs if unknown
    return render_template(
        "etf_detail.html",
        active="markets",
        etfs=TRACKED_ETFS,
        top_equity=[e for e in TRACKED_ETFS if e["symbol"] in ["SPY", "QQQ"]],
        top_commodity=[e for e in TRACKED_ETFS if e["symbol"] in ["GLD", "GOLDBEES"]],
        markets_ready=MARKETS_CACHE["ready"],
        markets_message=MARKETS_CACHE["message"]
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


def _slugify(text):
    """Turn a company name into a URL-safe slug."""
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


@app.route("/markets/ipo/<company_slug>")
def ipo_detail(company_slug):
    """Detailed IPO page for a single company."""
    ipos = MARKETS_CACHE["ipos"]

    # Attach slugs and status to every IPO
    from datetime import datetime
    today = datetime.today().date()
    enriched = []
    for ipo in ipos:
        slug = _slugify(ipo.get("company", ""))
        # Determine open/upcoming/closed status
        status = "upcoming"
        try:
            open_d = datetime.strptime(ipo.get("open_date", ""), "%d-%b-%Y").date()
            close_d = datetime.strptime(ipo.get("close_date", ""), "%d-%b-%Y").date()
            if today > close_d:
                status = "closed"
            elif open_d <= today <= close_d:
                status = "open"
        except Exception:
            pass
        enriched.append({**ipo, "slug": slug, "status": status, "lot_size": ipo.get("lot_size", "—"), "listing_date": ipo.get("listing_date", None)})

    # Find the requested IPO
    target = next((i for i in enriched if i["slug"] == company_slug), None)
    if not target:
        # Fallback: just take the first IPO if any
        if enriched:
            target = enriched[0]
        else:
            return render_template("market_detail.html", active="markets",
                                   category_id="ipos",
                                   config={
                                       "title": "IPO Calendar", "eyebrow": "Primary Market Issues",
                                       "badge": "Event Calendar", "is_live": False,
                                       "description": "Upcoming and current Initial Public Offerings listed on Indian exchanges.",
                                       "items_list": [], "type": "ipos"
                                   },
                                   markets_ready=MARKETS_CACHE["ready"],
                                   markets_message=MARKETS_CACHE["message"])

    other_ipos = [i for i in enriched if i["slug"] != company_slug][:6]

    return render_template(
        "ipo_detail.html",
        active="markets",
        ipo=target,
        other_ipos=other_ipos,
        markets_ready=MARKETS_CACHE["ready"],
        markets_message=MARKETS_CACHE["message"],
    )


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
        report_columns=reports_data.get_report_columns(period_days) if report else None,
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
