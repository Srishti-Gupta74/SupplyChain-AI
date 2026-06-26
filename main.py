"""
main.py — SupplyShield AI end-to-end pipeline
Run: python main.py
"""
import yaml
import numpy as np
import pandas as pd
from pathlib import Path

from data_pipeline import load_data
from models import BaseForecaster, fit_all
from evaluation import (evaluate_by_regime, simulate_inventory,
                         underestimation_audit, newsvendor_safety_stock,
                         plot_calibration_curves, plot_alpha_trajectory,
                         plot_interval_comparison)
from decision import build_decision_table

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def run():
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)

    target_alpha    = 1 - cfg["uq"]["confidence_levels"][1]   # 0.10
    target_coverage = 1 - target_alpha                         # 0.90

    # ── Data ─────────────────────────────────────────────────────────────────
    print("\n══ Step 1: Data Pipeline ══")
    train, val, test = load_data(cfg)

    # ── Base model ───────────────────────────────────────────────────────────
    print("\n══ Step 2: Base Forecaster ══")
    base = BaseForecaster(cfg)
    base.fit(train, val)
    point_pred = base.predict(test)

    # ── UQ methods ───────────────────────────────────────────────────────────
    print("\n══ Step 3: UQ Methods ══")
    qr, scp, aci = fit_all(cfg, train, val, base)

    # ── Inference ────────────────────────────────────────────────────────────
    print("\n══ Step 4: Inference ══")
    qr_lo,  qr_hi  = qr.predict_interval(test)
    scp_lo, scp_hi = scp.predict_interval(test)
    aci_lo, aci_hi, aci_alphas = aci.predict_interval_sequential(base, test)

    y_true      = test["demand"].values
    is_volatile = test["is_volatile"].values

    # ── Evaluation ───────────────────────────────────────────────────────────
    print("\n══ Step 5: Evaluation ══")
    results = []
    for name, lo, hi in [("QR",  qr_lo,  qr_hi),
                          ("SCP", scp_lo, scp_hi),
                          ("ACI", aci_lo, aci_hi)]:
        r = evaluate_by_regime(y_true, lo, hi, is_volatile, name)
        results.append(r)
        print(f"\n[{name}]")
        for k, v in r.items():
            if k != "method":
                print(f"  {k}: {v}")

    # ── Underestimation audit ─────────────────────────────────────────────────
    print("\n══ Underestimation Audit ══")
    audit = underestimation_audit(
        coverage_all=results[2]["coverage_all"],
        coverage_volatile=results[2].get("coverage_volatile", 0),
        target=target_coverage
    )
    for k, v in audit.items():
        print(f"  {k}: {v}")

    # ── Inventory simulation ──────────────────────────────────────────────────
    print("\n══ Step 6: Inventory Simulation ══")
    z_sl      = cfg["decision"]["service_level_z"]
    lead_time = cfg["decision"]["lead_time"]

    ss_aci  = newsvendor_safety_stock(aci_lo, aci_hi, z_sl, lead_time, target_alpha)

    # Baseline: QR-derived safety stock (fair comparison — both use
    # the same base model, only UQ method differs)
    ss_base = newsvendor_safety_stock(qr_lo, qr_hi, z_sl, lead_time, target_alpha)

    sim = simulate_inventory(y_true, point_pred, ss_aci, ss_base)
    print("\nInventory simulation (ACI vs QR baseline):")
    for k, v in sim.items():
        print(f"  {k}: {v}")

    # Volatile-only simulation (the key public-good story)
    v_mask = is_volatile == 1
    if v_mask.sum() > 0:
        sim_vol = simulate_inventory(
            y_true[v_mask], point_pred[v_mask],
            ss_aci[v_mask], ss_base[v_mask]
        )
        print("\nInventory simulation — VOLATILE periods only:")
        for k, v in sim_vol.items():
            print(f"  {k}: {v}")
    else:
        sim_vol = sim

    # ── Decision table ────────────────────────────────────────────────────────
    print("\n══ Step 7: Decision Table ══")
    decision_df = build_decision_table(
        test, point_pred, aci_lo, aci_hi, aci_alphas,
        qr_lo, qr_hi,          # ← pass QR intervals as baseline
        target_alpha, z_sl, lead_time
    )
    out_csv = OUTPUT_DIR / "decision_table.csv"
    decision_df.to_csv(out_csv, index=False)
    print(f"Decision table → {out_csv}  ({len(decision_df):,} rows)")
    print("\nRisk tier distribution:")
    print(decision_df["risk_tier"].value_counts().to_string())
    print("\nEscalation distribution:")
    print(decision_df["escalation"].value_counts().to_string())

    # ── Plots ──────────────────────────────────────────────────────────────────
    print("\n══ Step 8: Plots ══")
    plot_calibration_curves(results, target_alpha,
                             out_path=str(OUTPUT_DIR / "calibration.png"))
    plot_alpha_trajectory(aci_alphas, is_volatile, target_alpha,
                           out_path=str(OUTPUT_DIR / "alpha_trajectory.png"))
    plot_interval_comparison(
        y_true, point_pred,
        {"QR": (qr_lo, qr_hi), "SCP": (scp_lo, scp_hi), "ACI": (aci_lo, aci_hi)},
        n=150,
        out_path=str(OUTPUT_DIR / "interval_comparison.png")
    )

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "═"*55)
    print("SupplyShield AI — Run Complete")
    print("═"*55)
    print(f"Dataset          : M5 Competition (real Walmart data)")
    print(f"SKUs evaluated   : {test['sku_id'].nunique()}")
    print(f"Test rows        : {len(test):,}")
    print(f"Volatile rows    : {is_volatile.sum():,} ({is_volatile.mean():.1%})")
    print(f"Target coverage  : {target_coverage:.0%}")
    print()
    for r in results:
        m = r["method"]
        print(f"{m:4s}  all={r['coverage_all']:.2%}  "
              f"volatile={r.get('coverage_volatile', 0):.2%}")
    print()
    print(f"Stockout reduction (volatile)  : "
          f"{sim_vol.get('stockout_reduction_pct', 0):+.1f}%")
    print(f"Excess inv. change (volatile)  : "
          f"{sim_vol.get('excess_change_pct', 0):+.1f}%")
    print(f"\nOutputs → {OUTPUT_DIR.resolve()}")

    # Save summary for dashboard
    summary = {
        "dataset": "M5 Competition (Walmart, 150 SKUs, 2011–2016)",
        "target_coverage": target_coverage,
        "n_skus": int(test["sku_id"].nunique()),
        "n_test_rows": int(len(test)),
        "pct_volatile": float(is_volatile.mean()),
        **{f"{r['method']}_cov_all": r["coverage_all"] for r in results},
        **{f"{r['method']}_cov_volatile": r.get("coverage_volatile", 0) for r in results},
        "stockout_reduction_volatile_pct": sim_vol.get("stockout_reduction_pct", 0),
        "excess_change_volatile_pct": sim_vol.get("excess_change_pct", 0),
        **{f"audit_{k}": v for k, v in audit.items()},
    }
    import json
    with open(OUTPUT_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("Summary → outputs/summary.json")

    return decision_df, results, sim, sim_vol, audit


if __name__ == "__main__":
    run()
