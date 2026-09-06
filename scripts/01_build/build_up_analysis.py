from __future__ import annotations

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
UP_DIR = PROCESSED_DIR / "up"
UP_DIR.mkdir(parents=True, exist_ok=True)

# ── State code lookups ────────────────────────────────────────────────────────

NFHS4_STATE_CODES = {
    1: "andaman and nicobar islands",
    2: "andhra pradesh",
    3: "arunachal pradesh",
    4: "assam",
    5: "bihar",
    6: "chandigarh",
    7: "chhattisgarh",
    8: "dadra and nagar haveli",
    9: "daman and diu",
    10: "goa",
    11: "gujarat",
    12: "haryana",
    13: "himachal pradesh",
    14: "jammu and kashmir",
    15: "jharkhand",
    16: "karnataka",
    17: "kerala",
    18: "lakshadweep",
    19: "madhya pradesh",
    20: "maharashtra",
    21: "manipur",
    22: "meghalaya",
    23: "mizoram",
    24: "nagaland",
    25: "delhi",
    26: "odisha",
    27: "puducherry",
    28: "punjab",
    29: "rajasthan",
    30: "sikkim",
    31: "tamil nadu",
    32: "tripura",
    33: "uttar pradesh",
    34: "uttarakhand",
    35: "west bengal",
    36: "telangana",
}

NFHS5_STATE_CODES = {
    1: "jammu and kashmir",
    2: "himachal pradesh",
    3: "punjab",
    4: "chandigarh",
    5: "uttarakhand",
    6: "haryana",
    7: "delhi",
    8: "rajasthan",
    9: "uttar pradesh",
    10: "bihar",
    11: "sikkim",
    12: "arunachal pradesh",
    13: "nagaland",
    14: "manipur",
    15: "mizoram",
    16: "tripura",
    17: "meghalaya",
    18: "assam",
    19: "west bengal",
    20: "jharkhand",
    21: "odisha",
    22: "chhattisgarh",
    23: "madhya pradesh",
    24: "gujarat",
    25: "dadra and nagar haveli and daman and diu",
    27: "maharashtra",
    28: "andhra pradesh",
    29: "karnataka",
    30: "goa",
    31: "lakshadweep",
    32: "kerala",
    33: "tamil nadu",
    34: "puducherry",
    35: "andaman and nicobar islands",
    36: "telangana",
    37: "ladakh",
}


def add_state_name(df: pd.DataFrame) -> pd.DataFrame:
    lookup = df["survey_round"].map({"NFHS-4": NFHS4_STATE_CODES, "NFHS-5": NFHS5_STATE_CODES})
    df["state_name"] = [
        lookup.iloc[i].get(int(df["state_code"].iloc[i]), None)
        if pd.notna(df["state_code"].iloc[i]) else None
        for i in range(len(df))
    ]
    return df


def add_state_name_fast(df: pd.DataFrame) -> pd.DataFrame:
    """Vectorized version of add_state_name."""
    mask4 = df["survey_round"] == "NFHS-4"
    mask5 = df["survey_round"] == "NFHS-5"
    state_name = pd.Series(index=df.index, dtype="object")
    state_name[mask4] = df.loc[mask4, "state_code"].map(NFHS4_STATE_CODES)
    state_name[mask5] = df.loc[mask5, "state_code"].map(NFHS5_STATE_CODES)
    df["state_name"] = state_name
    return df


# ── NFHS district name lookup (UP districts, codes from NFHS coding) ──────────
# These are the NFHS district numeric codes for UP (shared across NFHS-4 and NFHS-5)
# Source: NFHS district code list (DHS India district codes for UP)
# All names use the canonical form defined in CANONICAL_NAME_MAP below.
UP_NFHS_DISTRICT_CODES = {
    132: "saharanpur",
    133: "muzaffarnagar",
    134: "bijnor",
    135: "moradabad",
    136: "rampur",
    137: "amroha",          # old NFHS-4 name: jyotiba phule nagar
    138: "meerut",
    139: "baghpat",
    140: "ghaziabad",
    141: "gautam buddha nagar",
    142: "bulandshahr",
    143: "aligarh",
    144: "hathras",         # MKSY calls this mahamaya nagar (hathras)
    145: "mathura",
    146: "agra",
    147: "firozabad",
    148: "mainpuri",
    149: "etah",
    150: "kasganj",
    151: "farrukhabad",
    152: "kannauj",
    153: "etawah",
    154: "auraiya",
    155: "kanpur dehat",
    156: "kanpur nagar",
    157: "jalaun",
    158: "hamirpur",
    159: "mahoba",
    160: "banda",
    161: "chitrakoot",
    162: "fatehpur",
    163: "prayagraj",       # old name: allahabad; PMMVY uses "allahabad"
    164: "kaushambi",
    165: "pratapgarh",
    166: "lucknow",
    167: "unnao",
    168: "rae bareli",
    169: "sitapur",
    170: "hardoi",
    171: "kheri",
    172: "barabanki",
    173: "ayodhya",         # old name: faizabad; PMMVY uses "faizabad"
    174: "ambedkar nagar",
    175: "sultanpur",
    176: "bahraich",
    177: "shravasti",
    178: "balrampur",
    179: "gonda",
    180: "siddharth nagar",
    181: "basti",
    182: "sant kabeer nagar",
    183: "gorakhpur",
    184: "maharajganj",
    185: "kushi nagar",
    186: "deoria",
    187: "azamgarh",
    188: "mau",
    189: "ballia",
    190: "jaunpur",
    191: "ghazipur",
    192: "chandauli",
    193: "varanasi",
    194: "bhadohi",         # official name: sant ravidas nagar bhadohi
    195: "mirzapur",
    196: "sonbhadra",
    197: "prayagraj",       # NFHS-5 re-coded after 2018 rename from allahabad
    198: "shahjahanpur",
    199: "pilibhit",
    200: "bareilly",
    201: "budaun",
    202: "sambhal",
    # newer districts added in NFHS-5 after district splits
    921: "amethi",
    922: "hapur",
    923: "shamli",
    924: "sambhal",
    925: "kasganj",
    926: "amroha",
    927: "amethi",
    928: "hapur",
    929: "shamli",
    930: "ambedkar nagar",
}

# Canonical name map: normalizes all source-specific variants to one agreed name.
# Key = any variant that appears after basic normalize_district_name(); value = canonical.
CANONICAL_NAME_MAP = {
    # NFHS-4 old district names
    "jyotiba phule nagar": "amroha",
    "sant ravidas nagar": "bhadohi",
    "siddharthnagar": "siddharth nagar",
    "kushinagar": "kushi nagar",
    # PMMVY old names (pre-rename)
    "allahabad": "prayagraj",
    "faizabad": "ayodhya",
    "kushi nagar": "kushi nagar",   # PMMVY spells it with space; canonical keeps space
    "siddharth nagar": "siddharth nagar",
    "bhadohi": "bhadohi",
    # MKSY-specific spellings
    "mahamaya nagar (hathras)": "hathras",
    "prayagraj": "prayagraj",
    "ayodhya": "ayodhya",
    # lakhimpur kheri / kheri variants
    "lakhimpur kheri": "kheri",
}


def normalize_district_name(name: str) -> str:
    """Lowercase, strip, collapse spaces, remove punctuation, then apply canonical map."""
    n = (
        str(name)
        .lower()
        .strip()
        .replace("  ", " ")
        .replace("-", " ")
        .replace(".", "")
        .replace("'", "")
    )
    # apply canonical map (handles renames and spelling variants across all sources)
    return CANONICAL_NAME_MAP.get(n, n)


# ── Load NFHS individual harmonized and patch state_name ─────────────────────

def patch_harmonized_with_state_name() -> None:
    indiv_path = PROCESSED_DIR / "nfhs" / "nfhs_individual_harmonized.parquet"
    hh_path = PROCESSED_DIR / "nfhs" / "nfhs_household_harmonized.parquet"

    print("Patching individual harmonized file with state_name...")
    indiv = pd.read_parquet(indiv_path)
    indiv = add_state_name_fast(indiv)
    indiv.to_parquet(indiv_path, index=False)
    print(f"  Saved {len(indiv):,} rows with state_name. UP counts:")
    print(indiv[indiv["state_name"] == "uttar pradesh"]["survey_round"].value_counts().to_string())

    print("Patching household harmonized file with state_name...")
    hh = pd.read_parquet(hh_path)
    hh = add_state_name_fast(hh)
    hh.to_parquet(hh_path, index=False)
    print(f"  Saved {len(hh):,} rows with state_name.")


# ── Build NFHS district code → name crosswalk for UP ─────────────────────────

def build_nfhs_up_district_lookup(indiv: pd.DataFrame) -> pd.DataFrame:
    up = indiv[indiv["state_name"] == "uttar pradesh"].copy()
    codes = sorted(up["district_code"].dropna().unique())
    rows = []
    for code in codes:
        n4 = len(up[(up["survey_round"] == "NFHS-4") & (up["district_code"] == code)])
        n5 = len(up[(up["survey_round"] == "NFHS-5") & (up["district_code"] == code)])
        rows.append({
            "nfhs_district_code": int(code),
            "nfhs_district_name_guess": UP_NFHS_DISTRICT_CODES.get(int(code), "unknown"),
            "nfhs4_rows": n4,
            "nfhs5_rows": n5,
        })
    return pd.DataFrame(rows)


# ── Load and normalize PMMVY UP ──────────────────────────────────────────────

def load_pmmvy_up() -> pd.DataFrame:
    path = PROJECT_ROOT / "data" / "raw" / "pmmvy" / "up_district_pmmvy_beneficiaries_2017_2019_and_2019_2020.csv"
    df = pd.read_csv(path)
    df.columns = ["serial_no", "district_name_raw", "beneficiaries_2017_2019", "beneficiaries_2019_2020"]
    df = df[df["district_name_raw"].str.lower().str.strip() != "total"].copy()
    df["district_name_norm"] = df["district_name_raw"].apply(normalize_district_name)
    df["beneficiaries_total"] = df["beneficiaries_2017_2019"].fillna(0) + df["beneficiaries_2019_2020"].fillna(0)
    return df[["district_name_raw", "district_name_norm", "beneficiaries_2017_2019", "beneficiaries_2019_2020", "beneficiaries_total"]]


# ── Load and label MKSY UP ────────────────────────────────────────────────────
# KPI label mapping derived from the MKSY public dashboard page
# kpi1 = total applications received
# kpi2 = total applications approved
# kpi3 = applications rejected
# kpi4 = applications pending / in process  (kpi2 - kpi3 = kpi4 approximately)
# kpi5 = applications pending at district level
# kpi6 = category 1 beneficiaries (Condition 1: birth registration)
# kpi7 = category 2 beneficiaries (Condition 2: school admission)
# Note: kpi1 - kpi2 = kpi5 approximately in most districts → confirms kpi2 = approved, kpi5 = pending

MKSY_KPI_LABELS = {
    "kpi1_data": "total_applications",
    "kpi2_data": "approved_applications",
    "kpi3_data": "rejected_applications",
    "kpi4_data": "net_approved",       # kpi2 - kpi3
    "kpi5_data": "pending_applications",
    "kpi6_data": "cat1_beneficiaries",
    "kpi7_data": "cat2_beneficiaries",
}


def load_mksy_up() -> pd.DataFrame:
    path = PROJECT_ROOT / "data" / "raw" / "state_women_dbt" / "uttar_pradesh" / "mksy_up_district_metrics.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={"district_name": "district_name_raw", **MKSY_KPI_LABELS})
    # normalize_district_name applies the canonical map, handling "mahamaya nagar (hathras)" → "hathras" etc.
    df["district_name_norm"] = df["district_name_raw"].apply(normalize_district_name)
    return df


# ── Build district crosswalk: NFHS codes ↔ PMMVY names ↔ MKSY names ─────────

def build_district_crosswalk(
    nfhs_lookup: pd.DataFrame,
    pmmvy: pd.DataFrame,
    mksy: pd.DataFrame,
) -> pd.DataFrame:
    cw = nfhs_lookup.copy()
    cw["district_name_norm"] = cw["nfhs_district_name_guess"].apply(normalize_district_name)

    # merge PMMVY
    pmmvy_map = pmmvy[["district_name_norm", "district_name_raw"]].rename(
        columns={"district_name_norm": "district_name_norm", "district_name_raw": "pmmvy_district_name"}
    )
    cw = cw.merge(pmmvy_map, on="district_name_norm", how="left")

    # merge MKSY
    mksy_map = mksy[["district_name_norm", "district_name_raw"]].rename(
        columns={"district_name_norm": "district_name_norm", "district_name_raw": "mksy_district_name"}
    )
    cw = cw.merge(mksy_map, on="district_name_norm", how="left")

    matched_pmmvy = cw["pmmvy_district_name"].notna().sum()
    matched_mksy = cw["mksy_district_name"].notna().sum()
    total = len(cw)
    print(f"  Crosswalk: {total} NFHS districts → PMMVY matched {matched_pmmvy}, MKSY matched {matched_mksy}")

    unmatched = cw[cw["pmmvy_district_name"].isna() | cw["mksy_district_name"].isna()]
    if len(unmatched):
        print("  Unmatched districts:")
        print(unmatched[["nfhs_district_code", "nfhs_district_name_guess", "pmmvy_district_name", "mksy_district_name"]].to_string(index=False))

    return cw


# ── Build UP analysis dataset ────────────────────────────────────────────────

# Maps RBI 2013 district names (lower) → canonical names used in UP analysis dataset.
# Needed because some RBI names differ from the NFHS-based canonical names.
RBI_TO_UP_CANONICAL = {
    # Spelling differences
    "bara banki": "barabanki",
    "kanauj": "kannauj",
    "kanshiram nagar": "kasganj",         # renamed to Kasganj
    "rai bareli": "rae bareli",
    "sant kabir nagar": "sant kabeer nagar",
    "bhim nagar": "sambhal",              # Bhim Nagar = Sambhal (RBI 2013 name for Sambhal)
    # District renames (RBI 2013 used old names)
    "allahabad": "prayagraj",
    "faizabad": "ayodhya",
    "jyotiba phule nagar": "amroha",
    "panchsheel nagar": "amroha",         # RBI sub-unit that is part of Amroha
    "prabudh nagar": "muzaffarnagar",     # RBI sub-unit that is part of Muzaffarnagar
    "siddharthnagar": "siddharth nagar",
    "sidharthanagar": "siddharth nagar",
    "siddharthanagar": "siddharth nagar", # annual deposits file spelling
    "mahamaya nagar": "hathras",
    "shrawasti": "shravasti",
    "kushinagar": "kushi nagar",
    "sant ravidas nagar": "bhadohi",
}

UP_RBI_PARENT = {
    # Districts carved after 2013 that are not in RBI 2013: inherit parent's density as proxy.
    # Amethi is excluded because it existed as a distinct district in RBI 2013 already.
    "hapur": "ghaziabad",       # Hapur carved from Ghaziabad ~2011
    "shamli": "muzaffarnagar",  # Shamli carved from Muzaffarnagar ~2011
}


def load_rbi_baseline_up() -> pd.DataFrame:
    raw_path = PROJECT_ROOT / "data" / "processed" / "rbi" / "rbi_district_baseline_dec_2013.csv"
    census_path = PROJECT_ROOT / "data" / "processed" / "census" / "census2011_district_population.csv"

    raw = pd.read_csv(raw_path)
    census = pd.read_csv(census_path)

    up_raw = raw[raw["state_name_clean"].str.upper().str.strip() == "UTTAR PRADESH"].copy()
    up_census = census[census["state_name_census_clean"].str.upper().str.strip() == "UTTAR PRADESH"].copy()

    # Build Census population lookup keyed by canonical name.
    # Census 2011 uses pre-rename district names; map them to canonical form here.
    CENSUS_TO_CANONICAL = {
        "allahabad": "prayagraj",
        "faizabad": "ayodhya",
        "jyotiba phule nagar": "amroha",
        "mahamaya nagar": "hathras",
        "mahrajganj": "maharajganj",
        "kanshiram nagar": "kasganj",
        "kushinagar": "kushi nagar",
        "sant ravidas nagar": "bhadohi",
        "sant kabir nagar": "sant kabeer nagar",  # Census spelling vs canonical double-e
        "bara banki": "barabanki",                 # Census spacing vs canonical no-space
        "shrawasti": "shravasti",
        "siddharthnagar": "siddharth nagar",
        # post-2011 carved districts: use parent as population proxy
        "sultanpur": "amethi",     # Amethi carved from Sultanpur; share population
        "moradabad": "sambhal",    # Sambhal carved from Moradabad ~2011-12
        "ghaziabad": "hapur",      # Hapur carved from Ghaziabad ~2011
        "muzaffarnagar": "shamli", # Shamli carved from Muzaffarnagar ~2011
    }

    pop_map_raw = dict(
        zip(
            up_census["district_name_census_clean"].str.lower().str.strip(),
            up_census["population_total_2011"],
        )
    )
    # direct + canonical entries
    census_canonical: dict[str, float] = {}
    for k, v in pop_map_raw.items():
        census_canonical[k] = v
        canon = CENSUS_TO_CANONICAL.get(k)
        if canon:
            census_canonical[canon] = v
    # keep original canonical name for districts that are their own parent
    # (sultanpur → amethi above, but sultanpur itself is also needed)
    # sultanpur's own entry is already in census_canonical via the direct k loop

    # Normalize RBI district names to canonical form
    up_raw["district_name_norm"] = (
        up_raw["district_name_clean"].str.lower().str.strip()
        .map(lambda x: RBI_TO_UP_CANONICAL.get(x, CANONICAL_NAME_MAP.get(x, x)))
    )

    # Aggregate RBI 2013 by canonical name (sums sub-units: PANCHSHEEL NAGAR+JYOTIBA = amroha, etc.)
    up_agg = up_raw.groupby("district_name_norm", as_index=False).agg(
        reporting_offices_dec2013=("reporting_offices_total", "sum"),
        deposits_total_crore_rs=("deposits_total_crore_rs", "sum"),
        credit_total_crore_rs=("credit_total_crore_rs", "sum"),
    )

    up_agg["population_2011"] = up_agg["district_name_norm"].map(census_canonical)
    pop = up_agg["population_2011"]
    up_agg["branch_density_2013"] = up_agg["reporting_offices_dec2013"] / pop * 100_000
    up_agg["deposits_per_capita_2013_rs"] = up_agg["deposits_total_crore_rs"] * 1e7 / pop
    up_agg["credit_per_capita_2013_rs"] = up_agg["credit_total_crore_rs"] * 1e7 / pop

    # Load 2015-16 deposits directly from the annual source file (avoids
    # merged-district artefacts in rbi_banking_baseline.csv where BHIM NAGAR+MORADABAD
    # and AMETHI+SULTANPUR were summed into single rows).
    dep_xlsx = (
        PROJECT_ROOT / "data" / "raw" / "rbi"
        / "bank_deposits_of_scbs_region_state_district_bank_group_population_group_wise_annual.xlsx"
    )
    dep_raw = pd.read_excel(dep_xlsx, sheet_name="Data", header=None, skiprows=3)
    dep_raw.columns = ["_drop", "year", "bank_group", "region", "state", "district",
                       "pop_group", "accounts_thousands", "deposits_crore"]
    dep_raw = dep_raw.drop(columns="_drop").dropna(subset=["year"])
    dep_raw = dep_raw[
        (dep_raw["year"] == "2015-16")
        & (dep_raw["state"].str.upper().str.strip() == "UTTAR PRADESH")
    ].copy()
    dep_agg = dep_raw.groupby("district", as_index=False).agg(
        deposits_crore=("deposits_crore", "sum"),
        accounts_thousands=("accounts_thousands", "sum"),
    )
    dep_agg["district_name_norm"] = (
        dep_agg["district"].str.lower().str.strip()
        .map(lambda x: RBI_TO_UP_CANONICAL.get(x, CANONICAL_NAME_MAP.get(x, x)))
    )
    # Re-aggregate after normalization (panchsheel nagar + jyotiba → amroha, etc.)
    dep_agg = dep_agg.groupby("district_name_norm", as_index=False).agg(
        deposits_crore_2015_16=("deposits_crore", "sum"),
        accounts_thousands_2015_16=("accounts_thousands", "sum"),
    )
    dep_map = dict(zip(dep_agg["district_name_norm"], dep_agg["deposits_crore_2015_16"]))
    acc_map = dict(zip(dep_agg["district_name_norm"], dep_agg["accounts_thousands_2015_16"]))

    up_agg["deposits_crore_2015_16"] = up_agg["district_name_norm"].map(dep_map)
    up_agg["deposits_per_capita_2015_16_rs"] = up_agg["deposits_crore_2015_16"] * 1e7 / pop
    up_agg["accounts_thousands_2015_16"] = up_agg["district_name_norm"].map(acc_map)
    up_agg["accounts_per_capita_2015_16"] = up_agg["accounts_thousands_2015_16"] * 1000 / pop

    # Add proxy rows for post-2013 carved districts not in RBI 2013
    existing = set(up_agg["district_name_norm"].values)
    extra_rows = []
    for child, parent in UP_RBI_PARENT.items():
        if child not in existing:
            parent_rows = up_agg[up_agg["district_name_norm"] == parent]
            if not parent_rows.empty:
                row = parent_rows.iloc[0].copy()
                row["district_name_norm"] = child
                extra_rows.append(row)
    if extra_rows:
        up_agg = pd.concat([up_agg, pd.DataFrame(extra_rows)], ignore_index=True)

    rbi_cols = [
        "district_name_norm", "population_2011",
        "reporting_offices_dec2013", "branch_density_2013",
        "deposits_per_capita_2013_rs", "credit_per_capita_2013_rs",
        "deposits_crore_2015_16", "deposits_per_capita_2015_16_rs",
        "accounts_per_capita_2015_16",
    ]
    return up_agg[rbi_cols]


def build_up_analysis_dataset(
    indiv: pd.DataFrame,
    crosswalk: pd.DataFrame,
    pmmvy: pd.DataFrame,
    mksy: pd.DataFrame,
    rbi_baseline: pd.DataFrame,
) -> pd.DataFrame:
    up = indiv[indiv["state_name"] == "uttar pradesh"].copy()

    code_to_norm = dict(zip(crosswalk["nfhs_district_code"], crosswalk["district_name_norm"]))
    up["district_name_norm"] = up["district_code"].map(code_to_norm)

    # merge PMMVY
    pmmvy_cols = pmmvy[["district_name_norm", "beneficiaries_2017_2019",
                         "beneficiaries_2019_2020", "beneficiaries_total"]]
    up = up.merge(pmmvy_cols, on="district_name_norm", how="left")

    # merge MKSY
    mksy_cols = mksy[["district_name_norm", "total_applications", "approved_applications",
                       "net_approved", "pending_applications",
                       "cat1_beneficiaries", "cat2_beneficiaries"]]
    mksy_cols = mksy_cols.rename(columns={c: f"mksy_{c}" for c in mksy_cols.columns
                                          if c != "district_name_norm"})
    up = up.merge(mksy_cols, on="district_name_norm", how="left")

    # merge RBI baseline
    up = up.merge(rbi_baseline, on="district_name_norm", how="left")

    up["post"] = (up["survey_round"] == "NFHS-5").astype(int)

    print(f"  UP analysis dataset: {len(up):,} rows")
    print(f"  PMMVY merge:         {up['beneficiaries_total'].notna().sum():,} / {len(up):,}")
    print(f"  MKSY merge:          {up['mksy_total_applications'].notna().sum():,} / {len(up):,}")
    print(f"  branch_density:      {up['branch_density_2013'].notna().sum():,} / {len(up):,}")
    print(f"  deposits_per_capita: {up['deposits_per_capita_2015_16_rs'].notna().sum():,} / {len(up):,}")
    print(f"  Outcome rows:        {up['bank_account_self_use'].notna().sum():,}")
    return up


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    # Step 1: patch state_name into harmonized files
    patch_harmonized_with_state_name()

    # Step 2: reload patched individual file
    print("\nLoading patched harmonized individual file...")
    indiv = pd.read_parquet(PROCESSED_DIR / "nfhs" / "nfhs_individual_harmonized.parquet")

    # Step 3: build NFHS UP district lookup
    print("\nBuilding NFHS UP district lookup...")
    nfhs_lookup = build_nfhs_up_district_lookup(indiv)
    nfhs_lookup_path = UP_DIR / "nfhs_up_district_lookup.csv"
    nfhs_lookup.to_csv(nfhs_lookup_path, index=False)
    print(f"  {len(nfhs_lookup)} UP district codes → {nfhs_lookup_path.name}")

    # Step 4: load treatment files
    print("\nLoading PMMVY UP district file...")
    pmmvy = load_pmmvy_up()
    print(f"  {len(pmmvy)} districts")

    print("Loading MKSY UP district file...")
    mksy = load_mksy_up()
    print(f"  {len(mksy)} districts")

    # Step 5: build crosswalk
    print("\nBuilding district crosswalk...")
    crosswalk = build_district_crosswalk(nfhs_lookup, pmmvy, mksy)
    crosswalk_path = UP_DIR / "up_district_crosswalk.csv"
    crosswalk.to_csv(crosswalk_path, index=False)
    print(f"  Saved → {crosswalk_path.name}")

    # Step 6: save labeled MKSY file
    mksy_labeled_path = UP_DIR / "mksy_up_district_labeled.csv"
    mksy.to_csv(mksy_labeled_path, index=False)
    print(f"\nSaved labeled MKSY file → {mksy_labeled_path.name}")

    # Step 7: load RBI baseline
    print("\nLoading RBI banking baseline for UP...")
    rbi_baseline = load_rbi_baseline_up()
    print(f"  {len(rbi_baseline)} UP districts with RBI data")

    # Step 8: build UP analysis dataset
    print("\nBuilding UP analysis dataset...")
    up_analysis = build_up_analysis_dataset(indiv, crosswalk, pmmvy, mksy, rbi_baseline)
    up_analysis_path = UP_DIR / "up_analysis_dataset.parquet"
    up_analysis.to_parquet(up_analysis_path, index=False)
    print(f"  Saved → {up_analysis_path.name}")

    # Step 8: save PMMVY normalized file
    pmmvy_path = UP_DIR / "pmmvy_up_district_normalized.csv"
    pmmvy.to_csv(pmmvy_path, index=False)
    print(f"  Saved → {pmmvy_path.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()
