"""Run historical trend analysis and 2026-2030 forecasts.

Uses sector-level yearly means (descriptive only) for trend visualization
and the new linear-trend forecasting model for extrapolation.  Tree models
are kept solely as a teaching contrast to illustrate why they cannot
extrapolate.

Period: 2011-2025 (15 years), Asian banking markets.
"""

import warnings

import pandas as pd

from config import FUTURE_YEARS, HISTORICAL_CSV, MODEL_PERFORMANCE_CSV, OUTPUT_DIR, PREDICTIONS_CSV
from data_processing import ensure_output_dir, load_banking_dataset
from forecasting import build_forecast_dataframe, linear_trend_forecast
from models import (
    best_model_name,
    build_metrics_dataframe,
    build_prediction_dataframe,
    evaluate_time_series_models,
    train_time_series_models,
)
from trend_plots import plot_detailed_trends, plot_forecast_dashboard, plot_statistics_summary

warnings.filterwarnings("ignore")


def run_trend_analysis() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run the trend analysis and write CSV/PNG outputs.

    The sector_yearly_means (15-row aggregate) is used here for
    DESCRIPTIVE trend plots only.  It is never used for correlation,
    regression, model training, or significance testing.
    """
    ensure_output_dir()
    dataset = load_banking_dataset()
    # Descriptive sector-level yearly means.
    # For plotting/context ONLY. Not for correlation, regression,
    # model training, or significance testing.
    sector_yearly_means = dataset.historical

    # ----- Tree-based models (kept for comparison / teaching contrast) -----
    tree_model_results = {
        "ESG_Score": train_time_series_models(
            sector_yearly_means["Year"], sector_yearly_means["ESG_Score"], FUTURE_YEARS
        ),
        "Pretax_ROA": train_time_series_models(
            sector_yearly_means["Year"], sector_yearly_means["Pretax_ROA"], FUTURE_YEARS
        ),
        "Pretax_ROE": train_time_series_models(
            sector_yearly_means["Year"], sector_yearly_means["Pretax_ROE"], FUTURE_YEARS
        ),
    }

    # ----- Out-of-sample evaluation for tree models (TimeSeriesSplit) -----
    ts_eval_results = {
        "ESG_Score": evaluate_time_series_models(
            sector_yearly_means["Year"].values, sector_yearly_means["ESG_Score"].values
        ),
        "Pretax_ROA": evaluate_time_series_models(
            sector_yearly_means["Year"].values, sector_yearly_means["Pretax_ROA"].values
        ),
        "Pretax_ROE": evaluate_time_series_models(
            sector_yearly_means["Year"].values, sector_yearly_means["Pretax_ROE"].values
        ),
    }

    # ----- Linear trend forecasts (extrapolation-capable, headline) -----
    linear_forecasts = {
        "ESG_Score": linear_trend_forecast(
            sector_yearly_means["Year"].values, sector_yearly_means["ESG_Score"].values
        ),
        "Pretax_ROA": linear_trend_forecast(
            sector_yearly_means["Year"].values, sector_yearly_means["Pretax_ROA"].values
        ),
        "Pretax_ROE": linear_trend_forecast(
            sector_yearly_means["Year"].values, sector_yearly_means["Pretax_ROE"].values
        ),
    }

    # ----- Build output DataFrames -----
    tree_predictions_df = build_prediction_dataframe(FUTURE_YEARS, tree_model_results)
    linear_forecast_df = build_forecast_dataframe(linear_forecasts)

    # Merge tree and linear into a single predictions CSV
    predictions_df = tree_predictions_df.merge(linear_forecast_df, on="Year")

    metrics_df = build_metrics_dataframe(tree_model_results, ts_eval_results)

    # ----- Save CSVs -----
    sector_yearly_means.to_csv(OUTPUT_DIR / HISTORICAL_CSV, index=False)
    predictions_df.to_csv(OUTPUT_DIR / PREDICTIONS_CSV, index=False)
    metrics_df.to_csv(OUTPUT_DIR / MODEL_PERFORMANCE_CSV, index=False)

    # ----- Plots -----
    plot_forecast_dashboard(sector_yearly_means, tree_model_results, FUTURE_YEARS,
                            linear_forecasts=linear_forecasts)
    plot_detailed_trends(sector_yearly_means, tree_model_results, FUTURE_YEARS,
                         linear_forecasts=linear_forecasts)
    plot_statistics_summary(sector_yearly_means, tree_model_results,
                            ts_eval_results=ts_eval_results,
                            linear_forecasts=linear_forecasts)

    return sector_yearly_means, predictions_df, metrics_df


def print_summary(
    historical_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
) -> None:
    print("=" * 80)
    print("BANKING SECTOR (Asian Markets): ESG, ROE & ROA TREND ANALYSIS")
    print("Historical Trends (2011-2025) & Forecasts (2026-2030)")
    print("=" * 80)
    print("\nSector-average historical data (DESCRIPTIVE ONLY):")
    print(historical_df.to_string(index=False))
    print("\nModel performance (train vs. out-of-sample):")
    print(metrics_df.to_string(index=False))
    print("\nForecasts (linear trend = headline; tree models = comparison only):")
    print(predictions_df.to_string(index=False))

    # Print linear trend headline
    for col in ["ESG_Score", "Pretax_ROA", "Pretax_ROE"]:
        fc_col = f"{col}_forecast"
        if fc_col in predictions_df.columns:
            vals = predictions_df[fc_col]
            print(f"\n  {col} linear trend forecast: {vals.iloc[0]:.2f} (2026) -> {vals.iloc[-1]:.2f} (2030)")

    print("\nCAVEAT: 15 annual observations is a very short series;")
    print("forecasts to 2030 are illustrative and highly uncertain.")
    print("\nFiles generated in outputs/:")
    print(f"  {HISTORICAL_CSV}")
    print(f"  {PREDICTIONS_CSV}")
    print(f"  {MODEL_PERFORMANCE_CSV}")
    print("  banking_esg_roa_roe_analysis.png")
    print("  banking_detailed_trends.png")
    print("  banking_statistics_summary.png")


def main() -> None:
    historical_df, predictions_df, metrics_df = run_trend_analysis()
    print_summary(historical_df, predictions_df, metrics_df)


if __name__ == "__main__":
    main()
