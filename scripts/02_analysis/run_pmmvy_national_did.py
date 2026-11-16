"""
All-India PMMVY Treatment Intensity DiD
PMMVY launched January 2017 (national). All states treated.
Identification: variation in PMMVY enrollment intensity across states.
Design: individual-level DiD, treatment = state PMMVY intensity × post (NFHS-5)
"""
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── 0. helpers ────────────────────────────────────────────────────────────────

def clustered_ols(formula, data, cluster_var):
    """OLS with cluster-robust SEs; returns (b, se, p, n)."""
    mod = smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data[cluster_var]}
    )
    return mod

def summarize(mod, var):
    b  = mod.params[var]
    se = mod.bse[var]
    p  = mod.pvalues[var]
    n  = int(mod.nobs)
    stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ("†" if p < 0.10 else "")
    return b, se, p, n, stars

# ── 1. PMMVY state intensity ──────────────────────────────────────────────────

def load_pmmvy_intensity():
    pmmvy = pd.read_csv(
        PROJECT_ROOT / "data" / "raw" / "pmmvy" / "state_wise_pmmvy_beneficiaries_upto_2024.csv"
    )
    pmmvy.columns = ["sl", "state_raw", "osc", "whl", "pmmvy_ben"]
    # Drop total row and zero/missing data states
    pmmvy = pmmvy[pmmvy["state_raw"].str.strip() != "Total"].copy()

    # Normalise names to match NFHS
    name_map = {
        "Andaman and Nicobar Islands":               "ANDAMAN AND NICOBAR ISLANDS",
        "Andhra Pradesh":                            "ANDHRA PRADESH",
        "Arunachal Pradesh":                         "ARUNACHAL PRADESH",
        "Assam":                                     "ASSAM",
        "Bihar":                                     "BIHAR",
        "Chandigarh":                                "CHANDIGARH",
        "Chhattisgarh":                              "CHHATTISGARH",
        "Dadra Nagar Haveli and Daman and Diu":      "DADRA AND NAGAR HAVELI AND DAMAN AND DIU",
        "Delhi":                                     "DELHI",
        "Goa":                                       "GOA",
        "Gujarat":                                   "GUJARAT",
        "Haryana":                                   "HARYANA",
        "Himachal Pradesh":                          "HIMACHAL PRADESH",
        "Jammu and Kashmir":                         "JAMMU AND KASHMIR",
        "Jharkhand":                                 "JHARKHAND",
        "Karnataka":                                 "KARNATAKA",
        "Kerala":                                    "KERALA",
        "Ladakh":                                    "LADAKH",
        "Lakshadweep":                               "LAKSHADWEEP",
        "Madhya Pradesh":                            "MADHYA PRADESH",
        "Maharashtra":                               "MAHARASHTRA",
        "Manipur":                                   "MANIPUR",
        "Meghalaya":                                 "MEGHALAYA",
        "Mizoram":                                   "MIZORAM",
        "Nagaland":                                  "NAGALAND",
        "Odisha":                                    "ODISHA",
        "Puducherry":                                "PUDUCHERRY",
        "Punjab":                                    "PUNJAB",
        "Rajasthan":                                 "RAJASTHAN",
        "Sikkim":                                    "SIKKIM",
        "Tamil Nadu":                                "TAMIL NADU",
        "Telangana":                                 "TELANGANA",
        "Tripura":                                   "TRIPURA",
        "Uttar Pradesh":                             "UTTAR PRADESH",
        "Uttarakhand":                               "UTTARAKHAND",
        "West Bengal":                               "WEST BENGAL",
    }
    pmmvy["state_n"] = pmmvy["state_raw"].str.strip().map(name_map)

    # Drop only the aggregate "Total" row; keep all states including zero-enrollment ones
    pmmvy = pmmvy[pmmvy["state_n"].notna()].copy()

    # --- Telangana / AP correction ---
    # Telangana opted OUT of PMMVY (0 beneficiaries — runs its own state scheme).
    # The source file correctly records Telangana = 0 and AP = 1,748,099.
    # AP's full enrollment is attributed to AP (residual post-2014 state) since
    # Telangana deliberately did not implement PMMVY.
    # Telangana row already exists in the file with pmmvy_ben = 0; no imputation needed.

    # --- Odisha correction ---
    # Odisha records 6 PMMVY beneficiaries (runs MAMATA scheme instead).
    # Keep as 0-intensity non-participant; do not filter out.
    pmmvy.loc[pmmvy["state_n"] == "ODISHA", "pmmvy_ben"] = 0

    return pmmvy[["state_n", "pmmvy_ben"]].reset_index(drop=True)


def load_census_female_pop():
    census = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "census" / "census2011_district_population.csv")
    st = (
        census.groupby("state_name_census_clean")["population_female_2011"]
        .sum()
        .reset_index()
    )
    st.columns = ["state_n", "female_pop_2011"]
    # Add Telangana (carved from AP after 2011)
    # Telangana = ~14.7M female (based on 35M total / 2.38 sex ratio adjustment)
    # AP residual = ~27.4M female
    ap_total = float(st.loc[st["state_n"] == "ANDHRA PRADESH", "female_pop_2011"])
    tg_share = 0.414
    tg_row = pd.DataFrame([{"state_n": "TELANGANA", "female_pop_2011": ap_total * tg_share}])
    st.loc[st["state_n"] == "ANDHRA PRADESH", "female_pop_2011"] = ap_total * (1 - tg_share)
    st = pd.concat([st, tg_row], ignore_index=True)
    # Odisha: already in census as-is (not split), no adjustment needed
    # Merge Dadra+Daman as single UT
    ddname = "DADRA AND NAGAR HAVELI AND DAMAN AND DIU"
    dd_pop = (
        st.loc[st["state_n"].isin(["DADRA AND NAGAR HAVELI", "DAMAN AND DIU"]),
               "female_pop_2011"]
        .sum()
    )
    st = st[~st["state_n"].isin(["DADRA AND NAGAR HAVELI", "DAMAN AND DIU"])].copy()
    st = pd.concat(
        [st, pd.DataFrame([{"state_n": ddname, "female_pop_2011": dd_pop}])],
        ignore_index=True,
    )
    return st


def build_pmmvy_treatment():
    pmmvy = load_pmmvy_intensity()
    census_pop = load_census_female_pop()
    df = pmmvy.merge(census_pop, on="state_n", how="inner")
    # Intensity: beneficiaries per 1,000 women (Census 2011 female pop proxy for eligible base)
    df["pmmvy_intensity"] = df["pmmvy_ben"] / (df["female_pop_2011"] / 1000)
    # Standardise
    df["pmmvy_intensity_std"] = (
        (df["pmmvy_intensity"] - df["pmmvy_intensity"].mean())
        / df["pmmvy_intensity"].std()
    )
    return df[["state_n", "pmmvy_ben", "female_pop_2011",
               "pmmvy_intensity", "pmmvy_intensity_std"]]


# ── 2. NFHS individual data ───────────────────────────────────────────────────

def load_nfhs(treatment_df):
    df = pd.read_parquet(PROJECT_ROOT / "data" / "processed" / "nfhs" / "nfhs_individual_harmonized.parquet")
    df["state_n"] = df["state_name"].str.upper().str.strip()

    # Keep only NFHS-4 and NFHS-5
    df = df[df["survey_round"].isin(["NFHS-4", "NFHS-5"])].copy()
    df["post"] = (df["survey_round"] == "NFHS-5").astype(int)

    # Recode outcomes to 0/1 -----------------------------------------------
    # bank_account_self_use: already 0/1 (or float 0/1 from harmonisation)
    df["bank_account"] = (df["bank_account_self_use"] == 1).astype(float)
    df.loc[df["bank_account_self_use"].isna(), "bank_account"] = np.nan

    # mobile phone self-use: 0/1
    df["mobile_use"] = (df["mobile_phone_self_use"] == 1).astype(float)
    df.loc[df["mobile_phone_self_use"].isna(), "mobile_use"] = np.nan

    # own money autonomy: already 0/1
    df["money_autonomy"] = df["own_money_autonomy"]

    # decision_health_care: coded 1-6
    #  1=woman alone, 2=woman+husband jointly → has say; 3+=no say or other
    df["decision_has_say"] = df["decision_health_care"].map(
        {1.0: 1.0, 2.0: 1.0, 4.0: 0.0, 5.0: 0.0, 6.0: 0.0}
    )

    # Controls
    df["age_sq"] = df["age"] ** 2
    # wealth_index: 1-5 scale, treat as continuous control
    # education_level: categorical
    # urban_rural: 1=urban, 2=rural → recode
    df["rural"] = (df["urban_rural"] == 2).astype(float)

    # Merge PMMVY intensity
    df = df.merge(treatment_df[["state_n", "pmmvy_intensity_std"]], on="state_n", how="left")

    # Harmonise Dadra+Daman: NFHS-4 has separate, NFHS-5 has combined
    dd_map = {
        "DADRA AND NAGAR HAVELI": "DADRA AND NAGAR HAVELI AND DAMAN AND DIU",
        "DAMAN AND DIU":          "DADRA AND NAGAR HAVELI AND DAMAN AND DIU",
    }
    df["state_fe"] = df["state_n"].replace(dd_map)

    return df


# ── 3. RBI banking baseline (for triple interaction) ─────────────────────────

def load_banking_state():
    """State-level log branch density from RBI 2013 district data, standardised."""
    rbi = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "rbi" / "rbi_district_baseline_dec_2013.csv")
    pop = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "census" / "census2011_district_population.csv")

    rbi["offices"] = pd.to_numeric(rbi["reporting_offices_total"], errors="coerce")
    rbi["state_n_rbi"] = rbi["state_name_clean"].str.upper().str.strip()
    state_rbi = rbi.groupby("state_n_rbi")["offices"].sum().reset_index()

    pop["state_n_census"] = pop["state_name_census_clean"].str.upper().str.strip()
    state_pop = pop.groupby("state_n_census")["population_total_2011"].sum().reset_index()

    # RBI clean names → Census names (only the divergent ones)
    rbi_to_census = {
        "ANDAMAN AND NICOBAR ISLANDS": "ANDAMAN AND NICOBAR ISLANDS",
        "JAMMU AND KASHMIR":           "JAMMU AND KASHMIR",
        "NCT OF DELHI":                "DELHI",
        "DADRA & NAGAR HAVELI":        "DADRA AND NAGAR HAVELI",
        "DAMAN & DIU":                 "DAMAN AND DIU",
    }
    state_rbi["state_n"] = state_rbi["state_n_rbi"].replace(rbi_to_census)
    state_pop["state_n"] = state_pop["state_n_census"]

    merged = state_rbi.merge(state_pop, on="state_n", how="inner")
    merged["branch_density"] = merged["offices"] / (merged["population_total_2011"] / 100000)
    merged["log_branch_density"] = np.log(merged["branch_density"].clip(lower=0.01))
    merged["log_branch_density_std"] = (
        (merged["log_branch_density"] - merged["log_branch_density"].mean())
        / merged["log_branch_density"].std()
    )

    # Duplicate AP row for Telangana (Telangana was part of AP in 2013)
    ap = merged[merged["state_n"] == "ANDHRA PRADESH"].copy()
    if not ap.empty:
        tg_row = ap.copy()
        tg_row["state_n"] = "TELANGANA"
        merged = pd.concat([merged, tg_row], ignore_index=True)

    return merged[["state_n", "log_branch_density_std"]]


# ── 4. regression wrappers ────────────────────────────────────────────────────

CONTROLS = "age + age_sq + C(education_level) + rural + C(wealth_index)"


def run_intensity_did(df, outcome, treatment="pmmvy_intensity_std"):
    """Individual-level DiD: outcome ~ intensity × post + state_FE + round_FE + controls."""
    col = df[[outcome, treatment, "post", "state_fe", "survey_round",
               "age", "age_sq", "education_level", "rural", "wealth_index"]].dropna()
    col["interact"] = col[treatment] * col["post"]
    formula = (
        f"{outcome} ~ interact + post + {CONTROLS} "
        f"+ C(state_fe) + C(survey_round)"
    )
    try:
        mod = clustered_ols(formula, col, "state_fe")
        return summarize(mod, "interact")
    except Exception as e:
        return (np.nan, np.nan, np.nan, 0, "")


def run_triple_interaction(df, outcome, treatment="pmmvy_intensity_std",
                           banking="log_branch_density_std"):
    """Triple interaction: intensity × banking × post."""
    col = df[[outcome, treatment, banking, "post", "state_fe", "survey_round",
               "age", "age_sq", "education_level", "rural", "wealth_index"]].dropna()
    col["int_post"]    = col[treatment] * col["post"]
    col["bank_post"]   = col[banking]   * col["post"]
    col["triple"]      = col[treatment] * col[banking] * col["post"]
    formula = (
        f"{outcome} ~ int_post + bank_post + triple + post + {treatment} + {banking} "
        f"+ {CONTROLS} + C(state_fe) + C(survey_round)"
    )
    try:
        mod = clustered_ols(formula, col, "state_fe")
        b2, se2, p2, n2, s2 = summarize(mod, "bank_post")
        b3, se3, p3, n3, s3 = summarize(mod, "triple")
        return (b2, se2, p2, b3, se3, p3, n2)
    except Exception as e:
        return (np.nan,) * 7


# ── 5. state-level descriptive validation ────────────────────────────────────

def build_state_summary(df, treatment_df):
    outcomes = ["bank_account", "mobile_use", "money_autonomy", "decision_has_say"]
    rows = []
    for rnd in ["NFHS-4", "NFHS-5"]:
        sub = df[df["survey_round"] == rnd]
        for st in sub["state_fe"].dropna().unique():
            row = {"state": st, "round": rnd}
            s = sub[sub["state_fe"] == st]
            for o in outcomes:
                row[o] = s[o].mean()
            rows.append(row)
    summary = pd.DataFrame(rows)
    summary = summary.merge(
        treatment_df[["state_n", "pmmvy_intensity", "pmmvy_intensity_std"]].rename(
            columns={"state_n": "state"}
        ),
        on="state", how="left"
    )
    # Change NFHS-4 → NFHS-5
    pre  = summary[summary["round"] == "NFHS-4"].set_index("state")[outcomes]
    post = summary[summary["round"] == "NFHS-5"].set_index("state")[outcomes]
    delta = (post - pre).dropna()
    delta.columns = [f"delta_{o}" for o in outcomes]
    intensity = treatment_df.set_index("state_n")["pmmvy_intensity_std"]
    delta = delta.join(intensity).dropna()
    return summary, delta


# ── 6. main ───────────────────────────────────────────────────────────────────

def main():
    print("Building PMMVY treatment intensity...")
    treatment_df = build_pmmvy_treatment()
    print(f"  States with PMMVY data: {len(treatment_df)}")
    print(f"  Intensity range: {treatment_df['pmmvy_intensity'].min():.2f} – "
          f"{treatment_df['pmmvy_intensity'].max():.2f} beneficiaries per 1,000 women")
    print(f"  Mean: {treatment_df['pmmvy_intensity'].mean():.2f}  "
          f"SD: {treatment_df['pmmvy_intensity'].std():.2f}")

    print("\nLoading NFHS individual data...")
    df = load_nfhs(treatment_df)
    n4 = (df["survey_round"] == "NFHS-4").sum()
    n5 = (df["survey_round"] == "NFHS-5").sum()
    matched = df["pmmvy_intensity_std"].notna().sum()
    print(f"  NFHS-4: {n4:,}  NFHS-5: {n5:,}  Matched to PMMVY: {matched:,}")

    print("\nLoading banking baseline...")
    banking_df = load_banking_state()
    df = df.merge(banking_df.rename(columns={"state_n": "state_fe"}),
                  on="state_fe", how="left")
    print(f"  States matched to banking: {df[df['log_branch_density_std'].notna()]['state_fe'].nunique()}")

    # ── Table 1: PMMVY intensity DiD ─────────────────────────────────────────
    OUTCOMES = [
        ("bank_account",    "Bank account ownership (%)"),
        ("mobile_use",      "Mobile phone self-use (%)"),
        ("money_autonomy",  "Own money autonomy (%)"),
        ("decision_has_say","Health-care decision has say (%)"),
    ]

    print("\n" + "=" * 80)
    print("TABLE 1: PMMVY intensity × Post DiD")
    print("(Individual-level; state FE + round FE + controls; SE clustered at state)")
    print(f"  {'Outcome':<40} {'Coeff':>10} {'SE':>8} {'p':>8} {'N':>10}")
    print("-" * 80)
    results = []
    for col, label in OUTCOMES:
        b, se, p, n, stars = run_intensity_did(df, col)
        sig = f"{b:+.4f}{stars}"
        print(f"  {label:<40} {sig:>14}  {se:>8.4f}  {p:>8.3f}  {n:>10,}")
        results.append({"outcome": col, "regressor": "pmmvy_intensity_did",
                         "b": b, "se": se, "p": p, "n": n})

    # ── Table 2: Pre vs Post means by intensity tercile ───────────────────────
    print("\n" + "=" * 80)
    print("TABLE 2: Descriptive — NFHS-4 → NFHS-5 change by PMMVY intensity tercile")
    print("(State-level means; terciles by PMMVY intensity)")
    treatment_df["intensity_tercile"] = pd.qcut(
        treatment_df["pmmvy_intensity"], q=3, labels=["Low", "Mid", "High"]
    )
    df_t = df.merge(
        treatment_df[["state_n", "intensity_tercile"]].rename(columns={"state_n": "state_fe"}),
        on="state_fe", how="left"
    )
    print(f"\n  {'Tercile':<8} {'N states':>9} {'Intensity':>12}  "
          f"{'ΔBank acc':>12} {'ΔMobile':>10} {'ΔAutonomy':>12} {'ΔDecision':>12}")
    print("  " + "-" * 80)
    tbl2_rows = []
    for terc in ["Low", "Mid", "High"]:
        sub = df_t[df_t["intensity_tercile"] == terc]
        n_st = sub["state_fe"].nunique()
        intensity_mean = treatment_df.loc[
            treatment_df["intensity_tercile"] == terc, "pmmvy_intensity"
        ].mean()
        deltas = {}
        for col, _ in OUTCOMES:
            pre_m  = sub.loc[sub["survey_round"] == "NFHS-4", col].mean()
            post_m = sub.loc[sub["survey_round"] == "NFHS-5", col].mean()
            deltas[col] = (post_m - pre_m) * 100
        print(f"  {terc:<8} {n_st:>9}  {intensity_mean:>12.1f}"
              f"  {deltas['bank_account']:>+10.1f}pp"
              f"  {deltas['mobile_use']:>+8.1f}pp"
              f"  {deltas['money_autonomy']:>+10.1f}pp"
              f"  {deltas['decision_has_say']:>+10.1f}pp")
        tbl2_rows.append({"tercile": terc, "n_states": n_st,
                           "intensity_mean": intensity_mean, **deltas})

    # ── Table 3: Triple interaction with banking ──────────────────────────────
    print("\n" + "=" * 80)
    print("TABLE 3: Triple interaction — PMMVY intensity × Banking × Post")
    print("(Does PMMVY effect vary by pre-existing banking depth?)")
    print(f"  {'Outcome':<40} {'Banking×Post':>14} {'Triple':>14}  {'p (triple)':>12}")
    print("-" * 80)
    for col, label in OUTCOMES:
        b2, se2, p2, b3, se3, p3, n = run_triple_interaction(df, col)
        s3 = "***" if p3 < 0.001 else "**" if p3 < 0.01 else "*" if p3 < 0.05 else ("†" if p3 < 0.10 else "")
        print(f"  {label:<40} {b2:>+10.4f}      {b3:>+10.4f}{s3}   {p3:>12.3f}")
        results.append({"outcome": col, "regressor": "triple_interaction",
                         "b": b3, "se": se3, "p": p3, "n": n})

    # ── Table 4: Robustness — exclude large states ────────────────────────────
    print("\n" + "=" * 80)
    print("TABLE 4: Robustness — exclude UP, Bihar, Maharashtra (large states)")
    large_states = {"UTTAR PRADESH", "BIHAR", "MAHARASHTRA"}
    df_rob = df[~df["state_fe"].isin(large_states)].copy()
    print(f"  (N individual obs after exclusion: {len(df_rob):,})")
    print(f"  {'Outcome':<40} {'Coeff':>10} {'SE':>8} {'p':>8}")
    print("-" * 80)
    for col, label in OUTCOMES:
        b, se, p, n, stars = run_intensity_did(df_rob, col)
        sig = f"{b:+.4f}{stars}"
        print(f"  {label:<40} {sig:>14}  {se:>8.4f}  {p:>8.3f}")
        results.append({"outcome": col, "regressor": "rob_excl_large",
                         "b": b, "se": se, "p": p, "n": n})

    # ── Table 5: Robustness — Tamil Nadu as non-participant (coded 0) ──────────
    print("\n" + "=" * 80)
    print("TABLE 5: Robustness — Tamil Nadu coded as 0 (competing state scheme)")
    print("  (Dr. Muthulakshmi Reddy scheme; Rs.18,000 > PMMVY Rs.5,000; crowds out uptake)")
    df_tn0 = df.copy()
    df_tn0.loc[df_tn0["state_fe"] == "TAMIL NADU", "pmmvy_intensity_std"] = (
        (0 - treatment_df["pmmvy_intensity"].mean()) / treatment_df["pmmvy_intensity"].std()
    )
    print(f"  {'Outcome':<40} {'Coeff':>10} {'SE':>8} {'p':>8}")
    print("-" * 80)
    for col, label in OUTCOMES:
        b, se, p, n, stars = run_intensity_did(df_tn0, col)
        sig = f"{b:+.4f}{stars}"
        print(f"  {label:<40} {sig:>14}  {se:>8.4f}  {p:>8.3f}")
        results.append({"outcome": col, "regressor": "rob_tn_zero",
                         "b": b, "se": se, "p": p, "n": n})

    # ── Table 6: Robustness — old AP-split spec (Telangana imputed from AP) ───
    print("\n" + "=" * 80)
    print("TABLE 6: Robustness — legacy AP-split spec (Telangana ≈ 41.4% of AP enrollment)")
    print("  (Original analysis assumption; now superseded by correct Telangana=0 spec)")
    # Re-build treatment with old AP split
    tdf_split = treatment_df.copy()
    ap_val = float(tdf_split.loc[tdf_split["state_n"] == "ANDHRA PRADESH", "pmmvy_ben"].iloc[0])
    ap_pop = float(tdf_split.loc[tdf_split["state_n"] == "ANDHRA PRADESH", "female_pop_2011"].iloc[0])
    # Restore split values
    tdf_split.loc[tdf_split["state_n"] == "ANDHRA PRADESH", "pmmvy_ben"] = ap_val * 0.586
    tdf_split.loc[tdf_split["state_n"] == "ANDHRA PRADESH", "female_pop_2011"] = ap_pop * 0.586
    tdf_split.loc[tdf_split["state_n"] == "TELANGANA", "pmmvy_ben"] = ap_val * 0.414
    tdf_split.loc[tdf_split["state_n"] == "TELANGANA", "female_pop_2011"] = ap_pop * 0.414
    tdf_split["pmmvy_intensity"] = tdf_split["pmmvy_ben"] / (tdf_split["female_pop_2011"] / 1000)
    tdf_split["pmmvy_intensity_std"] = (
        (tdf_split["pmmvy_intensity"] - tdf_split["pmmvy_intensity"].mean())
        / tdf_split["pmmvy_intensity"].std()
    )
    df_split = df.drop(columns=["pmmvy_intensity_std"]).merge(
        tdf_split[["state_n", "pmmvy_intensity_std"]].rename(columns={"state_n": "state_fe"}),
        on="state_fe", how="left"
    )
    print(f"  {'Outcome':<40} {'Coeff':>10} {'SE':>8} {'p':>8}")
    print("-" * 80)
    for col, label in OUTCOMES:
        b, se, p, n, stars = run_intensity_did(df_split, col)
        sig = f"{b:+.4f}{stars}"
        print(f"  {label:<40} {sig:>14}  {se:>8.4f}  {p:>8.3f}")
        results.append({"outcome": col, "regressor": "rob_ap_split_legacy",
                         "b": b, "se": se, "p": p, "n": n})

    # ── Comparison summary ─────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("COMPARISON: Main spec vs robustness — bank_account and money_autonomy")
    print(f"  {'Spec':<35} {'Bank acc coef':>14} {'p':>8}  {'Autonomy coef':>14} {'p':>8}")
    print("-" * 80)
    specs = [
        ("Main (TG=0, OD=0, TN=actual)", "pmmvy_intensity_did"),
        ("Rob: Tamil Nadu = 0",           "rob_tn_zero"),
        ("Rob: Legacy AP-split",          "rob_ap_split_legacy"),
        ("Rob: Excl large states",        "rob_excl_large"),
    ]
    res_df = pd.DataFrame(results)
    for label, reg in specs:
        ba = res_df[(res_df["regressor"]==reg) & (res_df["outcome"]=="bank_account")]
        ma = res_df[(res_df["regressor"]==reg) & (res_df["outcome"]=="money_autonomy")]
        if len(ba) and len(ma):
            bs = "***" if ba.iloc[0]["p"]<0.001 else "**" if ba.iloc[0]["p"]<0.01 else "*" if ba.iloc[0]["p"]<0.05 else ""
            ms = "***" if ma.iloc[0]["p"]<0.001 else "**" if ma.iloc[0]["p"]<0.01 else "*" if ma.iloc[0]["p"]<0.05 else ""
            print(f"  {label:<35} {ba.iloc[0]['b']:>+12.4f}{bs:<2}  {ba.iloc[0]['p']:>8.3f}"
                  f"  {ma.iloc[0]['b']:>+12.4f}{ms:<2}  {ma.iloc[0]['p']:>8.3f}")

    # ── PMMVY intensity distribution ──────────────────────────────────────────
    print("\n" + "=" * 80)
    print("PMMVY intensity distribution (beneficiaries per 1,000 women, by state):")
    top_states = treatment_df.nlargest(5, "pmmvy_intensity")[["state_n", "pmmvy_intensity"]]
    bot_states = treatment_df.nsmallest(5, "pmmvy_intensity")[["state_n", "pmmvy_intensity"]]
    print("  Top 5 (highest intensity):")
    for _, row in top_states.iterrows():
        print(f"    {row['state_n']:<35} {row['pmmvy_intensity']:>8.1f}")
    print("  Bottom 5 (lowest intensity):")
    for _, row in bot_states.iterrows():
        print(f"    {row['state_n']:<35} {row['pmmvy_intensity']:>8.1f}")

    # ── Save ──────────────────────────────────────────────────────────────────
    pd.DataFrame(results).to_csv(RESULTS_DIR / "pmmvy_national_did_results.csv", index=False)
    treatment_df.to_csv(RESULTS_DIR / "pmmvy_state_intensity.csv", index=False)
    pd.DataFrame(tbl2_rows).to_csv(RESULTS_DIR / "pmmvy_tercile_raw_changes.csv", index=False)
    print("\nSaved → results/tables/pmmvy_national_did_results.csv")
    print("Saved → results/tables/pmmvy_state_intensity.csv")
    print("Saved → results/tables/pmmvy_tercile_raw_changes.csv")
    print("Done.")


if __name__ == "__main__":
    main()
