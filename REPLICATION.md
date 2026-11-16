# Replication guide

## 1. Create the environment

Use Python 3.9 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 2. Obtain restricted survey inputs

Request NFHS-4 and NFHS-5 individual and household files from IIPS or DHS. Place the authorized files at the paths listed in `DATA_AVAILABILITY.md`. These files must remain local.

## 3. Build analysis data

Run scripts from the repository root:

```bash
python scripts/01_build/build_nfhs_extracts.py
python scripts/01_build/build_rbi_statement16_2013.py
python scripts/01_build/build_census2011_district_population.py
python scripts/01_build/build_rbi_banking_baseline.py
python scripts/01_build/build_up_analysis.py
python scripts/01_build/build_multistate_pmmvy_analysis.py
```

To build the optional PhonePe Pulse district-quarter panel:

```bash
git clone --depth 1 https://github.com/PhonePe/pulse.git data/raw/phonepe_pulse
python scripts/01_build/build_phonepe_pulse_panel.py
```

The upstream clone is a replaceable source download and should not be committed to this repository.

Public source spreadsheets and PDFs must be downloaded to the paths referenced by the build scripts. See `docs/data_docs/dataset_manifest.csv` for the source list.

## 4. Run analyses

```bash
python scripts/02_analysis/run_pmmvy_national_did.py
python scripts/02_analysis/run_up_did_estimation.py
python scripts/02_analysis/run_mksy_girls_did.py
python scripts/02_analysis/run_national_crosssection.py
python scripts/02_analysis/run_study_b_district_expansion.py
python scripts/02_analysis/run_study_a_state_panel.py
python scripts/02_analysis/run_upi_dbt_event_study.py
```

Analysis tables are written to `results/tables/`.

## 5. Generate final figures

```bash
python scripts/03_figures/make_paper_figures_v3.py
python scripts/03_figures/make_figure3_1_pmmvy_intensity.py
python scripts/03_figures/make_spatial_maps.py
```

## 6. Build the downloadable working paper

Install Pandoc and a LaTeX distribution that provides LuaLaTeX, then run:

```bash
make paper
```

The PDF is written to `output/pdf/cash_transfers_banking_womens_financial_empowerment_india.pdf`.

## Reproducibility notes

- Run every command from the repository root.
- The authoritative national PMMVY estimates are in `results/tables/pmmvy_national_did_results.csv`.
- The consolidated paper is the authoritative narrative; older component write-ups should not be cited when they conflict with current tables.
- The UPI event-study source files are not currently present in the public-data layout. The resulting panel is included for inspection, but full source acquisition must be documented before claiming end-to-end replication of that extension.
