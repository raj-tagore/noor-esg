"""Exploratory atlas of the firm-year panel (composition, coverage, groups).

Descriptive only — no regressions, forecasts, or ESG→CFP inference.
Geography uses country_hq; industry uses the raw industry label.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config import EXPLORE_DIR, EXPLORE_MIN_FIRMS


def ensure_explore_dir() -> None:
    EXPLORE_DIR.mkdir(parents=True, exist_ok=True)


def set_plot_style() -> None:
    plt.style.use("seaborn-v0_8-darkgrid")


def collapse_rare(
    panel: pd.DataFrame,
    column: str,
    min_firms: int = EXPLORE_MIN_FIRMS,
    other_label: str = "Other",
) -> pd.Series:
    """Map rare groups (by distinct firm_id count) to Other; keep frequent labels."""

    firm_counts = panel.groupby(column)["firm_id"].nunique()
    keep = set(firm_counts[firm_counts >= min_firms].index)
    return panel[column].where(panel[column].isin(keep), other_label)


def build_composition_summary(panel: pd.DataFrame) -> pd.DataFrame:
    """Exact (uncollapsed) firm and firm-year counts by country and by industry."""

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

    summary = pd.concat([country, industry], ignore_index=True)
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
    work = panel.copy()
    work["country_group"] = collapse_rare(work, "country_hq")
    work["industry_group"] = collapse_rare(work, "industry")

    industry_counts = (
        panel.groupby("industry")["firm_id"]
        .nunique()
        .sort_values(ascending=True)
    )

    # Firm counts for heatmap: one row per firm, then crosstab
    firms = work.drop_duplicates("firm_id")
    heat = pd.crosstab(firms["country_group"], firms["industry_group"])

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
        f"Country × industry firm counts\n(groups with <{EXPLORE_MIN_FIRMS} firms → Other)",
        fontsize=12, fontweight="bold",
    )
    axes[1].set_xlabel("Industry", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Country (HQ)", fontsize=11, fontweight="bold")
    plt.setp(axes[1].get_xticklabels(), rotation=35, ha="right")

    plt.suptitle("Sample composition: industry and country × industry", fontsize=14, fontweight="bold")
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
    work = panel.copy()
    work["country_group"] = collapse_rare(work, "country_hq")

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
    cov = pd.DataFrame(rows).sort_values("n_firms", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, max(5, 0.4 * len(cov))))

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
        f"Coverage intensity by country_hq (groups with <{EXPLORE_MIN_FIRMS} firms → Other)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
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
    work = panel.copy()
    work["country_group"] = collapse_rare(work, "country_hq")
    work["industry_group"] = collapse_rare(work, "industry")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    sns.boxplot(data=work, x="industry_group", y="esg", ax=axes[0, 0], color="#9B59B6")
    axes[0, 0].set_title("ESG by industry", fontsize=12, fontweight="bold")
    axes[0, 0].set_xlabel("Industry", fontsize=10, fontweight="bold")
    axes[0, 0].set_ylabel("ESG Score", fontsize=10, fontweight="bold")
    plt.setp(axes[0, 0].get_xticklabels(), rotation=30, ha="right")

    sns.boxplot(data=work, x="industry_group", y="roa", ax=axes[0, 1], color="#E67E22")
    axes[0, 1].set_title("ROA by industry", fontsize=12, fontweight="bold")
    axes[0, 1].set_xlabel("Industry", fontsize=10, fontweight="bold")
    axes[0, 1].set_ylabel("Pretax ROA (%)", fontsize=10, fontweight="bold")
    plt.setp(axes[0, 1].get_xticklabels(), rotation=30, ha="right")

    sns.boxplot(data=work, x="country_group", y="esg", ax=axes[1, 0], color="#9B59B6")
    axes[1, 0].set_title("ESG by country group", fontsize=12, fontweight="bold")
    axes[1, 0].set_xlabel("Country (HQ)", fontsize=10, fontweight="bold")
    axes[1, 0].set_ylabel("ESG Score", fontsize=10, fontweight="bold")
    plt.setp(axes[1, 0].get_xticklabels(), rotation=30, ha="right")

    sns.boxplot(data=work, x="country_group", y="roa", ax=axes[1, 1], color="#E67E22")
    axes[1, 1].set_title("ROA by country group", fontsize=12, fontweight="bold")
    axes[1, 1].set_xlabel("Country (HQ)", fontsize=10, fontweight="bold")
    axes[1, 1].set_ylabel("Pretax ROA (%)", fontsize=10, fontweight="bold")
    plt.setp(axes[1, 1].get_xticklabels(), rotation=30, ha="right")

    plt.suptitle(
        f"Distributions by group (groups with <{EXPLORE_MIN_FIRMS} firms → Other)",
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
    work = panel.copy()
    work["country_group"] = collapse_rare(work, "country_hq")
    work["industry_group"] = collapse_rare(work, "industry")

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for group, sub in work.groupby("country_group"):
        med = sub.groupby("year")["esg"].median()
        axes[0].plot(med.index, med.values, "o-", linewidth=2, markersize=5, label=str(group))
    axes[0].set_title("Median ESG by country group", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Year", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("Median ESG Score", fontsize=10, fontweight="bold")
    axes[0].legend(loc="best", fontsize=8, ncol=2)
    axes[0].set_xticks(sorted(work["year"].unique()))
    plt.setp(axes[0].get_xticklabels(), rotation=45, ha="right")

    for group, sub in work.groupby("industry_group"):
        med = sub.groupby("year")["esg"].median()
        axes[1].plot(med.index, med.values, "o-", linewidth=2, markersize=5, label=str(group))
    axes[1].set_title("Median ESG by industry", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Year", fontsize=10, fontweight="bold")
    axes[1].set_ylabel("Median ESG Score", fontsize=10, fontweight="bold")
    axes[1].legend(loc="best", fontsize=8)
    axes[1].set_xticks(sorted(work["year"].unique()))
    plt.setp(axes[1].get_xticklabels(), rotation=45, ha="right")

    plt.suptitle(
        "Median ESG trajectories by group (descriptive only — not for inference)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(EXPLORE_DIR / "07_median_trajectories_by_group.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 8. ESG vs ROA facets
# ---------------------------------------------------------------------------

def _facet_scatter(panel: pd.DataFrame, group_col: str, filename: str, title: str) -> None:
    set_plot_style()
    work = panel.dropna(subset=["esg", "roa"]).copy()
    groups = sorted(work[group_col].dropna().unique(), key=str)
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
    work = panel.copy()
    work["country_group"] = collapse_rare(work, "country_hq")
    work["industry_group"] = collapse_rare(work, "industry")

    _facet_scatter(
        work,
        "industry_group",
        "08a_esg_vs_roa_by_industry.png",
        f"ESG vs ROA by industry (descriptive; groups with <{EXPLORE_MIN_FIRMS} firms → Other)",
    )
    _facet_scatter(
        work,
        "country_group",
        "08b_esg_vs_roa_by_country.png",
        f"ESG vs ROA by country group (descriptive; groups with <{EXPLORE_MIN_FIRMS} firms → Other)",
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
