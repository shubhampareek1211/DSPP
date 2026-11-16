# NFHS Processed Extracts

This folder contains the research-ready NFHS extracts for the India women financial inclusion project. The source files are:

- `NFHS-4 Individual`: `data/raw/nfhs4/IAIR74DT/IAIR74FL.DTA`
- `NFHS-4 Household`: `data/raw/nfhs4/IAHR74DT/IAHR74FL.DTA`
- `NFHS-5 Individual`: `data/raw/nfhs5/dta/IAIR7EFL.DTA`
- `NFHS-5 Household`: `data/raw/nfhs5/dta/IAHR7EFL.DTA`

These source files and respondent-level derived Parquet files require authorized access and are excluded from the public Git repository. See `DATA_AVAILABILITY.md`.

## Output files

| File | Rows | Columns | Purpose |
|---|---:|---:|---|
| `nfhs4_individual_raw_selected.parquet` | 699,686 | 42 | Raw selected woman-level variables from NFHS-4 using original variable names |
| `nfhs4_household_raw_selected.parquet` | 601,509 | 24 | Raw selected household variables from NFHS-4 using original variable names |
| `nfhs5_individual_raw_selected.parquet` | 724,115 | 50 | Raw selected woman-level variables from NFHS-5 using original variable names |
| `nfhs5_household_raw_selected.parquet` | 636,699 | 26 | Raw selected household variables from NFHS-5 using original variable names |
| `nfhs_individual_harmonized.parquet` | 1,423,801 | 53 | Combined NFHS-4 and NFHS-5 woman-level file with harmonized names |
| `nfhs_household_harmonized.parquet` | 1,238,208 | 29 | Combined NFHS-4 and NFHS-5 household file with harmonized names |
| `nfhs_variable_crosswalk.csv` | 142 mappings | 8 | Original variable name to harmonized variable name |
| `nfhs_harmonized_variable_availability.csv` | 74 variables | 5 | Shows whether each harmonized variable exists in NFHS-4, NFHS-5, or both |
| `nfhs_extract_manifest.csv` | 6 entries | 5 | Machine-readable file inventory |

## Recommended files for analysis

- Use `nfhs_individual_harmonized.parquet` for the main women-level analysis.
- Use `nfhs_household_harmonized.parquet` for household controls and household-level merges.
- Use the `*_raw_selected.parquet` files only if you need the original NFHS variable names.

## Location and merge keys

- Individual geography is harmonized to `state_code`, `district_code`, and `urban_rural`.
- Household geography is harmonized to `state_code`, `district_code`, and `urban_rural`.
- The main merge keys are `survey_round`, `cluster_number`, and `household_number`.
- `caseid` is preserved in the individual file and `hhid` is preserved in the household file.

## Safe cross-round variables

The following harmonized variables are available in both NFHS-4 and NFHS-5 and are the cleanest candidates for the core paper:

- `bank_account_self_use`
- `mobile_phone_self_use`
- `own_money_autonomy`
- `currently_working`
- `worked_last_12_months`
- `earnings_type`
- `decision_spend_earnings`
- `decision_health_care`
- `decision_large_purchases`
- `decision_daily_purchases`
- `decision_visits_relatives`
- `decision_husband_earnings`
- `loan_program_knowledge`
- `loan_program_taken`
- `delivery_financial_assistance_recent_birth`
- `days_to_jsy_assistance_recent_birth`
- `wealth_index`
- `health_insurance`

## NFHS-5-only variables

These exist only in NFHS-5 in the harmonized extract:

- `mobile_phone_ownership_any`
- `mobile_fin_transactions_any`
- `mobile_fin_transactions_self_use`
- `bank_account_any`
- `internet_use_any`
- `internet_use_frequency`
- `internet_ever_used_self_report`
- `wealth_index_urban_rural`
- `wealth_factor_score_urban_rural`

## Important harmonization caveat

Do not stack the raw `s*` variables by name across rounds. Some of those names were reused with different meanings.

Examples:

- `NFHS-4 s929` = bank or savings account respondent uses
- `NFHS-5 s929` = woman has money of her own that she alone decides how to use
- `NFHS-4 s933` = knows loan programme for women
- `NFHS-5 s933` = uses mobile phone for financial transactions

Use `nfhs_variable_crosswalk.csv` and the harmonized parquet files instead of matching raw `s*` variable names directly.
