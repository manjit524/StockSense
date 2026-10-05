"""
================================================================================
 MULTI-EXCHANGE AI STOCK ADVISOR (NSE + BSE + US)
================================================================================
- Keeps your existing static NSE/BSE CSVs untouched as the historical base.
- Backfills NSE + BSE from BACKFILL_START_DATE to today using the exchanges'
  own official daily Bhavcopy files (free, no API key, real exchange data).
- Backfills US stocks from BACKFILL_START_DATE to today using the Twelve Data
  API (free tier, requires a free API key — no yfinance).
- Trains the GRU model on the combined pool and runs the same portfolio
  advisor flow as before, now currency-aware (₹ for NSE/BSE, $ for US).

NOTE ON RELIABILITY: NSE/BSE Bhavcopy URLs and column names are set by the
exchanges and occasionally change format. If a backfill run suddenly returns
no data, check the exchange's official Bhavcopy page and adjust the URL/
column names in get_nse_bhavcopy() / get_bse_bhavcopy() below.
================================================================================
"""

import os
import glob
import io
import time
import warnings
import requests
import numpy as np
import pandas as pd
from datetime import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GRU, Dropout
from sklearn.preprocessing import MinMaxScaler

print("✅ Cell 1 Ready: Libraries imported successfully.")

# ==============================================================================
# CONFIG — update these
# ==============================================================================
NSE_FOLDER = "C:/Ved/project/Model/Market_Data/NSE"
BSE_FOLDER = "C:/Ved/project/Model/Market_Data/BSE"
US_FOLDER = "C:/Ved/project/Model/Market_Data/US"   # will be created automatically

TWELVE_DATA_API_KEY = "f2a2afa08f944f429637b64d23044e13"   # sign up free at https://twelvedata.com

# Your static NSE/BSE data covers Jan 2026, so backfill picks up from Feb 2026.
BACKFILL_START_DATE = "2026-02-01"
BACKFILL_END_DATE = datetime.today().strftime("%Y-%m-%d")

# Seed list of US tickers to track — pulled from us_tickers.py, which fetches
# the real, current S&P 500 constituent list (~500 tickers) from a public
# dataset and caches it, rather than hand-typing hundreds of symbols.
import us_tickers

US_TICKERS_TO_TRACK = us_tickers.get_sp500_tickers()
print(f"💹 Tracking {len(US_TICKERS_TO_TRACK)} US tickers.")

os.makedirs(US_FOLDER, exist_ok=True)

# ==============================================================================
# NSE / BSE BACKFILL — official daily Bhavcopy (free, no key)
# ==============================================================================

def get_nse_bhavcopy(date_obj, session):
    """Downloads NSE full equity bhavcopy for one date. Returns None on holidays/weekends/errors."""
    date_str = date_obj.strftime("%d%m%Y")
    url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code != 200 or len(resp.content) < 500:
            return None
        df = pd.read_csv(io.BytesIO(resp.content))
        df.columns = [c.strip().upper() for c in df.columns]
        df = df[df['SERIES'].astype(str).str.strip() == 'EQ']
        out = pd.DataFrame({
            'date': date_obj.strftime("%Y-%m-%d"),
            'symbol': df['SYMBOL'].astype(str).str.strip().str.upper(),
            'close': pd.to_numeric(df['CLOSE_PRICE'], errors='coerce')
        }).dropna()
        return out
    except Exception:
        return None


def get_bse_bhavcopy(date_obj, session):
    """Downloads BSE full equity bhavcopy for one date. Returns None on holidays/weekends/errors."""
    date_str = date_obj.strftime("%d%m%y")
    url = f"https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISO_{date_str}.CSV"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code != 200 or len(resp.content) < 500:
            return None
        df = pd.read_csv(io.BytesIO(resp.content))
        df.columns = [c.strip().upper() for c in df.columns]
        symbol_col = 'TCKR_SYMB' if 'TCKR_SYMB' in df.columns else 'SC_NAME'
        close_col = 'CLSG_PRIC' if 'CLSG_PRIC' in df.columns else 'CLOSE'
        out = pd.DataFrame({
            'date': date_obj.strftime("%Y-%m-%d"),
            'symbol': df[symbol_col].astype(str).str.strip().str.upper(),
            'close': pd.to_numeric(df[close_col], errors='coerce')
        }).dropna()
        return out
    except Exception:
        return None


def _merge_into_symbol_files(new_data_df, folder):
    """Appends new (date, close) rows into each symbol's CSV in `folder`, de-duped by date."""
    os.makedirs(folder, exist_ok=True)
    for symbol, group in new_data_df.groupby('symbol'):
        file_path = os.path.join(folder, f"{symbol}.csv")
        new_rows = group[['date', 'close']].copy()
        if os.path.exists(file_path):
            existing = pd.read_csv(file_path)
            existing.columns = existing.columns.str.lower()
            date_col = 'datetime' if 'datetime' in existing.columns else 'date'
            existing = existing.rename(columns={date_col: 'date'})
            combined = pd.concat([existing[['date', 'close']], new_rows], ignore_index=True)
            combined = combined.drop_duplicates(subset='date', keep='last')
        else:
            combined = new_rows
        combined = combined.sort_values('date')
        combined.to_csv(file_path, index=False)


def backfill_nse_bse(nse_folder, bse_folder, start_date, end_date):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        session.get("https://www.nseindia.com", timeout=10)  # sets cookies NSE expects
    except Exception:
        pass

    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    nse_frames, bse_frames = [], []

    print(f"🔄 Backfilling NSE + BSE from {start_date} to {end_date} ({len(dates)} business days to check)...")
    for i, d in enumerate(dates):
        nse_day = get_nse_bhavcopy(d, session)
        if nse_day is not None:
            nse_frames.append(nse_day)
        bse_day = get_bse_bhavcopy(d, session)
        if bse_day is not None:
            bse_frames.append(bse_day)
        time.sleep(1)  # be polite to exchange servers
        if (i + 1) % 10 == 0:
            print(f"   ...checked {i + 1}/{len(dates)} days")

    if nse_frames:
        _merge_into_symbol_files(pd.concat(nse_frames, ignore_index=True), nse_folder)
        print(f"✅ NSE: merged data from {len(nse_frames)} trading days.")
    else:
        print("⚠️ NSE: no new data retrieved (check network access / bhavcopy URL format).")

    if bse_frames:
        _merge_into_symbol_files(pd.concat(bse_frames, ignore_index=True), bse_folder)
        print(f"✅ BSE: merged data from {len(bse_frames)} trading days.")
    else:
        print("⚠️ BSE: no new data retrieved (check network access / bhavcopy URL format).")


# ==============================================================================
# US STOCK BACKFILL — Twelve Data API (free tier, requires key)
# ==============================================================================

def backfill_us_stocks(us_folder, tickers, api_key, start_date, end_date):
    """
    Pulls daily close history for US tickers from Twelve Data and writes one
    CSV per symbol. Throttled for free-tier rate limits; on error for a symbol
    it skips and moves on so partial progress is preserved.
    """
    if api_key == "f2a2afa08f944f429637b64d23044e13":
        print("⚠️ US backfill skipped: set TWELVE_DATA_API_KEY to your real free API key first.")
        return

    print(f"🔄 Fetching US stock data for {len(tickers)} tickers via Twelve Data...")
    today_str = datetime.today().strftime("%Y-%m-%d")
    skipped = 0

    for i, ticker in enumerate(tickers):
        existing_path = os.path.join(us_folder, f"{ticker}.csv")
        if os.path.exists(existing_path):
            try:
                existing_df = pd.read_csv(existing_path)
                if not existing_df.empty and existing_df['date'].astype(str).str.contains(today_str).any():
                    skipped += 1
                    continue  # already have today's data for this ticker
            except Exception:
                pass

        try:
            resp = requests.get(
                "https://api.twelvedata.com/time_series",
                params={
                    "symbol": ticker,
                    "interval": "1day",
                    "start_date": start_date,
                    "end_date": end_date,
                    "apikey": api_key,
                    "outputsize": 5000,
                    "format": "JSON",
                },
                timeout=15,
            )
            data = resp.json()
            if "values" not in data:
                print(f"   ⚠️ Skipped {ticker}: {data.get('message', 'no data returned')}")
                continue

            df = pd.DataFrame(data["values"]).rename(columns={"datetime": "date"})
            df["close"] = pd.to_numeric(df["close"], errors="coerce")
            df = df[["date", "close"]].dropna().sort_values("date")
            df.to_csv(os.path.join(us_folder, f"{ticker}.csv"), index=False)

        except Exception as e:
            print(f"   ⚠️ Error fetching {ticker}: {e}")

        time.sleep(8)  # stay safely under free-tier per-minute limits
        if (i + 1) % 5 == 0:
            print(f"   ...fetched {i + 1}/{len(tickers)} tickers")

    print(f"✅ US stock backfill complete — {skipped} tickers skipped (already had today's data). See console for any fetch errors.")


# ==============================================================================
# RUN BACKFILL (comment out either line if you only need to refresh one side)
# ==============================================================================
backfill_nse_bse(NSE_FOLDER, BSE_FOLDER, BACKFILL_START_DATE, BACKFILL_END_DATE)
backfill_us_stocks(US_FOLDER, US_TICKERS_TO_TRACK, TWELVE_DATA_API_KEY, BACKFILL_START_DATE, BACKFILL_END_DATE)

# ==============================================================================
# BUILD TICKER REGISTRY (NSE + BSE + US)
# ==============================================================================
nse_files = glob.glob(os.path.join(NSE_FOLDER, "*.csv"))
bse_files = glob.glob(os.path.join(BSE_FOLDER, "*.csv"))
us_files = glob.glob(os.path.join(US_FOLDER, "*.csv"))

unique_ticker_registry = {}
for file in nse_files:
    symbol = os.path.splitext(os.path.basename(file))[0].upper()
    unique_ticker_registry[symbol] = {'path': file, 'exchange': 'NSE'}
for file in bse_files:
    symbol = os.path.splitext(os.path.basename(file))[0].upper()
    if symbol not in unique_ticker_registry:
        unique_ticker_registry[symbol] = {'path': file, 'exchange': 'BSE'}
for file in us_files:
    symbol = os.path.splitext(os.path.basename(file))[0].upper()
    key = f"US_{symbol}"  # prefix avoids collisions with same-named Indian tickers
    if key not in unique_ticker_registry:
        unique_ticker_registry[key] = {'path': file, 'exchange': 'US'}

print("\n--- 🗂️ EXCHANGE REGISTRY SUMMARY ---")
print(f"Total Unique Tickers Registered: {len(unique_ticker_registry)}")
for exch in ['NSE', 'BSE', 'US']:
    print(f" -> {exch} Unique Files Linked: {sum(1 for x in unique_ticker_registry.values() if x['exchange'] == exch)}")

# ==============================================================================
# MODEL SETUP
# ==============================================================================
time_steps = 30
scaler = MinMaxScaler(feature_range=(0, 1))

with tf.device('/CPU:0'):
    model = Sequential([
        GRU(units=32, activation='tanh', return_sequences=True, input_shape=(time_steps, 1)),
        Dropout(0.2),
        GRU(units=16, activation='tanh'),
        Dropout(0.2),
        Dense(units=1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')

# ==============================================================================
# TRAIN ON POOLED MULTI-EXCHANGE SAMPLE
# ==============================================================================
print("🔄 Training GRU model across a diverse multi-exchange sample pool...")
X_train_pool, y_train_pool = [], []
processed_count = 0

for meta in list(unique_ticker_registry.values())[:150]:
    file = meta['path']
    try:
        sample_df = pd.read_csv(file)
        if len(sample_df) < (time_steps + 20):
            continue

        sample_df.columns = sample_df.columns.str.lower()
        date_col = 'datetime' if 'datetime' in sample_df.columns else 'date'

        sample_df = sample_df.dropna(subset=['close'])
        sample_df = sample_df[sample_df['close'] > 0]

        if 'close' in sample_df.columns and date_col in sample_df.columns:
            sample_series = sample_df.sort_values(date_col)['close'].values.reshape(-1, 1)
            train_scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_series = train_scaler.fit_transform(sample_series)

            for i in range(len(scaled_series) - time_steps):
                X_train_pool.append(scaled_series[i:(i + time_steps)])
                y_train_pool.append(scaled_series[i + time_steps])

            processed_count += 1
    except Exception:
        continue

if X_train_pool:
    X_train = np.array(X_train_pool)
    y_train = np.array(y_train_pool)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    print(f"🧠 Training on {X_train.shape[0]} sequence samples from {processed_count} companies...")
    with tf.device('/CPU:0'):
        model.fit(X_train, y_train, epochs=5, batch_size=128, verbose=1)
    print("✨ Multi-asset model training complete!")
else:
    print("❌ ERROR: Training data compilation failed. Check file access.")

# ==============================================================================
# EVALUATE ALL TICKERS
# ==============================================================================
processed_stocks = []
print(f"🛸 Starting bulk evaluation loop across {len(unique_ticker_registry)} unique tickers...")

for index, (symbol, meta) in enumerate(unique_ticker_registry.items()):
    file_path = meta['path']
    exchange_source = meta['exchange']
    try:
        temp_df = pd.read_csv(file_path)
        if temp_df.empty or len(temp_df) < time_steps:
            continue

        temp_df.columns = temp_df.columns.str.lower()
        date_col = 'datetime' if 'datetime' in temp_df.columns else 'date'
        if 'close' not in temp_df.columns or date_col not in temp_df.columns:
            continue

        temp_df[date_col] = pd.to_datetime(temp_df[date_col])
        temp_df = temp_df.sort_values(date_col)

        current_price = temp_df['close'].iloc[-1]

        temp_df['daily_return'] = temp_df['close'].pct_change()
        volatility = temp_df['daily_return'].std() * np.sqrt(252)
        if pd.isna(volatility) or np.isinf(volatility):
            volatility = 0.0

        recent_window = temp_df['close'].values[-time_steps:].reshape(-1, 1)
        local_scaler = MinMaxScaler(feature_range=(0, 1))
        local_scaler.fit(temp_df['close'].values.reshape(-1, 1))
        scaled_window = local_scaler.transform(recent_window)

        rnn_input = np.reshape(scaled_window, (1, time_steps, 1))
        with tf.device('/CPU:0'):
            predicted_scaled = model.predict(rnn_input, verbose=0)
        predicted_price = local_scaler.inverse_transform(predicted_scaled)[0][0]

        base_annual_growth = (predicted_price - current_price) / current_price
        base_annual_growth = np.clip(base_annual_growth, -0.40, 0.60)

        processed_stocks.append({
            'symbol': symbol.replace('US_', ''),
            'exchange': exchange_source,
            'current_price': current_price,
            'volatility': volatility,
            'base_growth': base_annual_growth
        })

        if (index + 1) % 500 == 0:
            print(f"🔄 Processed {index + 1} / {len(unique_ticker_registry)} files...")
    except Exception:
        continue

master_df = pd.DataFrame(processed_stocks)
if not master_df.empty:
    low_thresh = master_df['volatility'].quantile(0.33)
    high_thresh = master_df['volatility'].quantile(0.66)

    def classify_risk(v):
        if v <= low_thresh:
            return 'Low Risk'
        elif v <= high_thresh:
            return 'Medium Risk'
        return 'High Risk'

    master_df['risk_category'] = master_df['volatility'].apply(classify_risk)
    print(f"\n✨ Framework successfully cached for {len(master_df)} distinct master tickers.")
else:
    print("\n❌ Error: Analytics matrix compilation failed.")

# ==============================================================================
# PORTFOLIO PREFERENCE CONFIGURATOR
# ==============================================================================
print("--- 🛠️ PORTFOLIO PREFERENCE CONFIGURATOR ---")
print("Choose Exchange Pool:")
print(" 1. NSE Only")
print(" 2. BSE Only")
print(" 3. Hybrid: NSE + BSE")
print(" 4. US Only")
print(" 5. Global Hybrid (NSE + BSE + US)")
exchange_choice = input("Select preference option (1-5): ").strip()

try:
    user_capital = float(input("Enter your One-time Capital Budget: "))
    investment_years = float(input("Enter your Investment Horizon (in Years): "))
except ValueError:
    print("⚠️ Invalid numeric input. Defaulting to Capital: 50,000, Horizon: 5 Years.")
    user_capital = 50000.0
    investment_years = 5.0

working_df = master_df.copy()
if exchange_choice == '1':
    working_df = working_df[working_df['exchange'] == 'NSE']
    selection_tag = "NSE EXCLUSIVE"
elif exchange_choice == '2':
    working_df = working_df[working_df['exchange'] == 'BSE']
    selection_tag = "BSE EXCLUSIVE"
elif exchange_choice == '3':
    working_df = working_df[working_df['exchange'].isin(['NSE', 'BSE'])]
    selection_tag = "HYBRID POOL (NSE + BSE)"
elif exchange_choice == '4':
    working_df = working_df[working_df['exchange'] == 'US']
    selection_tag = "US EXCLUSIVE"
else:
    selection_tag = "GLOBAL HYBRID (NSE + BSE + US)"

if exchange_choice == '5':
    print("⚠️ Note: Global Hybrid compares raw price magnitudes across ₹ and $ without "
          "FX conversion — treat cross-currency comparisons with caution.")

print("\n" + "=" * 120)
print(f" 💹 GENERATING MATRIX [{selection_tag}]: {user_capital:,.2f} over {investment_years} Year(s)")
print("=" * 120 + "\n")

filtered_pool = working_df[(working_df['current_price'] <= user_capital) & (working_df['current_price'] >= 1.0)].copy()

if not filtered_pool.empty:
    filtered_pool['shares_to_buy'] = (user_capital // filtered_pool['current_price']).astype(int)
    filtered_pool['invested_capital'] = filtered_pool['shares_to_buy'] * filtered_pool['current_price']
    filtered_pool['leftover_cash'] = user_capital - filtered_pool['invested_capital']

    def calculate_metrics(row):
        total_growth_factor = (1 + row['base_growth']) ** investment_years
        future_invested_value = row['invested_capital'] * total_growth_factor
        return future_invested_value - row['invested_capital']

    filtered_pool['net_profit'] = filtered_pool.apply(calculate_metrics, axis=1)

    def ccy(exchange):
        return '$' if exchange == 'US' else '₹'

    filtered_pool['ccy'] = filtered_pool['exchange'].apply(ccy)
    filtered_pool['current_price_fmt'] = filtered_pool.apply(lambda r: f"{r['ccy']}{r['current_price']:.2f}", axis=1)
    filtered_pool['leftover_cash_fmt'] = filtered_pool.apply(lambda r: f"{r['ccy']}{r['leftover_cash']:.2f}", axis=1)
    filtered_pool['net_profit_fmt'] = filtered_pool.apply(lambda r: f"{r['ccy']}{r['net_profit']:+,.2f}", axis=1)

    output_cols = ['symbol', 'exchange', 'current_price_fmt', 'shares_to_buy', 'leftover_cash_fmt', 'net_profit_fmt']
    display_names = {'current_price_fmt': 'current_price', 'leftover_cash_fmt': 'leftover_cash', 'net_profit_fmt': 'net_profit'}

    low_risk_bucket = filtered_pool[filtered_pool['risk_category'] == 'Low Risk'].sort_values(by='base_growth', ascending=False).head(5)
    med_risk_bucket = filtered_pool[filtered_pool['risk_category'] == 'Medium Risk'].sort_values(by='base_growth', ascending=False).head(5)
    high_risk_bucket = filtered_pool[filtered_pool['risk_category'] == 'High Risk'].sort_values(by='base_growth', ascending=False).head(5)

    print("🟢 [LOW RISK PROFILE] — Capital Preservation & Stable Compounding")
    print(low_risk_bucket[output_cols].rename(columns=display_names).to_string(index=False) if not low_risk_bucket.empty else "No assets matched your requirements.")

    print("\n🟡 [MEDIUM RISK PROFILE] — Core Structural Balanced Growth")
    print(med_risk_bucket[output_cols].rename(columns=display_names).to_string(index=False) if not med_risk_bucket.empty else "No assets matched your requirements.")

    print("\n🔴 [HIGH RISK PROFILE] — High-Yield Aggressive Momentum")
    print(high_risk_bucket[output_cols].rename(columns=display_names).to_string(index=False) if not high_risk_bucket.empty else "No assets matched your requirements.")

    print("\n⚠️  Disclaimer: this is a demo model with a small, lightly-trained GRU network — "
          "treat outputs as illustrative, not real investment advice.")
else:
    print("No matching securities found below your capital threshold.")
