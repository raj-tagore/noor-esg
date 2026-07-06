"""Analyze relationships between ESG scores and financial KPIs.

CRITICAL: ALL analyses (correlations, regressions, ML model training) use
the FIRM-LEVEL PANEL from build_panel_dataset() (~2,250 rows). There is no
sector-average aggregate anywhere in this module.

Period: 2011-2025 (15 years), Asian banking markets.
"""

import warnings

import numpy as np
import pandas as pd

from config import (
    OUTPUT_DIR,
    PANEL_CSV,
    RELATIONSHIP_MODEL_PERF_CSV,
    ROLLING_CORRELATIONS_CSV,
)
from data_processing import build_panel_dataset, ensure_output_dir
from models import evaluate_all_relationship_models
from panel_regression import run_all_panel_regressions, print_panel_summary
from relationship_plots import plot_detailed_relationship, plot_relationship_dashboard

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
#  Rolling correlations — on the PANEL, observed data only
# ---------------------------------------------------------------------------

def _rolling_correlations_panel(panel: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Compute rolling ESG-vs-outcome correlations on the firm-level panel.

    Within each sliding window of `window` years, we correlate ESG vs
    ROA/ROE across ALL firm-year observations in that window. This gives
    far more stable estimates than correlating a handful of yearly averages.

    IMPORTANT: uses observed data ONLY — no forecasted/predicted rows.
    The last window ends at the final observed year (2025).

    Caveat: 5-year windows on short data are noisy and exploratory.
    """
    years_sorted = sorted(panel["year"].unique())
    rows = []

    for i in range(window, len(years_sorted) + 1):
        window_years = years_sorted[i - window : i]
        window_data = panel[panel["year"].isin(window_years)]

        esg_roa = window_data.dropna(subset=["esg", "roa"])
        esg_roe = window_data.dropna(subset=["esg", "roe"])

        corr_roa = esg_roa["esg"].corr(esg_roa["roa"]) if len(esg_roa) > 2 else np.nan
        corr_roe = esg_roe["esg"].corr(esg_roe["roe"]) if len(esg_roe) > 2 else np.nan

        rows.append({
            "Window_End_Year": window_years[-1],
            "Window_Start_Year": window_years[0],
            "N_FirmYears_ROA": len(esg_roa),
            "N_FirmYears_ROE": len(esg_roe),
            "ESG_ROA_Correlation": corr_roa,
            "ESG_ROE_Correlation": corr_roe,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
#  Main analysis pipeline
# ---------------------------------------------------------------------------

def run_relationship_analysis() -> dict:
    """Run relationship analysis and write CSV/PNG outputs.

    Data source: firm-level panel (~2,250 rows) for every statistic,
    regression, and model in this module.
    """
    ensure_output_dir()

    # ===== PANEL DATA (all analyses use this) =====
    panel = build_panel_dataset()
    panel.to_csv(OUTPUT_DIR / PANEL_CSV, index=False)

    # --- Panel fixed-effects regressions (headline results) ---
    panel_results = run_all_panel_regressions(panel)

    # --- Out-of-sample ML evaluation on the panel (GroupKFold) ---
    ml_eval_results = evaluate_all_relationship_models(panel)

    # --- Save ML evaluation results ---
    ml_rows = []
    for outcome, models in ml_eval_results.items():
        for model_name, scores in models.items():
            ml_rows.append({
                "Outcome": outcome.upper(),
                "Model": model_name,
                "train_R2": scores["train_r2_mean"],
                "test_R2": scores["test_r2_mean"],
                "test_R2_std": scores["test_r2_std"],
                "test_RMSE": scores["test_rmse_mean"],
                "test_MAE": scores["test_mae_mean"],
                "overfit_gap": scores["train_r2_mean"] - scores["test_r2_mean"],
            })
    ml_perf_df = pd.DataFrame(ml_rows)
    ml_perf_df.to_csv(OUTPUT_DIR / RELATIONSHIP_MODEL_PERF_CSV, index=False)

    # --- Panel-level correlations (firm-year) ---
    panel_clean_roa = panel.dropna(subset=["esg", "roa"])
    panel_clean_roe = panel.dropna(subset=["esg", "roe"])

    panel_corr_roa = panel_clean_roa["esg"].corr(panel_clean_roa["roa"])
    panel_corr_roe = panel_clean_roe["esg"].corr(panel_clean_roe["roe"])

    # --- Rolling correlations on the panel (observed data only) ---
    rolling_df = _rolling_correlations_panel(panel)
    rolling_df.to_csv(OUTPUT_DIR / ROLLING_CORRELATIONS_CSV, index=False)

    # --- Save correlation results ---
    correlation_results = pd.DataFrame({
        "Relationship": [
            "ESG vs ROA (panel, firm-year)",
            "ESG vs ROE (panel, firm-year)",
        ],
        "Correlation": [panel_corr_roa, panel_corr_roe],
        "N_obs": [len(panel_clean_roa), len(panel_clean_roe)],
        "Note": [
            "Firm-level panel correlation",
            "Firm-level panel correlation",
        ],
    })
    correlation_results.to_csv(OUTPUT_DIR / "banking_correlation_results.csv", index=False)

    # --- Build context dict for plots ---
    context = {
        "panel": panel,
        "panel_results": panel_results,
        "ml_eval_results": ml_eval_results,
        "panel_corr_roa": panel_corr_roa,
        "panel_corr_roe": panel_corr_roe,
        "rolling_df": rolling_df,
    }

    plot_relationship_dashboard(context)
    plot_detailed_relationship(context)
    return context


def print_summary(context: dict) -> None:
    print("=" * 80)
    print("ASIAN BANKING SECTOR: ESG & FINANCIAL KPIs RELATIONSHIP ANALYSIS")
    print("Period: 2011-2025 (15 years)")
    print("=" * 80)

    # Headline: panel fixed-effects results
    print_panel_summary(context["panel_results"])

    # Panel-level correlations
    print(f"\nPanel-level correlations (firm-year, n~2000+):")
    print(f"  ESG vs ROA: r = {context['panel_corr_roa']:.4f}")
    print(f"  ESG vs ROE: r = {context['panel_corr_roe']:.4f}")

    # ML model evaluation
    print(f"\nML model out-of-sample performance (GroupKFold by firm):")
    for outcome, models in context["ml_eval_results"].items():
        print(f"\n  ESG -> {outcome.upper()}:")
        for model_name, scores in models.items():
            print(f"    {model_name}: test_R2 = {scores['test_r2_mean']:.4f} "
                  f"(train_R2 = {scores['train_r2_mean']:.4f}, gap = "
                  f"{scores['train_r2_mean'] - scores['test_r2_mean']:.4f})")

    print("\nFiles generated in outputs/:")
    print("  banking_esg_relationship_analysis.png")
    print("  banking_detailed_relationship.png")
    print("  banking_correlation_results.csv")
    print("  banking_rolling_correlations.csv")
    print("  banking_relationship_model_performance.csv")
    print("  banking_panel_regression_results.csv")


def main() -> None:
    context = run_relationship_analysis()
    print_summary(context)


if __name__ == "__main__":
    main()
