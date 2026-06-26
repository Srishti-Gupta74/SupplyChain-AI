"""
models.py
Base LightGBM forecaster + three UQ methods:
  1. Quantile Regression (LightGBM)
  2. Static Conformal Prediction (MAPIE)
  3. Adaptive Conformal Inference — ACI (Gibbs & Candès 2022)
"""
import numpy as np
import pandas as pd
import lightgbm as lgb
from mapie.regression import SplitConformalRegressor
from sklearn.base import BaseEstimator, RegressorMixin
import warnings
warnings.filterwarnings("ignore")

FEATURE_COLS = None   # populated at runtime


def get_feature_cols(df: pd.DataFrame) -> list:
    exclude = {"date", "sku_id", "demand", "rolling_cv", "is_volatile",
               "store_id", "cat_id", "dept_id"}
    return [c for c in df.columns
            if c not in exclude and df[c].dtype != object]


# ─── Base LightGBM forecaster ─────────────────────────────────────────────────

class BaseForecaster:
    def __init__(self, cfg: dict):
        params = cfg["model"]["base"]
        self.params = {
            "objective":         "regression_l1",
            "n_estimators":      params["n_estimators"],
            "learning_rate":     params["learning_rate"],
            "num_leaves":        params["num_leaves"],
            "min_child_samples": params["min_child_samples"],
            "verbose":           -1,
            "n_jobs":            -1,
        }
        self.model = None
        self.feature_cols = None

    def fit(self, train: pd.DataFrame, val: pd.DataFrame):
        self.feature_cols = get_feature_cols(train)
        X_tr = train[self.feature_cols].values
        y_tr = train["demand"].values
        X_val = val[self.feature_cols].values
        y_val = val["demand"].values

        self.model = lgb.LGBMRegressor(**self.params)
        self.model.fit(
            X_tr, y_tr,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(30, verbose=False),
                       lgb.log_evaluation(-1)]
        )
        preds = self.model.predict(X_val)
        mae = np.mean(np.abs(preds - y_val))
        print(f"[base] val MAE = {mae:.2f}")
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        return self.model.predict(df[self.feature_cols].values)


# ─── 1. Quantile Regression ───────────────────────────────────────────────────

class QuantileForecaster:
    """Two separate LightGBM models: lower and upper quantile."""

    def __init__(self, cfg: dict, alpha: float = 0.10):
        self.alpha = alpha           # miscoverage; 1-alpha = coverage
        self.cfg   = cfg
        self.lower_model = None
        self.upper_model = None
        self.feature_cols = None

    def _make_model(self, quantile: float):
        p = self.cfg["model"]["base"]
        return lgb.LGBMRegressor(
            objective="quantile",
            alpha=quantile,
            n_estimators=p["n_estimators"],
            learning_rate=p["learning_rate"],
            num_leaves=p["num_leaves"],
            min_child_samples=p["min_child_samples"],
            verbose=-1, n_jobs=-1
        )

    def fit(self, train: pd.DataFrame, val: pd.DataFrame):
        self.feature_cols = get_feature_cols(train)
        X_tr = train[self.feature_cols].values
        y_tr = train["demand"].values

        q_lo = self.alpha / 2
        q_hi = 1 - self.alpha / 2

        self.lower_model = self._make_model(q_lo)
        self.upper_model = self._make_model(q_hi)
        self.lower_model.fit(X_tr, y_tr, callbacks=[lgb.log_evaluation(-1)])
        self.upper_model.fit(X_tr, y_tr, callbacks=[lgb.log_evaluation(-1)])
        print(f"[QR ] alpha={self.alpha} → [{q_lo:.2f}, {q_hi:.2f}] fitted")
        return self

    def predict_interval(self, df: pd.DataFrame):
        X = df[self.feature_cols].values
        lower = self.lower_model.predict(X)
        upper = self.upper_model.predict(X)
        # Ensure lower ≤ upper
        lo = np.minimum(lower, upper)
        hi = np.maximum(lower, upper)
        return lo, hi


# ─── 2. Static Conformal Prediction (MAPIE) ───────────────────────────────────

class StaticConformal:
    """MAPIE MapieRegressor wrapping a LightGBM base model."""

    def __init__(self, cfg: dict, alpha: float = 0.10):
        self.alpha  = alpha
        self.cfg    = cfg
        self.mapie  = None
        self.feature_cols = None

    def fit(self, train: pd.DataFrame, val: pd.DataFrame):
        self.feature_cols = get_feature_cols(train)
        p = self.cfg["model"]["base"]
        base = lgb.LGBMRegressor(
            objective="regression_l1",
            n_estimators=p["n_estimators"],
            learning_rate=p["learning_rate"],
            num_leaves=p["num_leaves"],
            min_child_samples=p["min_child_samples"],
            verbose=-1, n_jobs=-1
        )
        # Train base on train set, calibrate on val set
        X_tr = train[self.feature_cols].values
        y_tr = train["demand"].values
        X_val = val[self.feature_cols].values
        y_val = val["demand"].values

        self.mapie = SplitConformalRegressor(estimator=base, confidence_level=1-self.alpha, prefit=False)
        self.mapie.fit(X_tr, y_tr)
        self.mapie.conformalize(X_val, y_val)
        print(f"[SCP] alpha={self.alpha} fitted (SplitConformalRegressor)")
        return self

    def predict_interval(self, df: pd.DataFrame):
        X = df[self.feature_cols].values
        _, intervals = self.mapie.predict_interval(X)
        # intervals shape: (n, 2, 1) → lower = [:, 0, 0], upper = [:, 1, 0]
        lower = intervals[:, 0, 0]
        upper = intervals[:, 1, 0]
        return np.array(lower).flatten(), np.array(upper).flatten()


# ─── 3. Adaptive Conformal Inference (ACI) ────────────────────────────────────

class ACI:
    """
    Gibbs & Candès (2022) Adaptive Conformal Inference.

    Update rule:
        α_{t+1} = α_t + γ · (α − 1{y_t ∉ Ĉ_t})

    α     = target miscoverage rate
    γ     = step-size (tuned on validation set)
    Ĉ_t  = [base_pred − q_t · σ̂, base_pred + q_t · σ̂]
            where σ̂ is estimated from a rolling residual std.

    Implementation note:
    We use the base forecaster's residuals on the calibration
    (val) set to initialise the conformal score scale, then
    update adaptively on the test sequence.
    """

    def __init__(self, cfg: dict, alpha: float = 0.10):
        self.alpha   = alpha
        self.cfg     = cfg
        self.gamma   = None    # set during tune()
        self.feature_cols = None
        self._cal_scores = None  # sorted calibration nonconformity scores
        self._sigma_hat  = None  # scale estimate

    # -- Calibration --------------------------------------------------------

    def calibrate(self, base_forecaster: BaseForecaster,
                  val: pd.DataFrame, gamma: float = 0.01):
        """
        Fit the ACI using the validation set as the calibration set.
        Computes nonconformity scores (absolute residuals) and sets
        the initial conformal quantile.
        """
        self.gamma        = gamma
        self.feature_cols = base_forecaster.feature_cols

        preds  = base_forecaster.predict(val)
        resids = np.abs(val["demand"].values - preds)

        # Initial conformal quantile level
        n = len(resids)
        level = np.ceil((n + 1) * (1 - self.alpha)) / n
        level = min(level, 1.0)
        self._cal_scores = np.sort(resids)
        self._q           = np.quantile(resids, level)
        self._sigma_hat   = resids.std() + 1e-9
        print(f"[ACI] gamma={gamma}, alpha={self.alpha}, "
              f"init_q={self._q:.3f}, sigma={self._sigma_hat:.3f}")
        return self

    def tune_gamma(self, base_forecaster: BaseForecaster,
                   val: pd.DataFrame, gamma_grid: list) -> float:
        """
        Grid-search γ on the validation set by minimising
        |empirical_coverage - target_coverage|.
        """
        best_gamma, best_err = None, np.inf
        preds  = base_forecaster.predict(val)
        y_true = val["demand"].values

        for g in gamma_grid:
            alpha_t = self.alpha
            covered = []
            for i, (pred, y) in enumerate(zip(preds, y_true)):
                q_t = max(self._q + alpha_t * self._sigma_hat, 0)
                lo  = pred - q_t
                hi  = pred + q_t
                hit = int(lo <= y <= hi)
                covered.append(hit)
                alpha_t = alpha_t + g * (self.alpha - (1 - hit))

            cov = np.mean(covered)
            err = abs(cov - (1 - self.alpha))
            if err < best_err:
                best_err, best_gamma = err, g

        print(f"[ACI] best_gamma={best_gamma} (coverage_err={best_err:.4f})")
        return best_gamma

    # -- Inference ----------------------------------------------------------

    def predict_interval_sequential(self,
                                     base_forecaster: BaseForecaster,
                                     test: pd.DataFrame):
        """
        Run ACI sequentially over the test set.
        Returns arrays: lower, upper, alpha_trajectory.
        The alpha_t is updated after each true observation is revealed.
        """
        preds  = base_forecaster.predict(test)
        y_true = test["demand"].values

        alpha_t = self.alpha
        lowers, uppers, alphas = [], [], []

        for pred, y in zip(preds, y_true):
            # Current interval
            q_t = max(self._q * (1 + alpha_t - self.alpha), 1e-6)
            lo  = pred - q_t
            hi  = pred + q_t
            lowers.append(lo)
            uppers.append(hi)
            alphas.append(alpha_t)

            # Update alpha_t  (the ACI rule)
            hit      = int(lo <= y <= hi)
            alpha_t  = alpha_t + self.gamma * (self.alpha - (1 - hit))
            alpha_t  = np.clip(alpha_t, 0.001, 0.999)

        return np.array(lowers), np.array(uppers), np.array(alphas)


# ─── Factory: fit all three UQ methods ───────────────────────────────────────

def fit_all(cfg: dict, train: pd.DataFrame, val: pd.DataFrame,
            base: BaseForecaster):
    alpha = 1 - cfg["uq"]["confidence_levels"][1]   # use the higher conf level

    print("\n── Fitting Quantile Regression ──")
    qr = QuantileForecaster(cfg, alpha=alpha)
    qr.fit(train, val)

    print("\n── Fitting Static Conformal (MAPIE) ──")
    scp = StaticConformal(cfg, alpha=alpha)
    scp.fit(train, val)

    print("\n── Calibrating ACI ──")
    aci = ACI(cfg, alpha=alpha)
    aci.calibrate(base, val)
    best_gamma = aci.tune_gamma(base, val, cfg["uq"]["aci"]["gamma_grid"])
    aci.calibrate(base, val, gamma=best_gamma)

    return qr, scp, aci
