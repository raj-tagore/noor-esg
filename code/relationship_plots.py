"""Visualizations for ESG-to-financial KPI relationship analysis.

Plots now reflect the corrected analysis:
- Headline results come from panel fixed-effects regression (n~2000+).
- ML model R2 bars show OUT-OF-SAMPLE (test) scores, not training scores.
- Rolling correlations use observed panel data only (no forecast contamination).
- Descriptive sector-average plots are clearly labelled.

Period: 2011-2025 (15 years), Asian banking markets.
"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from config import OUTPUT_DIR


def _normalize(series):
    rng = series.max() - series.min()
    if rng == 0:
        return series * 0
    return (series - series.min()) / rng * 100


def plot_relationship_dashboard(context: dict) -> None:
    """Create the relationship dashboard reflecting the corrected analysis."""

    panel = context["panel"]
    sector_yearly_means = context["sector_yearly_means"]
    rolling_df = context["rolling_df"]
    roa_models = context["roa_models"]
    roe_models = context["roe_models"]
    ml_eval = context["ml_eval_results"]

    panel_corr_roa = context["panel_corr_roa"]
    panel_corr_roe = context["panel_corr_roe"]
    desc_corr_roa = context["desc_corr_roa"]
    desc_corr_roe = context["desc_corr_roe"]

    panel_results = context["panel_results"]

    plt.style.use("seaborn-v0_8-darkgrid")
    fig = plt.figure(figsize=(22, 16))

    # --- Panel 1: ESG vs ROA scatter (firm-year panel) ---
    ax1 = plt.subplot(3, 4, 1)
    panel_clean = panel.dropna(subset=["esg", "roa"])
    scatter1 = ax1.scatter(
        panel_clean["esg"], panel_clean["roa"],
        c=panel_clean["year"], cmap="viridis",
        s=15, alpha=0.4, edgecolors="none",
    )
    # Add regression line from panel data
    z = np.polyfit(panel_clean["esg"], panel_clean["roa"], 1)
    x_line = np.linspace(panel_clean["esg"].min(), panel_clean["esg"].max(), 100)
    ax1.plot(x_line, np.polyval(z, x_line), "r--", linewidth=2,
             label=f"OLS fit (panel, r={panel_corr_roa:.3f})")
    ax1.set_xlabel("ESG Score", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Pretax ROA (%)", fontsize=11, fontweight="bold")
    ax1.set_title(f"ESG vs ROA (n={len(panel_clean)} firm-years)", fontsize=11, fontweight="bold")
    ax1.legend(loc="best", fontsize=8)
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=ax1, label="Year")

    # --- Panel 2: ESG vs ROE scatter (firm-year panel) ---
    ax2 = plt.subplot(3, 4, 2)
    panel_clean_roe = panel.dropna(subset=["esg", "roe"])
    # Clip extreme outliers for visibility
    roe_q99 = panel_clean_roe["roe"].quantile(0.99)
    roe_q01 = panel_clean_roe["roe"].quantile(0.01)
    plot_data = panel_clean_roe[
        (panel_clean_roe["roe"] >= roe_q01) & (panel_clean_roe["roe"] <= roe_q99)
    ]
    scatter2 = ax2.scatter(
        plot_data["esg"], plot_data["roe"],
        c=plot_data["year"], cmap="plasma",
        s=15, alpha=0.4, edgecolors="none",
    )
    z2 = np.polyfit(plot_data["esg"], plot_data["roe"], 1)
    x_line2 = np.linspace(plot_data["esg"].min(), plot_data["esg"].max(), 100)
    ax2.plot(x_line2, np.polyval(z2, x_line2), "r--", linewidth=2,
             label=f"OLS fit (panel, r={panel_corr_roe:.3f})")
    ax2.set_xlabel("ESG Score", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Pretax ROE (%)", fontsize=11, fontweight="bold")
    ax2.set_title(f"ESG vs ROE (n={len(panel_clean_roe)} firm-years)", fontsize=11, fontweight="bold")
    ax2.legend(loc="best", fontsize=8)
    ax2.grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=ax2, label="Year")

    # --- Panel 3: Correlation heatmap (sector-average, descriptive) ---
    ax3 = plt.subplot(3, 4, 3)
    corr_matrix = sector_yearly_means[["ESG_Score", "Pretax_ROA", "Pretax_ROE"]].corr()
    sns.heatmap(corr_matrix, annot=True, fmt=".3f", cmap="RdYlGn", center=0,
                square=True, linewidths=2, cbar_kws={"shrink": 0.8},
                vmin=-1, vmax=1, ax=ax3)
    ax3.set_title("Sector-Avg Correlation\n(descriptive, n=15)", fontsize=11, fontweight="bold")
    ax3.set_xticklabels(["ESG", "ROA", "ROE"], rotation=0)
    ax3.set_yticklabels(["ESG", "ROA", "ROE"], rotation=0)

    # --- Panel 4: Summary text ---
    ax4 = plt.subplot(3, 4, 4)
    ax4.axis("off")

    # Extract headline beta from panel results
    roa_contemp = [r for r in panel_results if r["outcome"] == "roa" and r["regressor"] == "esg"]
    roe_contemp = [r for r in panel_results if r["outcome"] == "roe" and r["regressor"] == "esg"]
    roa_beta = roa_contemp[0] if roa_contemp else None
    roe_beta = roe_contemp[0] if roe_contemp else None

    summary_text = "HEADLINE RESULTS\n(Panel FE, firm+year, clustered SE)\n\n"
    if roa_beta:
        sig_r = "***" if roa_beta["p_value"] < 0.01 else "**" if roa_beta["p_value"] < 0.05 else "*" if roa_beta["p_value"] < 0.1 else "ns"
        summary_text += f"ESG -> ROA:\n  beta={roa_beta['beta']:.4f} (p={roa_beta['p_value']:.3f}) {sig_r}\n  n={roa_beta['n_obs']}\n\n"
    if roe_beta:
        sig_e = "***" if roe_beta["p_value"] < 0.01 else "**" if roe_beta["p_value"] < 0.05 else "*" if roe_beta["p_value"] < 0.1 else "ns"
        summary_text += f"ESG -> ROE:\n  beta={roe_beta['beta']:.4f} (p={roe_beta['p_value']:.3f}) {sig_e}\n  n={roe_beta['n_obs']}\n\n"
    summary_text += f"Panel corr (firm-year):\n  ESG-ROA: {panel_corr_roa:.3f}\n  ESG-ROE: {panel_corr_roe:.3f}"

    ax4.text(0.05, 0.95, summary_text, fontsize=9, family="monospace", va="top",
             bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    # --- Panel 5: Sector-average ESG & ROA timeline (descriptive) ---
    ax5 = plt.subplot(3, 4, 5)
    ax5_twin = ax5.twinx()
    line1 = ax5.plot(sector_yearly_means["Year"], sector_yearly_means["ESG_Score"],
                     "o-", linewidth=2.5, markersize=8, color="#9B59B6", label="ESG Score")
    line2 = ax5_twin.plot(sector_yearly_means["Year"], sector_yearly_means["Pretax_ROA"],
                          "s-", linewidth=2.5, markersize=8, color="#E67E22", label="Pretax ROA (%)")
    ax5.set_xlabel("Year", fontsize=11, fontweight="bold")
    ax5.set_ylabel("ESG Score", fontsize=11, fontweight="bold", color="#9B59B6")
    ax5_twin.set_ylabel("Pretax ROA (%)", fontsize=11, fontweight="bold", color="#E67E22")
    ax5.set_title("ESG & ROA Timeline\n(sector avg, descriptive)", fontsize=11, fontweight="bold")
    ax5.legend(line1 + line2, [l.get_label() for l in line1 + line2], loc="upper left", fontsize=8)
    ax5.grid(True, alpha=0.3)

    # --- Panel 6: Sector-average ESG & ROE timeline (descriptive) ---
    ax6 = plt.subplot(3, 4, 6)
    ax6_twin = ax6.twinx()
    line3 = ax6.plot(sector_yearly_means["Year"], sector_yearly_means["ESG_Score"],
                     "o-", linewidth=2.5, markersize=8, color="#9B59B6", label="ESG Score")
    line4 = ax6_twin.plot(sector_yearly_means["Year"], sector_yearly_means["Pretax_ROE"],
                          "^-", linewidth=2.5, markersize=8, color="#1ABC9C", label="Pretax ROE (%)")
    ax6.set_xlabel("Year", fontsize=11, fontweight="bold")
    ax6.set_ylabel("ESG Score", fontsize=11, fontweight="bold", color="#9B59B6")
    ax6_twin.set_ylabel("Pretax ROE (%)", fontsize=11, fontweight="bold", color="#1ABC9C")
    ax6.set_title("ESG & ROE Timeline\n(sector avg, descriptive)", fontsize=11, fontweight="bold")
    ax6.legend(line3 + line4, [l.get_label() for l in line3 + line4], loc="upper left", fontsize=8)
    ax6.grid(True, alpha=0.3)

    # --- Panel 7: Rolling correlations (panel-based, observed only) ---
    ax7 = plt.subplot(3, 4, 7)
    ax7.plot(rolling_df["Window_End_Year"], rolling_df["ESG_ROA_Correlation"],
             "o-", linewidth=2.5, markersize=9, label="ESG-ROA (panel)", color="#E67E22")
    ax7.plot(rolling_df["Window_End_Year"], rolling_df["ESG_ROE_Correlation"],
             "s-", linewidth=2.5, markersize=9, label="ESG-ROE (panel)", color="#1ABC9C")
    ax7.axhline(y=0, color="gray", linestyle="--", linewidth=1.5, alpha=0.5)
    ax7.set_xlabel("Window End Year", fontsize=11, fontweight="bold")
    ax7.set_ylabel("5-Year Rolling Correlation\n(panel, firm-years)", fontsize=10, fontweight="bold")
    ax7.set_title("Correlation Evolution\n(observed data only, exploratory)", fontsize=11, fontweight="bold")
    ax7.legend(loc="best", fontsize=8)
    ax7.grid(True, alpha=0.3)

    # --- Panel 8: ML model test R2 comparison (out-of-sample) ---
    ax8 = plt.subplot(3, 4, 8)
    models = ["XGBoost", "Random Forest", "Decision Tree"]
    x = np.arange(len(models))
    width = 0.35
    roa_test_r2 = [ml_eval["roa"][name]["test_r2_mean"] for name in models]
    roe_test_r2 = [ml_eval["roe"][name]["test_r2_mean"] for name in models]
    ax8.bar(x - width / 2, roa_test_r2, width, label="ESG->ROA", color="#E67E22", alpha=0.8)
    ax8.bar(x + width / 2, roe_test_r2, width, label="ESG->ROE", color="#1ABC9C", alpha=0.8)
    ax8.set_ylabel("Test R2 (out-of-sample)", fontsize=11, fontweight="bold")
    ax8.set_title("ML Model Accuracy\n(OUT-OF-SAMPLE, GroupKFold)", fontsize=11, fontweight="bold")
    ax8.set_xticks(x)
    ax8.set_xticklabels(models, fontsize=9)
    ax8.legend(loc="upper right", fontsize=9)
    ax8.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax8.grid(True, alpha=0.3, axis="y")

    # --- Panel 9: Normalized sector-average trends (descriptive) ---
    ax9 = plt.subplot(3, 4, 9)
    ax9.plot(sector_yearly_means["Year"],
             _normalize(sector_yearly_means["ESG_Score"]),
             "o-", linewidth=2.5, markersize=8, label="ESG Score", color="#9B59B6")
    ax9.plot(sector_yearly_means["Year"],
             _normalize(sector_yearly_means["Pretax_ROA"]),
             "s-", linewidth=2.5, markersize=8, label="Pretax ROA", color="#E67E22")
    ax9.plot(sector_yearly_means["Year"],
             _normalize(sector_yearly_means["Pretax_ROE"]),
             "^-", linewidth=2.5, markersize=8, label="Pretax ROE", color="#1ABC9C")
    ax9.set_xlabel("Year", fontsize=11, fontweight="bold")
    ax9.set_ylabel("Normalized (0-100)", fontsize=11, fontweight="bold")
    ax9.set_title("Normalized Trends\n(sector avg, descriptive)", fontsize=11, fontweight="bold")
    ax9.legend(loc="best", fontsize=9)
    ax9.grid(True, alpha=0.3)

    # --- Panel 10: Year-over-Year growth (descriptive) ---
    ax10 = plt.subplot(3, 4, 10)
    years = sector_yearly_means["Year"].iloc[1:]
    ax10.plot(years, sector_yearly_means["ESG_Score"].pct_change().iloc[1:] * 100,
              "o-", linewidth=2, markersize=7, label="ESG Score", color="#9B59B6")
    ax10.plot(years, sector_yearly_means["Pretax_ROA"].pct_change().iloc[1:] * 100,
              "s-", linewidth=2, markersize=7, label="Pretax ROA", color="#E67E22")
    ax10.plot(years, sector_yearly_means["Pretax_ROE"].pct_change().iloc[1:] * 100,
              "^-", linewidth=2, markersize=7, label="Pretax ROE", color="#1ABC9C")
    ax10.axhline(y=0, color="red", linestyle="--", linewidth=2, alpha=0.5)
    ax10.set_xlabel("Year", fontsize=11, fontweight="bold")
    ax10.set_ylabel("YoY Change (%)", fontsize=11, fontweight="bold")
    ax10.set_title("Annual Growth Rates\n(sector avg, 2012-2025, descriptive)", fontsize=11, fontweight="bold")
    ax10.legend(loc="best", fontsize=8)
    ax10.grid(True, alpha=0.3)

    # --- Panel 11: Train vs Test R2 (overfitting visualization) ---
    ax11 = plt.subplot(3, 4, 11)
    model_names = list(ml_eval["roa"].keys())
    x = np.arange(len(model_names))
    width = 0.35
    train_vals = [ml_eval["roa"][m]["train_r2_mean"] for m in model_names]
    test_vals = [ml_eval["roa"][m]["test_r2_mean"] for m in model_names]
    ax11.bar(x - width / 2, train_vals, width, label="Train R2", color="#27AE60", alpha=0.8)
    ax11.bar(x + width / 2, test_vals, width, label="Test R2", color="#E74C3C", alpha=0.8)
    ax11.set_ylabel("R2 Score", fontsize=11, fontweight="bold")
    ax11.set_title("Overfitting Check: ESG->ROA\nTrain vs Test R2", fontsize=11, fontweight="bold")
    ax11.set_xticks(x)
    ax11.set_xticklabels(model_names, fontsize=9)
    ax11.legend(loc="best", fontsize=9)
    ax11.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax11.grid(True, alpha=0.3, axis="y")

    # --- Panel 12: Key insights text ---
    ax12 = plt.subplot(3, 4, 12)
    ax12.axis("off")
    insights = (
        "KEY INSIGHTS\n\n"
        "1. PANEL FIXED-EFFECTS:\n"
        f"   ESG->ROA: beta={roa_beta['beta']:.4f}\n"
        f"   ESG->ROE: beta={roe_beta['beta']:.4f}\n"
        "   (firm+year FE, clustered SE)\n\n"
        "2. ML OUT-OF-SAMPLE:\n"
        "   Negative test R2 = ESG alone\n"
        "   does not predict firm ROA/ROE\n\n"
        "3. ROLLING CORRELATIONS:\n"
        "   Based on panel, no forecasts\n"
        "   Exploratory (5yr windows)\n"
    ) if roa_beta and roe_beta else "Results pending"
    ax12.text(0.05, 0.95, insights, fontsize=9, family="monospace", va="top",
              bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.4))

    plt.suptitle(
        "Asian Banking Sector: ESG & Financial KPIs Relationship Analysis\n"
        "Firm-Level Panel (2011-2025, n~2,250)",
        fontsize=14, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUTPUT_DIR / "banking_esg_relationship_analysis.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_detailed_relationship(context: dict) -> None:
    """Create the panel-based residual and correlation comparison figure."""

    panel = context["panel"]
    panel_corr_roa = context["panel_corr_roa"]
    panel_corr_roe = context["panel_corr_roe"]
    desc_corr_roa = context["desc_corr_roa"]
    desc_corr_roe = context["desc_corr_roe"]
    panel_results = context["panel_results"]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # --- Residual plot for ESG -> ROA (panel OLS) ---
    ax = axes[0, 0]
    clean = panel.dropna(subset=["esg", "roa"])
    z = np.polyfit(clean["esg"], clean["roa"], 1)
    pred = np.polyval(z, clean["esg"])
    resid = clean["roa"] - pred
    ax.scatter(pred, resid, c=clean["year"], cmap="viridis", s=10, alpha=0.3, edgecolors="none")
    ax.axhline(y=0, color="red", linestyle="--", linewidth=2)
    ax.set_xlabel("Predicted ROA (%)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Residuals", fontsize=11, fontweight="bold")
    ax.set_title("Residual Analysis: ESG -> ROA\n(firm-year panel)", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)

    # --- Residual plot for ESG -> ROE (panel OLS) ---
    ax = axes[0, 1]
    clean_roe = panel.dropna(subset=["esg", "roe"])
    # Clip extreme outliers for visibility
    q99 = clean_roe["roe"].quantile(0.99)
    q01 = clean_roe["roe"].quantile(0.01)
    clean_roe = clean_roe[(clean_roe["roe"] >= q01) & (clean_roe["roe"] <= q99)]
    z2 = np.polyfit(clean_roe["esg"], clean_roe["roe"], 1)
    pred2 = np.polyval(z2, clean_roe["esg"])
    resid2 = clean_roe["roe"] - pred2
    ax.scatter(pred2, resid2, c=clean_roe["year"], cmap="plasma", s=10, alpha=0.3, edgecolors="none")
    ax.axhline(y=0, color="red", linestyle="--", linewidth=2)
    ax.set_xlabel("Predicted ROE (%)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Residuals", fontsize=11, fontweight="bold")
    ax.set_title("Residual Analysis: ESG -> ROE\n(firm-year panel)", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)

    # --- Correlation comparison: panel vs descriptive ---
    ax = axes[1, 0]
    categories = ["ESG vs\nROA", "ESG vs\nROE"]
    x = np.arange(len(categories))
    width = 0.35
    ax.bar(x - width / 2, [panel_corr_roa, panel_corr_roe], width,
           label=f"Panel (n~{len(panel)})", color="#3498DB", alpha=0.8)
    ax.bar(x + width / 2, [desc_corr_roa, desc_corr_roe], width,
           label="Sector Avg (n=15, descriptive)", color="#E74C3C", alpha=0.8)
    ax.set_ylabel("Correlation Coefficient", fontsize=11, fontweight="bold")
    ax.set_title("Panel vs Descriptive Correlation", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11, fontweight="bold")
    ax.legend(loc="best", fontsize=9)
    ax.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax.grid(True, alpha=0.3, axis="y")

    # --- Summary text ---
    ax = axes[1, 1]
    ax.axis("off")
    ax.text(
        0.05, 0.95,
        "METHODOLOGY NOTE\n\n"
        "Panel correlations use ~2,000+ firm-year\n"
        "observations and reflect cross-sectional\n"
        "variation + within-firm changes.\n\n"
        "Sector-average correlations (n=15) reflect\n"
        "only time-trend co-movement and are\n"
        "susceptible to the ecological fallacy.\n\n"
        "The headline results come from panel\n"
        "fixed-effects regression controlling for\n"
        "firm and year effects with clustered SE.",
        fontsize=11, family="monospace", va="top",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.5),
    )

    plt.suptitle(
        "Asian Banking Sector: Detailed ESG-Financial Relationship Analysis",
        fontsize=15, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUTPUT_DIR / "banking_detailed_relationship.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
