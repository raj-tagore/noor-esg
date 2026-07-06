"""Run the full corrected ESG analysis pipeline.

Pipeline order:
1. Build firm-level panel dataset (~2,250 rows)
2. Descriptive sector-average trend analysis + linear forecasts
3. Panel fixed-effects regression + relationship analysis
4. All outputs written to outputs/

Period: 2011-2025 (15 years), Asian banking markets.
"""

from relationship_analysis import run_relationship_analysis, print_summary as print_relationship_summary
from trend_analysis import run_trend_analysis, print_summary as print_trend_summary


def main() -> None:
    # 1. Trend analysis (descriptive sector averages + forecasts)
    historical_df, predictions_df, metrics_df = run_trend_analysis()
    print_trend_summary(historical_df, predictions_df, metrics_df)

    print()

    # 2. Relationship analysis (panel-based inference + descriptive context)
    relationship_context = run_relationship_analysis()
    print_relationship_summary(relationship_context)


if __name__ == "__main__":
    main()
