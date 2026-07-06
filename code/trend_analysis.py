"""Descriptive statistics and the illustrative 2026-2030 linear-trend forecast.

The only sector-level aggregate here is a per-year mean/std/N table built
from the firm-level panel. Forecasting uses a single OLS linear-trend
model with prediction intervals (see forecasting.py) — no tree models.

Period: 2011-2025 (15 years), Asian banking markets.
"""

import warnings

import pandas as pd

from config import DESCRIPTIVE_STATS_CSV, FORECAST_CSV, FUTURE_YEARS, OUTPUT_DIR
from data_processing import build_descriptive_stats, build_panel_dataset, ensure_output_dir
from forecasting import build_forecast_dataframe, linear_trend_forecast
from trend_plots import plot_forecast_chart

warnings.filterwarnings("ignore")


def run_trend_analysis() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build descriptive stats from the panel and the linear-trend forecast."""
    ensure_output_dir()

    panel = build_panel_dataset()
    descriptive_stats = build_descriptive_stats(panel)
    descriptive_stats.to_csv(OUTPUT_DIR / DESCRIPTIVE_STATS_CSV, index=False)

    forecasts = {
        "esg": linear_trend_forecast(descriptive_stats["Year"].values, descriptive_stats["ESG_mean"].values),
        "roa": linear_trend_forecast(descriptive_stats["Year"].values, descriptive_stats["ROA_mean"].values),
        "roe": linear_trend_forecast(descriptive_stats["Year"].values, descriptive_stats["ROE_mean"].values),
    }
    forecast_df = build_forecast_dataframe(forecasts, FUTURE_YEARS)
    forecast_df.to_csv(OUTPUT_DIR / FORECAST_CSV, index=False)

    plot_forecast_chart(descriptive_stats, forecasts, FUTURE_YEARS)

    return descriptive_stats, forecast_df


def print_summary(descriptive_stats: pd.DataFrame, forecast_df: pd.DataFrame) -> None:
    print("=" * 80)
    print("BANKING SECTOR (Asian Markets): DESCRIPTIVE STATS & ILLUSTRATIVE FORECAST")
    print("Observed (2011-2025) & Linear-Trend Forecast (2026-2030)")
    print("=" * 80)
    print("\nPer-year descriptive statistics (from the firm-level panel):")
    print(descriptive_stats.to_string(index=False))
    print("\nIllustrative sector-level linear-trend forecast:")
    print(forecast_df.to_string(index=False))

    for key in ["esg", "roa", "roe"]:
        fc_col = f"{key}_forecast"
        if fc_col in forecast_df.columns:
            vals = forecast_df[fc_col]
            print(f"\n  {key.upper()} linear trend forecast: {vals.iloc[0]:.2f} (2026) -> {vals.iloc[-1]:.2f} (2030)")

    print("\nCAVEAT: 15 annual observations is a very short series;")
    print("forecasts to 2030 are illustrative and highly uncertain.")
    print("\nFiles generated in outputs/:")
    print(f"  {DESCRIPTIVE_STATS_CSV}")
    print(f"  {FORECAST_CSV}")
    print("  banking_forecast_2026_2030.png")


def main() -> None:
    descriptive_stats, forecast_df = run_trend_analysis()
    print_summary(descriptive_stats, forecast_df)


if __name__ == "__main__":
    main()
