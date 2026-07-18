"""Forest plots for country- and industry-group FE coefficients."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import (
    COUNTRY_GROUP_ORDER,
    HETEROGENEITY_COUNTRY_FOREST_PNG,
    HETEROGENEITY_INDUSTRY_FOREST_PNG,
    INDUSTRY_GROUP_ORDER,
    OUTPUT_DIR,
)


def _ordered_groups(df: pd.DataFrame, order: list[str]) -> list[str]:
    present = list(df["group"].unique())
    ranked = [g for g in order if g in present]
    extras = [g for g in present if g not in ranked]
    return ranked + extras


def _forest_panel(ax, df: pd.DataFrame, outcome: str, order: list[str], title: str) -> None:
    """Plot beta +/- 1.96*SE for contemporaneous ESG -> outcome."""

    sub = df[(df["outcome"] == outcome) & (df["regressor"] == "esg")].copy()
    if sub.empty:
        ax.axis("off")
        ax.set_title(f"{title}\n(no results)", fontsize=11)
        return

    groups = _ordered_groups(sub, order)
    sub = sub.set_index("group").loc[groups].reset_index()

    y = np.arange(len(sub))
    betas = sub["beta"].values
    ses = sub["std_error"].values
    lo = betas - 1.96 * ses
    hi = betas + 1.96 * ses

    colors = ["#2C3E50" if g == "Full sample" else "#3498DB" for g in sub["group"]]
    ax.axvline(0, color="gray", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.errorbar(
        betas, y, xerr=1.96 * ses, fmt="o", color="none",
        ecolor="#7F8C8D", elinewidth=1.5, capsize=3, zorder=2,
    )
    ax.scatter(betas, y, c=colors, s=55, zorder=3, edgecolors="white", linewidths=0.6)

    ax.set_yticks(y)
    ax.set_yticklabels(
        [f"{g} (n={n}, firms={f})" for g, n, f in zip(sub["group"], sub["n_obs"], sub["n_firms"])],
        fontsize=9,
    )
    ax.invert_yaxis()
    ax.set_xlabel("beta (ESG -> " + outcome.upper() + ")", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.grid(True, axis="x", alpha=0.3)

    # Widen x a bit if intervals are tight near zero
    span = max(abs(lo.min()), abs(hi.max()), 0.01)
    ax.set_xlim(-span * 1.15, span * 1.15)


def plot_forest(df: pd.DataFrame, order: list[str], filename: str, heading: str) -> None:
    plt.style.use("seaborn-v0_8-darkgrid")
    fig, axes = plt.subplots(1, 2, figsize=(16, max(5, 0.55 * df["group"].nunique() + 2)))

    _forest_panel(axes[0], df, "roa", order, "Pretax ROA (contemporaneous ESG)")
    _forest_panel(axes[1], df, "roe", order, "Pretax ROE (contemporaneous ESG)")

    fig.suptitle(
        f"{heading}\nFirm + year FE, SE clustered by firm; whiskers = 95% CI (1.96*SE)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


def plot_heterogeneity_forests(country_df: pd.DataFrame, industry_df: pd.DataFrame) -> None:
    plot_forest(
        country_df,
        COUNTRY_GROUP_ORDER,
        HETEROGENEITY_COUNTRY_FOREST_PNG,
        "Heterogeneity by country group",
    )
    plot_forest(
        industry_df,
        INDUSTRY_GROUP_ORDER,
        HETEROGENEITY_INDUSTRY_FOREST_PNG,
        "Heterogeneity by industry group",
    )
