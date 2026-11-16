from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List
import warnings

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "nfhs"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


DATASETS = {
    "nfhs4_individual": {
        "survey_round": "NFHS-4",
        "survey_year_start": 2015,
        "survey_year_end": 2016,
        "level": "individual",
        "source_path": PROJECT_ROOT / "data" / "raw" / "nfhs4" / "IAIR74DT" / "IAIR74FL.DTA",
        "inventory_path": PROJECT_ROOT / "docs" / "data_docs" / "nfhs4_variable_inventory_individual.csv",
        "wanted_columns": [
            "caseid",
            "v001",
            "v002",
            "v003",
            "v005",
            "v006",
            "v007",
            "v024",
            "v025",
            "sdistri",
            "v012",
            "v106",
            "v130",
            "v714",
            "v716",
            "v717",
            "v719",
            "v721",
            "v731",
            "v739",
            "v741",
            "v743a",
            "v743b",
            "v743c",
            "v743d",
            "v743f",
            "v746",
            "v190",
            "v481",
            "ssmod",
            "sv005",
            "sd005",
            "s190s",
            "s190us",
            "s190rs",
            "s927",
            "s929",
            "s930",
            "s933",
            "s934",
            "s452_1",
            "s454_1",
        ],
    },
    "nfhs4_household": {
        "survey_round": "NFHS-4",
        "survey_year_start": 2015,
        "survey_year_end": 2016,
        "level": "household",
        "source_path": PROJECT_ROOT / "data" / "raw" / "nfhs4" / "IAHR74DT" / "IAHR74FL.DTA",
        "inventory_path": PROJECT_ROOT / "docs" / "data_docs" / "nfhs4_variable_inventory_household.csv",
        "wanted_columns": [
            "hhid",
            "hv001",
            "hv002",
            "hv005",
            "hv006",
            "hv007",
            "hv024",
            "hv025",
            "shdistri",
            "shv005",
            "hv206",
            "hv221",
            "hv243a",
            "hv247",
            "sh37n",
            "hv270",
            "hv271",
            "hv201",
            "hv204",
            "hv205",
            "hv225",
            "sv270s",
            "sv270us",
            "sv270rs",
        ],
    },
    "nfhs5_individual": {
        "survey_round": "NFHS-5",
        "survey_year_start": 2019,
        "survey_year_end": 2021,
        "level": "individual",
        "source_path": PROJECT_ROOT / "data" / "raw" / "nfhs5" / "dta" / "IAIR7EFL.DTA",
        "inventory_path": PROJECT_ROOT / "docs" / "data_docs" / "nfhs5_variable_inventory_individual.csv",
        "wanted_columns": [
            "caseid",
            "v001",
            "v002",
            "v003",
            "v005",
            "v006",
            "v007",
            "v024",
            "v025",
            "sdist",
            "v012",
            "v106",
            "v130",
            "v169a",
            "v169b",
            "v170",
            "v171a",
            "v171b",
            "v714",
            "v716",
            "v717",
            "v719",
            "v721",
            "v731",
            "v739",
            "v741",
            "v743a",
            "v743b",
            "v743c",
            "v743d",
            "v743f",
            "v746",
            "v190",
            "v190a",
            "v481",
            "ssmod",
            "sweight",
            "sdweight",
            "s190s",
            "s190us",
            "s190rs",
            "s929",
            "s931",
            "s932",
            "s933",
            "s934",
            "s940",
            "s941",
            "s457_1",
            "s459_1",
        ],
    },
    "nfhs5_household": {
        "survey_round": "NFHS-5",
        "survey_year_start": 2019,
        "survey_year_end": 2021,
        "level": "household",
        "source_path": PROJECT_ROOT / "data" / "raw" / "nfhs5" / "dta" / "IAHR7EFL.DTA",
        "inventory_path": PROJECT_ROOT / "docs" / "data_docs" / "nfhs5_variable_inventory_household.csv",
        "wanted_columns": [
            "hhid",
            "hv001",
            "hv002",
            "hv005",
            "hv006",
            "hv007",
            "hv024",
            "hv025",
            "shdist",
            "shweight",
            "hv206",
            "hv221",
            "hv243a",
            "hv247",
            "sh50n",
            "hv270",
            "hv270a",
            "hv271",
            "hv271a",
            "hv201",
            "hv204",
            "hv205",
            "hv225",
            "sv270s",
            "sv270us",
            "sv270rs",
        ],
    },
}


INDIVIDUAL_HARMONIZED_COLUMNS = [
    "survey_round",
    "survey_year_start",
    "survey_year_end",
    "caseid",
    "cluster_number",
    "household_number",
    "respondent_line",
    "woman_weight",
    "interview_month",
    "interview_year",
    "state_code",
    "district_code",
    "urban_rural",
    "age",
    "education_level",
    "religion",
    "currently_working",
    "occupation_code",
    "occupation_grouped",
    "work_for_whom",
    "work_location",
    "worked_last_12_months",
    "decision_spend_earnings",
    "earnings_type",
    "decision_health_care",
    "decision_large_purchases",
    "decision_daily_purchases",
    "decision_visits_relatives",
    "decision_husband_earnings",
    "relative_earnings_vs_husband",
    "wealth_index",
    "wealth_index_urban_rural",
    "health_insurance",
    "selected_state_module",
    "state_module_weight",
    "domestic_violence_weight",
    "wealth_within_state",
    "wealth_within_state_urban",
    "wealth_within_state_rural",
    "own_money_autonomy",
    "bank_account_self_use",
    "mobile_phone_self_use",
    "mobile_fin_transactions_self_use",
    "internet_ever_used_self_report",
    "loan_program_knowledge",
    "loan_program_taken",
    "delivery_financial_assistance_recent_birth",
    "days_to_jsy_assistance_recent_birth",
    "mobile_phone_ownership_any",
    "mobile_fin_transactions_any",
    "bank_account_any",
    "internet_use_any",
    "internet_use_frequency",
]


HOUSEHOLD_HARMONIZED_COLUMNS = [
    "survey_round",
    "survey_year_start",
    "survey_year_end",
    "hhid",
    "cluster_number",
    "household_number",
    "household_weight",
    "interview_month",
    "interview_year",
    "state_code",
    "district_code",
    "urban_rural",
    "state_household_weight",
    "electricity",
    "landline_telephone",
    "mobile_telephone",
    "bank_account",
    "household_internet",
    "wealth_index",
    "wealth_index_urban_rural",
    "wealth_factor_score",
    "wealth_factor_score_urban_rural",
    "drinking_water_source",
    "minutes_to_water_source",
    "toilet_facility",
    "toilet_shared",
    "wealth_within_state",
    "wealth_within_state_urban",
    "wealth_within_state_rural",
]


INDIVIDUAL_RENAME = {
    "nfhs4": {
        "caseid": "caseid",
        "v001": "cluster_number",
        "v002": "household_number",
        "v003": "respondent_line",
        "v005": "woman_weight",
        "v006": "interview_month",
        "v007": "interview_year",
        "v024": "state_code",
        "sdistri": "district_code",
        "v025": "urban_rural",
        "v012": "age",
        "v106": "education_level",
        "v130": "religion",
        "v714": "currently_working",
        "v716": "occupation_code",
        "v717": "occupation_grouped",
        "v719": "work_for_whom",
        "v721": "work_location",
        "v731": "worked_last_12_months",
        "v739": "decision_spend_earnings",
        "v741": "earnings_type",
        "v743a": "decision_health_care",
        "v743b": "decision_large_purchases",
        "v743c": "decision_daily_purchases",
        "v743d": "decision_visits_relatives",
        "v743f": "decision_husband_earnings",
        "v746": "relative_earnings_vs_husband",
        "v190": "wealth_index",
        "v481": "health_insurance",
        "ssmod": "selected_state_module",
        "sv005": "state_module_weight",
        "sd005": "domestic_violence_weight",
        "s190s": "wealth_within_state",
        "s190us": "wealth_within_state_urban",
        "s190rs": "wealth_within_state_rural",
        "s927": "own_money_autonomy",
        "s929": "bank_account_self_use",
        "s930": "mobile_phone_self_use",
        "s933": "loan_program_knowledge",
        "s934": "loan_program_taken",
        "s452_1": "delivery_financial_assistance_recent_birth",
        "s454_1": "days_to_jsy_assistance_recent_birth",
    },
    "nfhs5": {
        "caseid": "caseid",
        "v001": "cluster_number",
        "v002": "household_number",
        "v003": "respondent_line",
        "v005": "woman_weight",
        "v006": "interview_month",
        "v007": "interview_year",
        "v024": "state_code",
        "sdist": "district_code",
        "v025": "urban_rural",
        "v012": "age",
        "v106": "education_level",
        "v130": "religion",
        "v169a": "mobile_phone_ownership_any",
        "v169b": "mobile_fin_transactions_any",
        "v170": "bank_account_any",
        "v171a": "internet_use_any",
        "v171b": "internet_use_frequency",
        "v714": "currently_working",
        "v716": "occupation_code",
        "v717": "occupation_grouped",
        "v719": "work_for_whom",
        "v721": "work_location",
        "v731": "worked_last_12_months",
        "v739": "decision_spend_earnings",
        "v741": "earnings_type",
        "v743a": "decision_health_care",
        "v743b": "decision_large_purchases",
        "v743c": "decision_daily_purchases",
        "v743d": "decision_visits_relatives",
        "v743f": "decision_husband_earnings",
        "v746": "relative_earnings_vs_husband",
        "v190": "wealth_index",
        "v190a": "wealth_index_urban_rural",
        "v481": "health_insurance",
        "ssmod": "selected_state_module",
        "sweight": "state_module_weight",
        "sdweight": "domestic_violence_weight",
        "s190s": "wealth_within_state",
        "s190us": "wealth_within_state_urban",
        "s190rs": "wealth_within_state_rural",
        "s929": "own_money_autonomy",
        "s931": "bank_account_self_use",
        "s932": "mobile_phone_self_use",
        "s933": "mobile_fin_transactions_self_use",
        "s934": "internet_ever_used_self_report",
        "s940": "loan_program_knowledge",
        "s941": "loan_program_taken",
        "s457_1": "delivery_financial_assistance_recent_birth",
        "s459_1": "days_to_jsy_assistance_recent_birth",
    },
}


HOUSEHOLD_RENAME = {
    "nfhs4": {
        "hhid": "hhid",
        "hv001": "cluster_number",
        "hv002": "household_number",
        "hv005": "household_weight",
        "hv006": "interview_month",
        "hv007": "interview_year",
        "hv024": "state_code",
        "shdistri": "district_code",
        "hv025": "urban_rural",
        "shv005": "state_household_weight",
        "hv206": "electricity",
        "hv221": "landline_telephone",
        "hv243a": "mobile_telephone",
        "hv247": "bank_account",
        "sh37n": "household_internet",
        "hv270": "wealth_index",
        "hv271": "wealth_factor_score",
        "hv201": "drinking_water_source",
        "hv204": "minutes_to_water_source",
        "hv205": "toilet_facility",
        "hv225": "toilet_shared",
        "sv270s": "wealth_within_state",
        "sv270us": "wealth_within_state_urban",
        "sv270rs": "wealth_within_state_rural",
    },
    "nfhs5": {
        "hhid": "hhid",
        "hv001": "cluster_number",
        "hv002": "household_number",
        "hv005": "household_weight",
        "hv006": "interview_month",
        "hv007": "interview_year",
        "hv024": "state_code",
        "shdist": "district_code",
        "hv025": "urban_rural",
        "shweight": "state_household_weight",
        "hv206": "electricity",
        "hv221": "landline_telephone",
        "hv243a": "mobile_telephone",
        "hv247": "bank_account",
        "sh50n": "household_internet",
        "hv270": "wealth_index",
        "hv270a": "wealth_index_urban_rural",
        "hv271": "wealth_factor_score",
        "hv271a": "wealth_factor_score_urban_rural",
        "hv201": "drinking_water_source",
        "hv204": "minutes_to_water_source",
        "hv205": "toilet_facility",
        "hv225": "toilet_shared",
        "sv270s": "wealth_within_state",
        "sv270us": "wealth_within_state_urban",
        "sv270rs": "wealth_within_state_rural",
    },
}


def read_inventory(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def keep_available_columns(wanted: Iterable[str], inventory: pd.DataFrame) -> List[str]:
    available = set(inventory["variable"].astype(str))
    return [column for column in wanted if column in available]


def load_selected_stata(path: Path, columns: List[str]) -> pd.DataFrame:
    print(f"Reading {path.name} with {len(columns)} selected columns")
    chunks = pd.read_stata(path, columns=columns, convert_categoricals=False, chunksize=100_000)
    out = []
    total_rows = 0
    for i, chunk in enumerate(chunks, start=1):
        total_rows += len(chunk)
        print(f"  chunk {i}: cumulative rows {total_rows:,}")
        out.append(chunk)
    if not out:
        return pd.DataFrame(columns=columns)
    return pd.concat(out, ignore_index=True)


def add_missing_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    for column in columns:
        if column not in df.columns:
            df[column] = pd.NA
    return df[columns]


def build_individual_harmonized(df: pd.DataFrame, survey_key: str, meta: Dict[str, object]) -> pd.DataFrame:
    round_key = "nfhs4" if survey_key.startswith("nfhs4") else "nfhs5"
    renamed = df.rename(columns=INDIVIDUAL_RENAME[round_key]).copy()
    renamed["survey_round"] = meta["survey_round"]
    renamed["survey_year_start"] = meta["survey_year_start"]
    renamed["survey_year_end"] = meta["survey_year_end"]
    return add_missing_columns(renamed, INDIVIDUAL_HARMONIZED_COLUMNS)


def build_household_harmonized(df: pd.DataFrame, survey_key: str, meta: Dict[str, object]) -> pd.DataFrame:
    round_key = "nfhs4" if survey_key.startswith("nfhs4") else "nfhs5"
    renamed = df.rename(columns=HOUSEHOLD_RENAME[round_key]).copy()
    renamed["survey_round"] = meta["survey_round"]
    renamed["survey_year_start"] = meta["survey_year_start"]
    renamed["survey_year_end"] = meta["survey_year_end"]
    return add_missing_columns(renamed, HOUSEHOLD_HARMONIZED_COLUMNS)


def normalize_identifiers(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for column in columns:
        if column in df.columns:
            df[column] = df[column].astype("string")
    return df


def build_crosswalk_rows(
    survey_key: str,
    meta: Dict[str, object],
    inventory: pd.DataFrame,
    selected_columns: List[str],
) -> List[Dict[str, object]]:
    label_map = dict(zip(inventory["variable"], inventory["label"]))
    round_key = "nfhs4" if survey_key.startswith("nfhs4") else "nfhs5"
    rename_map = INDIVIDUAL_RENAME[round_key] if meta["level"] == "individual" else HOUSEHOLD_RENAME[round_key]

    rows = []
    for column in selected_columns:
        rows.append(
            {
                "survey_round": meta["survey_round"],
                "level": meta["level"],
                "source_file": meta["source_path"].name,
                "source_variable": column,
                "label": label_map.get(column, ""),
                "harmonized_variable": rename_map.get(column, ""),
                "kept_in_raw_selected_extract": 1,
                "kept_in_harmonized_extract": int(column in rename_map),
            }
        )
    return rows


def save_manifest_entry(entries: List[Dict[str, object]], path: Path, description: str) -> None:
    df = pd.read_parquet(path)
    entries.append(
        {
            "file_name": path.name,
            "relative_path": str(path.relative_to(PROJECT_ROOT)),
            "rows": len(df),
            "columns": len(df.columns),
            "description": description,
        }
    )


def main() -> None:
    manifest_entries: List[Dict[str, object]] = []
    crosswalk_rows: List[Dict[str, object]] = []
    raw_selected_frames: Dict[str, pd.DataFrame] = {}

    for dataset_key, meta in DATASETS.items():
        inventory = read_inventory(meta["inventory_path"])
        selected_columns = keep_available_columns(meta["wanted_columns"], inventory)
        missing_columns = [c for c in meta["wanted_columns"] if c not in selected_columns]
        if missing_columns:
            print(f"{dataset_key}: skipping unavailable columns {missing_columns}")

        df = load_selected_stata(meta["source_path"], selected_columns)
        df = normalize_identifiers(df, ["caseid", "hhid"])
        raw_selected_frames[dataset_key] = df

        raw_out = PROCESSED_DIR / f"{dataset_key}_raw_selected.parquet"
        df.to_parquet(raw_out, index=False)
        save_manifest_entry(
            manifest_entries,
            raw_out,
            f"Selected raw {meta['level']} variables extracted from {meta['survey_round']} for this project.",
        )
        crosswalk_rows.extend(build_crosswalk_rows(dataset_key, meta, inventory, selected_columns))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        harmonized_individual = pd.concat(
            [
                build_individual_harmonized(raw_selected_frames["nfhs4_individual"], "nfhs4_individual", DATASETS["nfhs4_individual"]),
                build_individual_harmonized(raw_selected_frames["nfhs5_individual"], "nfhs5_individual", DATASETS["nfhs5_individual"]),
            ],
            ignore_index=True,
        )
        harmonized_household = pd.concat(
            [
                build_household_harmonized(raw_selected_frames["nfhs4_household"], "nfhs4_household", DATASETS["nfhs4_household"]),
                build_household_harmonized(raw_selected_frames["nfhs5_household"], "nfhs5_household", DATASETS["nfhs5_household"]),
            ],
            ignore_index=True,
        )

    harmonized_individual = normalize_identifiers(harmonized_individual, ["caseid"])
    harmonized_household = normalize_identifiers(harmonized_household, ["hhid"])

    individual_out = PROCESSED_DIR / "nfhs_individual_harmonized.parquet"
    household_out = PROCESSED_DIR / "nfhs_household_harmonized.parquet"
    harmonized_individual.to_parquet(individual_out, index=False)
    harmonized_household.to_parquet(household_out, index=False)

    save_manifest_entry(
        manifest_entries,
        individual_out,
        "Harmonized woman-level extract combining NFHS-4 and NFHS-5 with consistent analysis variable names.",
    )
    save_manifest_entry(
        manifest_entries,
        household_out,
        "Harmonized household-level extract combining NFHS-4 and NFHS-5 with consistent analysis variable names.",
    )

    crosswalk_df = pd.DataFrame(crosswalk_rows).sort_values(
        ["level", "survey_round", "source_variable"]
    )
    crosswalk_df.to_csv(PROCESSED_DIR / "nfhs_variable_crosswalk.csv", index=False)

    availability_df = (
        crosswalk_df[crosswalk_df["harmonized_variable"].fillna("").ne("")]
        .assign(present=1)
        .pivot_table(
            index=["level", "harmonized_variable"],
            columns="survey_round",
            values="present",
            aggfunc="max",
            fill_value=0,
        )
        .reset_index()
        .rename(columns={"NFHS-4": "available_in_nfhs4", "NFHS-5": "available_in_nfhs5"})
    )
    availability_df.columns.name = None
    availability_df["available_in_both"] = (
        (availability_df["available_in_nfhs4"] == 1) & (availability_df["available_in_nfhs5"] == 1)
    ).astype(int)
    availability_df.to_csv(PROCESSED_DIR / "nfhs_harmonized_variable_availability.csv", index=False)

    pd.DataFrame(manifest_entries).to_csv(PROCESSED_DIR / "nfhs_extract_manifest.csv", index=False)
    print("Finished writing NFHS extracts to", PROCESSED_DIR)


if __name__ == "__main__":
    main()
