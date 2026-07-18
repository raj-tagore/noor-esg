"""Shared country / industry group assignment for explore and heterogeneity."""

from __future__ import annotations

import pandas as pd

from config import (
    BANKS_INDUSTRY,
    COUNTRY_GROUP_MAP,
    INDUSTRY_GROUP_BANKS,
    INDUSTRY_GROUP_INSURANCE,
    INDUSTRY_GROUP_OTHER,
    INSURANCE_INDUSTRIES,
)


def assign_country_group(country_hq: str) -> str:
    if pd.isna(country_hq):
        raise ValueError("Missing country_hq; cannot assign country group")
    key = str(country_hq).strip()
    if key not in COUNTRY_GROUP_MAP:
        raise ValueError(
            f"Unmapped country_hq={key!r}. Add an explicit regional group in "
            "config.COUNTRY_GROUP_MAP (no anonymous Other bin)."
        )
    return COUNTRY_GROUP_MAP[key]


def assign_industry_group(industry: str) -> str:
    if pd.isna(industry):
        return INDUSTRY_GROUP_OTHER
    name = str(industry).strip()
    if name == BANKS_INDUSTRY:
        return INDUSTRY_GROUP_BANKS
    if name in INSURANCE_INDUSTRIES:
        return INDUSTRY_GROUP_INSURANCE
    return INDUSTRY_GROUP_OTHER


def add_group_columns(panel: pd.DataFrame) -> pd.DataFrame:
    """Attach country_group and industry_group columns used in FE subsample analysis."""

    out = panel.copy()
    out["country_group"] = out["country_hq"].map(assign_country_group)
    out["industry_group"] = out["industry"].map(assign_industry_group)
    return out
