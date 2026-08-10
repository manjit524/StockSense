"""
================================================================================
 INTRADAY ENGINE — importable core logic for the intraday scanner
================================================================================
Same logic as intraday_advisor.py, refactored to return data structures
instead of printing, so Flask can render it. Runs live yfinance calls per
scan — swap fetch_intraday() for a broker API later, same as the CLI version.
================================================================================
"""

import warnings
warnings.filterwarnings('ignore')
import yfinance as yf
import pandas as pd

TICKERS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS",
    "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "TATAMOTORS.NS", "WIPRO.NS",
    "ADANIENT.NS", "BAJFINANCE.NS", "HINDUNILVR.NS", "ONGC.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS", "TECHM.NS",
]

INTERVAL = "5m"
PERIOD = "5d"


def fetch_intraday_batch(tickers):
    """
    One batched yfinance call for ALL tickers instead of one call per ticker —
    this is the main speed fix. Returns {ticker: dataframe}.
    """
    try:
        data = yf.download(
            tickers=tickers, period=PERIOD, interval=INTERVAL,
            group_by="ticker", progress=False, threads=True,
        )
    except Exception:
        return {}

    result = {}
    for ticker in tickers:
        try:
            df = data[ticker] if len(tickers) > 1 else data
            df = df.dropna(how="all").reset_index()
            df.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower() for c in df.columns]
            if not df.empty:
                result[ticker] = df
        except Exception:
            continue
    return result


def compute_indicators(df):
    df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()

    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    return df


def generate_signal(df):
    latest = df.iloc[-1]
    reasons = []

    if latest['ema_9'] > latest['ema_21']:
        signal = "BUY"
        reasons.append("EMA9 above EMA21 (short-term uptrend)")
    else:
        signal = "SELL"
        reasons.append("EMA9 below EMA21 (short-term downtrend)")

    if latest['rsi'] > 70:
        reasons.append("RSI overbought (>70)")
        if signal == "BUY":
            signal = "HOLD"
    elif latest['rsi'] < 30:
        reasons.append("RSI oversold (<30)")
        if signal == "SELL":
            signal = "HOLD"

    if latest['close'] > latest['vwap']:
        reasons.append("Price above VWAP (bullish bias)")
    else:
        reasons.append("Price below VWAP (bearish bias)")

    return signal, reasons, latest


def build_intraday_snapshot(tickers=TICKERS):
    rows = []
    batch = fetch_intraday_batch(tickers)

    for ticker, df in batch.items():
        try:
            if df.empty or len(df) < 25:
                continue
            df = compute_indicators(df)
            signal, reasons, latest = generate_signal(df)
            momentum = (latest['ema_9'] - latest['ema_21']) / latest['ema_21']
            volatility = df['close'].pct_change().std()
            if pd.isna(volatility):
                volatility = 0.0

            rows.append({
                'symbol': ticker,
                'current_price': float(latest['close']),
                'signal': signal,
                'momentum': float(momentum),
                'volatility': float(volatility),
                'rsi': float(latest['rsi']) if not pd.isna(latest['rsi']) else 50.0,
                'reasons': reasons,
            })
        except Exception:
            continue

    snapshot = pd.DataFrame(rows)
    if not snapshot.empty:
        low_thresh = snapshot['volatility'].quantile(0.33)
        high_thresh = snapshot['volatility'].quantile(0.66)

        def classify(v):
            if v <= low_thresh:
                return 'Low Risk'
            elif v <= high_thresh:
                return 'Medium Risk'
            return 'High Risk'

        snapshot['risk_category'] = snapshot['volatility'].apply(classify)
    return snapshot


def get_intraday_recommendations(snapshot, capital, risk_filter):
    """risk_filter: list of 'Low Risk' / 'Medium Risk' / 'High Risk' to include."""
    if snapshot.empty:
        return {'Low Risk': [], 'Medium Risk': [], 'High Risk': []}

    buy_pool = snapshot[(snapshot['signal'] == 'BUY') & (snapshot['current_price'] <= capital)].copy()
    if buy_pool.empty:
        return {'Low Risk': [], 'Medium Risk': [], 'High Risk': []}

    buy_pool['shares_to_buy'] = (capital // buy_pool['current_price']).astype(int)
    buy_pool['invested_capital'] = buy_pool['shares_to_buy'] * buy_pool['current_price']
    buy_pool['leftover_cash'] = capital - buy_pool['invested_capital']

    buckets = {}
    for risk in ['Low Risk', 'Medium Risk', 'High Risk']:
        if risk not in risk_filter:
            buckets[risk] = None  # not requested — template shows it differently than "0 matches"
            continue
        bucket = buy_pool[buy_pool['risk_category'] == risk].sort_values('momentum', ascending=False).head(5)
        buckets[risk] = bucket.to_dict('records')

    return buckets
