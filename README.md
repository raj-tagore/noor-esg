# noor-esg

Firm-level panel analysis of **ESG scores vs corporate financial performance (Pretax ROA / Pretax ROE)** for Asian Banking, Financial Services, and Insurance (BFSI) firms, 2011–2025.

This repo contains:

1. **Python analysis code** (`code/`) that builds the panel, runs regressions / ML checks / heterogeneity, and writes figures and CSVs to `outputs/`.
2. **The research paper** as a Typst source file (`paper.typ`) that embeds those outputs and compiles to `paper.pdf`.
3. A prose summary of methods and results in [`Methodology_and_Results.md`](Methodology_and_Results.md) (useful when editing the paper).

If you are new to the project, start with **Inspecting the paper**, then **Setup**, then **Running the analysis**.

---

## Project layout (what lives where)

```text
noor-esg/
├── README.md                          ← you are here
├── Methodology_and_Results.md         ← methods/results write-up (source of truth for empirical claims)
├── paper.typ                          ← Typst paper source
├── paper.pdf                          ← compiled paper (regenerate after edits)
├── references.bib                     ← bibliography (APA citations via @keys in paper.typ)
├── Banking (ESG, RoE, RoA)-Final Clean Data.xlsx   ← raw input data (required)
├── pyproject.toml                     ← Python dependencies (managed by uv)
├── code/                              ← all analysis scripts
│   ├── run_all.py                     ← full inferential pipeline
│   ├── explore_dataset.py             ← exploratory sample atlas (not part of run_all)
│   ├── config.py                      ← paths, group maps, output filenames
│   ├── groups.py                      ← shared country/industry group assignment
│   └── ...                            ← see code/README.md for module list
└── outputs/                           ← generated CSVs and PNGs (safe to delete and regenerate)
    ├── explore/                       ← exploratory atlas figures
    ├── banking_*.csv / *.png          ← main analysis outputs
    └── ...
```

Notes for beginners:

- **Do not edit files under `outputs/` by hand.** Re-run the Python scripts; they overwrite those files.
- The paper (`paper.typ`) **reads images from `outputs/`** (for example `outputs/explore/08b_esg_vs_roa_by_country.png`). If a figure is missing, compile will fail until you regenerate it.
- Root `main.py` is a placeholder (`Hello from noor-esg!`) and is **not** part of the analysis. Use `code/run_all.py` instead.

---

## Inspecting the paper

### Read the PDF

Open [`paper.pdf`](paper.pdf) in any PDF viewer. That is the rendered paper.

### Edit the paper source

The editable source is [`paper.typ`](paper.typ). It is written in [Typst](https://typst.app/docs/) (similar idea to LaTeX, usually simpler).

Install the Typst CLI if you do not have it: https://github.com/typst/typst/releases  
(or `winget install --id Typst.Typst` on Windows if available).

From the **project root** (`noor-esg/`):

```powershell
typst compile paper.typ paper.pdf
```

Watch mode (recompiles when you save):

```powershell
typst watch paper.typ paper.pdf
```

### How citations work

- Bibliography entries live in [`references.bib`](references.bib).
- In the paper text, cite with `@friede2015` (and similar keys).
- The list at the end is produced by `#bibliography("references.bib", ...)` near the bottom of `paper.typ`.

### How figures are included

In `paper.typ`, figures look like:

```typst
#figure(
  image("outputs/explore/01_composition_country.png", width: 90%),
  caption: [...],
)
```

Paths are relative to the project root. After regenerating plots, recompile the PDF so the paper picks up new images.

### Where the empirical story is documented

- Short, precise methods/results narrative: [`Methodology_and_Results.md`](Methodology_and_Results.md)
- Deeper code notes: [`code/README.md`](code/README.md)

---

## Setup (first time)

### 1. Prerequisites

- **Python 3.14+** (see `.python-version`)
- **[uv](https://docs.astral.sh/uv/)** — recommended package/runner tool for this repo  
  Install: https://docs.astral.sh/uv/getting-started/installation/
- **Typst** — only needed to compile the paper (see above)
- The Excel data file must sit in the project root:  
  `Banking (ESG, RoE, RoA)-Final Clean Data.xlsx`  
  (path is set in `code/config.py` as `DATA_FILE`)

### 2. Install Python dependencies

From the project root:

```powershell
cd path\to\noor-esg
uv sync
```

This creates/updates `.venv` and installs packages listed in `pyproject.toml` (pandas, matplotlib, scikit-learn, xgboost, linearmodels, etc.).

### 3. Working directory convention

**Always run analysis scripts from the `code/` folder**, or invoke them as `uv run python code\...` from the project root.

The scripts import modules like `from config import ...`, so the `code/` directory needs to be on Python’s import path. Easiest options:

```powershell
# Option A — from project root (recommended with uv)
uv run python code\run_all.py

# Option B — cd into code, then run
cd code
uv run python run_all.py
```

---

## Running the analysis

### Full inferential pipeline (main results)

```powershell
uv run python code\run_all.py
```

This runs, in order:

1. **Relationship analysis** — panel fixed-effects (firm + year FE, clustered SE), firm-year correlations, rolling correlations, out-of-sample ML (XGBoost / Random Forest / Decision Tree with `GroupKFold` by firm), relationship plots  
2. **Heterogeneity** — same FE model within country groups and industry groups + forest plots  
3. **Trends / forecast** — per-year descriptive stats + illustrative linear-trend forecast to 2026–2030 (with prediction intervals)

Outputs go to `outputs/`.

### Exploratory sample atlas (separate)

Not included in `run_all.py`. Run when you want composition / coverage / distribution / faceted ESG–ROA plots:

```powershell
uv run python code\explore_dataset.py
```

Outputs go to `outputs/explore/`.

### Run pieces individually

```powershell
uv run python code\relationship_analysis.py
uv run python code\heterogeneity.py
uv run python code\trend_analysis.py
uv run python code\explore_dataset.py
```

### Typical “I changed something” workflow

1. Edit code or `config.py` (groups, thresholds, paths).
2. Re-run the relevant script(s), or `run_all.py` + `explore_dataset.py` if unsure.
3. Open the new CSVs/PNGs under `outputs/` to sanity-check.
4. If the paper should show the new figures/numbers, update `paper.typ` if needed, then:

```powershell
typst compile paper.typ paper.pdf
```

---

## Where outputs are located

### Main analysis — `outputs/`

| File | What it is |
|------|------------|
| `banking_panel_long.csv` | Firm-year panel (~2,250 rows): ESG, ROA, ROE, firm/country/industry |
| `banking_panel_regression_results.csv` | Headline FE coefficients (contemp. + lagged ESG → ROA/ROE) |
| `banking_panel_regression_roa_summary.txt` | Full text summary for ROA FE model |
| `banking_panel_regression_roe_summary.txt` | Full text summary for ROE FE model |
| `banking_correlation_results.csv` | Pooled firm-year ESG–ROA / ESG–ROE correlations |
| `banking_rolling_correlations.csv` | Rolling 5-year correlations (observed firm-years only) |
| `banking_relationship_model_performance.csv` | ML out-of-sample metrics (test/train R², RMSE, MAE) |
| `banking_esg_relationship_analysis.png` | Multi-panel relationship / trends dashboard |
| `banking_detailed_relationship.png` | Detailed firm-year relationship diagnostics |
| `banking_heterogeneity_country.csv` | FE results by country group |
| `banking_heterogeneity_industry.csv` | FE results by industry group |
| `banking_heterogeneity_country_forest.png` | Forest plot — country groups |
| `banking_heterogeneity_industry_forest.png` | Forest plot — industry groups |
| `banking_descriptive_stats.csv` | Per-year means/medians/SDs (descriptive only) |
| `banking_forecast_2026_2030.csv` | Illustrative OLS trend forecast + 95% PIs |
| `banking_forecast_2026_2030.png` | Forecast chart |

### Exploratory atlas — `outputs/explore/`

| File | What it is |
|------|------------|
| `01_composition_country.png` | Distinct firms by raw `country_hq` |
| `02_composition_industry_heatmap.png` | Industry bars + country-group × industry-group heatmap |
| `03_coverage_over_time.png` | Non-null ESG/ROA/ROE counts by year |
| `04_coverage_by_country.png` | Coverage / ESG history depth by **analysis** country group |
| `05_univariate_distributions.png` | Histograms/KDEs of ESG, ROA, ROE |
| `06_distributions_by_group.png` | Box plots by analysis country / industry groups |
| `07_median_trajectories_by_group.png` | Median ESG over time by group |
| `08a_esg_vs_roa_by_industry.png` | ESG vs ROA facets by industry group |
| `08b_esg_vs_roa_by_country.png` | ESG vs ROA facets by country group |
| `panel_composition_summary.csv` | Firm and firm-year counts (raw + analysis groups) |

**Important:** Explore multi-series / facet plots use the **same country and industry groups** as the heterogeneity regressions (defined in `code/config.py` and applied in `code/groups.py`). There is no separate “Other” bin for rare countries in those plots.

---

## How to make common changes

### Change country or industry groupings

1. Edit maps in [`code/config.py`](code/config.py):
   - `COUNTRY_GROUP_MAP` — maps each raw `country_hq` string → analysis group label  
   - `INSURANCE_INDUSTRIES` / `BANKS_INDUSTRY` — industry grouping rules  
   - `COUNTRY_GROUP_ORDER` / `INDUSTRY_GROUP_ORDER` — display order in tables/plots  
2. Every raw headquarters country in the data must appear in `COUNTRY_GROUP_MAP` (no anonymous leftover bin).  
3. Re-run:

```powershell
uv run python code\explore_dataset.py
uv run python code\heterogeneity.py
```

(or full `run_all.py` if you also want headline results refreshed).

4. Update any tables/prose in `paper.typ` / `Methodology_and_Results.md` if group labels or membership changed.
5. Recompile the PDF.

### Change sample filters / winsorization / data path

- Data path and column layout: `code/config.py` (`DATA_FILE`, `ESG_COLUMNS`, …)
- Panel construction and winsorization: `code/data_processing.py` (`build_panel_dataset`)
- Heterogeneity minimum sample size: `HETERO_MIN_FIRMS`, `HETERO_MIN_FIRMYEARS` in `config.py`

After changing these, re-run `run_all.py` and `explore_dataset.py`.

### Change a plot’s look

- Explore atlas: `code/explore_plots.py`
- Relationship dashboards: `code/relationship_plots.py`
- Forecast chart: `code/trend_plots.py`
- Forest plots: `code/heterogeneity_plots.py`

Then re-run the script that calls that plot module and recompile the paper if the figure is embedded.

### Change paper text or tables

- Edit [`paper.typ`](paper.typ)
- Keep numbers consistent with CSVs under `outputs/` (or with [`Methodology_and_Results.md`](Methodology_and_Results.md))
- Run `typst compile paper.typ paper.pdf`

### Add a bibliography entry

1. Add a BibTeX entry to `references.bib` with a unique key (e.g. `smith2024`).
2. Cite it in `paper.typ` as `@smith2024`.
3. Recompile.

---

## Mental model of the analysis (short)

```text
Excel (wide, firm × years)
        │
        ▼
build_panel_dataset()   →  long firm-year panel  →  banking_panel_long.csv
        │
        ├─► Panel FE (firm + year)     →  headline null result
        ├─► Same FE by country/industry groups  →  heterogeneity (+ China/HK note)
        ├─► ML with GroupKFold by firm →  negative test R² (no predictive signal)
        ├─► Rolling correlations on firm-years →  stably weak
        └─► Annual medians (descriptive only) + OLS trend →  illustrative 2026–2030 forecast

Explore atlas (separate) →  understand sample composition; not used for inference
```

Design rule of this codebase: **inference uses the firm-year panel**, not sector averages of ESG plotted against sector averages of ROA/ROE. Annual aggregates are for description/context only.

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| `ModuleNotFoundError: config` / similar | Run via `uv run python code\...` from project root, or `cd code` first |
| `FileNotFoundError` for the Excel file | Confirm the `.xlsx` is in the project root and matches `DATA_FILE` in `config.py` |
| Typst error: image not found | Run `explore_dataset.py` and/or `run_all.py` so `outputs/` is populated |
| uv / Python version errors | Ensure Python ≥ 3.14 and run `uv sync` from the project root |
| Groups error: `Unmapped country_hq=...` | Add that country string to `COUNTRY_GROUP_MAP` in `config.py` |
| Plots look stale in the PDF | Re-run the Python script, then `typst compile paper.typ paper.pdf` again |

---

## Quick command cheat sheet

```powershell
# Setup (once)
uv sync

# Analysis
uv run python code\run_all.py
uv run python code\explore_dataset.py

# Paper
typst compile paper.typ paper.pdf
typst watch paper.typ paper.pdf
```

For module-by-module detail inside the analysis package, see [`code/README.md`](code/README.md).
