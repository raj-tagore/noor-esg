"""Exploratory atlas of the firm-year panel (composition, coverage, groups).

Descriptive only — no regressions, forecasts, or ESG→CFP inference.
Grouped plots use the same country_group / industry_group definitions as
heterogeneity analysis (config.COUNTRY_GROUP_MAP and industry rules).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config import (
    COUNTRY_GROUP_ORDER,
    EXPLORE_DIR,
    INDUSTRY_GROUP_ORDER,
)
from groups import add_group_columns


def ensure_explore_dir() -> None:
    EXPLORE_DIR.mkdir(parents=True, exist_ok=True)


def set_plot_style() -> None:
    plt.style.use("seaborn-v0_8-darkgrid")


def _ordered_labels(present: list[str], order: list[str]) -> list[str]:
    """Order labels by analysis display order; append any extras alphabetically."""

    rank = {g: i for i, g in enumerate(order) if g != "Full sample"}
    known = [g for g in order if g != "Full sample" and g in present]
    extras = sorted(g for g in present if g not in rank)
    return known + extras


def build_composition_summary(panel: pd.DataFrame) -> pd.DataFrame:
    """Exact firm and firm-year counts by raw country_hq, industry, and analysis groups."""

    country = (
        panel.groupby("country_hq", dropna=False)
        .agg(n_firms=("firm_id", "nunique"), n_firm_years=("firm_id", "size"))
        .reset_index()
        .rename(columns={"country_hq": "group"})
    )
    country.insert(0, "dimension", "country_hq")

    industry = (
        panel.groupby("industry", dropna=False)
        .agg(n_firms=("firm_id", "nunique"), n_firm_years=("firm_id", "size"))
        .reset_index()
        .rename(columns={"industry": "group"})
    )
    industry.insert(0, "dimension", "industry")

    grouped = add_group_columns(panel)
    country_g = (
        grouped.groupby("country_group", dropna=False)
        .agg(n_firms=("firm_id", "nunique"), n_firm_years=("firm_id", "size"))
        .reset_index()
        .rename(columns={"country_group": "group"})
    )
    country_g.insert(0, "dimension", "country_group")

    industry_g = (
        grouped.groupby("industry_group", dropna=False)
        .agg(n_firms=("firm_id", "nunique"), n_firm_years=("firm_id", "size"))
        .reset_index()
        .rename(columns={"industry_group": "group"})
    )
    industry_g.insert(0, "dimension", "industry_group")

    summary = pd.concat([country, industry, country_g, industry_g], ignore_index=True)
    return summary.sort_values(["dimension", "n_firms"], ascending=[True, False]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 1. Country composition
# ---------------------------------------------------------------------------

def plot_composition_country(panel: pd.DataFrame) -> None:
    set_plot_style()
    counts = (
        panel.groupby("country_hq")["firm_id"]
        .nunique()
        .sort_values(ascending=True)
    )
    n_firms = panel["firm_id"].nunique()
    n_rows = len(panel)

    fig, ax = plt.subplots(figsize=(10, max(6, 0.35 * len(counts))))
    ax.barh(counts.index.astype(str), counts.values, color="#2C3E50", alpha=0.85)
    ax.set_xlabel("Number of distinct firms", fontsize=11, fontweight="bold")
    ax.set_ylabel("Country (HQ)", fontsize=11, fontweight="bold")
    ax.set_title(
        f"Sample composition by country_hq\n"
        f"{n_firms} firms · {n_rows:,} firm-years · 2011–2025",
        fontsize=13, fontweight="bold",
    )
    for i, v in enumerate(counts.values):
        ax.text(v + 0.3, i, str(v), va="center", fontsize=9)
    plt.tight_layout()
    fig.savefig(EXPLORE_DIR / "01_composition_country.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Industry + country × industry
# ---------------------------------------------------------------------------

def plot_composition_industry_heatmap(panel: pd.DataFrame) -> None:
    set_plot_style()
    work = add_group_columns(panel)

    industry_counts = (
        panel.groupby("industry")["firm_id"]
        .nunique()
        .sort_values(ascending=True)
    )

    firms = work.drop_duplicates("firm_id")
    heat = pd.crosstab(firms["country_group"], firms["industry_group"])
    heat = heat.reindex(
        index=_ordered_labels(list(heat.index.astype(str)), COUNTRY_GROUP_ORDER),
        columns=_ordered_labels(list(heat.columns.astype(str)), INDUSTRY_GROUP_ORDER),
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, max(6, 0.35 * len(industry_counts))))

    axes[0].barh(
        industry_counts.index.astype(str),
        industry_counts.values,
        color="#1ABC9C",
        alpha=0.85,
    )
    axes[0].set_xlabel("Number of distinct firms", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Industry", fontsize=11, fontweight="bold")
    axes[0].set_title("Firms by industry", fontsize=12, fontweight="bold")
    for i, v in enumerate(industry_counts.values):
        axes[0].text(v + 0.3, i, str(v), va="center", fontsize=9)

    sns.heatmap(
        heat, annot=True, fmt="d", cmap="YlGnBu",
        linewidths=0.5, ax=axes[1], cbar_kws={"label": "Firms"},
    )
    axes[1].set_title(
        "Country group × industry group firm counts\n"
        "(same groups as heterogeneity analysis)",
        fontsize=12, fontweight="bold",
    )
    axes[1].set_xlabel("Industry group", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Country group", fontsize=11, fontweight="bold")
    plt.setp(axes[1].get_xticklabels(), rotation=35, ha="right")

    plt.suptitle("Sample composition: industry and country × industry groups", fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(EXPLORE_DIR / "02_composition_industry_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Coverage over time
# ---------------------------------------------------------------------------

def plot_coverage_over_time(panel: pd.DataFrame) -> None:
    set_plot_style()
    years = sorted(panel["year"].unique())
    rows = []
    for year in years:
        sub = panel[panel["year"] == year]
        rows.append({
            "year": year,
            "ESG": sub["esg"].notna().sum(),
            "ROA": sub["roa"].notna().sum(),
            "ROE": sub["roe"].notna().sum(),
            "Any firm-year": len(sub),
        })
    cov = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(12, 6))
    for col, color in [
        ("ESG", "#9B59B6"),
        ("ROA", "#E67E22"),
        ("ROE", "#1ABC9C"),
        ("Any firm-year", "#7F8C8D"),
    ]:
        ax.plot(cov["year"], cov[col], "o-", linewidth=2.2, markersize=7, label=col, color=color)

    ax.set_xlabel("Year", fontsize=11, fontweight="bold")
    ax.set_ylabel("Firm-year counts (non-null)", fontsize=11, fontweight="bold")
    ax.set_title(
        "Panel coverage over time\nNon-null ESG / ROA / ROE firm-years by calendar year",
        fontsize=13, fontweight="bold",
    )
    ax.legend(loc="best", fontsize=10)
    ax.set_xticks(years)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(EXPLORE_DIR / "03_coverage_over_time.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Coverage intensity by country
# ---------------------------------------------------------------------------

def plot_coverage_by_country(panel: pd.DataFrame) -> None:
    set_plot_style()
    work = add_group_columns(panel)

    rows = []
    for group, sub in work.groupby("country_group"):
        n_fy = len(sub)
        esg_share = sub["esg"].notna().mean()
        years_per_firm = (
            sub.dropna(subset=["esg"])
            .groupby("firm_id")["year"]
            .nunique()
        )
        rows.append({
            "country_group": group,
            "esg_share": esg_share,
            "median_esg_years": years_per_firm.median() if len(years_per_firm) else np.nan,
            "n_firms": sub["firm_id"].nunique(),
            "n_firm_years": n_fy,
        })
    cov = pd.DataFrame(rows)
    order = _ordered_labels(list(cov["country_group"].astype(str)), COUNTRY_GROUP_ORDER)
    cov["country_group"] = pd.Categorical(cov["country_group"], categories=order, ordered=True)
    cov = cov.sort_values("country_group", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, max(5, 0.45 * len(cov))))

    axes[0].barh(cov["country_group"].astype(str), cov["esg_share"] * 100, color="#9B59B6", alpha=0.85)
    axes[0].set_xlabel("Share of firm-years with non-null ESG (%)", fontsize=10, fontweight="bold")
    axes[0].set_title("ESG coverage rate by country group", fontsize=12, fontweight="bold")
    axes[0].set_xlim(0, 105)

    axes[1].barh(
        cov["country_group"].astype(str),
        cov["median_esg_years"],
        color="#3498DB",
        alpha=0.85,
    )
    axes[1].set_xlabel("Median years of ESG history per firm", fontsize=10, fontweight="bold")
    axes[1].set_title("ESG history depth by country group", fontsize=12, fontweight="bold")

    plt.suptitle(
        "Coverage intensity by analysis country group\n"
        "(Japan, China incl. HK, Korea, Taiwan, India, ASEAN, West Asia / Middle East)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(EXPLORE_DIR / "04_coverage_by_country.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Univariate distributions
# ---------------------------------------------------------------------------

def plot_univariate_distributions(panel: pd.DataFrame) -> None:
    set_plot_style()
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    specs = [
        ("esg", "ESG Score", "#9B59B6"),
        ("roa", "Pretax ROA (%)", "#E67E22"),
        ("roe", "Pretax ROE (%)", "#1ABC9C"),
    ]
    for ax, (col, title, color) in zip(axes, specs):
        data = panel[col].dropna()
        ax.hist(data, bins=40, color=color, alpha=0.55, density=True, edgecolor="white")
        try:
            data.plot.kde(ax=ax, color="#2C3E50", linewidth=2)
        except Exception:
            pass
        ax.set_title(f"{title}\n(n={len(data):,} firm-years)", fontsize=12, fontweight="bold")
        ax.set_xlabel(title, fontsize=10, fontweight="bold")
        ax.set_ylabel("Density", fontsize=10, fontweight="bold")

    plt.suptitle(
        "Univariate distributions (firm-year panel; ROA/ROE winsorized)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(EXPLORE_DIR / "05_univariate_distributions.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Distributions by group
# ---------------------------------------------------------------------------

def plot_distributions_by_group(panel: pd.DataFrame) -> None:
    set_plot_style()
    work = add_group_columns(panel)
    country_order = _ordered_labels(list(work["country_group"].unique()), COUNTRY_GROUP_ORDER)
    industry_order = _ordered_labels(list(work["industry_group"].unique()), INDUSTRY_GROUP_ORDER)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    sns.boxplot(
        data=work, x="industry_group", y="esg", ax=axes[0, 0], color="#9B59B6",
        order=industry_order,
    )
    axes[0, 0].set_title("ESG by industry group", fontsize=12, fontweight="bold")
    axes[0, 0].set_xlabel("Industry group", fontsize=10, fontweight="bold")
    axes[0, 0].set_ylabel("ESG Score", fontsize=10, fontweight="bold")
    plt.setp(axes[0, 0].get_xticklabels(), rotation=30, ha="right")

    sns.boxplot(
        data=work, x="industry_group", y="roa", ax=axes[0, 1], color="#E67E22",
        order=industry_order,
    )
    axes[0, 1].set_title("ROA by industry group", fontsize=12, fontweight="bold")
    axes[0, 1].set_xlabel("Industry group", fontsize=10, fontweight="bold")
    axes[0, 1].set_ylabel("Pretax ROA (%)", fontsize=10, fontweight="bold")
    plt.setp(axes[0, 1].get_xticklabels(), rotation=30, ha="right")

    sns.boxplot(
        data=work, x="country_group", y="esg", ax=axes[1, 0], color="#9B59B6",
        order=country_order,
    )
    axes[1, 0].set_title("ESG by country group", fontsize=12, fontweight="bold")
    axes[1, 0].set_xlabel("Country group", fontsize=10, fontweight="bold")
    axes[1, 0].set_ylabel("ESG Score", fontsize=10, fontweight="bold")
    plt.setp(axes[1, 0].get_xticklabels(), rotation=30, ha="right")

    sns.boxplot(
        data=work, x="country_group", y="roa", ax=axes[1, 1], color="#E67E22",
        order=country_order,
    )
    axes[1, 1].set_title("ROA by country group", fontsize=12, fontweight="bold")
    axes[1, 1].set_xlabel("Country group", fontsize=10, fontweight="bold")
    axes[1, 1].set_ylabel("Pretax ROA (%)", fontsize=10, fontweight="bold")
    plt.setp(axes[1, 1].get_xticklabels(), rotation=30, ha="right")

    plt.suptitle(
        "Distributions by analysis groups (same country / industry groups as FE heterogeneity)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(EXPLORE_DIR / "06_distributions_by_group.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 7. Median trajectories by group
# ---------------------------------------------------------------------------

def plot_median_trajectories_by_group(panel: pd.DataFrame) -> None:
    set_plot_style()
    work = add_group_columns(panel)
    country_order = _ordered_labels(list(work["country_group"].unique()), COUNTRY_GROUP_ORDER)
    industry_order = _ordered_labels(list(work["industry_group"].unique()), INDUSTRY_GROUP_ORDER)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for group in country_order:
        sub = work[work["country_group"] == group]
        med = sub.groupby("year")["esg"].median()
        axes[0].plot(med.index, med.values, "o-", linewidth=2, markersize=5, label=str(group))
    axes[0].set_title("Median ESG by country group", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Year", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("Median ESG Score", fontsize=10, fontweight="bold")
    axes[0].legend(loc="best", fontsize=8, ncol=2)
    axes[0].set_xticks(sorted(work["year"].unique()))
    plt.setp(axes[0].get_xticklabels(), rotation=45, ha="right")

    for group in industry_order:
        sub = work[work["industry_group"] == group]
        med = sub.groupby("year")["esg"].median()
        axes[1].plot(med.index, med.values, "o-", linewidth=2, markersize=5, label=str(group))
    axes[1].set_title("Median ESG by industry group", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Year", fontsize=10, fontweight="bold")
    axes[1].set_ylabel("Median ESG Score", fontsize=10, fontweight="bold")
    axes[1].legend(loc="best", fontsize=8)
    axes[1].set_xticks(sorted(work["year"].unique()))
    plt.setp(axes[1].get_xticklabels(), rotation=45, ha="right")

    plt.suptitle(
        "Median ESG trajectories by analysis group (descriptive only — not for inference)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(EXPLORE_DIR / "07_median_trajectories_by_group.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 8. ESG vs ROA facets
# ---------------------------------------------------------------------------

def _facet_scatter(
    panel: pd.DataFrame,
    group_col: str,
    filename: str,
    title: str,
    group_order: list[str],
) -> None:
    set_plot_style()
    work = panel.dropna(subset=["esg", "roa"]).copy()
    groups = [g for g in group_order if g in set(work[group_col].dropna().unique())]
    n = len(groups)
    ncols = min(3, max(1, n))
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4.2 * nrows), squeeze=False)
    for idx, group in enumerate(groups):
        ax = axes[idx // ncols][idx % ncols]
        sub = work[work[group_col] == group]
        ax.scatter(sub["esg"], sub["roa"], s=12, alpha=0.35, c=sub["year"], cmap="viridis", edgecolors="none")
        if len(sub) >= 3:
            z = np.polyfit(sub["esg"], sub["roa"], 1)
            x_line = np.linspace(sub["esg"].min(), sub["esg"].max(), 50)
            ax.plot(x_line, np.polyval(z, x_line), "r--", linewidth=1.5, alpha=0.8)
        ax.set_title(f"{group}\n(n={len(sub):,})", fontsize=11, fontweight="bold")
        ax.set_xlabel("ESG Score", fontsize=9)
        ax.set_ylabel("Pretax ROA (%)", fontsize=9)

    for idx in range(n, nrows * ncols):
        axes[idx // ncols][idx % ncols].axis("off")

    plt.suptitle(title, fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(EXPLORE_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_esg_roa_facets(panel: pd.DataFrame) -> None:
    work = add_group_columns(panel)
    country_order = _ordered_labels(list(work["country_group"].unique()), COUNTRY_GROUP_ORDER)
    industry_order = _ordered_labels(list(work["industry_group"].unique()), INDUSTRY_GROUP_ORDER)

    _facet_scatter(
        work,
        "industry_group",
        "08a_esg_vs_roa_by_industry.png",
        "ESG vs ROA by industry group (descriptive; Banks / Insurance / Other financials)",
        industry_order,
    )
    _facet_scatter(
        work,
        "country_group",
        "08b_esg_vs_roa_by_country.png",
        "ESG vs ROA by country group (descriptive; same groups as FE heterogeneity)",
        country_order,
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_all_explore_plots(panel: pd.DataFrame) -> list[str]:
    """Generate the full exploratory atlas; return list of output filenames."""

    ensure_explore_dir()
    plot_composition_country(panel)
    plot_composition_industry_heatmap(panel)
    plot_coverage_over_time(panel)
    plot_coverage_by_country(panel)
    plot_univariate_distributions(panel)
    plot_distributions_by_group(panel)
    plot_median_trajectories_by_group(panel)
    plot_esg_roa_facets(panel)

    return [
        "01_composition_country.png",
        "02_composition_industry_heatmap.png",
        "03_coverage_over_time.png",
        "04_coverage_by_country.png",
        "05_univariate_distributions.png",
        "06_distributions_by_group.png",
        "07_median_trajectories_by_group.png",
        "08a_esg_vs_roa_by_industry.png",
        "08b_esg_vs_roa_by_country.png",
        "panel_composition_summary.csv",
    ]
