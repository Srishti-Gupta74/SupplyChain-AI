"""
data_pipeline.py
Loads data (synthetic or real M5) and engineers features.
Swap mode in config.yaml to use real M5 CSVs.
"""
import numpy as np
import pandas as pd
from pathlib import Path


# ─── Synthetic data ───────────────────────────────────────────────────────────

def generate_synthetic_demand(n_skus: int = 50, n_days: int = 730,
                               seed: int = 42) -> pd.DataFrame:
    """
    Generate realistic multi-SKU demand with:
    - Trend + weekly + annual seasonality
    - SKU-level scale variation
    - Stable and volatile regimes (volatility regime switches)
    - Injected demand shocks (simulates COVID-style events)
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2022-01-01", periods=n_days, freq="D")
    records = []

    for sku_id in range(n_skus):
        base_demand = rng.uniform(50, 500)
        trend = rng.uniform(-0.02, 0.05)

        # Seasonality coefficients
        weekly_amp   = rng.uniform(0.05, 0.20)
        annual_amp   = rng.uniform(0.10, 0.30)
        weekly_phase = rng.uniform(0, 2 * np.pi)
        annual_phase = rng.uniform(0, 2 * np.pi)

        # Noise level: stable vs volatile blocks
        # Each SKU randomly alternates between low/high-noise periods
        noise_schedule = np.ones(n_days) * rng.uniform(0.05, 0.15)
        n_shocks = rng.integers(1, 4)
        for _ in range(n_shocks):
            shock_start = rng.integers(60, n_days - 90)
            shock_len   = rng.integers(20, 60)
            noise_schedule[shock_start:shock_start + shock_len] = rng.uniform(0.35, 0.70)

        demand = []
        for t, date in enumerate(dates):
            doy = date.day_of_year
            dow = date.dayofweek
            level = (
                base_demand
                * (1 + trend * t / 365)
                * (1 + weekly_amp * np.sin(2 * np.pi * dow / 7 + weekly_phase))
                * (1 + annual_amp * np.sin(2 * np.pi * doy / 365 + annual_phase))
            )
            noise  = rng.normal(0, noise_schedule[t] * level)
            value  = max(0.0, level + noise)
            demand.append(round(value, 1))

        df = pd.DataFrame({"date": dates, "demand": demand})
        df["sku_id"] = f"SKU_{sku_id:03d}"
        records.append(df)

    return pd.concat(records, ignore_index=True)


# ─── M5 loader ────────────────────────────────────────────────────────────────

def load_m5(sales_path, calendar_path, prices_path,
            n_skus=50, seed=42) -> pd.DataFrame:
    """
    Load a random subset of M5 data and return in the same
    long-format as synthetic: [date, sku_id, demand]
    """
    sales    = pd.read_csv(sales_path)
    calendar = pd.read_csv(calendar_path)

    rng = np.random.default_rng(seed)
    sample = sales.sample(n=min(n_skus, len(sales)), random_state=seed)

    day_cols = [c for c in sales.columns if c.startswith("d_")]
    id_col   = "id"

    cal_map = calendar.set_index("d")["date"].to_dict()

    records = []
    for _, row in sample.iterrows():
        for d in day_cols:
            date_str = cal_map.get(d)
            if date_str:
                records.append({
                    "date":   pd.to_datetime(date_str),
                    "sku_id": row[id_col],
                    "demand": float(row[d])
                })

    return pd.DataFrame(records).sort_values(["sku_id", "date"]).reset_index(drop=True)


# ─── Feature engineering ──────────────────────────────────────────────────────

def engineer_features(df: pd.DataFrame, lags=(7, 14, 28),
                       rolling_windows=(7, 28)) -> pd.DataFrame:
    """
    Add lag and rolling features per SKU. Drops rows with NaNs
    introduced by lags (first max_lag rows per SKU).
    """
    df = df.sort_values(["sku_id", "date"]).copy()
    df["dayofweek"] = pd.to_datetime(df["date"]).dt.dayofweek
    df["month"]     = pd.to_datetime(df["date"]).dt.month
    df["year"]      = pd.to_datetime(df["date"]).dt.year

    grp = df.groupby("sku_id")["demand"]

    for lag in lags:
        df[f"lag_{lag}"] = grp.shift(lag)

    for w in rolling_windows:
        shifted = grp.shift(1)   # avoid leakage
        df[f"roll_mean_{w}"] = shifted.transform(
            lambda x: x.rolling(w, min_periods=1).mean()
        )
        df[f"roll_std_{w}"] = shifted.transform(
            lambda x: x.rolling(w, min_periods=1).std().fillna(0)
        )

    df = df.dropna().reset_index(drop=True)
    return df


# ─── Volatility labelling ─────────────────────────────────────────────────────

def label_volatility(df: pd.DataFrame, window: int = 28,
                      cv_threshold: float = 0.30) -> pd.DataFrame:
    """
    Label each row as 'stable' or 'volatile' based on the rolling
    coefficient of variation (std/mean) of demand for that SKU.
    """
    df = df.copy()
    grp = df.groupby("sku_id")["demand"]
    roll_mean = grp.transform(lambda x: x.rolling(window, min_periods=7).mean())
    roll_std  = grp.transform(lambda x: x.rolling(window, min_periods=7).std().fillna(0))
    cv = roll_std / (roll_mean + 1e-9)
    df["rolling_cv"]  = cv
    df["is_volatile"] = (cv > cv_threshold).astype(int)
    return df


# ─── Train / val / test split ─────────────────────────────────────────────────

def time_split(df: pd.DataFrame,
               train_ratio: float = 0.70,
               val_ratio:   float = 0.15):
    """
    Chronological split — same cut-point applied across all SKUs.
    Returns (train, val, test) DataFrames.
    """
    dates = df["date"].sort_values().unique()
    n = len(dates)
    t1 = dates[int(n * train_ratio)]
    t2 = dates[int(n * (train_ratio + val_ratio))]

    train = df[df["date"] <  t1].copy()
    val   = df[(df["date"] >= t1) & (df["date"] < t2)].copy()
    test  = df[df["date"] >= t2].copy()
    return train, val, test


# ─── Master load function ─────────────────────────────────────────────────────

def load_data(cfg: dict):
    mode = cfg["data"]["mode"]
    if mode == "synthetic":
        raw = generate_synthetic_demand(
            n_skus=cfg["data"]["n_skus"],
            n_days=cfg["data"]["n_days"]
        )
    elif mode == "m5":
        raw = load_m5(
            cfg["data"]["m5_sales_path"],
            cfg["data"]["m5_calendar_path"],
            cfg["data"]["m5_prices_path"],
            n_skus=cfg["data"]["n_skus"]
        )
    else:
        raise ValueError(f"Unknown data mode: {mode}")

    df = engineer_features(
        raw,
        lags=cfg["features"]["lags"],
        rolling_windows=cfg["features"]["rolling_windows"]
    )
    df = label_volatility(df, cv_threshold=cfg["volatility"]["cv_threshold"])
    train, val, test = time_split(
        df,
        train_ratio=cfg["split"]["train_ratio"],
        val_ratio=cfg["split"]["val_ratio"]
    )
    print(f"[data] train={len(train):,}  val={len(val):,}  test={len(test):,}")
    print(f"[data] volatile rows in test: "
          f"{test['is_volatile'].mean():.1%}")
    return train, val, test
