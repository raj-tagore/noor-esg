"""Shared configuration for the banking ESG analyses."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "Banking (ESG, RoE, RoA)-Final Clean Data.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"

BASE_YEAR = 2025
FUTURE_YEARS = [2026, 2027, 2028, 2029, 2030]

COMPANY_COLUMNS = ["RIC", "Company_Name", "Country_HQ", "Country_Inc", "Industry"]

ESG_COLUMNS = slice(5, 20)
ROA_COLUMNS = slice(20, 35)
ROE_COLUMNS = slice(35, 50)

METRICS = [
    ("esg", "ESG Score"),
    ("roa", "Pretax ROA (%)"),
    ("roe", "Pretax ROE (%)"),
]

# --- Panel / inferential output filenames ---
PANEL_CSV = "banking_panel_long.csv"
DESCRIPTIVE_STATS_CSV = "banking_descriptive_stats.csv"
PANEL_REGRESSION_CSV = "banking_panel_regression_results.csv"
PANEL_REGRESSION_ROA_TXT = "banking_panel_regression_roa_summary.txt"
PANEL_REGRESSION_ROE_TXT = "banking_panel_regression_roe_summary.txt"
ROLLING_CORRELATIONS_CSV = "banking_rolling_correlations.csv"
RELATIONSHIP_MODEL_PERF_CSV = "banking_relationship_model_performance.csv"
FORECAST_CSV = "banking_forecast_2026_2030.csv"
