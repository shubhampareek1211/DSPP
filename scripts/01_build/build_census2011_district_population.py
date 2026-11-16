from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, List

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "census"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


SOURCE_PATH = PROJECT_ROOT / "data" / "raw" / "census" / "population_by_district_state.xlsx"
RBI_BASELINE_PATH = PROJECT_ROOT / "data" / "processed" / "rbi" / "rbi_district_baseline_dec_2013.csv"


def normalize_name(value: str) -> str:
    value = value.upper()
    replacements = {
        "&": " AND ",
        "NCT OF DELHI": "DELHI",
        "N.C.T. OF DELHI": "DELHI",
        "ANDAMAN & NICOBAR ISLANDS": "ANDAMAN AND NICOBAR ISLANDS",
        "THE DANGS": "DANG",
        "LEH(LADAKH)": "LEH",
        "LEH LADAKH": "LEH",
        "BANGALORE": "BENGALURU",
        "BELLARY": "BALLARI",
        "SHIMOGA": "SHIVAMOGGA",
        "CHIKMAGALUR": "CHIKKAMAGALURU",
        "CHIKMANGALUR": "CHIKKAMAGALURU",
        "TUTICORIN": "THOOTHUKUDI",
        "TRICHIRAPPALLI": "TIRUCHIRAPPALLI",
        "PONDICHERRY": "PUDUCHERRY",
        "ORISSA": "ODISHA",
        "UTTAR KANNAD": "UTTARA KANNADA",
        "DAKSHIN KANNAD": "DAKSHINA KANNADA",
        "NORTH AND MIDDLE ANDAMAN": "NORTH AND MIDDLE ANDAMAN",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"\(.*?\)", " ", value)
    value = value.replace(".", " ")
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def main() -> None:
    data = pd.read_excel(SOURCE_PATH, sheet_name="Data")

    states = (
        data[(data["Level"] == "STATE") & (data["TRU"] == "Total")]
        [["State", "Name"]]
        .drop_duplicates()
        .rename(columns={"State": "state_code_census", "Name": "state_name_census_raw"})
    )

    districts = (
        data[(data["Level"] == "DISTRICT") & (data["TRU"] == "Total")]
        [["State", "District", "Name", "No_HH", "TOT_P", "TOT_M", "TOT_F", "P_LIT", "M_LIT", "F_LIT"]]
        .copy()
        .rename(
            columns={
                "State": "state_code_census",
                "District": "district_code_census",
                "Name": "district_name_census_raw",
                "No_HH": "households_2011",
                "TOT_P": "population_total_2011",
                "TOT_M": "population_male_2011",
                "TOT_F": "population_female_2011",
                "P_LIT": "literate_total_2011",
                "M_LIT": "literate_male_2011",
                "F_LIT": "literate_female_2011",
            }
        )
    )

    districts = districts.merge(states, on="state_code_census", how="left")
    districts["state_name_census_clean"] = districts["state_name_census_raw"].map(normalize_name)
    districts["district_name_census_clean"] = districts["district_name_census_raw"].map(normalize_name)
    districts = districts.sort_values(["state_code_census", "district_code_census"]).reset_index(drop=True)

    census_out = PROCESSED_DIR / "census2011_district_population.csv"
    districts.to_csv(census_out, index=False)

    rbi = pd.read_csv(RBI_BASELINE_PATH)
    rbi["state_name_match"] = rbi["state_name_raw"].map(normalize_name)
    rbi["district_name_match"] = rbi["district_name_raw"].map(normalize_name)

    merged = rbi.merge(
        districts,
        left_on=["state_name_match", "district_name_match"],
        right_on=["state_name_census_clean", "district_name_census_clean"],
        how="left",
        indicator=True,
    )

    compare_cols = [
        "state_name_raw",
        "district_name_raw",
        "state_name_match",
        "district_name_match",
        "reporting_offices_total",
        "population_total_2011",
        "_merge",
    ]
    merged[compare_cols].to_csv(PROCESSED_DIR / "rbi_census_district_match_check.csv", index=False)

    unmatched = merged[merged["_merge"] != "both"][compare_cols].sort_values(
        ["state_name_raw", "district_name_raw"], ignore_index=True
    )
    unmatched.to_csv(PROCESSED_DIR / "rbi_census_district_unmatched.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "dataset": "census2011_district_population",
                "rows": len(districts),
                "columns": len(districts.columns),
                "description": "Census 2011 district-level total population and households extracted from the Primary Census Abstract.",
            },
            {
                "dataset": "rbi_census_district_match_check",
                "rows": len(merged),
                "columns": len(compare_cols),
                "description": "RBI December 2013 district baseline matched to Census 2011 district population using normalized state and district names.",
            },
            {
                "dataset": "rbi_census_district_unmatched",
                "rows": len(unmatched),
                "columns": len(compare_cols),
                "description": "RBI districts still unmatched to Census 2011 after normalized exact matching.",
            },
        ]
    )
    summary.to_csv(PROCESSED_DIR / "census2011_manifest.csv", index=False)

    print(f"Wrote census outputs to {PROCESSED_DIR}")
    print(f"RBI exact normalized matches: {(merged['_merge'] == 'both').sum()} / {len(merged)}")


if __name__ == "__main__":
    main()
