"""Data loading and preprocessing utilities for the ESG banking dataset."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from config import (
    BASE_YEAR,
    COMPANY_COLUMNS,
    DATA_FILE,
    ESG_COLUMNS,
    OUTPUT_DIR,
    ROA_COLUMNS,
    ROE_COLUMNS,
)


@dataclass(frozen=True)
class BankingDataset:
    """Processed banking panel data used by the analysis scripts."""

    historical: pd.DataFrame
    company_info: pd.DataFrame
    years: list[int]
    esg_data: np.ndarray
    roa_data: np.ndarray
    roe_data: np.ndarray


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


def _chronological_year_indices(year_labels: list) -> tuple[list[int], list[int]]:
    years = [fiscal_year_to_year(label) for label in year_labels]
    valid_pairs = [(index, year) for index, year in enumerate(years) if year is not None]
    valid_pairs.sort(key=lambda item: item[1])
    return [index for index, _ in valid_pairs], [year for _, year in valid_pairs]


def _numeric_metric_matrix(data_rows: pd.DataFrame, column_slice: slice, indices: list[int]) -> np.ndarray:
    metric_data = data_rows.iloc[:, column_slice].apply(pd.to_numeric, errors="coerce").values
    return metric_data[:, indices]


def load_banking_dataset(path=DATA_FILE) -> BankingDataset:
    """Load, clean, and aggregate the banking ESG/ROA/ROE dataset."""

    df_raw = load_raw_dataset(path)
    year_labels = df_raw.iloc[1, ESG_COLUMNS].tolist()
    chronological_indices, years = _chronological_year_indices(year_labels)

    data_rows = df_raw.iloc[2:, :].reset_index(drop=True)
    company_info = data_rows.iloc[:, 0:5].copy()
    company_info.columns = COMPANY_COLUMNS

    esg_data = _numeric_metric_matrix(data_rows, ESG_COLUMNS, chronological_indices)
    roa_data = _numeric_metric_matrix(data_rows, ROA_COLUMNS, chronological_indices)
    roe_data = _numeric_metric_matrix(data_rows, ROE_COLUMNS, chronological_indices)

    historical = pd.DataFrame(
        {
            "Year": years,
            "ESG_Score": np.nanmean(esg_data, axis=0),
            "Pretax_ROA": np.nanmean(roa_data, axis=0) * 100,
            "Pretax_ROE": np.nanmean(roe_data, axis=0) * 100,
        }
    )

    return BankingDataset(
        historical=historical,
        company_info=company_info,
        years=years,
        esg_data=esg_data,
        roa_data=roa_data,
        roe_data=roe_data,
    )


def build_panel_dataset(path=DATA_FILE) -> pd.DataFrame:
    """
    Return a long-format firm-year panel:
    columns = [firm_id, company_name, country_hq, country_inc, industry,
               year, esg, roa, roe]

    One row per (firm, year). ~2,250 rows for 150 firms x 15 years.
    This is the dataset ALL statistical tests and models must use.

    The 15-row yearly-average table returned by load_banking_dataset() is
    for descriptive trend plots ONLY — never for inference.
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
    # (e.g. 0.017 meaning 1.7%). The existing load_banking_dataset()
    # multiplies the yearly means by 100. Apply the same ×100 here so
    # 'roa'/'roe' are in PERCENT throughout the codebase.
    panel["roa"] = panel["roa"] * 100
    panel["roe"] = panel["roe"] * 100

    # Drop rows with no usable data at all
    panel = panel.dropna(subset=["esg", "roa", "roe"], how="all")

    # Types
    panel["year"] = panel["year"].astype(int)
    return panel.sort_values(["firm_id", "year"]).reset_index(drop=True)

