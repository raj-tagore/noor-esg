"""Exploratory inspection of the firm-year panel and sample atlas plots.

Builds the panel, prints composition facts, writes a composition CSV, and
generates descriptive plots under outputs/explore/.
"""

from __future__ import annotations

import pandas as pd

from config import EXPLORE_DIR
from data_processing import build_panel_dataset, load_raw_dataset
from explore_plots import build_composition_summary, ensure_explore_dir, run_all_explore_plots
from groups import add_group_columns


def print_panel_summary(panel: pd.DataFrame) -> None:
    n_firms = panel["firm_id"].nunique()
    n_rows = len(panel)
    years = sorted(panel["year"].unique())
    grouped = add_group_columns(panel)

    print("=" * 80)
    print("FIRM-YEAR PANEL: EXPLORATORY SUMMARY")
    print("=" * 80)
    print(f"Firms: {n_firms}")
    print(f"Firm-years: {n_rows:,}")
    print(f"Year range: {years[0]}-{years[-1]} ({len(years)} years)")
    print("Grouped plots use the same country/industry groups as heterogeneity analysis")

    print("\nFirms by country_hq:")
    country_counts = (
        panel.groupby("country_hq")["firm_id"]
        .nunique()
        .sort_values(ascending=False)
    )
    print(country_counts.to_string())

    print("\nFirms by analysis country_group:")
    print(
        grouped.groupby("country_group")["firm_id"]
        .nunique()
        .sort_values(ascending=False)
        .to_string()
    )

    print("\nFirms by industry:")
    industry_counts = (
        panel.groupby("industry")["firm_id"]
        .nunique()
        .sort_values(ascending=False)
    )
    print(industry_counts.to_string())

    print("\nFirms by analysis industry_group:")
    print(
        grouped.groupby("industry_group")["firm_id"]
        .nunique()
        .sort_values(ascending=False)
        .to_string()
    )

    print("\nNon-null rates (firm-years):")
    for col in ["esg", "roa", "roe"]:
        rate = panel[col].notna().mean() * 100
        print(f"  {col}: {rate:.1f}% ({panel[col].notna().sum():,} / {n_rows:,})")


def print_raw_peek() -> None:
    """Show the true two-row header layout (header=None), not pandas' Unnamed view."""

    raw_df = load_raw_dataset()
    print("\n" + "=" * 80)
    print("RAW WORKBOOK PEEK (header=None — how the panel loader reads it)")
    print("=" * 80)
    print("Raw shape:", raw_df.shape)
    print("\nRow 0 (block labels): cols 0-4 ids, then ESG / ROA / ROE blocks")
    print(raw_df.iloc[0, [0, 1, 2, 3, 4, 5, 20, 35]].to_string())
    print("\nRow 1 (fiscal-year labels under each metric block):")
    print("  ESG years (cols 5-19):", raw_df.iloc[1, 5:20].tolist())
    print("  ROA years (cols 20-34):", raw_df.iloc[1, 20:35].tolist())
    print("  ROE years (cols 35-49):", raw_df.iloc[1, 35:50].tolist())
    print("\nRow 2 (first firm):")
    print(raw_df.iloc[2, :6].to_string())
    print(f"\nFirm data rows: {len(raw_df) - 2} (rows index 2..{len(raw_df) - 1})")


def main() -> None:
    panel = build_panel_dataset()
    print_panel_summary(panel)

    ensure_explore_dir()
    summary = build_composition_summary(panel)
    summary_path = EXPLORE_DIR / "panel_composition_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"\nWrote {summary_path}")

    print("\nGenerating exploratory plots...")
    outputs = run_all_explore_plots(panel)
    print(f"Wrote {len(outputs)} files under {EXPLORE_DIR}:")
    for name in outputs:
        print(f"  {name}")

    print_raw_peek()


if __name__ == "__main__":
    main()
