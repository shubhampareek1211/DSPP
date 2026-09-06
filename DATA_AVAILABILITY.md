# Data availability

This repository separates public aggregate inputs from restricted respondent-level microdata.

## Not redistributed

NFHS-4 and NFHS-5 individual and household microdata are not included. Researchers must request access from the official IIPS or DHS distribution channel and accept the applicable terms. Do not commit the original survey files, selected respondent extracts, or analysis-ready respondent-level Parquet files.

Expected local inputs after authorized download:

- `data/raw/nfhs4/IAIR74DT/IAIR74FL.DTA`
- `data/raw/nfhs4/IAHR74DT/IAHR74FL.DTA`
- `data/raw/nfhs5/dta/IAIR7EFL.DTA`
- `data/raw/nfhs5/dta/IAHR7EFL.DTA`

The build scripts write restricted derived files under `data/processed/nfhs/`; those files are ignored by Git.

## Public aggregate data

Small public or derived aggregate CSV files used by the analysis are retained under `data/processed/`. They cover IIPS district indicators, Census 2011 population, RBI banking measures, PMMVY program intensity, and geographic crosswalks.

Large reports, source spreadsheets, and shapefiles are not intended for Git history. Their source information belongs in `docs/data_docs/dataset_manifest.csv`, including the provider, URL, access date, and any transformation notes.

## PhonePe Pulse

PhonePe Pulse data should be downloaded from <https://github.com/PhonePe/pulse>. It is platform-level aggregate data, not gender-disaggregated transaction data. Any analysis must describe it as PhonePe activity rather than total UPI or women's individual payment activity.
