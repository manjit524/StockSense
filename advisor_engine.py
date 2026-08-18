"""
================================================================================
 ADVISOR ENGINE — importable core logic for the multi-exchange advisor
================================================================================
This is your stock_advisor_multi_exchange.py logic refactored so a Flask app
can call it without hitting input() prompts or retraining the model on every
request. Backfill (Bhavcopy / Twelve Data) is NOT run automatically here —
run stock_advisor_multi_exchange.py (or call run_backfill() below) on a
schedule to keep the underlying CSVs fresh, then the website just reads
whatever's on disk.
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
from concurrent.futures import ThreadPoolExecutor, as_completed

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GRU, Dropout
from sklearn.preprocessing import MinMaxScaler

# ==============================================================================
# CONFIG — same as your standalone script
# ==============================================================================
NSE_FOLDER = "C:/Ved/project/Model/Market_Data/NSE"
BSE_FOLDER = "C:/Ved/project/Model/Market_Data/BSE"
US_FOLDER = "C:/Ved/project/Model/Market_Data/US"

TWELVE_DATA_API_KEY = "f2a2afa08f944f429637b64d23044e13"
TIME_STEPS = 30
MODEL_PATH = "advisor_model.keras"
MASTER_DF_CACHE_PATH = "master_df_cache.pkl"
MASTER_DF_CACHE_MAX_AGE_HOURS = 12  # recompute at most twice a day, not on every restart

os.makedirs(US_FOLDER, exist_ok=True)


# ==============================================================================
# BACKFILL (same logic as the standalone script — call manually / on a schedule)
# ==============================================================================

def get_nse_bhavcopy(date_obj, session):
    date_str = date_obj.strftime("%d%m%Y")
    url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code != 200 or len(resp.content) < 500:
            return None
        df = pd.read_csv(io.BytesIO(resp.content))
        df.columns = [c.strip().upper() for c in df.columns]
        df = df[df['SERIES'].astype(str).str.strip() == 'EQ']
        return pd.DataFrame({
            'date': date_obj.strftime("%Y-%m-%d"),
            'symbol': df['SYMBOL'].astype(str).str.strip().str.upper(),
            'close': pd.to_numeric(df['CLOSE_PRICE'], errors='coerce')
        }).dropna()
    except Exception:
        return None


def get_bse_bhavcopy(date_obj, session):
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
        return pd.DataFrame({
            'date': date_obj.strftime("%Y-%m-%d"),
            'symbol': df[symbol_col].astype(str).str.strip().str.upper(),
            'close': pd.to_numeric(df[close_col], errors='coerce')
        }).dropna()
    except Exception:
        return None


def _merge_into_symbol_files(new_data_df, folder):
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
        combined.sort_values('date').to_csv(file_path, index=False)


def run_backfill(start_date, end_date=None):
    end_date = end_date or datetime.today().strftime("%Y-%m-%d")
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    })
    try:
        session.get("https://www.nseindia.com", timeout=10)
    except Exception:
        pass

    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    nse_frames, bse_frames = [], []
    for d in dates:
        nse_day = get_nse_bhavcopy(d, session)
        if nse_day is not None:
            nse_frames.append(nse_day)
        bse_day = get_bse_bhavcopy(d, session)
        if bse_day is not None:
            bse_frames.append(bse_day)
        time.sleep(1)

    if nse_frames:
        _merge_into_symbol_files(pd.concat(nse_frames, ignore_index=True), NSE_FOLDER)
    if bse_frames:
        _merge_into_symbol_files(pd.concat(bse_frames, ignore_index=True), BSE_FOLDER)


# ==============================================================================
# REGISTRY + MODEL TRAINING (runs once at Flask startup)
# ==============================================================================

def load_registry():
    nse_files = glob.glob(os.path.join(NSE_FOLDER, "*.csv"))
    bse_files = glob.glob(os.path.join(BSE_FOLDER, "*.csv"))
    us_files = glob.glob(os.path.join(US_FOLDER, "*.csv"))

    registry = {}
    for file in nse_files:
        symbol = os.path.splitext(os.path.basename(file))[0].upper()
        registry[symbol] = {'path': file, 'exchange': 'NSE'}
    for file in bse_files:
        symbol = os.path.splitext(os.path.basename(file))[0].upper()
        if symbol not in registry:
            registry[symbol] = {'path': file, 'exchange': 'BSE'}
    for file in us_files:
        symbol = os.path.splitext(os.path.basename(file))[0].upper()
        key = f"US_{symbol}"
        if key not in registry:
            registry[key] = {'path': file, 'exchange': 'US'}
    return registry


def train_model(registry, time_steps=TIME_STEPS):
    with tf.device('/CPU:0'):
        model = Sequential([
            GRU(units=32, activation='tanh', return_sequences=True, input_shape=(time_steps, 1)),
            Dropout(0.2),
            GRU(units=16, activation='tanh'),
            Dropout(0.2),
            Dense(units=1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')

    X_train_pool, y_train_pool = [], []
    for meta in list(registry.values())[:150]:
        try:
            sample_df = pd.read_csv(meta['path'])
            if len(sample_df) < (time_steps + 20):
                continue
            sample_df.columns = sample_df.columns.str.lower()
            date_col = 'datetime' if 'datetime' in sample_df.columns else 'date'
            sample_df = sample_df.dropna(subset=['close'])
            sample_df = sample_df[sample_df['close'] > 0]
            if 'close' in sample_df.columns and date_col in sample_df.columns:
                series = sample_df.sort_values(date_col)['close'].values.reshape(-1, 1)
                train_scaler = MinMaxScaler(feature_range=(0, 1))
                scaled = train_scaler.fit_transform(series)
                for i in range(len(scaled) - time_steps):
                    X_train_pool.append(scaled[i:(i + time_steps)])
                    y_train_pool.append(scaled[i + time_steps])
        except Exception:
            continue

    if X_train_pool:
        X_train = np.reshape(np.array(X_train_pool), (len(X_train_pool), time_steps, 1))
        y_train = np.array(y_train_pool)
        with tf.device('/CPU:0'):
            model.fit(X_train, y_train, epochs=5, batch_size=128, verbose=0)

    return model


def _prepare_one_ticker(symbol, meta, time_steps):
    """Reads one ticker's CSV and prepares its scaled input window. Runs in a
    worker thread — file I/O releases the GIL, so this parallelizes well even
    in plain Python threads."""
    try:
        temp_df = pd.read_csv(meta['path'])
        if temp_df.empty or len(temp_df) < time_steps:
            return None
        temp_df.columns = temp_df.columns.str.lower()
        date_col = 'datetime' if 'datetime' in temp_df.columns else 'date'
        if 'close' not in temp_df.columns or date_col not in temp_df.columns:
            return None

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

        meta_row = {
            'symbol': symbol.replace('US_', ''),
            'exchange': meta['exchange'],
            'current_price': float(current_price),
            'volatility': float(volatility),
        }
        return scaled_window, local_scaler, meta_row
    except Exception:
        return None


def evaluate_all(registry, model, time_steps=TIME_STEPS):
    batch_inputs = []
    scalers = []
    rows_meta = []

    # Parallelize the read-and-prepare step across threads — with hundreds
    # or thousands of tickers, sequential disk reads were the remaining
    # bottleneck even after batching the model.predict() call.
    max_workers = min(32, (os.cpu_count() or 4) * 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_prepare_one_ticker, symbol, meta, time_steps): symbol
            for symbol, meta in registry.items()
        }
        for future in as_completed(futures):
            result = future.result()
            if result is None:
                continue
            scaled_window, local_scaler, meta_row = result
            batch_inputs.append(scaled_window)
            scalers.append(local_scaler)
            rows_meta.append(meta_row)

    if not batch_inputs:
        return pd.DataFrame()

    # ONE batched prediction call for every ticker, instead of one call per
    # ticker — this is the single biggest CPU-time saving on a no-GPU machine.
    X_batch = np.reshape(np.array(batch_inputs), (len(batch_inputs), time_steps, 1))
    with tf.device('/CPU:0'):
        predicted_scaled_batch = model.predict(X_batch, batch_size=256, verbose=0)

    rows = []
    for i, meta_row in enumerate(rows_meta):
        predicted_price = scalers[i].inverse_transform(predicted_scaled_batch[i].reshape(1, -1))[0][0]
        growth = np.clip((predicted_price - meta_row['current_price']) / meta_row['current_price'], -0.40, 0.60)
        meta_row['base_growth'] = float(growth)
        rows.append(meta_row)

    df = pd.DataFrame(rows)
    if not df.empty:
        low_thresh = df['volatility'].quantile(0.33)
        high_thresh = df['volatility'].quantile(0.66)

        def classify(v):
            if v <= low_thresh:
                return 'Low Risk'
            elif v <= high_thresh:
                return 'Medium Risk'
            return 'High Risk'

        df['risk_category'] = df['volatility'].apply(classify)
    return df


def save_model(model, path=MODEL_PATH):
    model.save(path)


def load_saved_model(path=MODEL_PATH):
    return tf.keras.models.load_model(path)


def initialize_engine(force_refresh=False):
    """
    Call once at Flask startup. Loads the pre-trained model from MODEL_PATH
    if it exists, and loads the EVALUATED master_df from a disk cache if it's
    still fresh (MASTER_DF_CACHE_MAX_AGE_HOURS) — this is what actually makes
    repeated `python app.py` restarts fast once you've got 500+ tickers, since
    it skips re-running predictions on every ticker every single startup.
    Pass force_refresh=True (e.g. after a fresh backfill) to recompute now.
    """
    registry = load_registry()
    if not registry:
        return pd.DataFrame()

    if not force_refresh and os.path.exists(MASTER_DF_CACHE_PATH):
        age_hours = (time.time() - os.path.getmtime(MASTER_DF_CACHE_PATH)) / 3600
        if age_hours < MASTER_DF_CACHE_MAX_AGE_HOURS:
            try:
                print(f"[CACHE] Loading cached evaluation ({age_hours:.1f}h old) -- skipping re-prediction...")
                return pd.read_pickle(MASTER_DF_CACHE_PATH)
            except Exception:
                pass  # fall through and recompute if the cache file is corrupt

    if os.path.exists(MODEL_PATH):
        print(f"[MODEL] Loading pre-trained model from {MODEL_PATH}...")
        model = load_saved_model()
    else:
        print("[MODEL] No saved model found -- training one now (this only happens once)...")
        model = train_model(registry)
        save_model(model)
        print(f"[MODEL] Saved trained model to {MODEL_PATH}")

    print(f"[EVAL] Evaluating {len(registry)} tickers (this is the slow step on a large registry)...")
    df = evaluate_all(registry, model)

    try:
        df.to_pickle(MASTER_DF_CACHE_PATH)
        print(f"[CACHE] Cached evaluation results to {MASTER_DF_CACHE_PATH} (valid for {MASTER_DF_CACHE_MAX_AGE_HOURS}h)")
    except Exception:
        pass

    return df


# ==============================================================================
# QUERY — called per web request, no retraining
# ==============================================================================

EXCHANGE_FILTERS = {
    'nse': (['NSE'], 'NSE Exclusive'),
    'bse': (['BSE'], 'BSE Exclusive'),
    'nse_bse': (['NSE', 'BSE'], 'Hybrid: NSE + BSE'),
    'us': (['US'], 'US Exclusive'),
    'global': (['NSE', 'BSE', 'US'], 'Global Hybrid (NSE + BSE + US)'),
}


def get_recommendations(master_df, exchange_choice, capital, years):
    exchanges, label = EXCHANGE_FILTERS.get(exchange_choice, EXCHANGE_FILTERS['nse_bse'])
    pool = master_df[master_df['exchange'].isin(exchanges)].copy()
    pool = pool[(pool['current_price'] <= capital) & (pool['current_price'] >= 1.0)]

    if pool.empty:
        return {'label': label, 'mixed_currency': 'US' in exchanges and len(exchanges) > 1,
                'buckets': {'Low Risk': [], 'Medium Risk': [], 'High Risk': []}}

    pool['shares_to_buy'] = (capital // pool['current_price']).astype(int)
    pool['invested_capital'] = pool['shares_to_buy'] * pool['current_price']
    pool['leftover_cash'] = capital - pool['invested_capital']
    pool['net_profit'] = pool.apply(
        lambda r: r['invested_capital'] * ((1 + r['base_growth']) ** years) - r['invested_capital'], axis=1
    )
    pool['currency'] = pool['exchange'].apply(lambda e: '$' if e == 'US' else '₹')

    buckets = {}
    for risk in ['Low Risk', 'Medium Risk', 'High Risk']:
        bucket = pool[pool['risk_category'] == risk].sort_values('base_growth', ascending=False).head(5)
        buckets[risk] = bucket.to_dict('records')

    return {
        'label': label,
        'mixed_currency': 'US' in exchanges and len(exchanges) > 1,
        'buckets': buckets,
    }
