# ESG-CFP Analysis Code

Panel-based ESG-to-financial-performance analysis pipeline for the Asian banking sector (2011-2025, 150 firms, 15 years).

## Design

All findings derive from the **firm-level panel** (~2,250 firm-year rows) built by `build_panel_dataset()`. There is no sector-average aggregate used for inference anywhere in this codebase:

1. **Panel fixed-effects regression** (firm + year FE, clustered SE) is the headline result.
2. **Out-of-sample ML evaluation** (GroupKFold by firm) reports test-set R2, never in-sample R2.
3. **Rolling correlations** are computed on the panel, using observed data only.
4. **Firm-year scatter plots** and residual diagnostics visualize the panel relationship directly.

The one sector-level output kept is a **descriptive statistics table** (`banking_descriptive_stats.csv`): per-year mean/std/N of ESG, ROA, and ROE, computed by grouping the panel by year. It is a table, not a chart, and never puts ESG and a financial metric on a shared axis.

The one forecasting method kept is an **illustrative linear-trend (OLS) projection** to 2030 with prediction intervals (`forecasting.py`), computed on the 15 annual descriptive means. It is explicitly labelled as a wide-uncertainty, sector-level projection — not a firm-level or causal estimate. There is no tree-model (XGBoost/Random Forest/Decision Tree) forecasting anywhere; those models are used only for the out-of-sample ESG->ROA/ROE relationship evaluation in `models.py`, where they are properly cross-validated.

## Files

- `config.py`: shared paths, column ranges, and output filenames.
- `data_processing.py`: Excel loading, FY label conversion, `build_panel_dataset()` (the firm-level panel), and `build_descriptive_stats()` (per-year mean/std/N).
- `panel_regression.py`: panel fixed-effects regressions (headline results).
- `models.py`: out-of-sample ESG->ROA/ROE model evaluation (GroupKFold by firm).
- `forecasting.py`: illustrative OLS linear-trend forecast with prediction intervals.
- `relationship_analysis.py`: panel-based ESG-financial relationship analysis (regressions, ML evaluation, correlations, rolling correlations).
- `relationship_plots.py`: visualizations for the panel-based relationship analysis (7-panel dashboard + residual diagnostics).
- `trend_analysis.py`: descriptive stats + illustrative linear-trend forecast.
- `trend_plots.py`: the single forecast chart (observed mean + linear trend + prediction band, per metric).
- `explore_dataset.py`: lightweight dataset inspection script.
- `run_all.py`: runs the full pipeline.

## Usage

Install `uv` if needed: https://docs.astral.sh/uv/getting-started/installation/

From the project root, use `uv run` to execute any script:

```powershell
uv run python code\run_all.py
uv run python code\relationship_analysis.py
uv run python code\trend_analysis.py
```

For a quick dataset inspection:

```powershell
uv run python code\explore_dataset.py
```

## Key Output Files

| File | Description |
|------|-------------|
| `banking_panel_long.csv` | Firm-level panel dataset (~2,250 rows) |
| `banking_panel_regression_results.csv` | Fixed-effects regression results (headline) |
| `banking_panel_regression_roa_summary.txt` | Full ROA regression model summary |
| `banking_panel_regression_roe_summary.txt` | Full ROE regression model summary |
| `banking_correlation_results.csv` | Panel firm-year correlations |
| `banking_rolling_correlations.csv` | Rolling correlations (panel, observed only) |
| `banking_relationship_model_performance.csv` | ML out-of-sample performance |
| `banking_descriptive_stats.csv` | Per-year ESG/ROA/ROE mean, std, N (the only descriptive aggregate) |
| `banking_forecast_2026_2030.csv` | Illustrative linear-trend forecast with prediction intervals |

Generated CSV and image outputs are written to the `outputs/` directory.
