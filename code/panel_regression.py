"""Panel fixed-effects regressions for ESG → financial performance.

These are the headline inferential results:
    outcome_it = alpha_i + gamma_t + beta * esg_it + e_it

- alpha_i : firm fixed effects (absorbs time-invariant firm traits)
- gamma_t : year fixed effects (absorbs macro shocks hitting all firms)
- beta    : the coefficient we care about (within-firm ESG → outcome)
- SE clustered by firm (accounts for within-firm serial correlation)

Both contemporaneous and lagged-ESG specifications are estimated.
"""

import pandas as pd
from linearmodels.panel import PanelOLS

from config import (
    OUTPUT_DIR,
    PANEL_REGRESSION_CSV,
    PANEL_REGRESSION_ROA_TXT,
    PANEL_REGRESSION_ROE_TXT,
)
from data_processing import ensure_output_dir


def run_panel_fixed_effects(panel: pd.DataFrame, outcome: str) -> dict:
    """
    Estimate:  outcome_it = alpha_i + gamma_t + beta * esg_it + e_it

    Standard errors clustered by firm.  ``outcome`` is 'roa' or 'roe'.

    NOTE: With entity_effects=True and time_effects=True the constant
    is absorbed — we do NOT add one to X.  We also pass
    drop_absorbed=True to handle any residual collinearity from the
    unbalanced panel gracefully.
    """
    df = panel.dropna(subset=["esg", outcome]).copy()
    df = df.set_index(["firm_id", "year"])  # MultiIndex: (entity, time)

    y = df[outcome]
    X = df[["esg"]]  # NO constant — absorbed by fixed effects

    model = PanelOLS(y, X, entity_effects=True, time_effects=True,
                     drop_absorbed=True)
    res = model.fit(cov_type="clustered", cluster_entity=True)

    return {
        "outcome": outcome,
        "regressor": "esg",
        "beta": res.params["esg"],
        "std_error": res.std_errors["esg"],
        "t_stat": res.tstats["esg"],
        "p_value": res.pvalues["esg"],
        "n_obs": int(res.nobs),
        "r2_within": res.rsquared_within,
        "summary_text": str(res.summary),
    }


def run_lagged_panel_regression(panel: pd.DataFrame, outcome: str) -> dict:
    """
    Same fixed-effects model but with *lagged* ESG (esg_{t-1}).

    ESG improvements may affect performance with a one-year lag: this
    year's ESG effort shows up in *next* year's ROA/ROE.  We create the
    lag within each firm (groupby → shift(1)).
    """
    df = panel.sort_values(["firm_id", "year"]).copy()
    df["esg_lag1"] = df.groupby("firm_id")["esg"].shift(1)
    df = df.dropna(subset=["esg_lag1", outcome]).copy()
    df = df.set_index(["firm_id", "year"])

    y = df[outcome]
    X = df[["esg_lag1"]]  # NO constant — absorbed by fixed effects

    model = PanelOLS(y, X, entity_effects=True, time_effects=True,
                     drop_absorbed=True)
    res = model.fit(cov_type="clustered", cluster_entity=True)

    return {
        "outcome": outcome,
        "regressor": "esg_lag1",
        "beta": res.params["esg_lag1"],
        "std_error": res.std_errors["esg_lag1"],
        "t_stat": res.tstats["esg_lag1"],
        "p_value": res.pvalues["esg_lag1"],
        "n_obs": int(res.nobs),
        "r2_within": res.rsquared_within,
        "summary_text": str(res.summary),
    }


def run_all_panel_regressions(panel: pd.DataFrame) -> list[dict]:
    """Run contemporaneous + lagged FE regressions for both ROA and ROE."""

    ensure_output_dir()
    results = []

    for outcome in ["roa", "roe"]:
        res_contemp = run_panel_fixed_effects(panel, outcome)
        res_lagged = run_lagged_panel_regression(panel, outcome)
        results.extend([res_contemp, res_lagged])

    # --- Save results CSV ---
    rows = []
    for r in results:
        rows.append({
            "outcome": r["outcome"],
            "regressor": r["regressor"],
            "beta": r["beta"],
            "std_error": r["std_error"],
            "t_stat": r["t_stat"],
            "p_value": r["p_value"],
            "n_obs": r["n_obs"],
            "r2_within": r["r2_within"],
        })

    results_df = pd.DataFrame(rows)
    results_df.to_csv(OUTPUT_DIR / PANEL_REGRESSION_CSV, index=False)

    # --- Save full model summaries ---
    summary_files = {
        "roa": PANEL_REGRESSION_ROA_TXT,
        "roe": PANEL_REGRESSION_ROE_TXT,
    }
    for outcome, fname in summary_files.items():
        texts = [r["summary_text"] for r in results if r["outcome"] == outcome]
        with open(OUTPUT_DIR / fname, "w", encoding="utf-8") as f:
            f.write(f"Panel Fixed-Effects Regressions: ESG → {outcome.upper()}\n")
            f.write("=" * 80 + "\n\n")
            for txt in texts:
                f.write(txt)
                f.write("\n\n" + "-" * 80 + "\n\n")

    return results


def print_panel_summary(results: list[dict]) -> None:
    """Print a human-readable summary of the panel regression results."""

    print("=" * 80)
    print("PANEL FIXED-EFFECTS REGRESSIONS (firm + year FE, clustered SE)")
    print("=" * 80)
    for r in results:
        sig = "***" if r["p_value"] < 0.01 else "**" if r["p_value"] < 0.05 else "*" if r["p_value"] < 0.1 else ""
        print(f"\n  {r['regressor']} -> {r['outcome'].upper()}:")
        print(f"    beta = {r['beta']:.6f}  (SE = {r['std_error']:.6f})")
        print(f"    t = {r['t_stat']:.3f},  p = {r['p_value']:.4f} {sig}")
        print(f"    n_obs = {r['n_obs']},  R2(within) = {r['r2_within']:.4f}")
    print()

