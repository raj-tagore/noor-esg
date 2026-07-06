"""Illustrative sector-level linear-trend forecast for 2026-2030.

OLS linear trend on the 15 annual descriptive means, with prediction
intervals. This is the sole forecasting method in the pipeline.

CAVEAT: 15 annual observations is a very short series; forecasts to
2030 are illustrative and highly uncertain.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats as sp_stats

from config import FUTURE_YEARS, OUTPUT_DIR


def linear_trend_forecast(
    years: np.ndarray,
    values: np.ndarray,
    future_years: list[int] | None = None,
    confidence: float = 0.95,
) -> dict:
    """
    OLS linear trend: value = a + b*year, with prediction intervals.

    This model CAN extrapolate (unlike trees) and honestly expresses
    the large uncertainty inherent in a 15-point projection.

    Returns point forecasts and lower/upper prediction intervals.
    """
    if future_years is None:
        future_years = FUTURE_YEARS

    years = np.asarray(years, dtype=float)
    values = np.asarray(values, dtype=float)

    # OLS via statsmodels for proper prediction intervals
    X = sm.add_constant(years)
    model = sm.OLS(values, X).fit()

    # Historical fitted values
    fitted = model.predict(X)

    # Future predictions with prediction intervals
    X_future = sm.add_constant(np.asarray(future_years, dtype=float))
    predictions = model.predict(X_future)
    pred_summary = model.get_prediction(X_future).summary_frame(alpha=1 - confidence)

    return {
        "model": model,
        "model_name": "Linear Trend (OLS)",
        "fitted_historical": fitted,
        "predictions": predictions,
        "pred_lower": pred_summary["obs_ci_lower"].values,
        "pred_upper": pred_summary["obs_ci_upper"].values,
        "slope": model.params[1],
        "intercept": model.params[0],
        "r2": model.rsquared,
        "future_years": future_years,
        "confidence": confidence,
        "n_obs": len(years),
        "caveat": (
            "15 annual observations is a very short series; "
            "forecasts to 2030 are illustrative and highly uncertain."
        ),
    }


def build_forecast_dataframe(
    forecast_results: dict[str, dict],
    future_years: list[int] | None = None,
) -> pd.DataFrame:
    """
    Build a CSV-ready DataFrame with point forecasts and prediction
    intervals for each metric (ESG, ROA, ROE).
    """
    if future_years is None:
        future_years = FUTURE_YEARS

    df = pd.DataFrame({"Year": future_years})
    for metric_name, result in forecast_results.items():
        df[f"{metric_name}_forecast"] = result["predictions"]
        df[f"{metric_name}_lower"] = result["pred_lower"]
        df[f"{metric_name}_upper"] = result["pred_upper"]

    return df
