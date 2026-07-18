"""Country-group and industry subsample panel FE (heterogeneity analysis).

Same estimator as the headline model: firm + year FE, clustered SE,
contemporaneous and one-year lagged ESG. Groups are geography- / industry-
based (see config), not residual firm-count bins.
"""

from __future__ import annotations

import pandas as pd

from config import (
    BANKS_INDUSTRY,
    COUNTRY_GROUP_MAP,
    COUNTRY_GROUP_ORDER,
    HETERO_MIN_FIRMS,
    HETERO_MIN_FIRMYEARS,
    HETEROGENEITY_COUNTRY_CSV,
    HETEROGENEITY_INDUSTRY_CSV,
    INDUSTRY_GROUP_BANKS,
    INDUSTRY_GROUP_INSURANCE,
    INDUSTRY_GROUP_ORDER,
    INDUSTRY_GROUP_OTHER,
    INSURANCE_INDUSTRIES,
    OUTPUT_DIR,
)
from data_processing import build_panel_dataset, ensure_output_dir
from heterogeneity_plots import plot_heterogeneity_forests
from panel_regression import run_lagged_panel_regression, run_panel_fixed_effects


def assign_country_group(country_hq: str) -> str:
    if pd.isna(country_hq):
        raise ValueError("Missing country_hq; cannot assign country group")
    key = str(country_hq).strip()
    if key not in COUNTRY_GROUP_MAP:
        raise ValueError(
            f"Unmapped country_hq={key!r}. Add an explicit regional group in "
            "config.COUNTRY_GROUP_MAP (no anonymous Other bin)."
        )
    return COUNTRY_GROUP_MAP[key]


def assign_industry_group(industry: str) -> str:
    if pd.isna(industry):
        return INDUSTRY_GROUP_OTHER
    name = str(industry).strip()
    if name == BANKS_INDUSTRY:
        return INDUSTRY_GROUP_BANKS
    if name in INSURANCE_INDUSTRIES:
        return INDUSTRY_GROUP_INSURANCE
    return INDUSTRY_GROUP_OTHER


def add_group_columns(panel: pd.DataFrame) -> pd.DataFrame:
    """Attach country_group and industry_group columns."""

    out = panel.copy()
    out["country_group"] = out["country_hq"].map(assign_country_group)
    out["industry_group"] = out["industry"].map(assign_industry_group)
    return out


def _meets_min_size(sub: pd.DataFrame, outcome: str, regressor: str) -> tuple[bool, str]:
    n_firms = sub["firm_id"].nunique()
    if n_firms < HETERO_MIN_FIRMS:
        return False, f"n_firms={n_firms} < {HETERO_MIN_FIRMS}"

    if regressor == "esg":
        usable = sub.dropna(subset=["esg", outcome])
    else:
        tmp = sub.sort_values(["firm_id", "year"]).copy()
        tmp["esg_lag1"] = tmp.groupby("firm_id")["esg"].shift(1)
        usable = tmp.dropna(subset=["esg_lag1", outcome])

    n_fy = len(usable)
    if n_fy < HETERO_MIN_FIRMYEARS:
        return False, f"n_firm_years={n_fy} < {HETERO_MIN_FIRMYEARS}"
    return True, ""


def _estimate_one(
    sub: pd.DataFrame,
    outcome: str,
    regressor: str,
    group_name: str,
    dimension: str,
) -> dict | None:
    ok, reason = _meets_min_size(sub, outcome, regressor)
    if not ok:
        print(f"  SKIP {dimension}={group_name!r} {regressor}->{outcome}: {reason}")
        return None

    try:
        if regressor == "esg":
            res = run_panel_fixed_effects(sub, outcome)
        else:
            res = run_lagged_panel_regression(sub, outcome)
    except Exception as exc:  # numerical / collinearity failures
        print(f"  SKIP {dimension}={group_name!r} {regressor}->{outcome}: {exc}")
        return None

    return {
        "dimension": dimension,
        "group": group_name,
        "outcome": res["outcome"],
        "regressor": res["regressor"],
        "beta": res["beta"],
        "std_error": res["std_error"],
        "t_stat": res["t_stat"],
        "p_value": res["p_value"],
        "n_obs": res["n_obs"],
        "n_firms": int(sub["firm_id"].nunique()),
        "r2_within": res["r2_within"],
    }


def run_subsample_fe(
    panel: pd.DataFrame,
    group_col: str,
    dimension: str,
    include_full_sample: bool = True,
) -> pd.DataFrame:
    """Run contemp + lag FE for each group (and optional full-sample row)."""

    rows: list[dict] = []

    if include_full_sample:
        for outcome in ["roa", "roe"]:
            for regressor in ["esg", "esg_lag1"]:
                row = _estimate_one(panel, outcome, regressor, "Full sample", dimension)
                if row is not None:
                    rows.append(row)

    for group_name, sub in panel.groupby(group_col, sort=False):
        for outcome in ["roa", "roe"]:
            for regressor in ["esg", "esg_lag1"]:
                row = _estimate_one(sub, outcome, regressor, str(group_name), dimension)
                if row is not None:
                    rows.append(row)

    return pd.DataFrame(rows)


def _sort_results(df: pd.DataFrame, order: list[str]) -> pd.DataFrame:
    if df.empty:
        return df
    rank = {name: i for i, name in enumerate(order)}
    out = df.copy()
    out["_rank"] = out["group"].map(lambda g: rank.get(g, 999))
    out["_reg_rank"] = out["regressor"].map({"esg": 0, "esg_lag1": 1})
    out["_out_rank"] = out["outcome"].map({"roa": 0, "roe": 1})
    out = out.sort_values(["_rank", "_out_rank", "_reg_rank"]).drop(
        columns=["_rank", "_reg_rank", "_out_rank"]
    )
    return out.reset_index(drop=True)


def run_heterogeneity_analysis() -> dict:
    """Estimate country- and industry-group FE; write CSVs and forest plots."""

    ensure_output_dir()
    panel = add_group_columns(build_panel_dataset())

    unmapped_check = set(panel["country_hq"].unique()) - set(COUNTRY_GROUP_MAP)
    if unmapped_check:
        raise ValueError(f"Unmapped country_hq values: {sorted(unmapped_check)}")

    print("Country-group sizes (firms):")
    print(panel.groupby("country_group")["firm_id"].nunique().sort_values(ascending=False).to_string())
    print("\nIndustry-group sizes (firms):")
    print(panel.groupby("industry_group")["firm_id"].nunique().sort_values(ascending=False).to_string())

    print("\nEstimating country-group subsample FE...")
    country_df = _sort_results(
        run_subsample_fe(panel, "country_group", "country"),
        COUNTRY_GROUP_ORDER,
    )
    country_path = OUTPUT_DIR / HETEROGENEITY_COUNTRY_CSV
    country_df.to_csv(country_path, index=False)
    print(f"Wrote {country_path}")

    print("\nEstimating industry-group subsample FE...")
    industry_df = _sort_results(
        run_subsample_fe(panel, "industry_group", "industry"),
        INDUSTRY_GROUP_ORDER,
    )
    industry_path = OUTPUT_DIR / HETEROGENEITY_INDUSTRY_CSV
    industry_df.to_csv(industry_path, index=False)
    print(f"Wrote {industry_path}")

    plot_heterogeneity_forests(country_df, industry_df)

    return {
        "panel": panel,
        "country_results": country_df,
        "industry_results": industry_df,
    }


def print_summary(context: dict) -> None:
    print("=" * 80)
    print("HETEROGENEITY: COUNTRY-GROUP AND INDUSTRY SUBSAMPLE FE")
    print("Firm + year FE, clustered SE (same as headline model)")
    print("=" * 80)

    for label, key in [("Country groups", "country_results"), ("Industry groups", "industry_results")]:
        df = context[key]
        print(f"\n{label}:")
        if df.empty:
            print("  (no results)")
            continue
        show = df[df["regressor"] == "esg"][
            ["group", "outcome", "beta", "std_error", "p_value", "n_obs", "n_firms"]
        ]
        print(show.to_string(index=False))

    print("\nFiles:")
    print(f"  {HETEROGENEITY_COUNTRY_CSV}")
    print(f"  {HETEROGENEITY_INDUSTRY_CSV}")
    print("  banking_heterogeneity_country_forest.png")
    print("  banking_heterogeneity_industry_forest.png")


def main() -> None:
    context = run_heterogeneity_analysis()
    print_summary(context)


if __name__ == "__main__":
    main()
