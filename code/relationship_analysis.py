"""Analyze relationships between ESG scores and financial KPIs.

CRITICAL: ALL inferential analyses (correlations used as research evidence,
regressions, ML model training) use the FIRM-LEVEL PANEL from
build_panel_dataset() (~2,250 rows).  The 15-row sector-average table is
used ONLY for descriptive trend plots and is clearly labelled as such.

Period: 2011-2025 (15 years), Asian banking markets.
"""

import warnings

import numpy as np
import pandas as pd
from scipy import stats

from config import (
    MODEL_PERFORMANCE_CSV,
    OUTPUT_DIR,
    PANEL_CSV,
    ROLLING_CORRELATIONS_CSV,
)
from data_processing import build_panel_dataset, ensure_output_dir, load_banking_dataset
from models import evaluate_all_relationship_models, train_relationship_models
from panel_regression import run_all_panel_regressions, print_panel_summary
from relationship_plots import plot_detailed_relationship, plot_relationship_dashboard

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
#  Rolling correlations — on the PANEL, observed data only (Task 5)
# ---------------------------------------------------------------------------

def _rolling_correlations_panel(panel: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Compute rolling ESG-vs-outcome correlations on the firm-level panel.

    Within each sliding window of `window` years, we correlate ESG vs
    ROA/ROE across ALL firm-year observations in that window.  This gives
    far more stable estimates than correlating 5 yearly averages.

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

    Data source: firm-level panel (~2,250 rows) for all inferential
    analyses.  The 15-row sector average is used only for descriptive
    trend context in plots.
    """
    ensure_output_dir()

    # ===== PANEL DATA (inferential — all stats/models use this) =====
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
    ml_perf_df.to_csv(OUTPUT_DIR / "banking_relationship_model_performance.csv", index=False)

    # --- Panel-level correlations (firm-year, the honest ones) ---
    panel_clean_roa = panel.dropna(subset=["esg", "roa"])
    panel_clean_roe = panel.dropna(subset=["esg", "roe"])

    panel_corr_roa = panel_clean_roa["esg"].corr(panel_clean_roa["roa"])
    panel_corr_roe = panel_clean_roe["esg"].corr(panel_clean_roe["roe"])

    # --- Rolling correlations on the panel (observed data only, Task 5) ---
    rolling_df = _rolling_correlations_panel(panel)
    rolling_df.to_csv(OUTPUT_DIR / ROLLING_CORRELATIONS_CSV, index=False)

    # ===== DESCRIPTIVE SECTOR AVERAGES (for context/trend plots only) =====
    dataset = load_banking_dataset()
    # Descriptive sector-level yearly means.
    # For plotting/context ONLY. Not for correlation, regression,
    # model training, or significance testing.
    sector_yearly_means = dataset.historical

    # Descriptive sector-level Pearson correlation on yearly averages.
    # This is NOT a firm-level or causal estimate — it reflects
    # time-trend co-movement only.
    desc_corr_roa = sector_yearly_means["ESG_Score"].corr(sector_yearly_means["Pretax_ROA"])
    desc_corr_roe = sector_yearly_means["ESG_Score"].corr(sector_yearly_means["Pretax_ROE"])
    desc_corr_roa_roe = sector_yearly_means["Pretax_ROA"].corr(sector_yearly_means["Pretax_ROE"])

    # --- Train relationship models on the panel for plot predictions ---
    panel_roa = panel.dropna(subset=["esg", "roa"])
    panel_roe = panel.dropna(subset=["esg", "roe"])
    roa_models = train_relationship_models(panel_roa["esg"].values, panel_roa["roa"].values)
    roe_models = train_relationship_models(panel_roe["esg"].values, panel_roe["roe"].values)

    # --- Save combined correlation results ---
    correlation_results = pd.DataFrame({
        "Relationship": [
            "ESG vs ROA (panel, firm-year)",
            "ESG vs ROE (panel, firm-year)",
            "ESG vs ROA (sector avg, descriptive only)",
            "ESG vs ROE (sector avg, descriptive only)",
            "ROA vs ROE (sector avg, descriptive only)",
        ],
        "Correlation": [
            panel_corr_roa, panel_corr_roe,
            desc_corr_roa, desc_corr_roe, desc_corr_roa_roe,
        ],
        "N_obs": [
            len(panel_clean_roa), len(panel_clean_roe),
            len(sector_yearly_means), len(sector_yearly_means), len(sector_yearly_means),
        ],
        "Note": [
            "Firm-level panel correlation",
            "Firm-level panel correlation",
            "Descriptive time-trend ONLY, NOT causal",
            "Descriptive time-trend ONLY, NOT causal",
            "Descriptive time-trend ONLY, NOT causal",
        ],
    })
    correlation_results.to_csv(OUTPUT_DIR / "banking_correlation_results.csv", index=False)

    # --- Build context dict for plots ---
    context = {
        # Panel data (inferential)
        "panel": panel,
        "panel_results": panel_results,
        "ml_eval_results": ml_eval_results,
        "panel_corr_roa": panel_corr_roa,
        "panel_corr_roe": panel_corr_roe,
        "rolling_df": rolling_df,
        "roa_models": roa_models,
        "roe_models": roe_models,
        # Descriptive sector averages (plotting only)
        "sector_yearly_means": sector_yearly_means,
        "desc_corr_roa": desc_corr_roa,
        "desc_corr_roe": desc_corr_roe,
        "desc_corr_roa_roe": desc_corr_roa_roe,
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

    # Descriptive sector-level (clearly labelled)
    print(f"\nDescriptive sector-average correlations (n=15, time-trend ONLY):")
    print(f"  ESG vs ROA: r = {context['desc_corr_roa']:.4f}")
    print(f"  ESG vs ROE: r = {context['desc_corr_roe']:.4f}")
    print(f"  (NOT causal or firm-level estimates)")

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
