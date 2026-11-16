from __future__ import annotations

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RBI_DIR = PROCESSED_DIR / "rbi"
RBI_DIR.mkdir(parents=True, exist_ok=True)

# ── Name normalization ─────────────────────────────────────────────────────────

def normalize(name: str) -> str:
    return (
        str(name).upper().strip()
        .replace("-", " ").replace(".", "").replace("'", "")
        .replace("&", "AND").replace("  ", " ")
    )


# (normalized_state, normalized_district) → normalized_census_district
# State-keyed to avoid cross-state collisions (e.g. CG Balrampur ≠ UP Balrampur).
# Post-2011 carved districts map to their Census 2011 parent.
RBI_TO_CENSUS: dict[tuple[str, str], str] = {
    ("ANDAMAN AND NICOBAR ISLANDS", "NICOBAR"): "NICOBARS",
    ("ANDHRA PRADESH", "NELLORE"): "SRI POTTI SRIRAMULU NELLORE",
    ("ANDHRA PRADESH", "RANGAREDDI"): "RANGAREDDY",
    ("ARUNACHAL PRADESH", "CHUNGLANG"): "CHANGLANG",
    ("ARUNACHAL PRADESH", "LONGDING"): "TIRAP",
    ("ARUNACHAL PRADESH", "PAPUMPARE"): "PAPUM PARE",
    ("ASSAM", "NORTH CACHAR HILLS"): "DIMA HASAO",
    ("ASSAM", "SIBSAGAR"): "SIVASAGAR",
    ("BIHAR", "PASCHIMI CHAMPARAN"): "PASHCHIM CHAMPARAN",
    ("BIHAR", "PURBI CHAMPARAN"): "PURBA CHAMPARAN",
    ("CHHATTISGARH", "BALOD"): "DURG",
    ("CHHATTISGARH", "BALODABAZAR"): "RAIPUR",
    ("CHHATTISGARH", "BALRAMPUR"): "SURGUJA",
    ("CHHATTISGARH", "BEMETARA"): "DURG",
    ("CHHATTISGARH", "DANTEWADA"): "BASTAR",
    ("CHHATTISGARH", "GARIYABAND"): "RAIPUR",
    ("CHHATTISGARH", "KANKER"): "UTTAR BASTAR KANKER",
    ("CHHATTISGARH", "KAWARDHA"): "KABEERDHAM",
    ("CHHATTISGARH", "KONDAGAON"): "BASTAR",
    ("CHHATTISGARH", "MUNGELI"): "BILASPUR",
    ("CHHATTISGARH", "SUKMA"): "DAKSHIN BASTAR DANTEWADA",
    ("CHHATTISGARH", "SURAJPUR"): "SURGUJA",
    ("GUJARAT", "AHMEDABAD"): "AHMADABAD",
    ("GUJARAT", "ARAVALLI"): "SABAR KANTHA",
    ("GUJARAT", "BOTAD"): "BHAVNAGAR",
    ("GUJARAT", "DANGS"): "DANG",
    ("GUJARAT", "MAHISAGAR"): "PANCH MAHALS",
    ("HIMACHAL PRADESH", "KULU"): "KULLU",
    ("HIMACHAL PRADESH", "SIMLA"): "SHIMLA",
    ("JAMMU AND KASHMIR", "BANDIPORA"): "BANDIPORE",
    ("JAMMU AND KASHMIR", "BARAMULLA"): "BARAMULA",
    ("JAMMU AND KASHMIR", "LEH LADAKH"): "LEH",
    ("JAMMU AND KASHMIR", "POONCH"): "PUNCH",
    ("JAMMU AND KASHMIR", "SHOPIAN"): "SHUPIYAN",
    ("JHARKHAND", "HAZARIBAG"): "HAZARIBAGH",
    ("JHARKHAND", "KODERMA"): "KODARMA",
    ("JHARKHAND", "LOHARDAGGA"): "LOHARDAGA",
    ("JHARKHAND", "PALAMAU"): "PALAMU",
    ("JHARKHAND", "PASCHIMI SINGHBHUM"): "PASHCHIMI SINGHBHUM",
    ("JHARKHAND", "SAHEBGANJ"): "SAHIBGANJ",
    ("JHARKHAND", "SERAIKELA KHARSAWAN"): "SARAIKELA KHARSAWAN",
    ("KARNATAKA", "BAGALKOTE"): "BAGALKOT",
    ("KARNATAKA", "BANGALORE RURAL"): "BENGALURU RURAL",
    ("KARNATAKA", "BANGALORE URBAN"): "BENGALURU",
    ("KARNATAKA", "BELLARY"): "BALLARI",
    ("KARNATAKA", "CHIKMAGALUR"): "CHIKKAMAGALURU",
    ("KARNATAKA", "DAKSHIN KANNAD"): "DAKSHINA KANNADA",
    ("KARNATAKA", "DAVANGERE"): "DAVANAGERE",
    ("KARNATAKA", "SHIMOGA"): "SHIVAMOGGA",
    ("KARNATAKA", "UDIPI"): "UDUPI",
    ("KARNATAKA", "UTTAR KANNAD"): "UTTARA KANNADA",
    ("KERALA", "ALAPUZHA"): "ALAPPUZHA",
    ("MADHYA PRADESH", "AGAR MALWA"): "SHAJAPUR",
    ("MADHYA PRADESH", "EAST NIMAR"): "KHANDWA",
    ("MADHYA PRADESH", "WEST NIMAR"): "KHARGONE",
    ("MAHARASHTRA", "BULDHANA"): "BULDANA",
    ("MAHARASHTRA", "GONDIA"): "GONDIYA",
    ("MAHARASHTRA", "NASIK"): "NASHIK",
    ("MAHARASHTRA", "RAIGAD"): "RAIGARH",
    ("MANIPUR", "BISHENPUR"): "BISHNUPUR",
    ("MEGHALAYA", "RI BHOI"): "RIBHOI",
    # Delhi: RBI reports one row; Census has 9 sub-districts.
    # load_census() sums all Delhi sub-districts into DELHI||DELHI.
    ("DELHI", "NCT OF DELHI"): "DELHI",
    ("ODISHA", "ANGUL"): "ANUGUL",
    ("ODISHA", "BOUDH"): "BAUDH",
    ("ODISHA", "DEOGARH"): "DEBAGARH",
    ("ODISHA", "JAGATSINGHPUR"): "JAGATSINGHAPUR",
    ("ODISHA", "JAJPUR"): "JAJAPUR",
    ("ODISHA", "KEONJHAR"): "KENDUJHAR",
    ("ODISHA", "KHURDA"): "KHORDHA",
    ("ODISHA", "NAWAPARA"): "NUAPADA",
    ("ODISHA", "NAWRANGPUR"): "NABARANGAPUR",
    ("ODISHA", "SONEPUR"): "SUBARNAPUR",
    ("PUNJAB", "FAZILKA"): "FIROZPUR",
    ("PUNJAB", "FEROZPUR"): "FIROZPUR",
    ("PUNJAB", "PATHANKOT"): "GURDASPUR",
    ("RAJASTHAN", "DHOLPUR"): "DHAULPUR",
    ("RAJASTHAN", "JHUNJHUNU"): "JHUNJHUNUN",
    ("SIKKIM", "EAST SIKKIM"): "EAST DISTRICT",
    ("SIKKIM", "NORTH SIKKIM"): "NORTH DISTRICT",
    ("SIKKIM", "SOUTH SIKKIM"): "SOUTH DISTRICT",
    ("SIKKIM", "WEST SIKKIM"): "WEST DISTRICT",
    ("TAMIL NADU", "KANYAKUMARI"): "KANNIYAKUMARI",
    ("TAMIL NADU", "NILGIRIS"): "THE NILGIRIS",
    ("TAMIL NADU", "TIRUCHIRAPALLI"): "TIRUCHIRAPPALLI",
    ("TAMIL NADU", "TIRUNELVALI"): "TIRUNELVELI",
    ("TAMIL NADU", "TOOTHUKUDI"): "THOOTHUKKUDI",
    ("TAMIL NADU", "VILLUPURAM"): "VILUPPURAM",
    ("TRIPURA", "GOMATI"): "SOUTH TRIPURA",
    ("TRIPURA", "KHOWAI"): "WEST TRIPURA",
    ("TRIPURA", "SEPAHIJALA"): "WEST TRIPURA",
    ("TRIPURA", "UNAKOTI"): "NORTH TRIPURA",
    ("UTTAR PRADESH", "AMETHI"): "SULTANPUR",
    ("UTTAR PRADESH", "BHIM NAGAR"): "MORADABAD",
    ("UTTAR PRADESH", "HATHRAS"): "MAHAMAYA NAGAR",
    ("UTTAR PRADESH", "KANAUJ"): "KANNAUJ",
    ("UTTAR PRADESH", "KUSHI NAGAR"): "KUSHINAGAR",
    ("UTTAR PRADESH", "MAHARAJGANJ"): "MAHRAJGANJ",
    ("UTTAR PRADESH", "PANCHSHEEL NAGAR"): "JYOTIBA PHULE NAGAR",
    ("UTTAR PRADESH", "PRABUDH NAGAR"): "MUZAFFARNAGAR",
    ("UTTAR PRADESH", "RAI BARELI"): "RAE BARELI",
    ("UTTAR PRADESH", "SHRAVASTI"): "SHRAWASTI",
    ("UTTAR PRADESH", "SIDHARTHANAGAR"): "SIDDHARTHNAGAR",
    ("UTTARAKHAND", "DEHRA DUN"): "DEHRADUN",
    ("UTTARAKHAND", "HARIDWAR"): "HARDWAR",
    ("UTTARAKHAND", "UTTAR KASHI"): "UTTARKASHI",
    ("WEST BENGAL", "NORTH 24 PARGANAS"): "NORTH TWENTY FOUR PARGANAS",
    ("WEST BENGAL", "SOUTH 24 PARGANAS"): "SOUTH TWENTY FOUR PARGANAS",
}

STATE_NAME_FIXES = {
    "NCT OF DELHI": "DELHI",
    "ANDAMAN AND NICOBAR": "ANDAMAN AND NICOBAR ISLANDS",
    "JAMMU AND KASHMIR": "JAMMU AND KASHMIR",
}


def fix_state(state: str) -> str:
    s = normalize(state)
    return STATE_NAME_FIXES.get(s, s)


def apply_fix(state: str, district: str) -> str:
    s = fix_state(state)
    d = normalize(district)
    return RBI_TO_CENSUS.get((s, d), d)


# ── Load Census 2011 population ────────────────────────────────────────────────

def load_census() -> pd.DataFrame:
    path = PROCESSED_DIR / "census" / "census2011_district_population.csv"
    df = pd.read_csv(path)
    df["state_key"] = df["state_name_census_clean"].apply(normalize)
    df["district_key"] = df["district_name_census_clean"].apply(normalize)

    # Aggregate all Delhi sub-districts into one row (RBI reports Delhi as one unit)
    delhi = df[df["state_key"] == "DELHI"].agg(
        {"population_total_2011": "sum", "population_female_2011": "sum"}
    )
    delhi_row = pd.DataFrame([{
        "state_key": "DELHI",
        "district_key": "DELHI",
        "state_name_census_clean": "DELHI",
        "district_name_census_clean": "DELHI",
        "population_total_2011": delhi["population_total_2011"],
        "population_female_2011": delhi["population_female_2011"],
    }])
    df = pd.concat([df[df["state_key"] != "DELHI"], delhi_row], ignore_index=True)

    df["merge_key"] = df["state_key"] + "||" + df["district_key"]
    return df[["merge_key", "state_name_census_clean", "district_name_census_clean",
               "population_total_2011", "population_female_2011"]]


# ── Load RBI 2013 ──────────────────────────────────────────────────────────────

def load_rbi_2013() -> pd.DataFrame:
    path = PROCESSED_DIR / "rbi" / "rbi_district_baseline_dec_2013.csv"
    df = pd.read_csv(path)
    df["state_key"] = df["state_name_clean"].apply(fix_state)
    df["district_key"] = df.apply(
        lambda r: apply_fix(r["state_name_clean"], r["district_name_clean"]), axis=1
    )
    df["merge_key"] = df["state_key"] + "||" + df["district_key"]
    return df[["merge_key", "state_name_clean", "district_name_clean",
               "reporting_offices_total", "deposits_total_crore_rs", "credit_total_crore_rs"]]


# ── Load annual deposits 2015-16 ──────────────────────────────────────────────

def load_deposits_2015_16() -> pd.DataFrame:
    path = (PROJECT_ROOT / "data" / "raw" / "rbi" /
            "bank_deposits_of_scbs_region_state_district_bank_group_population_group_wise_annual.xlsx")
    df = pd.read_excel(path, sheet_name="Data", header=None, skiprows=3)
    df.columns = ["_drop", "year", "bank_group", "region", "state", "district",
                  "pop_group", "accounts_thousands", "deposits_crore"]
    df = df.drop(columns="_drop").dropna(subset=["year"])
    df = df[df["year"] == "2015-16"].copy()

    agg = df.groupby(["state", "district"], as_index=False).agg(
        deposits_crore_2015_16=("deposits_crore", "sum"),
        accounts_thousands_2015_16=("accounts_thousands", "sum"),
    )
    agg["state_key"] = agg["state"].apply(fix_state)
    agg["district_key"] = agg.apply(
        lambda r: apply_fix(r["state"], r["district"]), axis=1
    )
    agg["merge_key"] = agg["state_key"] + "||" + agg["district_key"]

    # deduplicate: multiple source rows can normalize to the same merge_key
    agg = agg.groupby("merge_key", as_index=False).agg(
        deposits_crore_2015_16=("deposits_crore_2015_16", "sum"),
        accounts_thousands_2015_16=("accounts_thousands_2015_16", "sum"),
    )
    return agg[["merge_key", "deposits_crore_2015_16", "accounts_thousands_2015_16"]]


# ── Build merged baseline ──────────────────────────────────────────────────────

def build_baseline() -> pd.DataFrame:
    census = load_census()
    rbi13 = load_rbi_2013()
    dep1516 = load_deposits_2015_16()

    # deduplicate RBI 2013 on merge_key before joining
    # (post-2011 districts from same parent share a key; sum their banking vars)
    rbi13_agg = rbi13.groupby("merge_key", as_index=False).agg(
        state_name_clean=("state_name_clean", "first"),
        district_name_clean=("district_name_clean", "first"),
        reporting_offices_total=("reporting_offices_total", "sum"),
        deposits_total_crore_rs=("deposits_total_crore_rs", "sum"),
        credit_total_crore_rs=("credit_total_crore_rs", "sum"),
    )

    merged = rbi13_agg.merge(census, on="merge_key", how="left")
    matched = merged["population_total_2011"].notna().sum()
    total = len(merged)
    print(f"  RBI 2013 → Census match: {matched}/{total} ({100*matched/total:.1f}%)")

    unresolved = merged[merged["population_total_2011"].isna()][
        ["state_name_clean", "district_name_clean"]
    ]
    if len(unresolved):
        print(f"  Still unresolved ({len(unresolved)}):")
        for _, r in unresolved.iterrows():
            print(f"    {r['state_name_clean']} | {r['district_name_clean']}")

    merged = merged.merge(dep1516, on="merge_key", how="left")
    dep_matched = merged["deposits_crore_2015_16"].notna().sum()
    print(f"  2015-16 deposits match: {dep_matched}/{total} ({100*dep_matched/total:.1f}%)")
    print(f"  Final rows: {len(merged)}")

    pop = merged["population_total_2011"]
    merged["branch_density_2013"] = merged["reporting_offices_total"] / pop * 100_000
    merged["deposits_per_capita_2013_rs"] = merged["deposits_total_crore_rs"] * 1e7 / pop
    merged["credit_per_capita_2013_rs"] = merged["credit_total_crore_rs"] * 1e7 / pop
    merged["deposits_per_capita_2015_16_rs"] = merged["deposits_crore_2015_16"] * 1e7 / pop
    merged["accounts_per_capita_2015_16"] = merged["accounts_thousands_2015_16"] * 1000 / pop

    out = merged[[
        "state_name_clean", "district_name_clean",
        "state_name_census_clean", "district_name_census_clean",
        "population_total_2011",
        "reporting_offices_total",
        "deposits_total_crore_rs",
        "credit_total_crore_rs",
        "deposits_crore_2015_16",
        "accounts_thousands_2015_16",
        "branch_density_2013",
        "deposits_per_capita_2013_rs",
        "credit_per_capita_2013_rs",
        "deposits_per_capita_2015_16_rs",
        "accounts_per_capita_2015_16",
    ]].copy()
    out.columns = [
        "rbi_state", "rbi_district",
        "census_state", "census_district",
        "population_2011",
        "reporting_offices_dec2013",
        "deposits_crore_dec2013",
        "credit_crore_dec2013",
        "deposits_crore_2015_16",
        "accounts_thousands_2015_16",
        "branch_density_2013",
        "deposits_per_capita_2013_rs",
        "credit_per_capita_2013_rs",
        "deposits_per_capita_2015_16_rs",
        "accounts_per_capita_2015_16",
    ]
    return out


def main() -> None:
    print("Building RBI banking baseline...")
    baseline = build_baseline()

    out_path = RBI_DIR / "rbi_banking_baseline.csv"
    baseline.to_csv(out_path, index=False)
    print(f"\nSaved → {out_path.name}  ({len(baseline)} rows)")

    print("\nCoverage:")
    for col in ["branch_density_2013", "deposits_per_capita_2015_16_rs", "accounts_per_capita_2015_16"]:
        n = baseline[col].notna().sum()
        print(f"  {col}: {n}/{len(baseline)}")

    print("\nUP sample:")
    up = baseline[baseline["rbi_state"] == "UTTAR PRADESH"]
    print(f"  UP districts: {len(up)}")
    print(up[["rbi_district", "population_2011", "branch_density_2013",
              "deposits_per_capita_2015_16_rs", "accounts_per_capita_2015_16"]].head(8).to_string(index=False))


if __name__ == "__main__":
    main()
