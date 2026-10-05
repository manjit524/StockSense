"""
================================================================================
 INTRADAY SIGNAL SCANNER (separate from the long-term advisor)
================================================================================
Why this is a different approach from your GRU model:
Your long-term model predicts one point ~30 daily candles ahead — that works
because daily closes have enough history to learn from. Intraday data (1m/5m
candles) is only available for the last few days/weeks from free sources, which
isn't enough to train a deep model reliably. So instead, this script uses
proven technical-indicator signals (EMA crossover, RSI, VWAP) computed live —
more reliable with the limited intraday history you can actually get for free.

Data source: yfinance for now (you said this is fine until you get broker API
access — e.g. Zerodha Kite Connect — at which point swap fetch_intraday()
below to call that API instead; everything downstream stays the same).
================================================================================
"""

import warnings
warnings.filterwarnings('ignore')
import yfinance as yf
import pandas as pd

# ==============================================================================
# CONFIG
# ==============================================================================
# Use .NS for NSE tickers, .BO for BSE tickers, no suffix for US tickers.
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS",
    "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "TATAMOTORS.NS", "WIPRO.NS",
    "ADANIENT.NS", "BAJFINANCE.NS", "HINDUNILVR.NS", "ONGC.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS", "TECHM.NS",
]

INTERVAL = "5m"   # yfinance intraday intervals: 1m, 2m, 5m, 15m, 30m, 60m
PERIOD = "5d"     # yfinance limits intraday history — 5m data caps around 60 days


def fetch_intraday(ticker):
    """Pulls recent intraday candles for a ticker. Swap this out for a broker API later."""
    df = yf.download(ticker, period=PERIOD, interval=INTERVAL, progress=False)
    if df.empty:
        return df
    df = df.reset_index()
    df.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower() for c in df.columns]
    return df


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


def build_intraday_snapshot(tickers):
    """
    Scans every ticker and returns a DataFrame with current price, signal,
    intraday volatility, and a risk bucket — the same shape of analysis
    your long-term advisor produces, but computed from live intraday candles.
    """
    print("🛸 Scanning tickers for intraday signals...")
    rows = []
    for ticker in tickers:
        try:
            df = fetch_intraday(ticker)
            if df.empty or len(df) < 25:
                print(f"⚠️  {ticker}: insufficient intraday data, skipping")
                continue

            df = compute_indicators(df)
            signal, reasons, latest = generate_signal(df)

            # Momentum strength: how far EMA9 has diverged from EMA21, used to rank BUYs
            momentum = (latest['ema_9'] - latest['ema_21']) / latest['ema_21']

            # Intraday volatility: std of 5m returns over the session, used for risk bucketing
            intraday_volatility = df['close'].pct_change().std()
            if pd.isna(intraday_volatility):
                intraday_volatility = 0.0

            rows.append({
                'symbol': ticker,
                'current_price': latest['close'],
                'signal': signal,
                'momentum': momentum,
                'volatility': intraday_volatility,
                'rsi': latest['rsi'],
                'reasons': "; ".join(reasons),
            })
        except Exception as e:
            print(f"⚠️  {ticker}: error - {e}")

    snapshot = pd.DataFrame(rows)
    if not snapshot.empty:
        low_thresh = snapshot['volatility'].quantile(0.33)
        high_thresh = snapshot['volatility'].quantile(0.66)

        def classify_risk(v):
            if v <= low_thresh:
                return 'Low Risk'
            elif v <= high_thresh:
                return 'Medium Risk'
            return 'High Risk'

        snapshot['risk_category'] = snapshot['volatility'].apply(classify_risk)

    return snapshot


def run_portfolio_suggestion(snapshot):
    try:
        capital = float(input("\nEnter the amount you want to invest in intraday trading (one-time, ₹): "))
    except ValueError:
        print("⚠️ Invalid input. Defaulting to ₹20,000.")
        capital = 20000.0

    print("\nWhich risk level do you want suggestions for?")
    print(" 1. Low Risk")
    print(" 2. Medium Risk")
    print(" 3. High Risk")
    print(" 4. Show all three")
    risk_choice = input("Select an option (1-4): ").strip()

    risk_map = {'1': ['Low Risk'], '2': ['Medium Risk'], '3': ['High Risk']}
    risk_filter = risk_map.get(risk_choice, ['Low Risk', 'Medium Risk', 'High Risk'])

    # Only recommend stocks with an active BUY signal — SELL/HOLD aren't "buy now" candidates
    buy_pool = snapshot[(snapshot['signal'] == 'BUY') & (snapshot['current_price'] <= capital)].copy()

    if buy_pool.empty:
        print("\nNo BUY-signal stocks currently fit your budget. Try a larger amount, "
              "or re-run the scan later — intraday signals change through the session.")
        return

    buy_pool['shares_to_buy'] = (capital // buy_pool['current_price']).astype(int)
    buy_pool['invested_capital'] = buy_pool['shares_to_buy'] * buy_pool['current_price']
    buy_pool['leftover_cash'] = capital - buy_pool['invested_capital']

    output_cols = ['symbol', 'current_price', 'shares_to_buy', 'leftover_cash', 'rsi', 'reasons']
    formatters = {
        'current_price': '₹{:.2f}'.format,
        'leftover_cash': '₹{:.2f}'.format,
        'rsi': '{:.1f}'.format,
    }

    print("\n" + "=" * 110)
    print(f" 💹 INTRADAY PORTFOLIO SUGGESTION — Capital: ₹{capital:,.2f}")
    print("=" * 110)

    for risk in ['Low Risk', 'Medium Risk', 'High Risk']:
        if risk not in risk_filter:
            continue
        bucket = buy_pool[buy_pool['risk_category'] == risk].sort_values(by='momentum', ascending=False).head(5)
        icon = {'Low Risk': '🟢', 'Medium Risk': '🟡', 'High Risk': '🔴'}[risk]
        print(f"\n{icon} [{risk.upper()}] — sorted by strongest bullish momentum")
        if not bucket.empty:
            print(bucket[output_cols].to_string(index=False, formatters=formatters))
        else:
            print("No BUY-signal stocks in this risk band fit your budget right now.")

    print("\n⚠️  Rule-based intraday signals, not a trained model — not investment advice.")
    print("    Prices and signals shift fast intraday; re-scan before acting, and always use stop-losses.")


if __name__ == "__main__":
    market_snapshot = build_intraday_snapshot(TICKERS)
    if not market_snapshot.empty:
        run_portfolio_suggestion(market_snapshot)
    else:
        print("❌ No usable intraday data retrieved for any ticker.")
