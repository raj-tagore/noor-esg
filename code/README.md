# ESG-CFP Analysis Code (Corrected)

This directory contains the corrected, panel-based ESG-to-financial-performance analysis pipeline for the Asian banking sector (2011-2025, 150 firms, 15 years).

## Key Corrections

1. **Firm-level panel dataset** (~2,250 rows) replaces the 15-row yearly aggregate for all inference.
2. **Panel fixed-effects regression** (firm + year FE, clustered SE) replaces spurious aggregate correlations.
3. **Out-of-sample validation** (GroupKFold by firm) replaces in-sample R2 reporting.
4. **Linear trend forecasts** with prediction intervals replace tree-based extrapolation artifacts.
5. **Rolling correlations** use observed panel data only (no forecast contamination).

## Files

- `config.py`: shared paths, column ranges, output locations, and constants.
- `data_processing.py`: Excel loading, FY label conversion, and both:
  - `build_panel_dataset()` — firm-level panel for inference (~2,250 rows)
  - `load_banking_dataset()` — sector-level yearly means for descriptive plots only
- `panel_regression.py`: **NEW** — panel fixed-effects regressions (headline results).
- `forecasting.py`: **NEW** — OLS linear-trend forecasts with prediction intervals.
- `models.py`: ML model training with out-of-sample evaluation (GroupKFold, TimeSeriesSplit).
- `trend_analysis.py`: descriptive sector-average trend analysis and forecasts.
- `relationship_analysis.py`: panel-based ESG-financial relationship analysis.
- `trend_plots.py`: visualizations for historical trends and forecasts.
- `relationship_plots.py`: visualizations for ESG-to-financial KPI relationships.
- `explore_dataset.py`: lightweight dataset inspection script.
- `run_all.py`: runs the full pipeline.

## Usage

Install `uv` if needed: https://docs.astral.sh/uv/getting-started/installation/

From the project root, use `uv run` to execute any script:

```powershell
uv run python code\run_all.py
uv run python code\trend_analysis.py
uv run python code\relationship_analysis.py
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
| `banking_correlation_results.csv` | Panel + descriptive correlations |
| `banking_rolling_correlations.csv` | Rolling correlations (panel, observed only) |
| `banking_relationship_model_performance.csv` | ML out-of-sample performance |
| `banking_historical_data_2011_2025.csv` | Sector-average historical data (descriptive) |
| `banking_predictions_2026_2030.csv` | Forecasts with prediction intervals |
| `banking_model_performance.csv` | Time-series model performance (train vs test) |

Generated CSV and image outputs are written to the `outputs/` directory.
