"""Run the full panel-based ESG analysis pipeline.

Pipeline order:
1. Build firm-level panel dataset (~2,250 rows) + descriptive stats
2. Panel fixed-effects regression + out-of-sample ML evaluation + correlations
3. Illustrative linear-trend forecast (2026-2030)
4. All outputs written to outputs/

Period: 2011-2025 (15 years), Asian banking markets.
"""

from relationship_analysis import run_relationship_analysis, print_summary as print_relationship_summary
from trend_analysis import run_trend_analysis, print_summary as print_trend_summary


def main() -> None:
    # 1. Panel-based relationship analysis (regressions, ML, correlations)
    relationship_context = run_relationship_analysis()
    print_relationship_summary(relationship_context)

    print()

    # 2. Descriptive stats + illustrative linear-trend forecast
    descriptive_stats, forecast_df = run_trend_analysis()
    print_trend_summary(descriptive_stats, forecast_df)


if __name__ == "__main__":
    main()
