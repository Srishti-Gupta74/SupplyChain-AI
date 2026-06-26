"""
decision.py — Reliability Score, risk tiers, escalation
"""
import numpy as np
import pandas as pd
from evaluation import newsvendor_safety_stock


def compute_reliability_score(rolling_coverage: float,
                               calibration_error: float,
                               is_volatile: bool) -> float:
    """
    Forecast Reliability Score (0–100).
    Derived from rolling coverage quality, calibration error,
    and a volatility-regime adjustment — no fixed weights exposed.
    """
    coverage_component    = rolling_coverage
    calibration_component = 1.0 - min(calibration_error, 1.0)
    volatility_adjustment = 0.15 if is_volatile else 0.0

    raw   = (coverage_component * 0.50 +
             calibration_component * 0.35 -
             volatility_adjustment)
    score = max(0.0, min(1.0, raw)) * 100
    return round(score, 1)


def assign_risk_tier(ss_aci: float, ss_qr: float) -> str:
    """
    Risk tier: how much does ACI safety stock deviate from QR baseline?
    - Low:    ACI and QR agree — model is confident
    - Medium: ACI moderately more conservative than QR
    - High:   ACI substantially more conservative — signals demand shock
    """
    if ss_qr < 0.01:
        return "Low"
    ratio = ss_aci / ss_qr
    if ratio < 1.20:
        return "Low"
    elif ratio < 1.60:
        return "Medium"
    else:
        return "High"


def assign_escalation(tier: str, reliability: float) -> str:
    if tier == "Low" and reliability >= 70:
        return "Standard Reorder"
    elif tier == "High" or reliability < 55:
        return "Escalate to Procurement"
    else:
        return "Manual Review"


def build_decision_table(test: pd.DataFrame,
                          point_pred: np.ndarray,
                          aci_lower: np.ndarray,
                          aci_upper: np.ndarray,
                          aci_alphas: np.ndarray,
                          qr_lower: np.ndarray,
                          qr_upper: np.ndarray,
                          target_alpha: float,
                          z_sl: float = 1.65,
                          lead_time: int = 7) -> pd.DataFrame:

    ss_aci = newsvendor_safety_stock(aci_lower, aci_upper,
                                      z_sl=z_sl, lead_time=lead_time,
                                      alpha=target_alpha)
    ss_qr  = newsvendor_safety_stock(qr_lower, qr_upper,
                                      z_sl=z_sl, lead_time=lead_time,
                                      alpha=target_alpha)

    y_true  = test["demand"].values
    covered = ((y_true >= aci_lower) & (y_true <= aci_upper)).astype(float)

    window   = 28
    roll_cov = pd.Series(covered).rolling(window, min_periods=5).mean().fillna(0.5).values
    cal_err  = np.abs(aci_alphas - target_alpha)

    rows = []
    for i in range(len(test)):
        is_vol    = bool(test["is_volatile"].values[i])
        rel_score = compute_reliability_score(roll_cov[i], cal_err[i], is_vol)
        tier      = assign_risk_tier(ss_aci[i], ss_qr[i])
        escal     = assign_escalation(tier, rel_score)

        if aci_alphas[i] < target_alpha * 0.8:
            health = "Degrading"
        elif aci_alphas[i] > target_alpha * 1.2:
            health = "Recovering"
        else:
            health = "At-Target"

        rows.append({
            "date":               test["date"].values[i],
            "sku_id":             test["sku_id"].values[i],
            "true_demand":        round(float(y_true[i]), 1),
            "point_forecast":     round(float(point_pred[i]), 1),
            "interval_lower":     round(float(aci_lower[i]), 1),
            "interval_upper":     round(float(aci_upper[i]), 1),
            "alpha_t":            round(float(aci_alphas[i]), 4),
            "reliability_score":  rel_score,
            "risk_tier":          tier,
            "escalation":         escal,
            "safety_stock_aci":   round(float(ss_aci[i]), 2),
            "safety_stock_qr":    round(float(ss_qr[i]), 2),
            "is_volatile":        int(test["is_volatile"].values[i]),
            "calibration_health": health,
            "covered":            int(covered[i]),
        })

    return pd.DataFrame(rows)
