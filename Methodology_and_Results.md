# ESG and Corporate Financial Performance in Asian BFSI Firms: Methodology and Results

*Firm-level panel analysis, 2011–2025. This document supersedes the earlier sector-average methodology and reports the corrected findings.*

---

## 3. Methodology

### 3.1 Data

Firm-level ESG scores and financial performance data for the Banking, Financial Services, and Insurance (BFSI) sector were obtained from the Refinitiv Eikon database for the period 2011–2025. The sample comprises approximately **150 BFSI firms** headquartered across Asian markets (including Japan, China, Hong Kong, Turkey, Saudi Arabia, India, and Malaysia) that consistently disclosed ESG information for at least five years. Because each firm is observed over up to 15 fiscal years, the working dataset is a **firm-year panel of 2,250 firm-years** (2,230 with non-missing ROA; 2,225 with non-missing ROE), not a set of annual sector averages.

Three variables are used:

- **ESG Score** — a composite Refinitiv metric combining environmental, social, and governance performance on a 0–100 scale.
- **Pretax Return on Assets (ROA)** — pretax income divided by total assets (%).
- **Pretax Return on Equity (ROE)** — pretax income divided by shareholders' equity (%).

**Outlier handling.** ROA and ROE are ratios whose denominators (assets, equity) can collapse toward zero for a distressed firm, producing economically meaningless extremes. For example, one firm posted a 2020 ROE of roughly −4,162% after its equity was almost entirely eroded, even though its ROA that year was only modestly negative. A single such value can dominate a sector mean and distort regression estimates. To prevent this, ROA and ROE are **winsorized at the 1st and 99th percentiles** (pooled across all firm-years); raw values are retained for transparency.

**Descriptive aggregation (context only).** Annual sector means and medians are computed purely to describe broad trends. They are **not** used for correlation, regression, or model training, because averaging ~150 firms into a single number per year discards the cross-firm variation needed to identify any ESG–performance relationship and reduces the data to just 15 points, which produces spurious, trend-driven associations.

### 3.1.1 Exploratory sample diagnostics

Before inference, a descriptive atlas of the firm-year panel is produced (script: `code/explore_dataset.py`; figures under `outputs/explore/`). These plots use headquarters country (`country_hq`) and TRBC industry labels already present in the panel. For multi-series and faceted figures, country or industry groups with fewer than five distinct firms are collapsed into an “Other” category so thin cells do not dominate the display; exact uncollapsed counts are retained in `outputs/explore/panel_composition_summary.csv` and in the single-dimension bar charts.

In this sample the panel has **150 firms** and **2,250 firm-years** (2011–2025). Headquarters coverage is led by Japan (37), China (17), South Korea (16), India (13), and Taiwan (13). By industry, Banks predominate (97), followed by Life & Health Insurance (16) and Investment Banking & Brokerage Services (12). ESG is non-missing in all firm-years; pretax ROA and ROE are available for 99.1% and 98.9% of firm-years respectively.

The figures are for sample understanding only. Median trajectories and faceted ESG–ROA scatters are **not** used for correlation, regression, or causal claims; those rest on the panel fixed-effects results in §4.

| Figure | File | What it shows | Why it matters |
|---|---|---|---|
| 1 | `01_composition_country.png` | Distinct firms by `country_hq` (all countries) | Shows geographic concentration and which markets dominate the Asian BFSI sample |
| 2 | `02_composition_industry_heatmap.png` | Firms by industry, plus a country × industry firm-count heatmap (rare groups collapsed) | Clarifies industry mix and where country–industry cells are thin before subgroup work |
| 3 | `03_coverage_over_time.png` | Non-null ESG / ROA / ROE firm-year counts by calendar year | Reveals unbalancedness and whether disclosure or financial coverage changes over 2011–2025 |
| 4 | `04_coverage_by_country.png` | ESG coverage rate and median years of ESG history per firm, by country group | Flags thin or short-history country cells that would be unreliable for heterogeneity analysis |
| 5 | `05_univariate_distributions.png` | Histograms/KDEs of ESG, pretax ROA, and pretax ROE (firm-year; ROA/ROE winsorized) | Checks skew, tails after winsorization, and overall scale of each metric |
| 6 | `06_distributions_by_group.png` | Box plots of ESG and ROA by industry and by country group | Shows level differences across business models and markets (descriptive heterogeneity of levels) |
| 7 | `07_median_trajectories_by_group.png` | Median ESG over time by country group and by industry | Descriptive trend comparison across groups; not used for ESG–CFP inference |
| 8a / 8b | `08a_esg_vs_roa_by_industry.png`, `08b_esg_vs_roa_by_country.png` | Firm-year ESG vs ROA scatters faceted by industry and by country group | Makes within-group clouds visible; pooled scatter alone can hide composition |

### 3.2 Primary model: panel fixed-effects regression

The core inferential model is a **two-way (firm and year) fixed-effects panel regression**, estimated on the full firm-year panel. For firm *i* in year *t*:

$$Y_{it} = \alpha_i + \gamma_t + \beta \cdot ESG_{it} + \varepsilon_{it}$$

where:

- **Y_it** is Pretax ROA or Pretax ROE;
- **α_i** is a firm fixed effect, absorbing time-invariant firm characteristics (size class, business model, country, and so on);
- **γ_t** is a year fixed effect, absorbing macro-financial shocks common to all firms in a given year (e.g., the COVID-19 period, rate cycles);
- **β** is the coefficient of interest, capturing the *within-firm* association between ESG and performance;
- **ε_it** is the idiosyncratic error.

Standard errors are **clustered by firm** to account for within-firm serial correlation. The model is estimated in both a **contemporaneous** form (ESG_it) and a **one-year-lagged** form (ESG_i,t−1), the latter allowing current profitability to respond to prior ESG effort. Because the firm and year fixed effects remove the shared time trends that drive spurious correlations in aggregated data, β identifies whether *changes in a firm's own ESG score* are associated with *changes in its own profitability*.

For descriptive comparison, Pearson correlations between ESG and each financial metric are also reported at the firm-year level (across all observations, not on yearly averages).

### 3.2.1 Heterogeneity by country group and industry

To check whether the pooled null result masks differences across markets or business lines, the **same two-way FE estimator** is re-estimated on geography- and industry-based subsamples (script: `code/heterogeneity.py`). Group membership is defined by region / market identity first; firm counts only determine whether a country is estimated alone or remains inside its regional pool. There is no catch-all “Other” of unrelated small markets.

**Country groups** (`country_hq`):

| Group | Members |
|---|---|
| Japan | Japan |
| China (incl. Hong Kong) | China, Hong Kong |
| Korea | Korea; Republic (S. Korea) |
| Taiwan | Taiwan |
| India | India |
| ASEAN | Malaysia, Indonesia, Thailand, Singapore, Philippines |
| West Asia / Middle East | Turkey, Israel, Kuwait, Jordan, Oman, Qatar, Saudi Arabia |

**Industry groups** (TRBC): Banks; Insurance (Life & Health + Property & Casualty); Other financials (remaining industries).

A subsample is estimated only if it has at least **10 firms** and **100 firm-years** with usable ESG and outcome data. Contemporaneous and one-year-lagged ESG specifications are reported. Descriptive explore plots in §3.1.1 are not substitutes for these regressions. Forest plots of contemporaneous coefficients are saved as `banking_heterogeneity_country_forest.png` and `banking_heterogeneity_industry_forest.png`.

### 3.3 Machine-learning models and out-of-sample validation

Three tree-based models — **XGBoost, Random Forest, and Decision Tree** — are used to test whether ESG has any (possibly non-linear) predictive value for financial performance. Their reliability depends entirely on how they are evaluated:

- **Out-of-sample only.** Performance is measured on data the model did not see during fitting, using **k-fold cross-validation with folds grouped by firm** (`GroupKFold`), so that all observations of a given firm fall entirely within either the training or the test partition. This prevents a model from "recognizing" a firm across the train/test split.
- **Train and test scores are both reported.** A large gap between them reveals overfitting.

Evaluating a model on the same rows used to fit it — as in the earlier version of this study — yields near-perfect R² by memorization and is not evidence of predictive power.

### 3.4 Forecasting

Tree-based models **cannot extrapolate**: beyond the range of their training data they return a flat, constant value (the nearest leaf), so any apparent "stabilization" they produce for future years is a modeling artifact, not an economic finding. They are therefore **not** used for projection. Instead, an **illustrative linear-trend (ordinary least squares) forecast** is fitted to the annual **median** series, with 95% prediction intervals. Given only 15 annual observations, these projections are explicitly illustrative and carry wide uncertainty.

### 3.5 Evaluation metrics

Model fit is quantified with the coefficient of determination (R², reported out-of-sample), root mean squared error (RMSE), and mean absolute error (MAE). Statistical significance of regression coefficients is assessed with firm-clustered t-statistics and associated p-values, using a 5% threshold.

---

## 4. Results

### 4.1 Descriptive statistics and historical trends

Over 2011–2025, sector ESG scores rose markedly while profitability was broadly stable. Table 1 reports the pooled firm-year distribution; Table 2 shows the annual median trajectory.

**Table 1. Firm-year descriptive statistics (2011–2025, ROA/ROE winsorized).**

| Statistic | ESG Score | Pretax ROA (%) | Pretax ROE (%) |
|---|---|---|---|
| Mean | 47.00 | 1.65 | 13.64 |
| Standard deviation | 21.69 | 2.05 | 8.42 |
| Minimum | 2.42 | −1.39 | −8.08 |
| Maximum | 92.63 | 16.13 | 47.66 |
| 2011 (median) | 40.81 | 1.28 | 14.60 |
| 2025 (median) | 63.76 | 1.27 | 12.51 |
| Median change | +56.2% | −0.7% | −14.3% |

ESG scores climbed steadily (median 40.8 → 63.8), but cross-firm dispersion remained large throughout (annual standard deviation ≈ 18–20 points), indicating continued heterogeneity rather than convergence. Median ROA was essentially flat, dipping to about 0.96% in 2022 (post-pandemic adjustment) before recovering. Median ROE drifted modestly lower. After winsorization, the 2020 ROE shows **no** pandemic "crash" (median ≈ 12.6%, in line with adjacent years); the earlier apparent collapse was a single distressed firm, not a sector event.

**Table 2. Annual sector medians (N = 150 firms each year).**

| Year | ESG (median) | ROA (median, %) | ROE (median, %) |
|---|---|---|---|
| 2011 | 40.81 | 1.28 | 14.60 |
| 2012 | 37.94 | 1.48 | 15.90 |
| 2013 | 36.21 | 1.53 | 15.50 |
| 2014 | 35.38 | 1.51 | 15.00 |
| 2015 | 36.18 | 1.51 | 15.55 |
| 2016 | 39.64 | 1.50 | 14.76 |
| 2017 | 42.20 | 1.35 | 13.83 |
| 2018 | 46.16 | 1.24 | 12.19 |
| 2019 | 51.36 | 1.27 | 12.68 |
| 2020 | 56.36 | 1.28 | 12.61 |
| 2021 | 57.93 | 1.20 | 12.73 |
| 2022 | 60.91 | 0.96 | 10.54 |
| 2023 | 61.88 | 1.31 | 12.81 |
| 2024 | 63.82 | 1.21 | 12.52 |
| 2025 | 63.76 | 1.27 | 12.51 |

### 4.2 ESG and financial performance: panel fixed-effects results

**The central finding is a null result: ESG scores have no statistically significant association with Pretax ROA or Pretax ROE** once firm and year fixed effects are controlled and standard errors are clustered by firm (Table 3). All four specifications are insignificant, with within-firm R² essentially zero — that is, within-firm variation in ESG explains none of the within-firm variation in profitability.

**Table 3. Two-way fixed-effects panel regressions (firm + year FE; SE clustered by firm).**

| Outcome | ESG term | β | Std. error | t | p-value | n (firm-years) | Within-R² |
|---|---|---|---|---|---|---|---|
| Pretax ROA | contemporaneous | 0.00105 | 0.00329 | 0.32 | 0.750 | 2,230 | ≈ 0 |
| Pretax ROA | one-year lag | 0.00361 | 0.00305 | 1.18 | 0.237 | 2,082 | ≈ 0 |
| Pretax ROE | contemporaneous | 0.00147 | 0.02119 | 0.07 | 0.945 | 2,225 | ≈ 0 |
| Pretax ROE | one-year lag | 0.01341 | 0.02109 | 0.64 | 0.525 | 2,077 | ≈ 0 |

In substantive terms, a one-point change in a bank's ESG score is associated with a change in profitability that is statistically indistinguishable from zero. The pooled firm-year correlations tell the same story: **r = 0.014 for ESG–ROA** (n = 2,230) and **r = 0.120 for ESG–ROE** (n = 2,225) — both negligible.

This contrasts sharply with the strong negative correlation (r ≈ −0.55) reported when firms are collapsed into a single annual sector average. That approach reduces ~2,230 observations to 15 points and measures only the co-movement of two sector-wide trends (rising ESG, gently drifting profitability) — a spurious, trend-driven artifact rather than a firm-level relationship.

### 4.2.1 Heterogeneity: country groups and industry

Re-estimating the same FE model within geographic and industry groups largely **reproduces the pooled null**. Tables 3a–3b report contemporaneous ESG coefficients (lagged results are in `outputs/banking_heterogeneity_*.csv`; forest plots show the same contemporaneous pattern).

**Table 3a. Contemporaneous ESG FE coefficients by country group.**

| Group | Outcome | β | SE | p-value | n | Firms |
|---|---|---|---|---|---|---|
| Full sample | ROA | 0.00105 | 0.00329 | 0.750 | 2,230 | 150 |
| Full sample | ROE | 0.00147 | 0.02120 | 0.945 | 2,225 | 150 |
| Japan | ROA | 0.00298 | 0.00877 | 0.734 | 553 | 37 |
| Japan | ROE | 0.03576 | 0.04937 | 0.469 | 553 | 37 |
| China (incl. Hong Kong) | ROA | 0.00783 | 0.01352 | 0.563 | 352 | 24 |
| China (incl. Hong Kong) | ROE | 0.08102 | 0.03714 | 0.030 | 352 | 24 |
| Korea | ROA | 0.00293 | 0.00722 | 0.686 | 231 | 16 |
| Korea | ROE | 0.02159 | 0.05844 | 0.712 | 231 | 16 |
| Taiwan | ROA | 0.00181 | 0.00189 | 0.339 | 195 | 13 |
| Taiwan | ROE | −0.02069 | 0.02821 | 0.464 | 195 | 13 |
| India | ROA | 0.00550 | 0.01840 | 0.765 | 195 | 13 |
| India | ROE | −0.08920 | 0.10753 | 0.408 | 190 | 13 |
| ASEAN | ROA | −0.00238 | 0.00397 | 0.550 | 419 | 28 |
| ASEAN | ROE | −0.05578 | 0.05520 | 0.313 | 419 | 28 |
| West Asia / Middle East | ROA | −0.00361 | 0.00585 | 0.537 | 285 | 19 |
| West Asia / Middle East | ROE | −0.04189 | 0.04755 | 0.379 | 285 | 19 |

**Table 3b. Contemporaneous ESG FE coefficients by industry group.**

| Group | Outcome | β | SE | p-value | n | Firms |
|---|---|---|---|---|---|---|
| Full sample | ROA | 0.00105 | 0.00329 | 0.750 | 2,230 | 150 |
| Full sample | ROE | 0.00147 | 0.02120 | 0.945 | 2,225 | 150 |
| Banks | ROA | 0.00052 | 0.00191 | 0.785 | 1,445 | 97 |
| Banks | ROE | 0.01396 | 0.02168 | 0.520 | 1,445 | 97 |
| Insurance | ROA | 0.00342 | 0.00783 | 0.663 | 311 | 21 |
| Insurance | ROE | 0.01017 | 0.04405 | 0.818 | 306 | 21 |
| Other financials | ROA | −0.00235 | 0.01517 | 0.877 | 474 | 32 |
| Other financials | ROE | −0.00665 | 0.05066 | 0.896 | 474 | 32 |

Almost every subsample coefficient is statistically indistinguishable from zero, including Banks (the bulk of the sample) and Japan. No industry group shows any significant association, and outside the one exception below, no country group even approaches conventional significance (the next-smallest p-value in the heterogeneity results is 0.15, for lagged ESG → ROE in Japan; all other contemporaneous p-values exceed 0.31).

**Secondary finding: a positive contemporaneous ESG–ROE association in China (incl. Hong Kong).** The single exception to the null is the Greater China subsample (24 firms, 352 firm-years), where a one-point increase in a firm's ESG score is associated with a same-year increase of roughly **0.08 percentage points in pretax ROE** (β ≈ 0.081, SE ≈ 0.037, p ≈ 0.030) — equivalently, a 10-point ESG improvement corresponds to about +0.8 pp ROE. It is the only positive market-level signal in the sample and is consistent with the view that ESG performance carries more financial relevance in Chinese and Hong Kong-listed financials — for example through state-aligned policy incentives, green-finance mandates, or investor attention — than elsewhere in Asia over this period.

Several features nonetheless mark this as a suggestive rather than a confirmed result. The association appears only for ROE, not ROA (p ≈ 0.56), in the same group; it does not survive a one-year lag (p ≈ 0.45), so there is no evidence that ESG improvements *precede* the profitability gains; the specification's within-R² is negative (−0.14, i.e. no explanatory gain); and with roughly 40 subsample regressions estimated, about two significant results at the 5% level would be expected by chance alone. It is therefore reported as an exploratory, hypothesis-generating finding — a candidate for targeted future work on Greater China financials (e.g., with ESG pillar scores, ownership controls, or an event-study design around disclosure mandates) — rather than as a confirmed regional “ESG pays” effect.

### 4.3 Machine-learning models: no out-of-sample predictive power

Evaluated honestly out-of-sample (GroupKFold by firm), none of the three models can predict either financial metric from ESG (Table 4). **Every test R² is negative**, meaning the models predict worse than simply using the mean. The large gap between training R² (≈ 0.08–0.17) and test R² confirms that any in-sample fit is overfitting. This directly reverses earlier claims of near-perfect accuracy (R² ≈ 1.0), which were produced by evaluating models on their own training data.

**Table 4. Out-of-sample ML performance (GroupKFold by firm).**

| Outcome | Model | Test R² | Train R² | Test RMSE | Test MAE |
|---|---|---|---|---|---|
| ROA | XGBoost | −0.088 | 0.140 | 2.244 | 1.312 |
| ROA | Random Forest | −0.123 | 0.172 | 2.279 | 1.306 |
| ROA | Decision Tree | −0.219 | 0.119 | 2.339 | 1.328 |
| ROE | XGBoost | −0.020 | 0.114 | 9.118 | 6.792 |
| ROE | Random Forest | −0.006 | 0.125 | 9.058 | 6.725 |
| ROE | Decision Tree | −0.019 | 0.078 | 9.115 | 6.782 |

### 4.4 Illustrative forecast (2026–2030)

Using a linear-trend model on the annual median series, ESG is projected to continue rising while profitability drifts modestly lower (Table 5). These are illustrative sector-trend extrapolations with wide prediction intervals, based on only 15 annual points; they describe the continuation of past trends, not a causal consequence of ESG integration, and should not be read as an ESG-driven "steady state."

**Table 5. Linear-trend forecast with 95% prediction intervals.**

| Year | ESG (95% PI) | Pretax ROA %, (95% PI) | Pretax ROE %, (95% PI) |
|---|---|---|---|
| 2026 | 67.4 (57.8–77.0) | 1.14 (0.84–1.45) | 11.29 (9.03–13.56) |
| 2027 | 69.7 (59.9–79.6) | 1.12 (0.81–1.43) | 11.01 (8.69–13.33) |
| 2028 | 72.1 (62.0–82.2) | 1.10 (0.78–1.41) | 10.72 (8.34–13.10) |
| 2029 | 74.4 (64.0–84.8) | 1.07 (0.75–1.40) | 10.43 (8.00–12.87) |
| 2030 | 76.7 (66.1–87.4) | 1.05 (0.71–1.38) | 10.15 (7.64–12.65) |

### 4.5 Rolling correlations: stably weak, no turning point

Recomputed on firm-year data using observed values only, the rolling 5-year correlations are consistently weak throughout the period (Table 6): ESG–ROA stays close to zero and ESG–ROE remains mildly positive but small. There is **no** swing from strong negative to strong positive values. The earlier "cost-heavy negative phase → value-creation turning point" narrative was an artifact of correlating only 15 sector-average points and of extending the rolling windows into forecasted (rather than observed) values, which mechanically produced near-perfect correlations.

**Table 6. Rolling 5-year correlations (observed firm-year data only).**

| Window end year | ESG–ROA | ESG–ROE |
|---|---|---|
| 2015 | 0.018 | 0.138 |
| 2016 | 0.011 | 0.151 |
| 2017 | 0.021 | 0.172 |
| 2018 | 0.021 | 0.171 |
| 2019 | 0.022 | 0.174 |
| 2020 | 0.038 | 0.196 |
| 2021 | 0.054 | 0.204 |
| 2022 | 0.040 | 0.173 |
| 2023 | 0.042 | 0.180 |
| 2024 | 0.066 | 0.213 |
| 2025 | 0.075 | 0.221 |

### 4.6 Summary

Across every method — panel fixed-effects regression, country- and industry-group subsample FE, firm-year correlations, out-of-sample machine learning, and rolling-window analysis — the evidence points the same way: **once firm heterogeneity, common time shocks, and outliers are properly handled, there is no robust short-run within-firm association between ESG scores and pretax profitability for Asian BFSI firms in this sample.** Country and industry splits largely confirm the pooled null (Banks and Japan included); the one secondary finding — a positive contemporaneous ESG → ROE association in China (incl. Hong Kong), reported in §4.2.1 as exploratory and hypothesis-generating — does not overturn that pattern. The strong relationships and near-perfect predictions reported under the earlier sector-average methodology were artifacts of aggregation, in-sample evaluation, and a single distressed-firm outlier.
