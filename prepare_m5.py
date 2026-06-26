"""
prepare_m5.py
Run this ONCE after downloading M5 data from Kaggle.
Creates data/m5_processed.parquet which main.py uses.

Usage:
    python prepare_m5.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

M5_DIR  = Path("data")
OUT_DIR = Path("data")
OUT_DIR.mkdir(exist_ok=True)

print("Loading M5 files...")
sales = pd.read_csv(M5_DIR / "sales_train_validation.csv")
cal   = pd.read_csv(M5_DIR / "calendar.csv")

print(f"  Sales shape : {sales.shape}")
print(f"  Calendar    : {cal.shape}")

# Build day-index map  (d_1 = first calendar row, etc.)
day_cols   = [c for c in sales.columns if c.startswith("d_")]
cal["d"]   = ["d_" + str(i + 1) for i in range(len(cal))]
cal_map    = cal.set_index("d")[[
    "date", "wday", "month", "year",
    "event_name_1", "snap_CA", "snap_TX", "snap_WI"
]].to_dict(orient="index")

# Filter to SKUs with average demand >= 0.5 (avoids pure-zero series)
# and sample 150 diverse SKUs across categories and stores
print("Filtering SKUs...")
means      = sales[day_cols].mean(axis=1)
valid_mask = means >= 0.5
sales_filt = sales[valid_mask].reset_index(drop=True)
print(f"  Valid SKUs (mean demand ≥ 0.5): {len(sales_filt)}")

np.random.seed(42)
# Stratified sample: ~15 SKUs per store (10 stores)
records = []
for store in sales_filt["store_id"].unique():
    store_df = sales_filt[sales_filt["store_id"] == store]
    n        = min(15, len(store_df))
    sample   = store_df.sample(n, random_state=42)
    records.append(sample)

sampled = pd.concat(records, ignore_index=True)
print(f"  Sampled SKUs: {len(sampled)} across {sampled['store_id'].nunique()} stores")

# Convert wide → long format
print("Converting to long format...")
rows = []
for _, row in sampled.iterrows():
    sku = f"{row['item_id']}_{row['store_id']}"
    for d in day_cols:
        info = cal_map.get(d)
        if info is None:
            continue
        snap = int(bool(info.get("snap_CA", 0)) or
                   bool(info.get("snap_TX", 0)) or
                   bool(info.get("snap_WI", 0)))
        rows.append({
            "date":    info["date"],
            "sku_id":  sku,
            "demand":  float(row[d]),
            "wday":    info["wday"],
            "month":   info["month"],
            "year":    info["year"],
            "event":   1 if pd.notna(info.get("event_name_1")) else 0,
            "snap":    snap,
            "store_id": row["store_id"],
            "cat_id":   row["cat_id"],
            "dept_id":  row["dept_id"],
        })

df = pd.DataFrame(rows)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["sku_id", "date"]).reset_index(drop=True)

# Save
out_path = OUT_DIR / "m5_processed.parquet"
df.to_parquet(out_path, index=False)

print(f"\n✓ Saved → {out_path}")
print(f"  Rows      : {len(df):,}")
print(f"  SKUs      : {df['sku_id'].nunique()}")
print(f"  Date range: {df['date'].min().date()} → {df['date'].max().date()}")
print(f"  Avg demand: {df['demand'].mean():.2f}")
print(f"  Volatile % (CV>0.30): "
      f"{(df.groupby('sku_id')['demand'].std() / (df.groupby('sku_id')['demand'].mean() + 1e-9) > 0.3).mean():.1%}")

print("\nNext step: update config.yaml → data.mode: m5")
print("Then run:  python main.py")
