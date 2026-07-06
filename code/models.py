"""Model training and evaluation helpers for the ESG analyses.

Key principle: NEVER report accuracy metrics computed on the same data the
model was trained on.  Every reported metric is out-of-sample.

- Relationship models (ESG -> ROA/ROE on the panel): GroupKFold by firm_id
  so all rows of a firm are either in train or test.
- Time-series forecasting models (year -> metric): TimeSeriesSplit for
  rolling/expanding backtest.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, TimeSeriesSplit, cross_validate
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor


def _default_models() -> dict:
    return {
        "XGBoost": XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42,
            verbosity=0,
        ),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42,
        ),
        "Decision Tree": DecisionTreeRegressor(max_depth=4, random_state=42),
    }


def _regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute regression metrics. Used internally for train-set reference."""
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mse": mse,
        "rmse": np.sqrt(mse),
        "mae": mean_absolute_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
    }


# ---------------------------------------------------------------------------
#  Relationship models (ESG -> financial KPI) on the panel
# ---------------------------------------------------------------------------

def evaluate_relationship_model(panel: pd.DataFrame, outcome: str, model,
                                 n_splits: int = 5) -> dict:
    """
    Cross-validate an ESG->outcome model using GroupKFold by firm_id.

    All rows for a given firm are always in the same fold — prevents
    the model from 'recognizing' a firm across train/test.

    Returns both train and test scores; the gap reveals overfitting.
    """
    df = panel.dropna(subset=["esg", outcome]).copy()
    X = df[["esg"]].values
    y = df[outcome].values
    groups = df["firm_id"].values

    cv = GroupKFold(n_splits=n_splits)
    scores = cross_validate(
        model, X, y, groups=groups, cv=cv,
        scoring=["r2", "neg_root_mean_squared_error", "neg_mean_absolute_error"],
        return_train_score=True,
    )

    return {
        "test_r2_mean": float(scores["test_r2"].mean()),
        "test_r2_std": float(scores["test_r2"].std()),
        "train_r2_mean": float(scores["train_r2"].mean()),
        "test_rmse_mean": float(-scores["test_neg_root_mean_squared_error"].mean()),
        "test_mae_mean": float(-scores["test_neg_mean_absolute_error"].mean()),
    }


def evaluate_all_relationship_models(panel: pd.DataFrame) -> dict:
    """
    Evaluate all default models for ESG->ROA and ESG->ROE relationships.

    Returns a nested dict: {outcome: {model_name: {metrics}}}.
    """
    results = {}
    for outcome in ["roa", "roe"]:
        results[outcome] = {}
        for model_name, model in _default_models().items():
            cv_scores = evaluate_relationship_model(panel, outcome, model)
            results[outcome][model_name] = cv_scores
    return results


# ---------------------------------------------------------------------------
#  Time-series forecasting models (year -> metric) — for descriptive trends
# ---------------------------------------------------------------------------

def train_time_series_models(
    years: np.ndarray,
    values: np.ndarray,
    future_years: list[int],
) -> dict:
    """
    Train forecasting models using year as the single feature.

    NOTE: These tree models CANNOT extrapolate — forecasts beyond the
    training range produce flat lines (an artifact, not a prediction).
    They are kept for comparison only; the headline forecast uses
    linear/time-series models (see forecasting.py).
    """
    X = np.asarray(years).reshape(-1, 1)
    y = np.asarray(values)
    X_future = np.asarray(future_years).reshape(-1, 1)

    results = {}
    for model_name, model in _default_models().items():
        model.fit(X, y)
        training_predictions = model.predict(X)
        future_predictions = model.predict(X_future)

        # In-sample metrics are stored for reference but labelled as TRAIN.
        # They are NOT used for model selection.
        results[model_name] = {
            "model": model,
            "predictions_train": training_predictions,
            "predictions_future": future_predictions,
            **{f"train_{k}": v for k, v in _regression_metrics(y, training_predictions).items()},
        }

    return results


def evaluate_time_series_models(
    years: np.ndarray,
    values: np.ndarray,
    n_splits: int = 3,
) -> dict:
    """
    Evaluate forecasting models with TimeSeriesSplit (rolling backtest).

    Returns per-model held-out metrics so we can honestly compare them.
    """
    X = np.asarray(years).reshape(-1, 1)
    y = np.asarray(values)

    results = {}
    for model_name, model in _default_models().items():
        cv = TimeSeriesSplit(n_splits=n_splits)
        scores = cross_validate(
            model, X, y, cv=cv,
            scoring=["r2", "neg_root_mean_squared_error", "neg_mean_absolute_error"],
            return_train_score=True,
        )
        results[model_name] = {
            "test_r2_mean": float(scores["test_r2"].mean()),
            "test_r2_std": float(scores["test_r2"].std()),
            "train_r2_mean": float(scores["train_r2"].mean()),
            "test_rmse_mean": float(-scores["test_neg_root_mean_squared_error"].mean()),
            "test_mae_mean": float(-scores["test_neg_mean_absolute_error"].mean()),
        }
    return results


# ---------------------------------------------------------------------------
#  Relationship model training (for predictions, after evaluation)
# ---------------------------------------------------------------------------

def train_relationship_models(esg_scores: np.ndarray, values: np.ndarray) -> dict:
    """Train models that predict a financial KPI from ESG score.

    NOTE: in-sample metrics are labelled 'train_*' to make clear they
    must NOT be used for model selection or reported as accuracy.
    """
    X = np.asarray(esg_scores).reshape(-1, 1)
    y = np.asarray(values)

    results = {}
    for model_name, model in _default_models().items():
        model.fit(X, y)
        predictions = model.predict(X)

        results[model_name] = {
            "model": model,
            "predictions": predictions,
            **{f"train_{k}": v for k, v in _regression_metrics(y, predictions).items()},
        }

    return results


# ---------------------------------------------------------------------------
#  DataFrame builders for CSV output
# ---------------------------------------------------------------------------

def build_prediction_dataframe(future_years: list[int], model_results: dict) -> pd.DataFrame:
    """Create the wide predictions table used by the original notebook."""

    predictions = pd.DataFrame({"Year": future_years})
    for metric_name, results in model_results.items():
        for model_name, result in results.items():
            column = f"{metric_name}_{model_name.replace(' ', '_')}"
            predictions[column] = result["predictions_future"]

    return predictions


def build_metrics_dataframe(model_results: dict, ts_eval_results: dict = None) -> pd.DataFrame:
    """Flatten model performance metrics into a CSV-friendly table.

    Includes both train and test (out-of-sample) metrics side by side
    so the overfitting gap is visible.
    """
    rows = []
    for metric_name, results in model_results.items():
        for model_name, result in results.items():
            row = {
                "Metric": metric_name.replace("_", " "),
                "Model": model_name,
                "train_RMSE": result.get("train_rmse"),
                "train_MAE": result.get("train_mae"),
                "train_R2": result.get("train_r2"),
            }
            # Attach out-of-sample metrics if available
            if ts_eval_results and metric_name in ts_eval_results:
                eval_r = ts_eval_results[metric_name].get(model_name, {})
                row["test_R2"] = eval_r.get("test_r2_mean")
                row["test_RMSE"] = eval_r.get("test_rmse_mean")
                row["test_MAE"] = eval_r.get("test_mae_mean")
            rows.append(row)

    return pd.DataFrame(rows)


def best_model_name(results: dict, eval_results: dict = None) -> str:
    """Return the model with the highest OUT-OF-SAMPLE R2.

    Selection uses held-out score only — never training score.
    If eval_results are not provided, falls back to training R2
    with a warning comment.
    """
    if eval_results:
        # Selection by out-of-sample R2 only
        return max(eval_results.keys(),
                   key=lambda name: eval_results[name].get("test_r2_mean", float("-inf")))
    else:
        # Fallback: training R2 (should be avoided)
        return max(results.keys(), key=lambda name: results[name].get("train_r2", float("-inf")))
