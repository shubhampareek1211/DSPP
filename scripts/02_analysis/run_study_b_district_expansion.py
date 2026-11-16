"""
Study B: District banking expansion (2013 → 2019-20) and NFHS-5 outcomes.

Extends the national cross-section (Study 0) by adding a banking GROWTH measure
alongside the level. Districts that expanded banking faster during the PMMVY
rollout window (2017-20) may show systematically better women's outcomes in NFHS-5.

Specification:
    Y_d = alpha + beta_1 * level_2013_d + beta_2 * growth_d + controls_d + state_FE + eps_d

    growth_d = log(branch_density_2020 / branch_density_2013)
             = percentage-point change in log branch density over the period

Also tested standalone: growth_d as the only banking regressor (without level).

Data:
    Level (2013): RBI Statement 16 (Dec 2013), as in Study 0.
    Level + growth (2019-20): RBI Statement 4a Q4 2019-20 — 741 districts.
    Outcomes: NFHS-5 district factsheet (699 districts).
    Population: Census 2011.

Sample: ~480-530 districts matched across all three sources.
"""

from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def norm(s):
    return (str(s).upper().strip()
            .replace("&", "AND").replace(".", "").replace(",", "")
            .replace("-", " ").replace("  ", " ").strip())


NFHS_TO_RBI_STATE = {
    "MAHARASTRA": "MAHARASHTRA",
    "NCT OF DELHI": "NCT OF DELHI",
    "TELANGANA": "ANDHRA PRADESH",
}

NFHS_TO_RBI_DIST = {
    "ANUGUL": "ANGUL", "BAUDH": "BOUDH", "DEBAGARH": "DEOGARH",
    "JAGATSINGHAPUR": "JAGATSINGHPUR", "JAJAPUR": "JAJPUR",
    "KENDUJHAR": "KEONJHAR", "KHORDHA": "KHURDA",
    "NABARANGAPUR": "NAWRANGPUR", "NUAPADA": "NAWAPARA", "SUBARNAPUR": "SONEPUR",
    "JANJGIR   CHAMPA": "JANJGIR CHAMPA", "JANJGIR - CHAMPA": "JANJGIR CHAMPA",
    "UTTAR BASTAR KANKER": "KANKER", "KABIRDHAM": "KAWARDHA", "KABEERDHAM": "KAWARDHA",
    "BENGALURU RURAL": "BANGALORE RURAL", "BENGALURU URBAN": "BANGALORE URBAN",
    "BELAGAVI": "BELGAUM", "BALLARI": "BELLARY", "VIJAYAPURA": "BIJAPUR",
    "KALABURAGI": "GULBARGA", "MYSURU": "MYSORE", "SHIVAMOGGA": "SHIMOGA",
    "TUMAKURU": "TUMKUR", "HUBBALLI DHARWAD": "DHARWAD",
    "PRAYAGRAJ": "ALLAHABAD", "AYODHYA": "FAIZABAD", "AMROHA": "JYOTIBA PHULE NAGAR",
    "HATHRAS": "MAHAMAYA NAGAR", "KASGANJ": "KANSHIRAM NAGAR",
    "KUSHI NAGAR": "KUSHINAGAR", "BHADOHI": "SANT RAVIDAS NAGAR",
    "SAMBHAL": "MORADABAD", "SHAMLI": "MUZAFFARNAGAR", "HAPUR": "GHAZIABAD",
    "BISWANATH": "SONITPUR", "CHARAIDEO": "SIBSAGAR", "HOJAI": "NAGAON",
    "MAJULI": "JORHAT", "SIVASAGAR": "SIBSAGAR",
    "SOUTH SALMARA MANCACHAR": "DHUBRI", "WEST KARBI ANGLONG": "KARBI ANGLONG",
    "RAMGARH": "HAZARIBAG", "KHUNTI": "RANCHI",
    "TENKASI": "TIRUNELVELI", "RANIPET": "VELLORE", "TIRUPATHUR": "VELLORE",
    "SRI POTTI SRIRAMULU NELLO": "NELLORE", "Y S R": "KADAPA", "YSR": "KADAPA",
}


def load_rbi_2013():
    rbi = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "rbi" / "rbi_district_baseline_dec_2013.csv")
    census = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "census" / "census2011_district_population.csv")
    rbi["state_n"] = rbi["state_name_clean"].apply(norm)
    rbi["dist_n"]  = rbi["district_name_clean"].apply(norm)
    census["state_n"] = census["state_name_census_clean"].apply(norm)
    census["dist_n"]  = census["district_name_census_clean"].apply(norm)

    rbi_c = rbi.merge(census[["state_n", "dist_n", "population_total_2011"]],
                      on=["state_n", "dist_n"], how="left")
    agg = (rbi_c.groupby(["state_n", "dist_n"])
           .agg(offices_2013=("reporting_offices_total", "sum"),
                deposits_cr_2013=("deposits_total_crore_rs", "sum"),
                pop=("population_total_2011", "first"))
           .reset_index())
    agg["branch_density_2013"] = agg["offices_2013"] / (agg["pop"] / 100_000)
    agg["deposits_pc_2013"]    = (agg["deposits_cr_2013"] * 1e7) / agg["pop"]
    return agg


def load_rbi4a_2020():
    rbi4a = pd.read_excel(
        PROJECT_ROOT / "data" / "raw" / "rbi" /
        "rbi_statement_4a_district_reporting_offices_deposits_credit_2017_2022.xlsx",
        header=None
    )
    row5 = rbi4a.iloc[5].tolist()
    row6 = rbi4a.iloc[6].tolist()

    period_labels, cur = [], None
    for v in row5:
        if pd.notna(v) and str(v).strip() not in ("Region","State or UTs","District ",""):
            cur = str(v).strip()
        period_labels.append(cur)

    col_map = {}
    for i, (p, s) in enumerate(zip(period_labels, row6)):
        s_c = str(s).replace("\n", " ").strip() if pd.notna(s) else ""
        if p and s_c:
            col_map[(p, s_c)] = i

    data = rbi4a.iloc[7:][rbi4a.iloc[7:, 2].notna()].copy()
    period = "2019-20:Q4"
    off_i = col_map.get((period, "Number of Reporting Offices"))
    dep_i = col_map.get((period, "Deposit"))

    records = []
    for _, row in data.iterrows():
        records.append({
            "state_n": norm(str(row[2])),
            "dist_n":  norm(str(row[3])),
            "offices_2020": pd.to_numeric(row[off_i], errors="coerce"),
            "deposits_cr_2020": pd.to_numeric(row[dep_i], errors="coerce"),
        })
    return pd.DataFrame(records)


def load_nfhs5():
    nf5 = pd.read_excel(
        PROJECT_ROOT / "data" / "raw" / "nfhs_support" / "nfhs5_india_districts_factsheet_data.xls"
    )
    nf5["state_orig_n"] = nf5["State/UT"].apply(norm)
    nf5["state_n"]      = nf5["state_orig_n"].replace(NFHS_TO_RBI_STATE)
    nf5["dist_raw_n"]   = nf5["District Names"].apply(norm)
    nf5["dist_n"]       = nf5["dist_raw_n"].replace(NFHS_TO_RBI_DIST)

    col_map = {
        "Women age 20-24 years married before age 18 years (%)": "child_marriage",
        "Women age 15-19 years who were already mothers or pregnant at the time of the survey (%)": "teen_pregnancy",
        "Women (age 15-49) who are literate4 (%)": "literacy",
        "Women (age 15-49)  with 10 or more years of schooling (%)": "schooling_10plus",
        "Population living in households with electricity (%)": "electricity_pct",
        "Households using clean fuel for cooking3 (%)": "clean_fuel_pct",
        "Female population age 6 years and above who ever attended school (%)": "school_attended_f",
    }
    nf5 = nf5.rename(columns=col_map)
    nf5["state_fe"] = nf5["state_orig_n"]
    return nf5


def build_dataset():
    rbi13  = load_rbi_2013()
    rbi20  = load_rbi4a_2020()
    nf5    = load_nfhs5()
    census = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "census" / "census2011_district_population.csv")
    census["state_n"] = census["state_name_census_clean"].apply(norm)
    census["dist_n"]  = census["district_name_census_clean"].apply(norm)

    # Merge 2020 data with census population
    rbi20 = rbi20.merge(census[["state_n","dist_n","population_total_2011"]],
                        on=["state_n","dist_n"], how="left")
    rbi20["branch_density_2020"] = rbi20["offices_2020"] / (rbi20["population_total_2011"]/100_000)
    rbi20["deposits_pc_2020"]    = (rbi20["deposits_cr_2020"]*1e7) / rbi20["population_total_2011"]

    # Delhi: RBI 4a has NCT OF DELHI as single entity — assign to all NFHS-5 Delhi sub-districts
    delhi_row = rbi20[rbi20["dist_n"] == "NCT OF DELHI"].copy()
    delhi_nfhs = nf5[nf5["state_orig_n"] == "NCT OF DELHI"]["dist_n"].unique()
    extras = [delhi_row.assign(dist_n=d) for d in delhi_nfhs if d != "NCT OF DELHI"]
    if extras:
        rbi20 = pd.concat([rbi20] + extras, ignore_index=True)

    # Merge 2013 baseline with 2020
    joint = rbi13.merge(
        rbi20[["state_n","dist_n","offices_2020","deposits_cr_2020","branch_density_2020","deposits_pc_2020"]],
        on=["state_n","dist_n"], how="left"
    )

    # Banking growth measures
    joint["log_branch_growth"] = np.log(
        joint["branch_density_2020"].replace(0, np.nan) /
        joint["branch_density_2013"].replace(0, np.nan)
    )
    joint["log_deposits_growth"] = np.log(
        joint["deposits_pc_2020"].replace(0, np.nan) /
        joint["deposits_pc_2013"].replace(0, np.nan)
    )
    joint["log_branch_2013"]  = np.log(joint["branch_density_2013"].replace(0, np.nan))
    joint["log_branch_2020"]  = np.log(joint["branch_density_2020"].replace(0, np.nan))

    # Merge into NFHS-5
    merged = nf5.merge(
        joint[["state_n","dist_n","branch_density_2013","branch_density_2020",
               "deposits_pc_2013","deposits_pc_2020",
               "log_branch_2013","log_branch_2020",
               "log_branch_growth","log_deposits_growth"]],
        on=["state_n","dist_n"], how="left"
    )

    # Standardise
    for v in ["log_branch_2013","log_branch_2020","log_branch_growth","log_deposits_growth"]:
        s = merged[v]
        merged[f"{v}_std"] = (s - s.mean()) / s.std()

    return merged


def pick(m, key):
    if key in m.params.index:
        return m.params[key], m.bse[key], m.pvalues[key]
    cands = [k for k in m.params.index if key in k]
    if not cands: return np.nan, np.nan, np.nan
    return m.params[cands[-1]], m.bse[cands[-1]], m.pvalues[cands[-1]]


def stars(p):
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def run_ols(df, outcome, regressors, controls=True):
    sub = df.copy()
    for r in regressors:
        sub = sub[sub[r].notna()]
    sub = sub[sub[outcome].notna()].copy()

    ctrl = ""
    if controls:
        for c in ["electricity_pct","clean_fuel_pct","school_attended_f"]:
            if sub[c].notna().mean() > 0.5:
                ctrl += f" + {c}"

    rhs = " + ".join(regressors)
    formula = f"{outcome} ~ {rhs}{ctrl} + C(state_fe)"
    m = smf.ols(formula, data=sub).fit(cov_type="HC3")
    results = {}
    for r in regressors:
        b, se, p = pick(m, r)
        results[r] = (b, se, p)
    results["n"]  = len(sub)
    results["r2"] = m.rsquared
    return results


OUTCOMES = {
    "child_marriage":   "Child marriage rate (%)",
    "teen_pregnancy":   "Teen pregnancy/motherhood (%)",
    "literacy":         "Women's literacy rate (%)",
    "schooling_10plus": "Women with 10+ yrs schooling (%)",
}


def main():
    print("Building district expansion dataset...")
    df = build_dataset()
    n_both = df[df["log_branch_growth"].notna()].shape[0]
    n_13only = df[df["log_branch_2013"].notna() & df["log_branch_growth"].isna()].shape[0]
    print(f"  Districts matched to both 2013 and 2019-20 RBI: {n_both}")
    print(f"  Districts with 2013 only (new districts post-2013): {n_13only}")
    print()

    # ── TABLE 1: Level 2013 vs Level 2020 comparison ──────────────────────────
    print("=" * 80)
    print("TABLE 1: Level specification — 2013 baseline vs 2019-20 branch density")
    print("(Cross-sectional; state FE + controls; HC3 SEs)")
    print(f"  {'Outcome':<36} {'2013 level coeff':>18} {'2020 level coeff':>18} {'N':>6}")
    print("-" * 80)

    rows = []
    for col, label in OUTCOMES.items():
        r13 = run_ols(df, col, ["log_branch_2013_std"])
        r20 = run_ols(df, col, ["log_branch_2020_std"])
        b13, se13, p13 = r13["log_branch_2013_std"]
        b20, se20, p20 = r20["log_branch_2020_std"]
        s13 = f"{b13:+.3f}{stars(p13)}"
        s20 = f"{b20:+.3f}{stars(p20)}"
        print(f"  {label:<36} {s13:>18} {s20:>18} {r13['n']:>6}")
        rows.append({"outcome": col, "regressor": "log_branch_2013", "b": b13, "se": se13, "p": p13, "n": r13["n"]})
        rows.append({"outcome": col, "regressor": "log_branch_2020", "b": b20, "se": se20, "p": p20, "n": r20["n"]})
    print()

    # ── TABLE 2: Banking growth 2013→2020 as standalone regressor ────────────
    print("=" * 80)
    print("TABLE 2: Banking growth (log branch density change 2013→2019-20)")
    print("(Cross-sectional; state FE + controls; HC3 SEs)")
    print(f"  {'Outcome':<36} {'Coeff (growth)':>16} {'SE':>8} {'p':>7} {'N':>6}")
    print("-" * 80)

    for col, label in OUTCOMES.items():
        r = run_ols(df, col, ["log_branch_growth_std"])
        b, se, p = r["log_branch_growth_std"]
        sig = stars(p)
        print(f"  {label:<36} {b:>+16.3f}{sig:<4} {se:>8.3f} {p:>7.3f} {r['n']:>6}")
        rows.append({"outcome": col, "regressor": "log_branch_growth", "b": b, "se": se, "p": p, "n": r["n"]})
    print()

    # ── TABLE 3: Level + Growth jointly ──────────────────────────────────────
    print("=" * 80)
    print("TABLE 3: Level (2013) + Growth jointly — decomposing banking effects")
    print(f"  {'Outcome':<36} {'Level 2013':>14} {'Growth 2013→20':>16} {'N':>6}")
    print("-" * 80)

    for col, label in OUTCOMES.items():
        r = run_ols(df, col, ["log_branch_2013_std","log_branch_growth_std"])
        bl, sel, pl = r["log_branch_2013_std"]
        bg, seg, pg = r["log_branch_growth_std"]
        sl = f"{bl:+.3f}{stars(pl)}"
        sg = f"{bg:+.3f}{stars(pg)}"
        print(f"  {label:<36} {sl:>14} {sg:>16} {r['n']:>6}")
        rows.append({"outcome": col, "regressor": "joint_level_growth",
                     "b_level": bl, "p_level": pl, "b_growth": bg, "p_growth": pg, "n": r["n"]})
    print()

    # ── TABLE 4: Deposits growth as robustness ────────────────────────────────
    print("=" * 80)
    print("TABLE 4: Deposits per capita growth (2013→2019-20) — robustness check")
    print(f"  {'Outcome':<36} {'Coeff':>14} {'SE':>8} {'p':>7} {'N':>6}")
    print("-" * 80)

    for col, label in OUTCOMES.items():
        r = run_ols(df, col, ["log_deposits_growth_std"])
        b, se, p = r["log_deposits_growth_std"]
        sig = stars(p)
        print(f"  {label:<36} {b:>+14.3f}{sig:<4} {se:>8.3f} {p:>7.3f} {r['n']:>6}")
        rows.append({"outcome": col, "regressor": "log_deposits_growth", "b": b, "se": se, "p": p, "n": r["n"]})
    print()

    # ── Distribution of banking growth ───────────────────────────────────────
    print("=" * 80)
    print("Banking growth distribution (log branch density change 2013→2019-20)")
    g = df["log_branch_growth"].dropna()
    print(f"  N districts with growth data: {len(g)}")
    print(f"  Mean: {g.mean():+.3f}  SD: {g.std():.3f}  p10: {g.quantile(0.1):+.3f}"
          f"  p50: {g.median():+.3f}  p90: {g.quantile(0.9):+.3f}")
    print(f"  Positive growth (expanded): {(g > 0).sum()} districts ({(g>0).mean()*100:.0f}%)")
    print(f"  Negative growth (contracted): {(g < 0).sum()} districts ({(g<0).mean()*100:.0f}%)")

    pd.DataFrame([r for r in rows if "b_level" not in r])\
        .to_csv(RESULTS_DIR / "study_b_district_expansion_results.csv", index=False)
    print("\nSaved → results/tables/study_b_district_expansion_results.csv")
    print("Done.")


if __name__ == "__main__":
    main()
