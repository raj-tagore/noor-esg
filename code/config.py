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
    ("ESG_Score", "ESG Score"),
    ("Pretax_ROA", "Pretax ROA (%)"),
    ("Pretax_ROE", "Pretax ROE (%)"),
]

# --- Panel / inferential output filenames ---
PANEL_CSV = "banking_panel_long.csv"
PANEL_REGRESSION_CSV = "banking_panel_regression_results.csv"
PANEL_REGRESSION_ROA_TXT = "banking_panel_regression_roa_summary.txt"
PANEL_REGRESSION_ROE_TXT = "banking_panel_regression_roe_summary.txt"
MODEL_PERFORMANCE_CSV = "banking_model_performance.csv"
ROLLING_CORRELATIONS_CSV = "banking_rolling_correlations.csv"
PREDICTIONS_CSV = "banking_predictions_2026_2030.csv"
HISTORICAL_CSV = "banking_historical_data_2011_2025.csv"
