"""
All-India district cross-sectional analysis.

Design
------
Unit of observation: district d in India (NFHS-5 factsheet, 2019-21).
Estimation: cross-sectional OLS with state fixed effects.

    Y_d = alpha + beta * banking_d + controls_d + state_FE + epsilon_d

banking_d = pre-treatment (2013) RBI branch density per 100,000 population.
            Also tested: deposits per capita (2013).

Outcomes (from NFHS-5 district factsheet):
    child_marriage    — Women 20-24 married before age 18 (%)     [lower = better]
    teen_pregnancy    — Women 15-19 who are/were mothers (%)      [lower = better]
    literacy          — Women 15-49 who are literate (%)          [higher = better]
    schooling_10plus  — Women with 10+ years of schooling (%)     [higher = better]

Controls (from NFHS-5 factsheet):
    electricity_pct   — Households with electricity
    clean_fuel_pct    — Households using clean cooking fuel
    school_attended_f — Female population age 6+ ever attended school

Identification: Within-state variation in banking density predicts outcomes.
Caveat: This is cross-sectional — not causal. Omitted variables (e.g. economic
development, urbanisation) may drive both banking and outcomes. State FE partially
addresses this by removing state-level confounders.

Sample: 699 NFHS-5 districts; ~516-530 matched to RBI 2013 baseline.
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


# ── Name normalisation ─────────────────────────────────────────────────────────

def norm(s: str) -> str:
    return (str(s).upper().strip()
            .replace("&", "AND").replace(".", "").replace(",", "")
            .replace("-", " ").replace("  ", " ").strip())


# NFHS-5 state → RBI state
NFHS_TO_RBI_STATE = {
    "MAHARASTRA":                            "MAHARASHTRA",
    "NCT OF DELHI":                          "NCT OF DELHI",   # handle via district fix
    "TELANGANA":                             "ANDHRA PRADESH", # pre-bifurcation in 2013
}

# NFHS-5 district name → RBI district name (within same state after state mapping)
NFHS_TO_RBI_DIST = {
    # Odisha
    "ANUGUL":          "ANGUL",
    "BAUDH":           "BOUDH",
    "DEBAGARH":        "DEOGARH",
    "JAGATSINGHAPUR":  "JAGATSINGHPUR",
    "JAJAPUR":         "JAJPUR",
    "KENDUJHAR":       "KEONJHAR",
    "KHORDHA":         "KHURDA",
    "NABARANGAPUR":    "NAWRANGPUR",
    "NUAPADA":         "NAWAPARA",
    "SUBARNAPUR":      "SONEPUR",
    # Chhattisgarh
    "JANJGIR   CHAMPA":   "JANJGIR CHAMPA",
    "JANJGIR - CHAMPA":   "JANJGIR CHAMPA",
    "UTTAR BASTAR KANKER":"KANKER",
    "KABIRDHAM":       "KAWARDHA",
    "KABEERDHAM":      "KAWARDHA",
    # Karnataka
    "BENGALURU RURAL": "BANGALORE RURAL",
    "BENGALURU URBAN": "BANGALORE URBAN",
    "BELAGAVI":        "BELGAUM",
    "BALLARI":         "BELLARY",
    "VIJAYAPURA":      "BIJAPUR",
    "KALABURAGI":      "GULBARGA",
    "MYSURU":          "MYSORE",
    "SHIVAMOGGA":      "SHIMOGA",
    "TUMAKURU":        "TUMKUR",
    "HUBBALLI DHARWAD":"DHARWAD",
    # Gujarat
    "BOTAD":           "BHAVNAGAR",
    # UP renames
    "PRAYAGRAJ":       "ALLAHABAD",
    "AYODHYA":         "FAIZABAD",
    "AMROHA":          "JYOTIBA PHULE NAGAR",
    "HATHRAS":         "MAHAMAYA NAGAR",
    "KASGANJ":         "KANSHIRAM NAGAR",
    "KUSHI NAGAR":     "KUSHINAGAR",
    "BHADOHI":         "SANT RAVIDAS NAGAR",
    "SAMBHAL":         "MORADABAD",
    "SHAMLI":          "MUZAFFARNAGAR",
    "HAPUR":           "GHAZIABAD",
    # Assam new districts — map back to parent
    "BISWANATH":       "SONITPUR",
    "CHARAIDEO":       "SIBSAGAR",
    "HOJAI":           "NAGAON",
    "MAJULI":          "JORHAT",
    "SIVASAGAR":       "SIBSAGAR",
    "SOUTH SALMARA MANCACHAR": "DHUBRI",
    "WEST KARBI ANGLONG": "KARBI ANGLONG",
    # Jharkhand new
    "RAMGARH":         "HAZARIBAG",
    "KHUNTI":          "RANCHI",
    # Tamil Nadu new
    "TENKASI":         "TIRUNELVELI",
    "RANIPET":         "VELLORE",
    "TIRUPATHUR":      "VELLORE",
    # Andhra Pradesh renames
    "SRI POTTI SRIRAMULU NELLO": "NELLORE",
    "Y S R":           "KADAPA",
    "YSR":             "KADAPA",
    "Y.S.R.":          "KADAPA",
}


def load_and_merge() -> pd.DataFrame:
    nf5    = pd.read_excel(PROJECT_ROOT / "data" / "raw" / "nfhs_support" /
                           "nfhs5_india_districts_factsheet_data.xls")
    rbi    = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "rbi" / "rbi_district_baseline_dec_2013.csv")
    census = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "census" / "census2011_district_population.csv")

    # Normalise RBI
    rbi["state_n"] = rbi["state_name_clean"].apply(norm)
    rbi["dist_n"]  = rbi["district_name_clean"].apply(norm)

    # Normalise census
    census["state_n"] = census["state_name_census_clean"].apply(norm)
    census["dist_n"]  = census["district_name_census_clean"].apply(norm)

    # Merge RBI + census population
    rbi_c = rbi.merge(census[["state_n", "dist_n", "population_total_2011"]],
                      on=["state_n", "dist_n"], how="left")
    rbi_agg = (rbi_c.groupby(["state_n", "dist_n"])
               .agg(offices=("reporting_offices_total", "sum"),
                    deposits_cr=("deposits_total_crore_rs", "sum"),
                    pop=("population_total_2011", "first"))
               .reset_index())
    rbi_agg["branch_density"] = rbi_agg["offices"] / (rbi_agg["pop"] / 100_000)
    rbi_agg["deposits_pc"]    = (rbi_agg["deposits_cr"] * 1e7) / rbi_agg["pop"]
    rbi_agg["log_branch"]     = np.log(rbi_agg["branch_density"].replace(0, np.nan))
    rbi_agg["log_deposits"]   = np.log(rbi_agg["deposits_pc"].replace(0, np.nan))

    # Normalise NFHS-5
    nf5["state_orig_n"] = nf5["State/UT"].apply(norm)
    nf5["state_n"]      = nf5["state_orig_n"].replace(NFHS_TO_RBI_STATE)
    nf5["dist_raw_n"]   = nf5["District Names"].apply(norm)
    nf5["dist_n"]       = nf5["dist_raw_n"].replace(NFHS_TO_RBI_DIST)

    # Delhi special: RBI has a single row for NCT OF DELHI
    delhi_rbi = rbi_agg[rbi_agg["dist_n"] == "NCT OF DELHI"].copy()
    delhi_nfhs = nf5[nf5["state_orig_n"] == "NCT OF DELHI"]["dist_n"].unique()
    extras = []
    for dd in delhi_nfhs:
        row = delhi_rbi.copy()
        row["dist_n"] = dd
        extras.append(row)
    if extras:
        rbi_agg = pd.concat([rbi_agg] + extras, ignore_index=True)

    # First-pass merge
    merged = nf5.merge(
        rbi_agg[["state_n", "dist_n", "branch_density", "deposits_pc",
                 "log_branch", "log_deposits", "offices", "pop"]],
        on=["state_n", "dist_n"], how="left"
    )

    # Rename factsheet columns to short names
    col_map = {
        "Women age 20-24 years married before age 18 years (%)":
            "child_marriage",
        "Women age 15-19 years who were already mothers or pregnant at the time of the survey (%)":
            "teen_pregnancy",
        "Women (age 15-49) who are literate4 (%)":
            "literacy",
        "Women (age 15-49)  with 10 or more years of schooling (%)":
            "schooling_10plus",
        "Population living in households with electricity (%)":
            "electricity_pct",
        "Households using clean fuel for cooking3 (%)":
            "clean_fuel_pct",
        "Female population age 6 years and above who ever attended school (%)":
            "school_attended_f",
    }
    merged = merged.rename(columns=col_map)

    # State FE code (use original state name for readability)
    merged["state_fe"] = merged["state_orig_n"]

    # Standardise banking regressors
    for v in ["branch_density", "deposits_pc", "log_branch", "log_deposits"]:
        s = merged[v]
        merged[f"{v}_std"] = (s - s.mean()) / s.std()

    return merged


# ── Estimation ─────────────────────────────────────────────────────────────────

def pick(m, key):
    if key in m.params.index:
        return m.params[key], m.bse[key], m.pvalues[key]
    cands = [k for k in m.params.index if key in k]
    if not cands:
        return np.nan, np.nan, np.nan
    k = cands[-1]
    return m.params[k], m.bse[k], m.pvalues[k]


def stars(p):
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def run_ols(df, outcome, regressor, controls=True, state_fe=True):
    sub = df[df[outcome].notna() & df[regressor].notna()].copy()
    ctrl = ""
    if controls:
        for c in ["electricity_pct", "clean_fuel_pct", "school_attended_f"]:
            if sub[c].notna().mean() > 0.5:
                ctrl += f" + {c}"
    fe = " + C(state_fe)" if state_fe else ""
    formula = f"{outcome} ~ {regressor}{ctrl}{fe}"
    m = smf.ols(formula, data=sub).fit(
        cov_type="HC3"  # heteroskedasticity-robust (no clustering needed — one obs per district)
    )
    b, se, p = pick(m, regressor)
    return {"b": b, "se": se, "p": p, "n": len(sub), "r2": m.rsquared}


# ── Main ───────────────────────────────────────────────────────────────────────

OUTCOMES = {
    "child_marriage":   "Child marriage rate (women 20-24 wed <18)",
    "teen_pregnancy":   "Teen pregnancy/motherhood (15-19)",
    "literacy":         "Women's literacy rate (15-49)",
    "schooling_10plus": "Women with 10+ yrs schooling (15-49)",
}

REGRESSORS = {
    "branch_density_std":  "Branch density 2013 (std)",
    "log_branch_std":      "Log branch density 2013 (std)",
    "deposits_pc_std":     "Deposits per capita 2013 (std)",
}


def main():
    print("Building national district dataset...")
    df = load_and_merge()
    matched = df["branch_density"].notna().sum()
    print(f"  NFHS-5 districts: {len(df)}")
    print(f"  Matched to RBI 2013: {matched} ({matched/len(df)*100:.1f}%)")
    print(f"  States: {df['state_orig_n'].nunique()}")
    print()

    # Descriptive: banking density and outcomes by tercile
    print("=== Outcomes by Banking Density Tercile (state FE removed, raw means) ===")
    df_m = df[df["branch_density"].notna()].copy()
    df_m["banking_t"] = pd.qcut(df_m["branch_density"], 3, labels=["Low", "Mid", "High"])
    print(f"  {'Outcome':<44} {'Low':>8} {'Mid':>8} {'High':>8} {'Hi−Lo':>8}")
    for col, label in OUTCOMES.items():
        t = df_m.groupby("banking_t", observed=True)[col].mean()
        diff = t.get("High", np.nan) - t.get("Low", np.nan)
        print(f"  {label:<44} {t.get('Low',np.nan):>8.1f} {t.get('Mid',np.nan):>8.1f}"
              f" {t.get('High',np.nan):>8.1f} {diff:>+8.1f}")
    print()

    # ── TABLE 1: Branch density → outcomes (state FE + controls) ─────────────
    print("=" * 80)
    print("TABLE 1: Pre-treatment branch density (2013) and women's outcomes")
    print("(Cross-sectional OLS; state FE + controls; HC3 SEs; N ≈ 516 districts)")
    print(f"  {'Outcome':<44} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>6} {'R²':>6}")
    print("-" * 80)

    rows = []
    for col, label in OUTCOMES.items():
        r = run_ols(df, col, "branch_density_std")
        sig = stars(r["p"])
        print(f"  {label:<44} {r['b']:>+10.3f}{sig:<4} {r['se']:>8.3f} "
              f"{r['p']:>7.3f} {r['n']:>6} {r['r2']:>6.3f}")
        rows.append({"outcome": col, "regressor": "branch_density_std", **r})
    print()

    # ── TABLE 2: Log branch density (more robust to outliers) ────────────────
    print("=" * 80)
    print("TABLE 2: Log branch density (2013) and women's outcomes")
    print(f"  {'Outcome':<44} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>6}")
    print("-" * 80)

    for col, label in OUTCOMES.items():
        r = run_ols(df, col, "log_branch_std")
        sig = stars(r["p"])
        print(f"  {label:<44} {r['b']:>+10.3f}{sig:<4} {r['se']:>8.3f} "
              f"{r['p']:>7.3f} {r['n']:>6}")
        rows.append({"outcome": col, "regressor": "log_branch_std", **r})
    print()

    # ── TABLE 3: Deposits per capita as alternative banking measure ───────────
    print("=" * 80)
    print("TABLE 3: Deposits per capita 2013 and women's outcomes")
    print(f"  {'Outcome':<44} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>6}")
    print("-" * 80)

    for col, label in OUTCOMES.items():
        r = run_ols(df, col, "deposits_pc_std")
        sig = stars(r["p"])
        print(f"  {label:<44} {r['b']:>+10.3f}{sig:<4} {r['se']:>8.3f} "
              f"{r['p']:>7.3f} {r['n']:>6}")
        rows.append({"outcome": col, "regressor": "deposits_pc_std", **r})
    print()

    # ── TABLE 4: No state FE (OLS only) for comparison ───────────────────────
    print("=" * 80)
    print("TABLE 4: Without state FE — raw correlation (branch density, std)")
    print(f"  {'Outcome':<44} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>6} {'R²':>6}")
    print("-" * 80)

    for col, label in OUTCOMES.items():
        r = run_ols(df, col, "branch_density_std", state_fe=False)
        sig = stars(r["p"])
        print(f"  {label:<44} {r['b']:>+10.3f}{sig:<4} {r['se']:>8.3f} "
              f"{r['p']:>7.3f} {r['n']:>6} {r['r2']:>6.3f}")
        rows.append({"outcome": col, "regressor": "branch_density_nofixed", **r})
    print()

    # ── Heterogeneity: state-level summary ───────────────────────────────────
    print("=" * 80)
    print("State-level summary: banking density vs child marriage (partial corr)")
    state_means = df_m.groupby("state_orig_n").agg(
        branch_density=("branch_density","mean"),
        child_marriage=("child_marriage","mean"),
        literacy=("literacy","mean"),
        n_districts=("child_marriage","count"),
    ).reset_index().sort_values("branch_density")
    print(state_means[["state_orig_n","branch_density","child_marriage","literacy","n_districts"]]
          .rename(columns={"state_orig_n":"state","branch_density":"branch/100k",
                            "child_marriage":"child_marr%","literacy":"literacy%"})
          .to_string(index=False))

    # Save
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "national_crosssection_results.csv", index=False)
    df_m[["state_orig_n","dist_raw_n","branch_density","deposits_pc",
          "child_marriage","teen_pregnancy","literacy","schooling_10plus"]]\
        .to_csv(RESULTS_DIR / "national_district_dataset.csv", index=False)
    print("\nSaved → results/tables/national_crosssection_results.csv, "
          "results/tables/national_district_dataset.csv")
    print("Done.")


if __name__ == "__main__":
    main()
