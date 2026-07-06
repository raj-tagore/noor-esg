"""Data loading and preprocessing utilities for the ESG banking dataset."""

import pandas as pd

from config import (
    BASE_YEAR,
    DATA_FILE,
    ESG_COLUMNS,
    OUTPUT_DIR,
    ROA_COLUMNS,
    ROE_COLUMNS,
)


def ensure_output_dir() -> None:
    """Create the outputs directory used by the analysis scripts."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_dataset(path=DATA_FILE) -> pd.DataFrame:
    """Load the Excel workbook without promoting rows to headers."""

    return pd.read_excel(path, header=None)


def fiscal_year_to_year(label, base_year: int = BASE_YEAR) -> int | None:
    """Convert FY labels such as FY0 and FY-1 into calendar years."""

    if pd.isna(label):
        return None

    label_text = str(label).strip().upper()
    if label_text == "FY0":
        return base_year

    if label_text.startswith("FY-"):
        try:
            return base_year - int(label_text.replace("FY-", ""))
        except ValueError:
            return None

    return None


def build_panel_dataset(path=DATA_FILE) -> pd.DataFrame:
    """
    Return a long-format firm-year panel:
    columns = [firm_id, company_name, country_hq, country_inc, industry,
               year, esg, roa, roe]

    One row per (firm, year). ~2,250 rows for 150 firms x 15 years.
    This is the dataset ALL statistical tests and models must use.
    """
    df_raw = load_raw_dataset(path)

    # Year labels live in row index 1; data starts at row index 2.
    year_labels = df_raw.iloc[1, ESG_COLUMNS].tolist()
    years = [fiscal_year_to_year(lbl) for lbl in year_labels]  # e.g. [2025, 2024, ... 2011]

    data_rows = df_raw.iloc[2:, :].reset_index(drop=True)

    # Identifiers (columns 0..4)
    ids = data_rows.iloc[:, 0:5].copy()
    ids.columns = ["firm_id", "company_name", "country_hq", "country_inc", "industry"]

    # Numeric metric blocks → coerce to numeric so text/blank cells become NaN
    esg = data_rows.iloc[:, ESG_COLUMNS].apply(pd.to_numeric, errors="coerce")
    roa = data_rows.iloc[:, ROA_COLUMNS].apply(pd.to_numeric, errors="coerce")
    roe = data_rows.iloc[:, ROE_COLUMNS].apply(pd.to_numeric, errors="coerce")

    # Give every metric block the SAME column names = the calendar years,
    # so we can melt each to long and merge on (firm_id, year).
    esg.columns = roa.columns = roe.columns = years

    def _melt_metric(frame: pd.DataFrame, value_name: str) -> pd.DataFrame:
        m = frame.copy()
        m["firm_id"] = ids["firm_id"].values
        return m.melt(id_vars="firm_id", var_name="year", value_name=value_name)

    esg_long = _melt_metric(esg, "esg")
    roa_long = _melt_metric(roa, "roa")
    roe_long = _melt_metric(roe, "roe")

    panel = (
        esg_long
        .merge(roa_long, on=["firm_id", "year"])
        .merge(roe_long, on=["firm_id", "year"])
    )

    # Attach firm attributes (country, industry) back on
    panel = panel.merge(ids, on="firm_id", how="left")

    # Unit convention: in the wide data ROA/ROE are stored as fractions
    # (e.g. 0.017 meaning 1.7%). Apply ×100 so 'roa'/'roe' are in PERCENT
    # throughout the codebase.
    panel["roa"] = panel["roa"] * 100
    panel["roe"] = panel["roe"] * 100

    # Drop rows with no usable data at all
    panel = panel.dropna(subset=["esg", "roa", "roe"], how="all")

    # Types
    panel["year"] = panel["year"].astype(int)
    return panel.sort_values(["firm_id", "year"]).reset_index(drop=True)


def build_descriptive_stats(panel: pd.DataFrame) -> pd.DataFrame:
    """Per-year descriptive statistics from the firm-level panel.

    This is the ONLY sector-level aggregate kept in the pipeline: a plain
    mean/std/N table (not a chart, not correlated against a financial
    metric on a shared axis).
    """
    grouped = panel.groupby("year")
    stats = pd.DataFrame({
        "Year": grouped.size().index,
        "ESG_mean": grouped["esg"].mean().values,
        "ESG_std": grouped["esg"].std().values,
        "ROA_mean": grouped["roa"].mean().values,
        "ROA_std": grouped["roa"].std().values,
        "ROE_mean": grouped["roe"].mean().values,
        "ROE_std": grouped["roe"].std().values,
        "N_firms": grouped["firm_id"].nunique().values,
    })
    return stats.sort_values("Year").reset_index(drop=True)

