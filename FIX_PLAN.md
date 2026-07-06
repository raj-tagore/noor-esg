# Fix Plan: ESG–CFP Analysis Code (`code/` directory)

**Audience:** the coding assistant who will implement these changes.
**Read this whole document before writing any code.** It is long on purpose. Every instruction has a reason attached so you don't "fix" the wrong thing or undo a fix while making a change elsewhere.

---

## 0. TL;DR — what you are doing and why

The current code answers the research question *"Does a bank's ESG score affect its financial performance (Pretax ROA / Pretax ROE)?"* **incorrectly**. It does three fatal things:

1. It **averages all 150 firms into one number per year**, turning a rich dataset of ~2,250 firm-year observations into just **15 yearly points**, then runs every analysis on those 15 points.
2. It **measures model accuracy on the same data the model was trained on** (no train/test split), so the reported "R² ≈ 0.999" is memorization, not predictive skill.
3. It **forecasts with tree models (XGBoost/Random Forest/Decision Tree) that mathematically cannot extrapolate**, then interprets the resulting flat line as an economic "steady state."

Your job is to fix these at the root. The single most important change is **Task 1: stop averaging, build a firm-level panel dataset.** Almost everything else depends on it. Do the tasks **in the order given.**

**A rule you must not break:** *the number of observations that goes into every statistical test and model must be the firm-level count (thousands), not 15.* If at any point you find yourself running a regression, correlation, or model on a 15-row table, you have made a mistake — stop and re-read Task 1.

---

## 1. Background you need (do not skip)

### 1.1 What the data physically is

The file is `Banking (ESG, RoE, RoA)-Final Clean Data.xlsx` in the project root. Its raw shape is **152 rows × 50 columns**, laid out in "wide" format:

- **Row 0**: section headers (e.g. "ESG Score In the last 15 FY"). Ignore for data.
- **Row 1**: fiscal-year labels: `FY0, FY-1, FY-2, … FY-14`. These repeat three times (once per metric block).
- **Rows 2–151**: the actual data. **One row = one firm.** There are exactly **150 firms.**

Columns:

| Columns (0-indexed) | Meaning |
|---|---|
| 0 | RIC (unique firm identifier, e.g. `8341.T`) |
| 1 | Company Name |
| 2 | Country of Headquarters |
| 3 | Country of Incorporation |
| 4 | TRBC Industry Name (e.g. Banks, Life & Health Insurance) |
| 5–19 | **ESG Score**, one column per fiscal year `FY0 … FY-14` |
| 20–34 | **Pretax ROA**, one column per fiscal year `FY0 … FY-14` |
| 35–49 | **Pretax ROE**, one column per fiscal year `FY0 … FY-14` |

`FY0` is the most recent year and maps to **2025**; `FY-1` = 2024; … `FY-14` = 2011. The existing `config.py` already encodes the column ranges (`ESG_COLUMNS = slice(5,20)`, etc.) and `data_processing.py::fiscal_year_to_year` already converts the FY labels to calendar years. **Reuse those; do not reinvent them.**

**The key mental model:** each firm has 15 ESG values, 15 ROA values, and 15 ROE values. Cross a firm with a year and you get one observation with three numbers. 150 firms × 15 years = **2,250 firm-year rows**. That is the dataset the analysis should use. The current code destroys it by averaging.

### 1.2 Why averaging to 15 points is wrong (so you understand what "fixed" means)

When you compute `np.nanmean(esg_data, axis=0)` you collapse across all 150 firms and keep one mean per year. This throws away **all variation between firms** — which is exactly the signal needed to answer "do higher-ESG firms perform differently?" What's left only tells you whether *years* with high average ESG were *years* with low average ROA. Because ESG rose steadily and ROA drifted down over 2011–2025, the two averaged series correlate almost mechanically — a **spurious time-trend correlation**, not evidence about firms. Drawing firm-level conclusions from group averages is the **ecological fallacy**. The fix is to keep firm-level rows and use a method that separates firm-to-firm differences from year-to-year shifts (a panel/fixed-effects model — Task 2).

### 1.3 Current file map (what exists today)

- `config.py` — paths, column slices, constants. **Keep, extend slightly.**
- `data_processing.py` — loads Excel, converts FY→year, and currently **aggregates to 15 rows** via `np.nanmean(..., axis=0)`. **This is where the biggest change happens.** It already loads and stores the firm-level matrices (`esg_data`, `roa_data`, `roe_data`) on the `BankingDataset` object — they are loaded and then ignored. You will start using them.
- `models.py` — trains XGBoost/RF/DT, currently **scores on training data** (`model.predict(X)` on the same `X` it was `.fit()` on). **Must add real validation.**
- `trend_analysis.py` — runs the forecast pipeline (year → metric, forecast 2026–2030).
- `relationship_analysis.py` — correlations, linear regression, and a rolling correlation, all on the 15-row table; the rolling correlation is additionally **contaminated with forecasted values**.
- `trend_plots.py`, `relationship_plots.py` — plotting only. Touch only to relabel/repoint at new data.
- `run_all.py`, `explore_dataset.py` — orchestration/inspection. Minor.

---

## 2. Global rules for this job

1. **Do the tasks in order.** Task 1 creates the panel; Tasks 2–5 consume it. Don't jump ahead.
2. **Never run a model, regression, correlation, or significance test on the 15-row yearly-average table.** The yearly averages may ONLY be used for descriptive plots/trends, and must be clearly labelled "descriptive only" (Task 6).
3. **Never compute R² (or any accuracy metric) on the same rows a model was trained on.** Always hold data out (Task 3).
4. **Do not select a "best model" by training-set R².** That rewards overfitting. Select by out-of-sample (held-out) score only.
5. **Preserve reproducibility:** keep `random_state=42` everywhere it appears, keep outputs going to the existing `outputs/` folder, keep the modular structure.
6. **Add, don't silently delete.** When you replace an analysis, keep the old descriptive output but rename/relabel it so nothing that downstream plots expect suddenly disappears. If you remove a CSV that a plot reads, update the plot too.
7. **Every new statistical result must be written to a CSV in `outputs/`** so it can be checked by a human.
8. **Write short docstrings and inline comments** explaining *why*, not just *what* — this codebase will be read by non-experts.
9. **After each task, run the pipeline and confirm it executes without error** before moving to the next task.

---

## 3. Dependencies

Add one library for proper panel regression. Prefer **`linearmodels`** (clean fixed-effects API). `statsmodels` is an acceptable fallback.

```bash
uv add linearmodels
# or, if uv is not being used:  pip install linearmodels --break-system-packages
```

`scikit-learn`, `xgboost`, `pandas`, `numpy`, `scipy` are already present.

---

## 4. THE TASKS

### TASK 1 — Build the firm-level panel dataset (foundational, do first)

**Problem:** `data_processing.py::load_banking_dataset` returns a 15-row yearly-average table (`historical`). Everything downstream uses it. We need instead a **long-format panel**: one row per (firm, year), with columns for ESG, ROA, ROE, plus firm identifiers.

**What "long format" means (worked example).** Firm `8341.T` currently occupies ONE wide row with 45 numeric cells (15 ESG + 15 ROA + 15 ROE). In long format it becomes **15 rows**, one per year:

| firm_id | company_name | country_hq | industry | year | esg | roa | roe |
|---|---|---|---|---|---|---|---|
| 8341.T | 77 Bank Ltd | Japan | Banks | 2025 | 37.85 | … | … |
| 8341.T | 77 Bank Ltd | Japan | Banks | 2024 | 39.72 | … | … |
| … | … | … | … | … | … | … | … |
| 8341.T | 77 Bank Ltd | Japan | Banks | 2011 | … | … | … |

Do this for all 150 firms → **~2,250 rows** (fewer if some firm-years are missing; that's fine, drop rows where all three metrics are NaN).

**Exactly what to implement** (in `data_processing.py`, add a new function; do **not** delete the existing aggregation yet — Task 6 keeps it for descriptive use):

```python
def build_panel_dataset(path=DATA_FILE) -> pd.DataFrame:
    """
    Return a long-format firm-year panel:
    columns = [firm_id, company_name, country_hq, country_inc, industry,
               year, esg, roa, roe]
    One row per (firm, year). ~2,250 rows for 150 firms x 15 years.
    This is the dataset ALL statistical tests and models must use.
    """
    df_raw = load_raw_dataset(path)                      # header=None, existing helper

    # Year labels live in row index 1; data starts at row index 2.
    year_labels = df_raw.iloc[1, ESG_COLUMNS].tolist()
    years = [fiscal_year_to_year(lbl) for lbl in year_labels]   # e.g. [2025, 2024, ... 2011]

    data_rows = df_raw.iloc[2:, :].reset_index(drop=True)

    # Identifiers (columns 0..4)
    ids = data_rows.iloc[:, 0:5].copy()
    ids.columns = ["firm_id", "company_name", "country_hq", "country_inc", "industry"]

    # Numeric metric blocks -> coerce to numeric so text/blank cells become NaN
    esg = data_rows.iloc[:, ESG_COLUMNS].apply(pd.to_numeric, errors="coerce")
    roa = data_rows.iloc[:, ROA_COLUMNS].apply(pd.to_numeric, errors="coerce")
    roe = data_rows.iloc[:, ROE_COLUMNS].apply(pd.to_numeric, errors="coerce")

    # Give every metric block the SAME column names = the calendar years,
    # so we can melt each to long and merge on (firm_id, year).
    esg.columns = roa.columns = roe.columns = years

    def melt_metric(frame, value_name):
        m = frame.copy()
        m["firm_id"] = ids["firm_id"].values
        long = m.melt(id_vars="firm_id", var_name="year", value_name=value_name)
        return long

    esg_long = melt_metric(esg, "esg")
    roa_long = melt_metric(roa, "roa")
    roe_long = melt_metric(roe, "roe")

    panel = (esg_long
             .merge(roa_long, on=["firm_id", "year"])
             .merge(roe_long, on=["firm_id", "year"]))

    # Attach firm attributes (country, industry) back on
    panel = panel.merge(ids, on="firm_id", how="left")

    # IMPORTANT unit check: in the wide data ROA/ROE may be stored as fractions
    # (e.g. 0.017) rather than percentages (1.7). The old code multiplied the
    # yearly means by 100. Inspect a few raw values and apply the SAME convention
    # here so 'roa'/'roe' are in PERCENT. Do this ONCE, here, and nowhere else.
    # (If raw values look like 0.0xx, multiply roa and roe by 100.)

    # Drop rows with no usable data at all
    panel = panel.dropna(subset=["esg", "roa", "roe"], how="all")

    # Types
    panel["year"] = panel["year"].astype(int)
    return panel.sort_values(["firm_id", "year"]).reset_index(drop=True)
```

**Acceptance criteria for Task 1:**
- A function returns a DataFrame with roughly 2,000–2,250 rows and the columns listed above.
- `panel["firm_id"].nunique()` ≈ 150.
- `panel["year"].nunique()` == 15, ranging 2011–2025.
- Save it once for inspection: `panel.to_csv(OUTPUT_DIR / "banking_panel_long.csv", index=False)`.
- **Verification step:** print `panel.shape`, `panel["firm_id"].nunique()`, `panel["year"].min()/max()`, and `panel[["esg","roa","roe"]].describe()`. A human will eyeball these. ROA should be roughly single-digit percent, ROE roughly low-double-digit percent.
- **Unit sanity:** confirm ROA/ROE magnitudes match the paper's descriptive stats (ROA ~1–3%, ROE ~14–18%). If they come out as 0.0x, you missed the ×100 conversion.

---

### TASK 2 — Replace the aggregate correlation/regression with a panel fixed-effects regression

**Problem:** `relationship_analysis.py` computes the ESG↔ROA/ROE correlation and a `LinearRegression` on the **15 yearly averages**. That is the spurious-trend problem from §1.2. The p-values use `n = 15`. All of this must move to the firm-level panel and use a method that controls for firm and year.

**Why fixed effects (explain to yourself before coding):** A **firm fixed effect** gives every firm its own baseline, so the model measures whether *a given firm's* ROA changes when *its own* ESG changes — not whether high-ESG firms happen to be different companies. A **year fixed effect** absorbs shocks that hit everyone at once (e.g. COVID in 2020, interest-rate cycles), so a sector-wide dip doesn't get mislabelled as an ESG effect. Standard errors should be **clustered by firm** because a firm's own observations across years are correlated.

**What to implement** (new module `panel_regression.py`, called from `relationship_analysis.py`):

```python
from linearmodels.panel import PanelOLS
import statsmodels.api as sm  # only if you prefer the statsmodels path

def run_panel_fixed_effects(panel: pd.DataFrame, outcome: str) -> dict:
    """
    Estimate:  outcome_it = alpha_i + gamma_t + beta * esg_it + e_it
    - alpha_i : firm fixed effects (entity effects)
    - gamma_t : year fixed effects (time effects)
    - beta    : the coefficient we care about (ESG -> outcome)
    Standard errors clustered by firm.
    outcome is 'roa' or 'roe'.
    """
    df = panel.dropna(subset=["esg", outcome]).copy()
    df = df.set_index(["firm_id", "year"])          # MultiIndex: (entity, time)

    y = df[outcome]
    X = sm.add_constant(df[["esg"]])                 # constant + ESG

    model = PanelOLS(y, X, entity_effects=True, time_effects=True)
    res = model.fit(cov_type="clustered", cluster_entity=True)

    return {
        "outcome": outcome,
        "beta_esg": res.params["esg"],
        "std_error": res.std_errors["esg"],
        "t_stat": res.tstats["esg"],
        "p_value": res.pvalues["esg"],
        "n_obs": int(res.nobs),
        "r2_within": res.rsquared_within,
        "summary_text": str(res.summary),
    }
```

**Also add a lagged-ESG version.** ESG effects on performance are often not contemporaneous — this year's ESG may relate to *next* year's performance. Within each firm, create `esg_lag1 = esg` shifted by one year (sort by firm then year, `groupby("firm_id")["esg"].shift(1)`), and run the same regression with `esg_lag1` as the regressor. Report both contemporaneous and lagged results.

**Recommended (not mandatory) enhancement:** add control variables if you can derive them — e.g. firm size proxy, and keep industry/country (these are largely absorbed by firm fixed effects, so they matter more in a random-effects or pooled spec). Note this as a "future" comment if you don't implement it.

**What to remove / relabel:**
- Keep a *descriptive* Pearson correlation of yearly averages **only if** it is clearly labelled in the output as "descriptive, sector-level time trend — NOT a firm-level or causal estimate." Do not report its p-value as if it tests the research hypothesis.
- The headline relationship result in every output/CSV/plot must now be the **panel fixed-effects beta, p-value, and n_obs** (n_obs should be ~2,000+, not 15).

**Acceptance criteria for Task 2:**
- `outputs/banking_panel_regression_results.csv` exists with columns: outcome, regressor (esg / esg_lag1), beta, std_error, t_stat, p_value, n_obs, r2_within.
- `n_obs` is in the thousands.
- The full `res.summary` text for each model is saved to `outputs/` as a `.txt` for human review.
- **Verification step:** confirm `n_obs > 1500` for at least the contemporaneous ROA model; if it's 15 you are still using the aggregate table.

---

### TASK 3 — Add real out-of-sample validation to the ML models; stop reporting in-sample R²

**Problem:** `models.py` does `model.fit(X, y)` then `model.predict(X)` on the **same X**, and reports `r2_score(y, predictions)`. With flexible tree models this yields R² ≈ 0.999 by memorization. `best_model_name()` then picks the model with the highest **training** R² — i.e. the most overfit one.

**Rule:** metrics must be computed on data the model has **never seen during fitting**.

**Two distinct evaluation settings — implement the right one for each use:**

**(a) Relationship models (ESG → ROA/ROE) on the panel.** Use **`GroupKFold` grouped by `firm_id`** so that all rows of a firm are either in train or in test, never split across both (prevents the model from "recognizing" a firm). Report the **mean and standard deviation of the held-out R², RMSE, MAE across folds.**

```python
from sklearn.model_selection import GroupKFold, cross_validate

def evaluate_relationship_model(panel, outcome, model):
    df = panel.dropna(subset=["esg", outcome])
    X = df[["esg"]].values
    y = df[outcome].values
    groups = df["firm_id"].values
    cv = GroupKFold(n_splits=5)
    scores = cross_validate(
        model, X, y, groups=groups, cv=cv,
        scoring=["r2", "neg_root_mean_squared_error", "neg_mean_absolute_error"],
        return_train_score=True,
    )
    # Report BOTH train and test; the gap between them reveals overfitting.
    return {
        "test_r2_mean": scores["test_r2"].mean(),
        "test_r2_std":  scores["test_r2"].std(),
        "train_r2_mean": scores["train_r2"].mean(),
        "test_rmse_mean": -scores["test_neg_root_mean_squared_error"].mean(),
        "test_mae_mean":  -scores["test_neg_mean_absolute_error"].mean(),
    }
```

**(b) Time-series forecasting models (year → metric).** Cross-validation by random folds is wrong for time series. Use a **rolling/expanding backtest**: train on years up to T, predict year T+1, step forward. `sklearn.model_selection.TimeSeriesSplit` on the time-ordered data is acceptable. Report held-out error. **But also read Task 4 — the forecasting approach itself is flawed.**

**Fix `best_model_name`:** rank models by **held-out** score (`test_r2_mean`), never training score. Add an explicit assertion/comment: "selection uses out-of-sample R² only."

**What you will observe and must report honestly:** once evaluated out-of-sample, the tree models' R² will **drop dramatically** (likely near zero or negative for a single-feature ESG→ROA relationship). That is the correct, honest result, and it tells the true story: a single ESG number does not predict a firm's ROA well. Do not tune the model to hide this. Write the train-vs-test gap into the output so the overfitting is visible.

**Acceptance criteria for Task 3:**
- No metric anywhere is computed via `model.predict(X)` on the same `X` used in `.fit(X, y)` for reporting purposes.
- `outputs/banking_model_performance.csv` now has both `train_r2` and `test_r2` columns (plus test RMSE/MAE).
- `best_model_name` (or its replacement) selects on `test_r2`.
- **Verification step:** print train_r2 and test_r2 side by side; a large positive gap (e.g. train 0.99 vs test 0.1) confirms the evaluation is now honest.

---

### TASK 4 — Fix (or honestly reframe) the 2026–2030 forecast

**Problem:** Trees (XGBoost, Random Forest, Decision Tree) **cannot extrapolate**. For any input beyond the training range they output the value of the nearest leaf — a flat constant. So forecasting 2026–2030 with `Year` as the only feature produces a flat line by construction, which the paper wrongly interprets as an economic "steady state / ESG maturity." This is a modeling artifact, not a finding.

**Do this:**
1. **Stop using tree models for extrapolative forecasting.** Replace the forecast engine with models that can express a trend: at minimum a **linear trend / OLS on year**, and optionally a proper time-series model (e.g. `statsmodels` ARIMA/`AutoReg`) if you want to show uncertainty.
2. **Attach uncertainty.** Report prediction intervals (e.g. OLS confidence/prediction intervals), not point values only. A forecast without an interval on 15 annual points is misleading.
3. **Add a plain-language caveat in the output**: "15 annual observations is a very short series; forecasts to 2030 are illustrative and highly uncertain."
4. **If you keep the tree forecasts at all**, keep them ONLY as an explicit teaching contrast, labelled: "Tree models cannot extrapolate; the flat line below is an artifact, not a prediction." Do not present them as the headline forecast.

**Acceptance criteria for Task 4:**
- The primary forecast comes from a model capable of extrapolation (linear/time-series), with prediction intervals saved to CSV.
- Any tree-based forecast is either removed or explicitly labelled as an artifact.
- Plots and text no longer describe the flat tree output as a "steady state" or "maturity" finding.

---

### TASK 5 — Fix the rolling-correlation analysis

**Problem:** `relationship_analysis.py::_rolling_correlations` runs on `combined_df = historical + XGBoost-predicted future rows`. So the rolling windows for later years correlate **forecasted** values, producing meaningless ±1.0 correlations for 2026–2030. Also, each window is only 5 points, so even the historical part is extremely noisy.

**Do this:**
1. **Never include forecasted/predicted rows in a correlation.** Compute rolling correlations on **observed data only** (historical panel/averages), stopping at the last real year (2025). Remove the concatenation with `future_df` entirely from this computation.
2. Ideally compute the rolling relationship **on the panel** within each window (i.e. within a 5-year window, correlate firm-year ESG vs ROA across all firms in those years) rather than on 5 yearly averages, which gives far more stable estimates.
3. Add a caveat that 5-year windows on short data are noisy and exploratory.

**Acceptance criteria for Task 5:**
- The rolling-correlation output contains no year beyond 2025.
- No ±1.0 degenerate values from forecast contamination.
- If computed on the panel, each window's correlation is based on many firm-year points, not 5.

---

### TASK 6 — Keep descriptive/aggregate trends, but quarantine and relabel them

The yearly-average trends (ESG rising, ROA falling) are fine as **descriptive context** and for the trend plots. They are only dangerous when used for inference.

**Do this:**
- Keep `load_banking_dataset` (the 15-row aggregate) but rename its output usage to make intent obvious, e.g. call it `sector_yearly_means` and add a docstring: "Descriptive sector-level yearly means. For plotting/context ONLY. Not to be used for correlation, regression, model training, or significance testing."
- Every plot/table derived from it must carry a label like "Sector-average trend (descriptive)."
- Ensure no statistical test or model in the codebase imports from this path anymore (grep for its usages after Tasks 2–3).

**Acceptance criteria for Task 6:**
- The 15-row table is used only by descriptive trend plots.
- A grep for the aggregate table shows zero usage inside regression/model/correlation code paths.

---

### TASK 7 — Housekeeping and consistency (lower priority, still do it)

- **Reconcile the time period.** The draft variously says 2011–2025, 2011–2024, and "10 years (2014–2024)." The data is FY0..FY-14 = **2011–2025 (15 years)**. Make the code, output labels, and any generated captions consistently say **2011–2025**.
- **Reconcile geography.** The dataset is Asian markets (Japan, China, Hong Kong, Turkey, Saudi Arabia, India, Malaysia, etc.). Any leftover text/labels saying "USA, UK, Germany" are wrong — remove them from code-generated outputs.
- **Update `README.md`** in `code/` to describe the new panel-based pipeline and the new output files.
- Keep `random_state=42` everywhere for reproducibility.

---

## 5. Suggested final module layout

```
code/
  config.py                 # extend: add panel output filenames
  data_processing.py        # + build_panel_dataset(); keep sector_yearly_means (descriptive)
  panel_regression.py       # NEW: fixed-effects regression (Task 2)
  models.py                 # rewrite metrics to out-of-sample (Task 3)
  forecasting.py            # NEW or refactor trend_analysis: extrapolation-capable forecast (Task 4)
  relationship_analysis.py  # consume panel; rolling corr on observed data only (Task 5)
  trend_analysis.py         # descriptive trends + honest forecast
  trend_plots.py            # relabel; point at new data
  relationship_plots.py     # relabel; point at new data
  run_all.py                # orchestrate
```

---

## 6. Definition of Done (final verification checklist)

Before declaring finished, confirm **every** box:

- [ ] A firm-level panel (~2,250 rows, ~150 firms, 15 years) is built and saved to `outputs/banking_panel_long.csv`.
- [ ] The headline ESG→ROA and ESG→ROE results come from a **panel fixed-effects regression** (firm + year effects, clustered SE) with **n_obs in the thousands**, saved to CSV + summary `.txt`.
- [ ] A **lagged-ESG** specification is also reported.
- [ ] No model reports R² on its own training rows; every reported metric is **out-of-sample** (GroupKFold by firm for relationship models; time-ordered backtest for forecasts).
- [ ] Model selection uses **held-out** score, not training score.
- [ ] The `train_r2` vs `test_r2` gap is written to the performance CSV (overfitting is visible, not hidden).
- [ ] Forecasts use an **extrapolation-capable** model with **prediction intervals**; any tree forecast is removed or explicitly labelled an artifact; no output calls the flat line a "steady state."
- [ ] Rolling correlations contain **no forecasted rows** and no degenerate ±1.0 values.
- [ ] The 15-row yearly-average table is used **only** for descriptive plots, clearly labelled, and is absent from all inferential code paths (verified by grep).
- [ ] Period is labelled **2011–2025** and geography as **Asian markets** consistently.
- [ ] `uv run python code/run_all.py` executes end-to-end without error.
- [ ] `README.md` updated.

---

## 7. Things you might get wrong — read once more

- **Do not** "fix" the 15-point problem by generating more yearly averages, smoothing, or interpolating. The fix is firm-level data, full stop.
- **Do not** improve the tree models' out-of-sample R² by feeding them more engineered features until it looks good — if the honest signal is weak, report it weak.
- **Do not** leave any forecasted value inside a correlation or a reported historical statistic.
- **Do not** delete the descriptive trend plots — they're useful; just relabel them.
- If any regression or model you write ends up with `n = 15`, you have reintroduced the original bug. The whole point of this work is that **n should be in the thousands.**
