"""Run the full panel-based ESG analysis pipeline.

Pipeline order:
1. Panel fixed-effects regression + out-of-sample ML evaluation + correlations
2. Country-group and industry subsample FE (heterogeneity)
3. Descriptive stats + illustrative linear-trend forecast (2026-2030)

All outputs are written to outputs/.

Period: 2011-2025 (15 years), Asian banking markets.
"""

from heterogeneity import run_heterogeneity_analysis, print_summary as print_heterogeneity_summary
from relationship_analysis import run_relationship_analysis, print_summary as print_relationship_summary
from trend_analysis import run_trend_analysis, print_summary as print_trend_summary


def main() -> None:
    # 1. Panel-based relationship analysis (regressions, ML, correlations)
    relationship_context = run_relationship_analysis()
    print_relationship_summary(relationship_context)

    print()

    # 2. Country / industry heterogeneity (same FE estimator on subsamples)
    heterogeneity_context = run_heterogeneity_analysis()
    print_heterogeneity_summary(heterogeneity_context)

    print()

    # 3. Descriptive stats + illustrative linear-trend forecast
    descriptive_stats, forecast_df = run_trend_analysis()
    print_trend_summary(descriptive_stats, forecast_df)


if __name__ == "__main__":
    main()
