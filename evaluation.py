"""
evaluation.py
Calibration curves, coverage statistics, stable vs volatile breakdown,
and inventory simulation.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path


# ─── Coverage & calibration ───────────────────────────────────────────────────

def empirical_coverage(y_true: np.ndarray,
                        lower: np.ndarray,
                        upper: np.ndarray) -> float:
    return np.mean((y_true >= lower) & (y_true <= upper))


def mean_interval_width(lower: np.ndarray, upper: np.ndarray) -> float:
    return np.mean(upper - lower)


def calibration_curve(y_true: np.ndarray,
                       point_pred: np.ndarray,
                       residuals_cal: np.ndarray,
                       levels=np.arange(0.50, 1.00, 0.05)):
    """
    For each stated coverage level, compute the empirical coverage
    by scaling the interval from calibration residuals.
    Returns (stated_levels, observed_coverages).
    """
    sigma = np.std(residuals_cal) + 1e-9
    stated, observed = [], []
    for lv in levels:
        q = np.quantile(np.abs(residuals_cal), lv)
        lo = point_pred - q
        hi = point_pred + q
        cov = empirical_coverage(y_true, lo, hi)
        stated.append(lv)
        observed.append(cov)
    return np.array(stated), np.array(observed)


def evaluate_by_regime(y_true: np.ndarray,
                        lower: np.ndarray,
                        upper: np.ndarray,
                        is_volatile: np.ndarray,
                        name: str) -> dict:
    mask_s = is_volatile == 0
    mask_v = is_volatile == 1

    results = {"method": name}
    for label, mask in [("all", np.ones(len(y_true), dtype=bool)),
                         ("stable", mask_s),
                         ("volatile", mask_v)]:
        if mask.sum() == 0:
            continue
        cov = empirical_coverage(y_true[mask], lower[mask], upper[mask])
        wid = mean_interval_width(lower[mask], upper[mask])
        results[f"coverage_{label}"]       = round(cov, 4)
        results[f"interval_width_{label}"] = round(wid, 2)

    return results


# ─── Inventory simulation ─────────────────────────────────────────────────────

def newsvendor_safety_stock(lower: np.ndarray,
                             upper: np.ndarray,
                             z_sl: float = 1.65,
                             lead_time: int = 7,
                             alpha: float = 0.10) -> np.ndarray:
    """
    Derive σ̂_t from the ACI interval and compute newsvendor SS:
        σ̂_t = (U_t - L_t) / (2 * z_{1-α/2})
        SS_t = z_SL * σ̂_t * sqrt(lead_time)
    """
    z_ci    = 1.645 if abs(alpha - 0.10) < 0.01 else 1.28
    sigma_t = (upper - lower) / (2 * z_ci)
    ss_t    = z_sl * sigma_t * np.sqrt(lead_time)
    return np.maximum(ss_t, 0)


def simulate_inventory(y_true: np.ndarray,
                        point_pred: np.ndarray,
                        ss_aci: np.ndarray,
                        ss_baseline: np.ndarray) -> dict:
    """
    Compare ACI-informed safety stock vs a naive baseline.
    
    Baseline = point_pred + z * historical_std (fixed, conservative).
    ACI      = point_pred + newsvendor SS from interval width.
    
    ACI is expected to be more conservative during volatile periods
    (wider intervals → more SS) and tighter during stable periods
    (narrower intervals → less excess). The net result:
    - More coverage during shocks (fewer stockouts when it matters)
    - Similar or lower excess during stable periods
    """
    def metrics(ss):
        order    = np.maximum(point_pred + ss, 0)
        stockout = np.mean(y_true > order)
        excess   = np.mean(np.maximum(order - y_true, 0))
        return stockout, excess

    so_aci,  ex_aci  = metrics(ss_aci)
    so_base, ex_base = metrics(ss_baseline)

    return {
        "stockout_rate_aci":      round(so_aci,  4),
        "stockout_rate_baseline": round(so_base, 4),
        "stockout_reduction_pct": round((so_base - so_aci) / (so_base + 1e-9) * 100, 1),
        "excess_inv_aci":         round(ex_aci,  2),
        "excess_inv_baseline":    round(ex_base, 2),
        "excess_change_pct":      round((ex_aci - ex_base) / (ex_base + 1e-9) * 100, 1),
    }


# ─── Underestimation audit ────────────────────────────────────────────────────

def underestimation_audit(coverage_all: float,
                           coverage_volatile: float,
                           target: float,
                           threshold: float = 0.05) -> dict:
    """
    Flag when volatile-period coverage falls more than `threshold`
    below target — the key ACI failure-detection check.
    """
    gap = target - coverage_volatile
    return {
        "target_coverage":        round(target, 4),
        "coverage_all":           round(coverage_all, 4),
        "coverage_volatile":      round(coverage_volatile, 4),
        "volatile_gap":           round(gap, 4),
        "underestimation_flag":   gap > threshold,
    }


# ─── Plotting ─────────────────────────────────────────────────────────────────

def plot_calibration_curves(results: list, target: float,
                              out_path: str = "calibration.png"):
    """
    results: list of dicts from evaluate_by_regime
    Plots stated vs observed coverage for each method.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, regime in zip(axes, ["all", "volatile"]):
        ax.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect calibration")
        for r in results:
            cov = r.get(f"coverage_{regime}")
            if cov is None:
                continue
            # Plot a single point (overall coverage) vs stated level
            ax.scatter([1 - target], [cov], s=100, label=r["method"], zorder=5)
            ax.axhline(1 - target, color="gray", lw=0.5, ls=":")

        ax.set_xlabel("Stated confidence level")
        ax.set_ylabel("Empirical coverage")
        ax.set_title(f"Calibration — {regime} demand periods")
        ax.legend()
        ax.set_xlim(0.7, 1.0)
        ax.set_ylim(0.5, 1.0)

    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()
    print(f"[eval] calibration plot saved → {out_path}")


def plot_alpha_trajectory(alphas: np.ndarray,
                           is_volatile: np.ndarray,
                           target_alpha: float,
                           out_path: str = "alpha_traj.png"):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(alphas, color="steelblue", lw=1, label="α_t (ACI adaptive level)")
    ax.axhline(target_alpha, color="red", lw=1, ls="--", label=f"Target α = {target_alpha}")

    # Shade volatile regions
    volatile_idx = np.where(is_volatile)[0]
    if len(volatile_idx):
        changes = np.diff(volatile_idx)
        starts  = volatile_idx[np.concatenate([[True], changes > 1])]
        ends    = volatile_idx[np.concatenate([changes > 1, [True]])]
        for s, e in zip(starts, ends):
            ax.axvspan(s, e, alpha=0.15, color="orange", label="_volatile region")

    ax.set_xlabel("Test time step")
    ax.set_ylabel("α_t")
    ax.set_title("ACI Adaptive α Trajectory (orange = volatile demand regime)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()
    print(f"[eval] alpha trajectory saved → {out_path}")


def plot_interval_comparison(y_true: np.ndarray,
                              point_pred: np.ndarray,
                              intervals: dict,
                              n: int = 100,
                              out_path: str = "intervals.png"):
    """Plot first n test points showing intervals from each method."""
    y   = y_true[:n]
    pp  = point_pred[:n]
    idx = np.arange(n)

    colors = {"QR": "steelblue", "SCP": "seagreen", "ACI": "darkorange"}
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(y, "ko", ms=3, label="True demand", zorder=5)
    ax.plot(pp, "gray", lw=1, ls="--", label="Point forecast")

    for name, (lo, hi) in intervals.items():
        ax.fill_between(idx, lo[:n], hi[:n],
                         alpha=0.25, color=colors.get(name, "purple"),
                         label=f"{name} interval")

    ax.set_xlabel("Test time step")
    ax.set_ylabel("Demand")
    ax.set_title("Prediction Intervals: QR vs SCP vs ACI (first 100 test points)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()
    print(f"[eval] interval comparison saved → {out_path}")
