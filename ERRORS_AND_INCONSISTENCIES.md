# Review: errors & inconsistencies — code/ and research paper

Reviewed: `code/` (vs git HEAD), `AI Research Paper Draft_ Modified on 8.1.26 (1).docx`, `Revised References-2026.docx`, `outputs/`, and the raw Excel data.

> **UPDATE (re-check, Jul 8):** Sections 1 and 2's data-side problems are now RESOLVED — the code files are restored (content-identical to git HEAD), the pipeline was re-run, `banking_panel_long.csv` has all 2,250 rows / 150 firms, descriptive stats reach 2025, all regression/ML/correlation outputs still match the paper, and the regenerated figures show the full 2011–2025 series. **The docx itself is unchanged**, so every paper-side item below (Table 4 pooled stats, Figures 1–5, Section 3, and Section 4 citation issues) is still open.

---

## 1. ~~CRITICAL~~ RESOLVED — several files were truncated (corrupted)

The working copies of these files are cut off mid-file. Git HEAD has the complete versions, so this happened after the last commit (likely a bad sync/copy):

| File | Problem |
|---|---|
| `code/config.py` | Ends mid-comment; all output-filename constants (`PANEL_CSV`, `FORECAST_CSV`, etc.) missing → every module that imports them crashes |
| `code/data_processing.py` | Syntax error at line 93; most of `build_panel_dataset()` and all of `build_descriptive_stats()` missing |
| `code/run_all.py` | `main()` missing — imports only |
| `code/README.md` | Truncated |
| `outputs/banking_panel_long.csv` | **1,807 of 2,250 rows (121 of 150 firms)** |
| `outputs/banking_descriptive_stats.csv` | Ends mid-row at 2021; years 2022–2025 missing |

**The pipeline cannot run in its current state.** Fix: `git restore code/config.py code/data_processing.py code/run_all.py code/README.md`, then re-run the pipeline to regenerate the two truncated CSVs.

## 2. Paper errors caused by the truncated data

Someone evidently computed parts of the paper from the truncated CSVs:

- **Table 4 (pooled descriptive stats) is wrong.** Its values exactly match the 1,807-row truncated panel. Correct full-panel (2,250-row, winsorized) values:

  | Statistic | Paper | Correct |
  |---|---|---|
  | ESG mean / std | 47.00 / 21.69 | **47.84 / 20.89** |
  | ROA mean / std | 1.65 / 2.05 | **1.84 / 2.31** |
  | ROE mean / std | 13.64 / 8.42 | **14.85 / 9.10** |

  (Min/max and the median rows of Table 4 happen to be correct — the table mixes two data sources.)
- **Figure 1** is titled "2011–2025" but plots only 2011–2021 (ROE stops at 2020) — built from the truncated descriptive-stats CSV.
- **Figures 4 & 5**: observed median series stops at 2021/2020, leaving a visible gap before the 2026–2030 forecast; the title claims "15 annual points". (The forecast line itself matches the correct full-data CSV.)
- **Figure 2 contradicts the text.** The text reports r = +0.014 (ESG–ROA), but the plotted OLS line slopes *down* (slope ≈ −0.0034 ⇒ r ≈ −0.036) — the truncated-panel value. Figure 3 has the same provenance (r ≈ 0.098 plotted vs 0.120 reported), just less visible.
- Figure 6 (rolling correlations) is fine — matches outputs.

**Fix:** restore code, re-run pipeline, regenerate Figures 1–5 and recompute Table 4's pooled rows.

## 3. Internal inconsistencies in the paper

- **Table 7 is titled "XGBoost Predictions for 2026-2030"** but contains the linear-trend (OLS) forecast — and the paper explicitly states tree models are not used for forecasting. Leftover caption from the old draft.
- **Abstract vs results text:** abstract says median Pretax ROE was "in the 12–16% range"; the results section (and data) say 10.5–15.9% (2022 median ≈ 10.5%). The abstract is wrong.
- **Two tables are numbered "Table 4"** (primary-variables table in §3.1 and descriptive statistics in §4.1). "Table 5 and 6" is a single combined table; Table 8's caption appears after its data.
- **§3.1 describes a different dataset.** The paragraph on missing data ("funds", "80–90% missing", "threshold of approximately 4,600 null entries per column") cannot apply to a 2,250-row panel and appears lifted from Martin-Melero et al. It also contradicts the actual processing: it claims rows with any missing data were dropped for a "fully complete dataset", yet the paper's own n differs by metric (2,230 ROA vs 2,225 ROE), and the code drops a row only if all three metrics are missing.
- Minor: text says annual ESG std was "roughly 18–20 points"; actual range 17.4–20.4. Table 3 gives 16 firms = 10.7% (Life & Health) but 16 firms = 10.6% (Other) — rounding forced to sum to 100%.

## 4. Citation and reference problems

- **7 placeholder citations "(xxxx…)"** remain in the Introduction and Literature Review.
- **Year mismatches vs the reference list:** Avramov et al., 2024 → refs say 2025; Chung et al., 2023 → refs say 2024; Kim and Yoon, 2020 → refs say 2023; Saetra, 2022 (Table 1) → refs say 2023.
- **"Ferrera, 2024"** (Table 2) is a misspelling of Ferrara (& Ciano).
- **Sætra (2023) appears twice** in the reference list (#24 and #49).
- **"Random Forest, initially introduced by Breiman in 1999"** — the canonical citation is Breiman (2001); Breiman is not in the reference list at all.
- **Friede et al. (2015) is cited for 2018 statistics** ($17.5T of $74.3T AUM "as of 2018") — a 2015 paper cannot source 2018 data.
- **Table 1 rows are internally inconsistent:** Chung et al. listed as Vietnam/hospitality but the methodology cell says U.S. hotel firms; Minkkinen et al.'s focus is described as "AI in education" while the findings concern ESG-investing expert interviews; Kim & Yoon marked "South Korea" though the study covers U.S. mutual funds.
- Name-style mismatches between text and references: "Melero et al." vs Martin-Melero; "Giri and Chaparro" vs Suárez Giri & Sánchez Chaparro; "Heever et al." vs Van den Heever; "Vitto et al." vs Del Vitto.

## 5. Code review (git HEAD versions)

The methodology is sound and consistent with the paper: firm-level panel (2,250 obs), two-way FE with firm-clustered SEs, GroupKFold out-of-sample ML evaluation, linear-trend forecast with prediction intervals. All reported statistics (betas, t, p, n, R², RMSE/MAE, rolling correlations, forecasts, per-year medians) match the outputs exactly. Minor points:

- `forecasting.py` docstring and `code/README.md` say the forecast is fitted to annual **means**, but `trend_analysis.py` (and the paper) use **medians**. Update the docs.
- Winsorization bounds use pooled full-sample (2011–2025) quantiles — a mild look-ahead for the illustrative forecast; worth a one-line acknowledgment at most.
- The correlation t-test in §3.3 (Eq. 4) assumes independent observations; firm-year rows are serially correlated. The paper already flags these correlations as descriptive-only, which covers it.

## Recommended actions (in order)

1. `git restore` the four truncated code files; re-run `run_all.py`; confirm `banking_panel_long.csv` has 2,250 rows and descriptive stats reach 2025.
2. Regenerate Figures 1–5 from the restored outputs; replace them in the docx.
3. Correct Table 4's pooled mean/std rows; fix the Table 7 caption; fix the abstract's ROE range; renumber duplicate Table 4.
4. Rewrite the §3.1 missing-data paragraph to describe the actual dataset.
5. Resolve all placeholder (xxxx) citations; fix the year/spelling mismatches and the duplicate/missing references.
