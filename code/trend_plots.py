"""Visualizations for historical trends and 2026-2030 forecasts.

All trend plots use sector-level yearly means (descriptive only).
Labels consistently use 2011-2025 (15 years), Asian banking markets.
"""

import numpy as np
import matplotlib.pyplot as plt

from config import METRICS, OUTPUT_DIR
from models import best_model_name


MODEL_COLORS = {
    "XGBoost": "#E74C3C",
    "Random Forest": "#3498DB",
    "Decision Tree": "#2ECC71",
}


def set_plot_style() -> None:
    plt.style.use("seaborn-v0_8-darkgrid")


def plot_forecast_dashboard(historical_df, model_results, future_years,
                            linear_forecasts=None) -> None:
    """Create the main 3x3 trend, model, and forecast dashboard.

    The linear-trend forecast (with prediction intervals) is the
    headline.  Tree-model forecasts are shown for contrast only.
    """
    set_plot_style()
    fig = plt.figure(figsize=(20, 14))

    for index, (column, title) in enumerate(METRICS, 1):
        results = model_results[column]
        ax = plt.subplot(3, 3, index)
        ax.plot(
            historical_df["Year"],
            historical_df[column],
            "o-",
            color="#2C3E50",
            linewidth=2.5,
            markersize=8,
            label="Historical Data (Sector Avg)",
        )

        # Linear trend forecast (headline)
        if linear_forecasts and column in linear_forecasts:
            lf = linear_forecasts[column]
            ax.plot(
                future_years,
                lf["predictions"],
                "D-",
                color="#8E44AD",
                linewidth=2.5,
                markersize=8,
                label="Linear Trend (headline)",
                zorder=7,
            )
            ax.fill_between(
                future_years,
                lf["pred_lower"],
                lf["pred_upper"],
                alpha=0.15,
                color="#8E44AD",
                label="95% Prediction Interval",
            )

        # Tree forecasts (comparison only, labelled as artifacts)
        for model_name, result in results.items():
            ax.plot(
                future_years,
                result["predictions_future"],
                "s--",
                color=MODEL_COLORS[model_name],
                linewidth=1.5,
                markersize=5,
                label=f"{model_name} (cannot extrapolate)",
                alpha=0.5,
            )

        ax.axvline(x=2025, color="red", linestyle=":", linewidth=1.5, alpha=0.5)
        ax.axvspan(2025, 2030, alpha=0.1, color="orange")
        ax.set_xlabel("Year", fontsize=11, fontweight="bold")
        ax.set_ylabel(title, fontsize=11, fontweight="bold")
        ax.set_title(f"{title} - Sector-Average Trend (Descriptive)", fontsize=12, fontweight="bold")
        ax.legend(loc="best", frameon=True, shadow=True, fontsize=7)
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.set_xlim(2010, 2031)

    for index, (column, title) in enumerate(METRICS, 4):
        results = model_results[column]
        ax = plt.subplot(3, 3, index)
        model_names = list(results.keys())
        rmse_values = [results[name].get("train_rmse", 0) for name in model_names]
        r2_values = [results[name].get("train_r2", 0) for name in model_names]
        x = np.arange(len(model_names))
        width = 0.35

        ax2 = ax.twinx()
        bars1 = ax.bar(x - width / 2, rmse_values, width, label="Train RMSE", color="#E74C3C", alpha=0.8)
        bars2 = ax2.bar(x + width / 2, r2_values, width, label="Train R2", color="#27AE60", alpha=0.8)

        ax.set_xlabel("Model", fontsize=11, fontweight="bold")
        ax.set_ylabel("RMSE", fontsize=10, fontweight="bold", color="#E74C3C")
        ax2.set_ylabel("R2 Score (TRAIN ONLY)", fontsize=10, fontweight="bold", color="#27AE60")
        ax.set_title(f"{title} - Model Performance (Train Set)", fontsize=12, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, rotation=15, ha="right", fontsize=9)
        ax.tick_params(axis="y", labelcolor="#E74C3C")
        ax2.tick_params(axis="y", labelcolor="#27AE60")
        ax.grid(True, alpha=0.3, axis="y")

        for bar in bars1:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=8)
        for bar in bars2:
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=8)

        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(handles1 + handles2, labels1 + labels2, loc="upper left", fontsize=8)

    for index, (column, title) in enumerate(METRICS, 7):
        results = model_results[column]
        ax = plt.subplot(3, 3, index)
        all_years = list(historical_df["Year"]) + future_years

        ax.plot(
            historical_df["Year"],
            historical_df[column],
            "o-",
            color="#34495E",
            linewidth=3,
            markersize=9,
            label="Historical (2011-2025, Sector Avg)",
            zorder=5,
        )

        # Linear trend as headline
        if linear_forecasts and column in linear_forecasts:
            lf = linear_forecasts[column]
            # Show full fitted + forecast line
            hist_fitted = lf["fitted_historical"]
            all_fitted = np.concatenate([hist_fitted, lf["predictions"]])
            ax.plot(all_years, all_fitted, "-", color="#8E44AD", linewidth=2,
                    label="Linear Trend (headline)", alpha=0.8)
            ax.fill_between(
                future_years, lf["pred_lower"], lf["pred_upper"],
                alpha=0.15, color="#8E44AD", label="95% PI",
            )

        # Tree models dimmed
        for model_name, result in results.items():
            full_prediction = np.concatenate([result["predictions_train"], result["predictions_future"]])
            ax.plot(all_years, full_prediction, "--", color=MODEL_COLORS[model_name],
                    linewidth=1, label=f"{model_name} (artifact)", alpha=0.4)

        last_year = historical_df["Year"].iloc[-1]
        last_value = historical_df[column].iloc[-1]
        ax.annotate(
            f"{last_year}: {last_value:.2f}",
            xy=(last_year, last_value),
            xytext=(-40, 15),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
            fontsize=8,
            fontweight="bold",
        )

        ax.axvspan(2025.5, 2030.5, alpha=0.15, color="red", label="Forecast Period")
        ax.axvline(x=2025, color="red", linestyle="--", linewidth=2, alpha=0.7)
        ax.set_xlabel("Year", fontsize=11, fontweight="bold")
        ax.set_ylabel(title, fontsize=11, fontweight="bold")
        ax.set_title(f"{title} - Complete Trend (2011-2030, Descriptive)", fontsize=12, fontweight="bold")
        ax.legend(loc="best", frameon=True, shadow=True, fontsize=7)
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.set_xlim(2010, 2031)

    plt.suptitle(
        "Asian Banking Sector: ESG Score, Pretax ROE & ROA Analysis (Descriptive)\n"
        "Historical Sector-Average Trends (2011-2025) & Forecasts (2026-2030)",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUTPUT_DIR / "banking_esg_roa_roe_analysis.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_detailed_trends(historical_df, model_results, future_years,
                         linear_forecasts=None) -> None:
    """Create one detailed trend plot per metric."""

    set_plot_style()
    fig, axes = plt.subplots(3, 1, figsize=(16, 14))

    for ax, (column, title) in zip(axes, METRICS):
        results = model_results[column]
        values = historical_df[column].values

        ax.plot(
            historical_df["Year"],
            values,
            "ko-",
            linewidth=3,
            markersize=10,
            label="Historical Data (2011-2025, Sector Avg)",
            markerfacecolor="#2C3E50",
            markeredgecolor="white",
            markeredgewidth=2,
        )

        # Linear trend headline
        if linear_forecasts and column in linear_forecasts:
            lf = linear_forecasts[column]
            ax.plot(
                future_years,
                lf["predictions"],
                "D-",
                color="#8E44AD",
                linewidth=3,
                markersize=10,
                label="Linear Trend Forecast (headline)",
                markeredgecolor="white",
                markeredgewidth=1.5,
                zorder=7,
            )
            ax.fill_between(
                future_years, lf["pred_lower"], lf["pred_upper"],
                alpha=0.2, color="#8E44AD", label="95% Prediction Interval",
            )

        # Tree models as artifacts
        markers = {"XGBoost": "s", "Random Forest": "^", "Decision Tree": "D"}
        for model_name, result in results.items():
            ax.plot(
                future_years,
                result["predictions_future"],
                marker=markers[model_name],
                linestyle="--",
                color=MODEL_COLORS[model_name],
                linewidth=1.5,
                markersize=7,
                label=f"{model_name} (flat line = artifact)",
                markeredgecolor="white",
                markeredgewidth=1,
                alpha=0.4,
            )

        change = values[-1] - values[0]
        pct_change = (change / values[0]) * 100
        stats_text = f"2011: {values[0]:.2f}\n2025: {values[-1]:.2f}\nChange: {change:+.2f} ({pct_change:+.1f}%)"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10, va="top", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

        ax.axvspan(2025.5, 2030.5, alpha=0.1, color="red")
        ax.axvline(x=2025, color="red", linestyle="--", linewidth=2.5, alpha=0.5, label="Prediction Start")
        ax.set_xlabel("Year", fontsize=12, fontweight="bold")
        ax.set_ylabel(title, fontsize=12, fontweight="bold")
        ax.set_title(f"{title} - Detailed Trend Analysis (2011-2030, Descriptive)", fontsize=14, fontweight="bold")
        ax.legend(loc="best", frameon=True, shadow=True, fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.7)
        ax.set_xlim(2010, 2031)

    plt.suptitle("Asian Banking Sector: Detailed ESG, ROA & ROE Trend Analysis (Descriptive)", fontsize=16, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(OUTPUT_DIR / "banking_detailed_trends.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_statistics_summary(historical_df, model_results,
                            ts_eval_results=None,
                            linear_forecasts=None) -> None:
    """Create text-panel summary statistics for each metric."""

    set_plot_style()
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for ax, (column, title) in zip(axes, METRICS):
        data = historical_df[column]
        results = model_results[column]

        # Use linear forecast as headline if available
        if linear_forecasts and column in linear_forecasts:
            lf = linear_forecasts[column]
            forecast_2030 = lf["predictions"][-1]
            forecast_source = "Linear Trend (OLS)"
        else:
            eval_r = ts_eval_results.get(column, {}) if ts_eval_results else {}
            best = best_model_name(results, eval_r)
            forecast_2030 = results[best]["predictions_future"][-1]
            forecast_source = best

        summary = f"""
HISTORICAL SUMMARY (2011-2025)
(Sector-average, descriptive only)

Starting Value (2011):  {data.iloc[0]:8.2f}
Ending Value (2025):    {data.iloc[-1]:8.2f}

Minimum:                {data.min():8.2f}
Maximum:                {data.max():8.2f}
Average:                {data.mean():8.2f}
Std Deviation:          {data.std():8.2f}

Total Change:           {data.iloc[-1] - data.iloc[0]:+8.2f}
Percentage Growth:      {((data.iloc[-1] - data.iloc[0]) / data.iloc[0] * 100):+8.1f}%

HEADLINE FORECAST:
Model: {forecast_source}
2030 Forecast: {forecast_2030:8.2f}
"""

        ax.text(0.1, 0.5, summary, fontsize=10, family="monospace", va="center", bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.3))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title(title, fontsize=14, fontweight="bold")

    plt.suptitle("Asian Banking Sector: Historical Statistics Summary (2011-2025, Descriptive)", fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(OUTPUT_DIR / "banking_statistics_summary.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
