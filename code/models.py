"""Out-of-sample relationship model evaluation for the ESG banking panel.

Key principle: NEVER report accuracy metrics computed on the same data the
model was trained on. Every reported metric is out-of-sample.

Relationship models (ESG -> ROA/ROE on the panel) are evaluated with
GroupKFold by firm_id, so all rows of a firm are always in the same fold.
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold, cross_validate
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
