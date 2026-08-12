"""
================================================================================
 REPORTS_DATA.PY — full growth/technical report: how much did SYMBOL move,
 and what do the standard technical indicators say about it
================================================================================
Uses yfinance historical downloads directly (not the local backfilled CSVs)
because reports need arbitrary date ranges uniformly across NSE (.NS), BSE
(.BO), and US tickers.

HONESTY NOTES — read before presenting this anywhere official:
- News Sentiment uses yfinance's own `.news` feed + a small built-in
  positive/negative keyword list. It is a simple heuristic, not a trained
  NLP/sentiment model. Coverage varies a lot by ticker — many symbols will
  have zero recent articles, in which case it reports "Neutral" by default.
- AI Score / AI Trend / AI Recommendation / Confidence are a transparent,
  rule-based composite of the RSI/MACD/SMA/return signals computed in this
  same report. They are NOT the trained GRU model's output — the GRU predicts
  one price point ahead and isn't built to score a historical window. Keep
  that distinction clear in your project writeup.
- Sharpe Ratio uses a flat assumed risk-free rate (6.5% INR, 4.5% USD) —
  a simplification, not a live rate. Worth stating as an assumption.
- Beta is computed against ^NSEI (Nifty 50) for NSE/BSE tickers and ^GSPC
  (S&P 500) for US tickers. Not computed for crypto/commodities — there's no
  single obvious benchmark for those, so it's left as "—".
================================================================================
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

PERIOD_OPTIONS = [
    {"value": "7", "label": "1 Week"},
    {"value": "14", "label": "2 Weeks"},
    {"value": "30", "label": "1 Month"},
    {"value": "90", "label": "3 Months"},
    {"value": "180", "label": "6 Months"},
    {"value": "365", "label": "1 Year"},
]

_PERIOD_LABELS = {int(p["value"]): p["label"] for p in PERIOD_OPTIONS}

POS_WORDS = {
    "beat", "beats", "surge", "surges", "rally", "rallies", "gain", "gains", "up", "rise", "rises",
    "growth", "strong", "record", "upgrade", "upgraded", "outperform", "bullish", "profit", "profits",
    "positive", "boost", "jump", "jumps", "soar", "soars", "higher", "wins", "win",
}
NEG_WORDS = {
    "miss", "misses", "fall", "falls", "drop", "drops", "plunge", "plunges", "decline", "declines",
    "weak", "downgrade", "downgraded", "underperform", "bearish", "loss", "losses", "negative",
    "cut", "cuts", "lower", "crash", "crashes", "slump", "slumps", "fraud", "lawsuit", "probe", "warns",
}


def _to_yf_ticker(symbol, exchange):
    if exchange == "NSE":
        return f"{symbol}.NS"
    if exchange == "BSE":
        return f"{symbol}.BO"
    return symbol  # US, or already a raw yfinance ticker (crypto, commodities, etc.)


def _benchmark_ticker(exchange):
    if exchange in ("NSE", "BSE"):
        return "^NSEI"
    if exchange == "US":
        return "^GSPC"
    return None


def _period_label(period_days):
    return _PERIOD_LABELS.get(int(period_days), f"{period_days} Days")


def _flatten(df):
    df = df.reset_index()
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df.sort_values("Date").reset_index(drop=True)


def _rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _macd(series, fast=12, slow=26):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    return ema_fast - ema_slow


def _max_drawdown_pct(series):
    cummax = series.cummax()
    drawdown = (series - cummax) / cummax
    return float(drawdown.min() * 100)


def _simple_sentiment(headlines):
    if not headlines:
        return 0.0, "Neutral", 0
    score_total, counted = 0, 0
    for h in headlines:
        words = set(h.lower().replace(",", " ").replace(".", " ").split())
        pos, neg = len(words & POS_WORDS), len(words & NEG_WORDS)
        if pos or neg:
            score_total += (pos - neg)
            counted += 1
    if counted == 0:
        return 0.0, "Neutral", len(headlines)
    avg = score_total / counted
    score = max(-1.0, min(1.0, avg / 3))
    label = "Positive" if score > 0.15 else "Negative" if score < -0.15 else "Neutral"
    return score, label, len(headlines)


def generate_full_report(symbol, exchange, period_days):
    """Returns a dict with every field needed by both the short and long
    report column sets, or None if price history isn't available."""
    yf_ticker = _to_yf_ticker(symbol, exchange)
    period_days = int(period_days)

    end_date = datetime.today()
    lookback_buffer = max(100, period_days + 60)  # room for stable SMA50/MACD/RSI
    fetch_start = end_date - timedelta(days=period_days + lookback_buffer)

    try:
        hist = yf.download(yf_ticker, start=fetch_start.strftime("%Y-%m-%d"),
                            end=end_date.strftime("%Y-%m-%d"), progress=False)
    except Exception:
        hist = None
    if hist is None or hist.empty:
        return None
    hist = _flatten(hist)

    period_start_date = pd.Timestamp(end_date - timedelta(days=period_days))
    period_df = hist[hist["Date"] >= period_start_date]
    if len(period_df) < 2:
        period_df = hist.tail(max(2, min(len(hist), period_days)))
    if len(period_df) < 2:
        return None

    open_price = float(period_df.iloc[0]["Open"])
    high_price = float(period_df["High"].max())
    low_price = float(period_df["Low"].min())
    close_price = float(period_df.iloc[-1]["Close"])
    start_price = float(period_df.iloc[0]["Close"])
    price_change = close_price - start_price
    return_pct = (price_change / start_price * 100) if start_price else 0.0
    avg_price = float(period_df["Close"].mean())

    has_volume = "Volume" in period_df.columns
    volume_latest = float(period_df.iloc[-1]["Volume"]) if has_volume else None
    avg_volume = float(period_df["Volume"].mean()) if has_volume else None

    prev_period_start = period_start_date - timedelta(days=period_days)
    prev_period_df = hist[(hist["Date"] >= prev_period_start) & (hist["Date"] < period_start_date)]
    volume_change_pct = None
    if avg_volume and has_volume and not prev_period_df.empty:
        prev_avg_vol = float(prev_period_df["Volume"].mean())
        if prev_avg_vol:
            volume_change_pct = (avg_volume - prev_avg_vol) / prev_avg_vol * 100

    hist["rsi"] = _rsi(hist["Close"])
    hist["macd"] = _macd(hist["Close"])
    hist["sma20"] = hist["Close"].rolling(20).mean()
    hist["sma50"] = hist["Close"].rolling(50).mean()

    last_row = hist[hist["Date"] <= period_df.iloc[-1]["Date"]].iloc[-1]
    rsi_value = None if pd.isna(last_row["rsi"]) else float(last_row["rsi"])
    macd_value = None if pd.isna(last_row["macd"]) else float(last_row["macd"])
    sma20_value = None if pd.isna(last_row["sma20"]) else float(last_row["sma20"])
    sma50_value = None if pd.isna(last_row["sma50"]) else float(last_row["sma50"])

    period_returns = period_df["Close"].pct_change().dropna()
    volatility = float(period_returns.std() * (252 ** 0.5) * 100) if len(period_returns) > 1 else None
    max_drawdown = _max_drawdown_pct(period_df["Close"])

    beta_value = None
    benchmark_ticker = _benchmark_ticker(exchange)
    if benchmark_ticker and len(period_returns) > 1:
        try:
            bench_hist = _flatten(yf.download(
                benchmark_ticker, start=period_df.iloc[0]["Date"].strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"), progress=False,
            ))
            bench_returns = bench_hist["Close"].pct_change().dropna()
            n = min(len(bench_returns), len(period_returns))
            if n > 1:
                cov = np.cov(period_returns.values[-n:], bench_returns.values[-n:])[0][1]
                var = np.var(bench_returns.values[-n:])
                beta_value = float(cov / var) if var else None
        except Exception:
            beta_value = None

    risk_free_rate = 0.065 if exchange in ("NSE", "BSE") else 0.045  # assumption, not live
    sharpe_ratio = None
    if len(period_returns) > 1 and period_returns.std():
        annual_return = period_returns.mean() * 252
        annual_vol = period_returns.std() * (252 ** 0.5)
        sharpe_ratio = float((annual_return - risk_free_rate) / annual_vol)

    sentiment_score, news_sentiment, headline_count = 0.0, "Neutral", 0
    try:
        news_items = yf.Ticker(yf_ticker).news or []
        headlines = [item.get("title", "") for item in news_items if item.get("title")]
        sentiment_score, news_sentiment, headline_count = _simple_sentiment(headlines)
    except Exception:
        pass

    # Rule-based composite — see the honesty note at the top of this file.
    signals = []
    if rsi_value is not None:
        if 45 <= rsi_value <= 65:
            signals.append(0.6)
        elif rsi_value > 70:
            signals.append(-0.4)
        elif rsi_value < 30:
            signals.append(-0.2)
        else:
            signals.append(0.2)
    if macd_value is not None:
        signals.append(0.6 if macd_value > 0 else -0.6)
    if sma20_value and sma50_value:
        signals.append(0.5 if sma20_value > sma50_value else -0.5)
    if sma20_value:
        signals.append(0.4 if close_price > sma20_value else -0.4)
    signals.append(max(-1.0, min(1.0, return_pct / 10)))

    raw_score = sum(signals) / len(signals) if signals else 0.0
    ai_score = round((raw_score + 1) / 2 * 100, 1)
    ai_trend = "Bullish" if ai_score > 60 else "Bearish" if ai_score < 40 else "Neutral"
    ai_recommendation = "Buy" if ai_score > 65 else "Sell" if ai_score < 35 else "Hold"
    agreement = (sum(1 for s in signals if (s > 0) == (raw_score > 0)) / len(signals)) if signals else 0.0
    confidence = round(agreement * 100, 1)

    currency = "$" if exchange == "US" else "₹"

    def money(v): return f"{currency}{v:,.2f}" if v is not None else "—"
    def pct(v): return f"{v:+.2f}%" if v is not None else "—"
    def num(v, d=2): return f"{v:,.{d}f}" if v is not None else "—"

    # Build per-day OHLCV rows for the price-history table.
    # Adj Close is approximated as Close * (last_close / last_adj_close) when the
    # yfinance download includes an "Adj Close" column; otherwise we fall back to Close.
    has_adj = "Adj Close" in period_df.columns
    chart_points = []
    for _, row in period_df.iterrows():
        adj_c = float(row["Adj Close"]) if has_adj and not pd.isna(row.get("Adj Close")) else float(row["Close"])
        chart_points.append({
            "date":      row["Date"].strftime("%Y-%m-%d"),
            "price":     float(row["Close"]),   # kept for the SVG sparkline
            "open":      float(row["Open"]),
            "high":      float(row["High"]),
            "low":       float(row["Low"]),
            "close":     float(row["Close"]),
            "adj_close": adj_c,
            "volume":    int(row["Volume"]) if has_volume and not pd.isna(row.get("Volume")) else None,
        })

    return {
        "symbol": symbol, "exchange": exchange, "currency": currency,
        "period_label": _period_label(period_days), "period_days": period_days,
        "start_date": period_df.iloc[0]["Date"].strftime("%Y-%m-%d"),
        "end_date": period_df.iloc[-1]["Date"].strftime("%Y-%m-%d"),
        "direction": "up" if price_change >= 0 else "down",
        "chart_points": chart_points,
        "start_price": start_price, "end_price": close_price,
        "abs_change": price_change, "pct_change": return_pct,

        "open": open_price, "high": high_price, "low": low_price, "close": close_price,
        "price_change": price_change, "return_pct": return_pct, "avg_price": avg_price,
        "volume": volume_latest, "avg_volume": avg_volume, "volume_change_pct": volume_change_pct,
        "rsi": rsi_value, "macd": macd_value, "sma20": sma20_value, "sma50": sma50_value,
        "volatility": volatility, "max_drawdown": max_drawdown,
        "beta": beta_value, "sharpe_ratio": sharpe_ratio,
        "news_sentiment": news_sentiment, "sentiment_score": sentiment_score,
        "headline_count": headline_count,
        "ai_score": ai_score, "ai_trend": ai_trend,
        "ai_recommendation": ai_recommendation, "confidence": confidence,

        "open_fmt": money(open_price), "high_fmt": money(high_price),
        "low_fmt": money(low_price), "close_fmt": money(close_price),
        "avg_price_fmt": money(avg_price), "price_change_fmt": money(price_change),
        "return_pct_fmt": pct(return_pct),
        "volume_fmt": f"{volume_latest:,.0f}" if volume_latest is not None else "—",
        "avg_volume_fmt": f"{avg_volume:,.0f}" if avg_volume is not None else "—",
        "volume_change_pct_fmt": pct(volume_change_pct),
        "rsi_fmt": num(rsi_value, 1), "macd_fmt": num(macd_value, 3),
        "sma20_fmt": money(sma20_value), "sma50_fmt": money(sma50_value),
        "volatility_fmt": f"{volatility:.2f}%" if volatility is not None else "—",
        "max_drawdown_fmt": f"{max_drawdown:.2f}%" if max_drawdown is not None else "—",
        "beta_fmt": num(beta_value, 2), "sharpe_fmt": num(sharpe_ratio, 2),
        "sentiment_score_fmt": num(sentiment_score, 2),
        "ai_score_fmt": f"{ai_score:.1f}", "confidence_fmt": f"{confidence:.1f}%",
    }


# Backward-compatible name used before this file grew — points to the same function.
generate_growth_report = generate_full_report


SHORT_COLUMNS = [
    ("Stock", "symbol"), ("Period", "period_label"), ("Open", "open_fmt"), ("High", "high_fmt"),
    ("Low", "low_fmt"), ("Close", "close_fmt"), ("Price Change", "price_change_fmt"),
    ("Return %", "return_pct_fmt"), ("Volume", "volume_fmt"), ("Avg Volume", "avg_volume_fmt"),
    ("RSI", "rsi_fmt"), ("MACD", "macd_fmt"), ("Volatility", "volatility_fmt"),
    ("Max Drawdown", "max_drawdown_fmt"), ("AI Score", "ai_score_fmt"), ("AI Trend", "ai_trend"),
    ("AI Recommendation", "ai_recommendation"),
]

LONG_COLUMNS = [
    ("Stock", "symbol"), ("Period", "period_label"), ("Open", "open_fmt"), ("High", "high_fmt"),
    ("Low", "low_fmt"), ("Close", "close_fmt"), ("Price Change", "price_change_fmt"),
    ("Return %", "return_pct_fmt"), ("Average Price", "avg_price_fmt"),
    ("Volume", "volume_fmt"), ("Avg Volume", "avg_volume_fmt"), ("Volume Change %", "volume_change_pct_fmt"),
    ("RSI", "rsi_fmt"), ("SMA 20", "sma20_fmt"), ("SMA 50", "sma50_fmt"), ("MACD", "macd_fmt"),
    ("Volatility", "volatility_fmt"), ("Max Drawdown", "max_drawdown_fmt"),
    ("Beta", "beta_fmt"), ("Sharpe Ratio", "sharpe_fmt"),
    ("News Sentiment", "news_sentiment"), ("Sentiment Score", "sentiment_score_fmt"),
    ("AI Score", "ai_score_fmt"), ("AI Trend", "ai_trend"),
    ("AI Recommendation", "ai_recommendation"), ("Confidence", "confidence_fmt"),
]


def get_report_columns(period_days):
    """1 week / 2 weeks get the short set; everything longer gets the full set."""
    return SHORT_COLUMNS if int(period_days) <= 14 else LONG_COLUMNS


# ==============================================================================
# EXPORTS — PDF and Excel versions of the same report data
# ==============================================================================

def _rows_with_change(report):
    rows = []
    prev = None
    for pt in report["chart_points"]:
        change = (pt["price"] - prev) if prev is not None else None
        rows.append({"date": pt["date"], "price": pt["price"], "change": change})
        prev = pt["price"]
    return rows


def build_pdf_report(report):
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=f"{report['symbol']} Report")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Report — {report['symbol']} ({report['exchange']}) — {report['period_label']}", styles["Title"]))
    elements.append(Spacer(1, 10))

    columns = get_report_columns(report["period_days"])
    metric_rows = [["Metric", "Value"]] + [[label, str(report.get(key, "—"))] for label, key in columns[2:]]
    metrics_table = Table(metric_rows, colWidths=[180, 250])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#141C30")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Price History", styles["Heading3"]))
    price_rows = [["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]]
    cur = report["currency"]
    for pt in report["chart_points"]:
        vol_str = f"{pt['volume']:,}" if pt.get("volume") is not None else "—"
        price_rows.append([
            pt["date"],
            f"{cur}{pt['open']:.2f}",
            f"{cur}{pt['high']:.2f}",
            f"{cur}{pt['low']:.2f}",
            f"{cur}{pt['close']:.2f}",
            f"{pt['adj_close']:.8g}",
            vol_str,
        ])
    price_table = Table(price_rows, colWidths=[70, 65, 65, 65, 65, 80, 60])
    price_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#141C30")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    elements.append(price_table)
    elements.append(Spacer(1, 16))
    elements.append(Paragraph(
        "AI Score/Trend/Recommendation are a rule-based composite of the technical indicators above, "
        "not the trained model's output. News Sentiment is a simple keyword heuristic, not an NLP model. "
        "Generated for educational purposes only — not investment advice.",
        styles["Italic"],
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_excel_report(report):
    import io
    buffer = io.BytesIO()

    columns = get_report_columns(report["period_days"])
    metrics_df = pd.DataFrame([{label: report.get(key, "—") for label, key in columns}])
    price_df = pd.DataFrame([
        {
            "Date": pt["date"],
            "Open": pt["open"],
            "High": pt["high"],
            "Low": pt["low"],
            "Close": pt["close"],
            "Adj Close": pt["adj_close"],
            "Volume": pt["volume"] if pt["volume"] is not None else "",
        }
        for pt in report["chart_points"]
    ])

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        metrics_df.to_excel(writer, sheet_name="Report", index=False)
        price_df.to_excel(writer, sheet_name="Price History", index=False)

    buffer.seek(0)
    return buffer
