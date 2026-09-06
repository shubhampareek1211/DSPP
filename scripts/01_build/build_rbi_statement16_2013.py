from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, List

import pandas as pd
import xlrd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "rbi"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


DATASETS = [
    {
        "snapshot_label": "2013-09",
        "snapshot_year": 2013,
        "snapshot_month": 9,
        "source_path": PROJECT_ROOT / "data" / "raw" / "rbi" / "rbi_statement_16_district_bankgroup_sep_2013.xls",
    },
    {
        "snapshot_label": "2013-12",
        "snapshot_year": 2013,
        "snapshot_month": 12,
        "source_path": PROJECT_ROOT / "data" / "raw" / "rbi" / "rbi_statement_16_district_bankgroup_dec_2013.xls",
    },
]


def clean_name(value: str) -> str:
    value = re.sub(r"\s+", " ", value.strip())
    return value


def slugify_name(value: str) -> str:
    value = value.upper()
    value = value.replace("&", " AND ")
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def normalize_group_name(value: str) -> str:
    value = slugify_name(value).lower()
    mapping = {
        "state bank of india its associates": "sbi_associates",
        "nationalised banks": "nationalised_banks",
        "foreign banks": "foreign_banks",
        "regional rural bank": "regional_rural_banks",
        "old private sector banks": "old_private_banks",
        "new private sector banks": "new_private_banks",
    }
    return mapping.get(value, value.replace(" ", "_"))


def is_blank(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return pd.isna(value)


def is_missing_marker(value: object) -> bool:
    if is_blank(value):
        return True
    if isinstance(value, str) and value.strip() in {"-", "—"}:
        return True
    return False


def coerce_number(value: object) -> float:
    if is_blank(value):
        return 0.0
    if isinstance(value, str):
        stripped = value.strip()
        if stripped in {"-", "—"}:
            return 0.0
        stripped = stripped.replace(",", "")
        try:
            return float(stripped)
        except ValueError:
            return 0.0
    return float(value)


def repair_shifted_new_private_row(row: List[object], group_headers: List[str]) -> List[object]:
    repaired = list(row)
    if group_headers != ["regional_rural_banks", "old_private_banks", "new_private_banks"]:
        return repaired

    old_private_credit = repaired[8]
    new_private_offices = repaired[9]
    new_private_deposits = repaired[10]
    new_private_credit = repaired[11]

    if (
        coerce_number(new_private_offices) > 1000
        and coerce_number(old_private_credit) > 0
        and is_missing_marker(new_private_credit)
        and coerce_number(new_private_deposits) > 0
    ):
        repaired[8] = "-"
        repaired[9] = old_private_credit
        repaired[10] = new_private_offices
        repaired[11] = new_private_deposits

    return repaired


def parse_workbook(path: Path, snapshot_label: str, snapshot_year: int, snapshot_month: int) -> pd.DataFrame:
    book = xlrd.open_workbook(str(path))
    records: List[Dict[str, object]] = []
    current_region = ""
    current_state = ""

    sheets = book.sheets()
    for pair_start in range(0, len(sheets), 2):
        primary_sheet = sheets[pair_start]
        secondary_sheet = sheets[pair_start + 1] if pair_start + 1 < len(sheets) else None

        sheet_blocks = [
            (
                primary_sheet,
                [
                    normalize_group_name(str(primary_sheet.cell_value(3, 3))),
                    normalize_group_name(str(primary_sheet.cell_value(3, 6))),
                    normalize_group_name(str(primary_sheet.cell_value(3, 9))),
                ],
            )
        ]
        if secondary_sheet is not None:
            sheet_blocks.append(
                (
                    secondary_sheet,
                    [
                        normalize_group_name(str(secondary_sheet.cell_value(3, 3))),
                        normalize_group_name(str(secondary_sheet.cell_value(3, 6))),
                        normalize_group_name(str(secondary_sheet.cell_value(3, 9))),
                    ],
                )
            )

        max_rows = max(sheet.nrows for sheet, _ in sheet_blocks)

        for row_idx in range(6, max_rows):
            row_candidates = []
            for sheet, _ in sheet_blocks:
                if row_idx < sheet.nrows:
                    row_candidates.append(sheet.row_values(row_idx))

            location = ""
            serial = ""
            for row in row_candidates:
                if not is_blank(row[2]):
                    location = clean_name(str(row[2]))
                    serial = row[1]
                    break

            if not location:
                continue

            if "REGION" in location.upper():
                current_region = location
                current_state = ""
                continue

            if is_blank(serial):
                current_state = location
                row_type = "state_total"
                district_name = pd.NA
            else:
                row_type = "district"
                district_name = location

            for sheet, group_headers in sheet_blocks:
                if row_idx >= sheet.nrows:
                    continue
                row = repair_shifted_new_private_row(sheet.row_values(row_idx), group_headers)
                for group_offset, group_name in enumerate(group_headers):
                    start_col = 3 + (group_offset * 3)
                    records.append(
                        {
                            "snapshot_label": snapshot_label,
                            "snapshot_year": snapshot_year,
                            "snapshot_month": snapshot_month,
                            "source_file": path.name,
                            "sheet_name": sheet.name,
                            "row_type": row_type,
                            "region_name_raw": current_region,
                            "state_name_raw": current_state,
                            "district_name_raw": district_name,
                            "bank_group": group_name,
                            "offices": coerce_number(row[start_col]),
                            "deposits_million_rs": coerce_number(row[start_col + 1]),
                            "credit_million_rs": coerce_number(row[start_col + 2]),
                        }
                    )

    df = pd.DataFrame(records)
    df["region_name_clean"] = df["region_name_raw"].map(slugify_name)
    df["state_name_clean"] = df["state_name_raw"].map(slugify_name)
    df["district_name_clean"] = df["district_name_raw"].astype("string").map(
        lambda x: slugify_name(x) if pd.notna(x) else pd.NA
    )
    return df


def build_district_totals(raw_df: pd.DataFrame) -> pd.DataFrame:
    district_df = (
        raw_df[raw_df["row_type"] == "district"]
        .groupby(
            [
                "snapshot_label",
                "snapshot_year",
                "snapshot_month",
                "region_name_raw",
                "region_name_clean",
                "state_name_raw",
                "state_name_clean",
                "district_name_raw",
                "district_name_clean",
            ],
            as_index=False,
        )[["offices", "deposits_million_rs", "credit_million_rs"]]
        .sum()
        .rename(
            columns={
                "offices": "reporting_offices_total",
                "deposits_million_rs": "deposits_total_million_rs",
                "credit_million_rs": "credit_total_million_rs",
            }
        )
    )
    district_df = district_df[
        district_df["district_name_clean"].ne("ALL INDIA") & district_df["state_name_clean"].ne("ALL INDIA")
    ].copy()

    state_totals = raw_df[raw_df["row_type"] == "state_total"][
        ["snapshot_label", "state_name_clean"]
    ].drop_duplicates()
    state_totals = state_totals[state_totals["state_name_clean"].ne("ALL INDIA")].copy()
    district_states = district_df[["snapshot_label", "state_name_clean"]].drop_duplicates()
    state_only = state_totals.merge(
        district_states,
        on=["snapshot_label", "state_name_clean"],
        how="left",
        indicator=True,
    )
    state_only = state_only[state_only["_merge"] == "left_only"][
        ["snapshot_label", "state_name_clean"]
    ]

    if not state_only.empty:
        fallback_rows = (
            raw_df.merge(state_only, on=["snapshot_label", "state_name_clean"], how="inner")
            .query("row_type == 'state_total'")
            .groupby(
                [
                    "snapshot_label",
                    "snapshot_year",
                    "snapshot_month",
                    "region_name_raw",
                    "region_name_clean",
                    "state_name_raw",
                    "state_name_clean",
                ],
                as_index=False,
            )[["offices", "deposits_million_rs", "credit_million_rs"]]
            .sum()
        )
        fallback_rows["district_name_raw"] = fallback_rows["state_name_raw"]
        fallback_rows["district_name_clean"] = fallback_rows["state_name_clean"]
        fallback_rows["reporting_offices_total"] = fallback_rows.pop("offices")
        fallback_rows["deposits_total_million_rs"] = fallback_rows.pop("deposits_million_rs")
        fallback_rows["credit_total_million_rs"] = fallback_rows.pop("credit_million_rs")
        district_df = pd.concat([district_df, fallback_rows], ignore_index=True)

    district_df["deposits_total_crore_rs"] = district_df["deposits_total_million_rs"] / 10
    district_df["credit_total_crore_rs"] = district_df["credit_total_million_rs"] / 10
    district_df = district_df.sort_values(
        ["snapshot_label", "state_name_clean", "district_name_clean"], ignore_index=True
    )
    return district_df


def build_bankgroup_wide(raw_df: pd.DataFrame) -> pd.DataFrame:
    district_rows = raw_df[raw_df["row_type"] == "district"].copy()
    district_rows = district_rows[
        district_rows["district_name_clean"].ne("ALL INDIA") & district_rows["state_name_clean"].ne("ALL INDIA")
    ].copy()
    wide = (
        district_rows.pivot_table(
            index=[
                "snapshot_label",
                "snapshot_year",
                "snapshot_month",
                "region_name_raw",
                "region_name_clean",
                "state_name_raw",
                "state_name_clean",
                "district_name_raw",
                "district_name_clean",
            ],
            columns="bank_group",
            values=["offices", "deposits_million_rs", "credit_million_rs"],
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    flattened_columns = []
    for col in wide.columns.to_flat_index():
        if isinstance(col, str):
            flattened_columns.append(col)
        else:
            parts = [str(part) for part in col if str(part).strip()]
            flattened_columns.append("_".join(parts))
    wide.columns = flattened_columns
    return wide.sort_values(
        ["snapshot_label", "state_name_clean", "district_name_clean"], ignore_index=True
    )


def main() -> None:
    raw_frames = []
    manifest_rows: List[Dict[str, object]] = []

    for dataset in DATASETS:
        raw_df = parse_workbook(
            dataset["source_path"],
            dataset["snapshot_label"],
            dataset["snapshot_year"],
            dataset["snapshot_month"],
        )
        raw_frames.append(raw_df)

    raw_all = pd.concat(raw_frames, ignore_index=True)
    raw_out = PROCESSED_DIR / "rbi_statement16_2013_bankgroup_long.csv"
    raw_all.to_csv(raw_out, index=False)

    district_totals = build_district_totals(raw_all)
    district_out = PROCESSED_DIR / "rbi_district_baseline_2013_snapshots.csv"
    district_totals.to_csv(district_out, index=False)

    bankgroup_wide = build_bankgroup_wide(raw_all)
    bankgroup_out = PROCESSED_DIR / "rbi_district_bankgroup_2013_snapshots.csv"
    bankgroup_wide.to_csv(bankgroup_out, index=False)

    dec_out = PROCESSED_DIR / "rbi_district_baseline_dec_2013.csv"
    district_totals[district_totals["snapshot_label"] == "2013-12"].to_csv(dec_out, index=False)

    sep_out = PROCESSED_DIR / "rbi_district_baseline_sep_2013.csv"
    district_totals[district_totals["snapshot_label"] == "2013-09"].to_csv(sep_out, index=False)

    for path, description in [
        (raw_out, "Long bank-group-level RBI Statement 16 extract for September and December 2013."),
        (district_out, "District-level total reporting offices, deposits, and credit across all bank groups for both 2013 snapshots."),
        (bankgroup_out, "District-level wide extract with separate fields for each bank group across both 2013 snapshots."),
        (dec_out, "Recommended pre-treatment district baseline using the December 2013 RBI Statement 16 snapshot."),
        (sep_out, "Supplementary district baseline using the September 2013 RBI Statement 16 snapshot."),
    ]:
        df = pd.read_csv(path)
        manifest_rows.append(
            {
                "file_name": path.name,
                "relative_path": str(path.relative_to(PROJECT_ROOT)),
                "rows": len(df),
                "columns": len(df.columns),
                "description": description,
            }
        )

    pd.DataFrame(manifest_rows).to_csv(PROCESSED_DIR / "rbi_statement16_2013_manifest.csv", index=False)
    print(f"Wrote RBI Statement 16 outputs to {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
