# RBI Processed Extracts

This folder contains cleaned RBI district banking extracts for the India women financial inclusion project.

## Recommended file

- `rbi_district_baseline_dec_2013.csv`

This is the best pre-treatment district baseline currently available in the project. It comes from RBI Statement 16 and includes district-level totals across all bank groups for:

- `reporting_offices_total`
- `deposits_total_million_rs`
- `credit_total_million_rs`
- converted crore fields:
  - `deposits_total_crore_rs`
  - `credit_total_crore_rs`

## Output files

| File | Rows | Purpose |
|---|---:|---|
| `rbi_district_baseline_dec_2013.csv` | 656 | Recommended pre-treatment district baseline |
| `rbi_district_baseline_sep_2013.csv` | 654 | Supplementary September 2013 baseline |
| `rbi_district_baseline_2013_snapshots.csv` | 1,310 | Combined September and December 2013 district totals |
| `rbi_district_bankgroup_2013_snapshots.csv` | 1,304 | District-level wide file with separate bank-group fields |
| `rbi_statement16_2013_bankgroup_long.csv` | 8,250 | Long bank-group-level raw cleaned extract |
| `rbi_statement16_2013_manifest.csv` | 5 | Machine-readable file manifest |

## Variables to use in the paper

Use these as baseline banking-access measures:

- `reporting_offices_total`
- `branch_density_2013 = reporting_offices_total / district_population`
- optionally:
  - `deposits_total_crore_rs`
  - `credit_total_crore_rs`
  - `deposits_per_capita_2013`
  - `credit_per_capita_2013`

## Notes

- District names are preserved in `district_name_raw` and normalized in `district_name_clean`.
- State names are preserved in `state_name_raw` and normalized in `state_name_clean`.
- The cleaner repairs a small source-workbook anomaly in a few December 2013 rows where new-private-bank values shift left because of a missing old-private-bank credit cell.
- State-total rows remain in the long raw extract, but the recommended district baseline files exclude all-India aggregate rows.
