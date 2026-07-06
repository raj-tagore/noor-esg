"""Visualizations for ESG-to-financial KPI relationship analysis.

Every panel here is built from the firm-level panel (~2,250 rows):
- Headline results come from panel fixed-effects regression (n~2000+).
- ML model R2 bars show OUT-OF-SAMPLE (test) scores, not training scores.
- Rolling correlations use observed panel data only (no forecast contamination).

Period: 2011-2025 (15 years), Asian banking markets.
"""

import numpy as np
import matplotlib.pyplot as plt

from config import OUTPUT_DIR


def plot_relationship_dashboard(context: dict) -> None:
    """Create the relationship dashboard (panel-only, 7 panels)."""

    panel = context["panel"]
    rolling_df = context["rolling_df"]
    ml_eval = context["ml_eval_results"]

    panel_corr_roa = context["panel_corr_roa"]
    panel_corr_roe = context["panel_corr_roe"]

    panel_results = context["panel_results"]

    plt.style.use("seaborn-v0_8-darkgrid")
    fig = plt.figure(figsize=(20, 10))
    gs = fig.add_gridspec(2, 4)

    # --- Panel 1: ESG vs ROA scatter (firm-year panel) ---
    ax1 = fig.add_subplot(gs[0, 0])
    panel_clean = panel.dropna(subset=["esg", "roa"])
    scatter1 = ax1.scatter(
        panel_clean["esg"], panel_clean["roa"],
        c=panel_clean["year"], cmap="viridis",
        s=15, alpha=0.4, edgecolors="none",
    )
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
    ax2 = fig.add_subplot(gs[0, 1])
    panel_clean_roe = panel.dropna(subset=["esg", "roe"])
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
    ax2.set_title(f"ESG vs ROE (n={len(plot_data)} firm-years)", fontsize=11, fontweight="bold")
    ax2.legend(loc="best", fontsize=8)
    ax2.grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=ax2, label="Year")

    # --- Panel 3: Summary text (headline panel FE results) ---
    ax4 = fig.add_subplot(gs[0, 2])
    ax4.axis("off")

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

    # --- Panel 4: Rolling correlations (panel-based, observed only) ---
    ax7 = fig.add_subplot(gs[0, 3])
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

    # --- Panel 5: ML model test R2 comparison (out-of-sample) ---
    ax8 = fig.add_subplot(gs[1, 0:2])
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

    # --- Panel 6: Train vs Test R2 (overfitting visualization) ---
    ax11 = fig.add_subplot(gs[1, 2])
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

    # --- Panel 7: Key insights text ---
    ax12 = fig.add_subplot(gs[1, 3])
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
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(OUTPUT_DIR / "banking_esg_relationship_analysis.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_detailed_relationship(context: dict) -> None:
    """Create the panel-based residual figure (3 panels: residuals + methodology note)."""

    panel = context["panel"]
    panel_corr_roa = context["panel_corr_roa"]
    panel_corr_roe = context["panel_corr_roe"]

    fig, axes = plt.subplots(1, 3, figsize=(20, 6.5))

    # --- Residual plot for ESG -> ROA (panel OLS) ---
    ax = axes[0]
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
    ax = axes[1]
    clean_roe = panel.dropna(subset=["esg", "roe"])
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

    # --- Methodology note ---
    ax = axes[2]
    ax.axis("off")
    ax.text(
        0.05, 0.95,
        "METHODOLOGY NOTE\n\n"
        f"Panel correlations use ~{len(panel):,} firm-year\n"
        "observations and reflect cross-sectional\n"
        "variation + within-firm changes.\n\n"
        f"ESG-ROA: r = {panel_corr_roa:.3f}\n"
        f"ESG-ROE: r = {panel_corr_roe:.3f}\n\n"
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
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(OUTPUT_DIR / "banking_detailed_relationship.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
