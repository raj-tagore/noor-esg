"""Shared configuration for the banking ESG analyses."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "Banking (ESG, RoE, RoA)-Final Clean Data.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"
EXPLORE_DIR = OUTPUT_DIR / "explore"

BASE_YEAR = 2025
FUTURE_YEARS = [2026, 2027, 2028, 2029, 2030]

# Collapse country/industry groups with fewer than this many distinct firms
# in multi-series and facet exploratory plots (full detail kept in count bars).
EXPLORE_MIN_FIRMS = 5

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

# --- Heterogeneity (country / industry subsample FE) ---
HETEROGENEITY_COUNTRY_CSV = "banking_heterogeneity_country.csv"
HETEROGENEITY_INDUSTRY_CSV = "banking_heterogeneity_industry.csv"
HETEROGENEITY_COUNTRY_FOREST_PNG = "banking_heterogeneity_country_forest.png"
HETEROGENEITY_INDUSTRY_FOREST_PNG = "banking_heterogeneity_industry_forest.png"

# Skip a subsample if below either threshold
HETERO_MIN_FIRMS = 10
HETERO_MIN_FIRMYEARS = 100

# Geography-first country groups (country_hq -> group label)
COUNTRY_GROUP_MAP = {
    "Japan": "Japan",
    "China": "China (incl. Hong Kong)",
    "Hong Kong": "China (incl. Hong Kong)",
    "Korea; Republic (S. Korea)": "Korea",
    "Taiwan": "Taiwan",
    "India": "India",
    "Malaysia": "ASEAN",
    "Indonesia": "ASEAN",
    "Thailand": "ASEAN",
    "Singapore": "ASEAN",
    "Philippines": "ASEAN",
    "Turkey": "West Asia / Middle East",
    "Israel": "West Asia / Middle East",
    "Kuwait": "West Asia / Middle East",
    "Jordan": "West Asia / Middle East",
    "Oman": "West Asia / Middle East",
    "Qatar": "West Asia / Middle East",
    "Saudi Arabia": "West Asia / Middle East",
}

# Industry groups (TRBC industry -> group label); unlisted -> Other financials
INSURANCE_INDUSTRIES = {
    "Life & Health Insurance",
    "Property & Casualty Insurance",
}
BANKS_INDUSTRY = "Banks"
INDUSTRY_GROUP_BANKS = "Banks"
INDUSTRY_GROUP_INSURANCE = "Insurance"
INDUSTRY_GROUP_OTHER = "Other financials"

# Display order for forest plots / tables
COUNTRY_GROUP_ORDER = [
    "Full sample",
    "Japan",
    "China (incl. Hong Kong)",
    "Korea",
    "Taiwan",
    "India",
    "ASEAN",
    "West Asia / Middle East",
]
INDUSTRY_GROUP_ORDER = [
    "Full sample",
    "Banks",
    "Insurance",
    "Other financials",
]
