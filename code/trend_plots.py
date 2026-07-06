"""Visualization for the illustrative 2026-2030 linear-trend forecast.

Exactly one chart: per-metric descriptive mean line (2011-2025) plus the
OLS linear-trend fitted/forecast line and its prediction band. No tree
model lines, no dual-axis overlays.
"""

import matplotlib.pyplot as plt

from config import METRICS, OUTPUT_DIR


def plot_forecast_chart(descriptive_stats, forecasts: dict, future_years: list[int]) -> None:
    """One PNG with one subplot per metric: descriptive mean + linear forecast + PI band."""

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    for ax, (key, title) in zip(axes, METRICS):
        mean_col = f"{key.upper()}_mean"
        lf = forecasts[key]

        ax.plot(
            descriptive_stats["Year"], descriptive_stats[mean_col],
            "o-", color="#2C3E50", linewidth=2.5, markersize=7,
            label="Sector mean (observed)",
        )
        ax.plot(
            future_years, lf["predictions"],
            "D-", color="#8E44AD", linewidth=2.5, markersize=7,
            label="Linear trend forecast", zorder=5,
        )
        ax.fill_between(
            future_years, lf["pred_lower"], lf["pred_upper"],
            alpha=0.15, color="#8E44AD", label="95% Prediction Interval",
        )
        ax.axvline(x=descriptive_stats["Year"].max(), color="red", linestyle=":", linewidth=1.5, alpha=0.5)
        ax.set_xlabel("Year", fontsize=11, fontweight="bold")
        ax.set_ylabel(title, fontsize=11, fontweight="bold")
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.suptitle(
        "Illustrative Sector-Level Projection (15 annual points, wide uncertainty)\n"
        "2011-2025 Observed Means & 2026-2030 Linear-Trend Forecast",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.9])
    plt.savefig(OUTPUT_DIR / "banking_forecast_2026_2030.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
