"""
Study A: Three-round state panel DiD — banking expansion and women's outcomes.

Design
------
Panel: 37 states × 3 NFHS rounds (2005-06, 2015-16, 2019-21).
Unit: state s in round t.

    Y_st = alpha_s + lambda_t + beta*(banking_st) + epsilon_st

State FE absorb all time-invariant state characteristics.
Round FE absorb common national trends.
beta = within-state, over-time relationship between banking density growth
       and women's outcomes.

Banking variable: deposits per capita (Rs.) from RBI annual data.
    2005-06: approximated from RBI Dec-2013 baseline (earliest available).
             For NFHS-3, 2013 deposits are the closest available pre-survey proxy.
             Sensitivity: results using only NFHS-4 → NFHS-5 window (2015-16 data available).
    2015-16: from annual deposits file (BSR-2 state-wise).
    2019-20: from RBI Statement 4a Q4 2019-20 (state aggregates).

Outcomes (from NFHS-3/4/5 state factsheets):
    bank_account_use  — women with bank account they themselves use (%)
    mobile_use        — women with mobile phone they themselves use (%)
    decisions         — married women participating in household decisions (%)
    child_marriage    — women 20-24 married before 18 (%)
    literacy          — women 15-49 who are literate (%)

Standard errors: clustered at state level.
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

def norm(s):
    return (str(s).upper().strip()
            .replace("&", "AND").replace(".", "").replace(",", "")
            .replace("-", " ").replace("  ", " ").strip())


# NFHS → canonical state name
NFHS_TO_CANON = {
    "JAMMU AND KASHMIR": "JAMMU AND KASHMIR",
    "JAMMU & KASHMIR":   "JAMMU AND KASHMIR",
    "NCT OF DELHI":      "DELHI",
    "DELHI":             "DELHI",
    "ODISHA":            "ODISHA",
    "ORISSA":            "ODISHA",
    "UTTARAKHAND":       "UTTARAKHAND",
    "UTTARANCHAL":       "UTTARAKHAND",
    "CHHATTISGARH":      "CHHATTISGARH",
    "TELANGANA":         "TELANGANA",
}

# RBI state → canonical
RBI_TO_CANON = {
    "NCT OF DELHI":                  "DELHI",
    "ORISSA":                        "ODISHA",
    "UTTARANCHAL":                   "UTTARAKHAND",
    "ANDAMAN AND NICOBAR ISLANDS":   "ANDAMAN AND NICOBAR ISLANDS",
    "ANDAMAN AND NICOBAR":           "ANDAMAN AND NICOBAR ISLANDS",
    "DADRA AND NAGAR HAVELI":        "DADRA AND NAGAR HAVELI AND DAMAN AND DIU",
    "DAMAN AND DIU":                 "DADRA AND NAGAR HAVELI AND DAMAN AND DIU",
    "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "DADRA AND NAGAR HAVELI AND DAMAN AND DIU",
}


def canon_state(s):
    n = norm(s)
    return NFHS_TO_CANON.get(n, RBI_TO_CANON.get(n, n))


# ── Load banking data ──────────────────────────────────────────────────────────

def load_banking_state_panel() -> pd.DataFrame:
    """Returns state × year with deposits_cr and accounts_thou."""
    dep = pd.read_excel(
        PROJECT_ROOT / "data" / "raw" / "rbi" /
        "bank_deposits_of_scbs_region_state_district_bank_group_population_group_wise_annual.xlsx",
        header=None
    )
    data = dep.iloc[5:, [1, 2, 3, 4]].copy()
    data.columns = ["year", "state", "accounts_thou", "deposits_cr"]
    data["year"] = data["year"].ffill()
    data = data[data["state"].notna() & ~data["state"].astype(str).str.startswith("State")].copy()
    for col in ["deposits_cr", "accounts_thou"]:
        data[col] = pd.to_numeric(data[col].replace("-", np.nan), errors="coerce")
    data["state_canon"] = data["state"].apply(canon_state)
    # Keep relevant years
    data = data[data["year"].isin(["2009-10","2010-11","2011-12","2012-13","2013-14",
                                    "2014-15","2015-16","2016-17","2017-18"])].copy()
    # Two former UTs are mapped to their current combined unit; aggregate before merges.
    return data.groupby(["year", "state_canon"], as_index=False).agg(
        accounts_thou=("accounts_thou", "sum"),
        deposits_cr=("deposits_cr", "sum"),
    )


def load_rbi_state_2013() -> pd.DataFrame:
    """State-level aggregates from RBI Dec-2013 district snapshot."""
    rbi = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "rbi" / "rbi_district_baseline_dec_2013.csv")
    census = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "census" / "census2011_district_population.csv")

    rbi["state_canon"] = rbi["state_name_clean"].apply(canon_state)
    census["state_canon"] = census["state_name_census_clean"].apply(canon_state)

    state_rbi = rbi.groupby("state_canon").agg(
        offices_2013=("reporting_offices_total", "sum"),
        deposits_cr_2013=("deposits_total_crore_rs", "sum"),
    ).reset_index()
    state_pop = census.groupby("state_canon")["population_total_2011"].sum().reset_index()
    state_pop.columns = ["state_canon", "pop_2011"]

    merged = state_rbi.merge(state_pop, on="state_canon", how="left")
    merged["branch_density_2013"] = merged["offices_2013"] / (merged["pop_2011"] / 100_000)
    merged["deposits_pc_2013"]    = (merged["deposits_cr_2013"] * 1e7) / merged["pop_2011"]
    return merged


def load_rbi4a_state_panel() -> pd.DataFrame:
    """State aggregates from RBI Statement 4a quarterly district panel (Q4 each year)."""
    rbi4a = pd.read_excel(
        PROJECT_ROOT / "data" / "raw" / "rbi" /
        "rbi_statement_4a_district_reporting_offices_deposits_credit_2017_2022.xlsx",
        header=None
    )
    row5 = rbi4a.iloc[5].tolist()
    row6 = rbi4a.iloc[6].tolist()

    period_labels = []
    cur = None
    for v in row5:
        if pd.notna(v) and str(v).strip() not in ("Region", "State or UTs", "District ", ""):
            cur = str(v).strip()
        period_labels.append(cur)

    col_map = {}
    for i, (p, s) in enumerate(zip(period_labels, row6)):
        s_clean = str(s).replace("\n", " ").strip() if pd.notna(s) else ""
        if p and s_clean:
            col_map[(p, s_clean)] = i

    data = rbi4a.iloc[7:].copy()
    data = data[data.iloc[:, 2].notna()].copy()

    records = []
    for period in ["2017-18:Q4", "2018-19:Q4", "2019-20:Q4", "2020-21:Q4", "2021-22:Q4"]:
        off_col = col_map.get((period, "Number of Reporting Offices"))
        dep_col = col_map.get((period, "Deposit"))
        if off_col is None:
            continue
        for _, row in data.iterrows():
            records.append({
                "period": period,
                "state_raw": str(row[2]).strip(),
                "district": str(row[3]).strip(),
                "offices": pd.to_numeric(row[off_col], errors="coerce"),
                "deposits_cr": pd.to_numeric(row[dep_col], errors="coerce") if dep_col else np.nan,
            })

    df = pd.DataFrame(records)
    df["state_canon"] = df["state_raw"].apply(canon_state)
    state_agg = df.groupby(["period", "state_canon"]).agg(
        offices=("offices", "sum"),
        deposits_cr=("deposits_cr", "sum"),
    ).reset_index()
    return state_agg


# ── Load NFHS outcomes ─────────────────────────────────────────────────────────

def load_nfhs_outcomes() -> pd.DataFrame:
    """
    Combine NFHS-3, NFHS-4, NFHS-5 state-level Total-area outcomes.
    Returns one row per (state, round).
    """
    # ── NFHS-3 and NFHS-4 ────────────────────────────────────────────────────
    nf34 = pd.read_csv(
        PROJECT_ROOT / "data" / "raw" / "nfhs_support" /
        "nfhs4_nfhs3_factsheet_all_india_indicators_r1.csv"
    )
    nf34 = nf34[nf34["Area"] == "Total"].copy()
    nf34["state_canon"] = nf34["India/States/UTs"].apply(canon_state)
    nf34["round"] = nf34["Survey"]

    col_bank34  = next(c for c in nf34.columns if "bank or savings account" in c.lower())
    col_mob34   = next(c for c in nf34.columns if "mobile phone that they themselves" in c.lower())
    col_dec34   = next(c for c in nf34.columns if "participate in household decisions" in c.lower()
                        and "Note" not in c)
    col_marr34  = next(c for c in nf34.columns if "married before age 18" in c.lower()
                        and "Note" not in c)
    col_lit34   = next(c for c in nf34.columns if "women who are literate" in c.lower()
                        and "Note" not in c)

    nf34_clean = nf34[["state_canon", "round",
                         col_bank34, col_mob34, col_dec34, col_marr34, col_lit34]].copy()
    nf34_clean.columns = ["state_canon", "round",
                           "bank_account_use", "mobile_use", "decisions",
                           "child_marriage", "literacy"]

    # ── NFHS-5 ───────────────────────────────────────────────────────────────
    nf5 = pd.read_excel(
        PROJECT_ROOT / "data" / "raw" / "nfhs_support" / "nfhs5_factsheets_data.xls"
    )
    nf5 = nf5[nf5["Area"] == "Total"].copy()
    nf5["state_canon"] = nf5["States/UTs"].apply(canon_state)
    nf5["round"] = "NFHS-5"

    col_bank5 = next(c for c in nf5.columns if "bank or savings account" in c.lower())
    col_mob5  = next(c for c in nf5.columns if "mobile phone that they themselves" in c.lower())
    col_dec5  = next(c for c in nf5.columns if "participate" in c.lower())
    col_marr5 = next(c for c in nf5.columns if "married before age 18" in c.lower())
    col_lit5  = next(c for c in nf5.columns if "literate" in c.lower()
                      and "Women" in c)

    nf5_clean = nf5[["state_canon", "round",
                       col_bank5, col_mob5, col_dec5, col_marr5, col_lit5]].copy()
    nf5_clean.columns = ["state_canon", "round",
                          "bank_account_use", "mobile_use", "decisions",
                          "child_marriage", "literacy"]

    outcomes = pd.concat([nf34_clean, nf5_clean], ignore_index=True)
    for col in ["bank_account_use", "mobile_use", "decisions", "child_marriage", "literacy"]:
        outcomes[col] = pd.to_numeric(outcomes[col], errors="coerce")
    # NFHS-4 reports Dadra & Nagar Haveli and Daman & Diu separately. They are
    # mapped to the current combined UT, so collapse to one state-round record.
    return outcomes.groupby(["state_canon", "round"], as_index=False).agg(
        bank_account_use=("bank_account_use", "mean"),
        mobile_use=("mobile_use", "mean"),
        decisions=("decisions", "mean"),
        child_marriage=("child_marriage", "mean"),
        literacy=("literacy", "mean"),
    )


# ── Build merged panel ─────────────────────────────────────────────────────────

def build_panel() -> pd.DataFrame:
    outcomes   = load_nfhs_outcomes()
    dep_panel  = load_banking_state_panel()
    rbi2013    = load_rbi_state_2013()
    rbi4a      = load_rbi4a_state_panel()

    # Census 2011 population for per-capita
    census = pd.read_csv(
        PROJECT_ROOT / "data" / "processed" / "census" / "census2011_district_population.csv"
    )
    state_pop = census.groupby(
        census["state_name_census_clean"].apply(canon_state)
    )["population_total_2011"].sum().reset_index()
    state_pop.columns = ["state_canon", "pop_2011"]

    # ── Map banking to NFHS rounds ────────────────────────────────────────────
    # NFHS-3 (2005-06): use 2013 deposits as proxy (earliest available)
    # NFHS-4 (2015-16): use 2015-16 from annual deposits file
    # NFHS-5 (2019-21): use 2019-20 Q4 from statement 4a

    # 2013 state deposits
    deposits_2013 = rbi2013[["state_canon", "deposits_cr_2013", "offices_2013", "pop_2011"]].copy()

    # 2015-16 from annual file
    dep1516 = dep_panel[dep_panel["year"] == "2015-16"][["state_canon", "deposits_cr"]].copy()
    dep1516.columns = ["state_canon", "deposits_cr_2016"]

    # 2019-20 from 4a
    dep1920 = rbi4a[rbi4a["period"] == "2019-20:Q4"][["state_canon", "offices", "deposits_cr"]].copy()
    dep1920.columns = ["state_canon", "offices_2020", "deposits_cr_2020"]

    # Merge all banking into outcomes
    panel = outcomes.copy()
    panel = panel.merge(state_pop, on="state_canon", how="left")
    panel = panel.merge(deposits_2013[["state_canon","deposits_cr_2013","offices_2013"]],
                        on="state_canon", how="left")
    panel = panel.merge(dep1516, on="state_canon", how="left")
    panel = panel.merge(dep1920, on="state_canon", how="left")

    # Assign per-capita banking measure by round
    panel["deposits_pc"] = np.where(
        panel["round"] == "NFHS-3",
        (panel["deposits_cr_2013"] * 1e7) / panel["pop_2011"],
        np.where(
            panel["round"] == "NFHS-4",
            (panel["deposits_cr_2016"] * 1e7) / panel["pop_2011"],
            (panel["deposits_cr_2020"] * 1e7) / panel["pop_2011"],
        )
    )
    panel["log_deposits_pc"] = np.log(panel["deposits_pc"].replace(0, np.nan))

    # Branch density (available for 2013 and 2020)
    panel["branch_density"] = np.where(
        panel["round"] == "NFHS-5",
        panel["offices_2020"] / (panel["pop_2011"] / 100_000),
        panel["offices_2013"] / (panel["pop_2011"] / 100_000),
    )
    panel["log_branch"] = np.log(panel["branch_density"].replace(0, np.nan))

    # Standardise within the full panel
    for v in ["deposits_pc", "log_deposits_pc", "branch_density", "log_branch"]:
        s = panel[v]
        panel[f"{v}_std"] = (s - s.mean()) / s.std()

    # Round and time codes
    round_map = {"NFHS-3": 0, "NFHS-4": 1, "NFHS-5": 2}
    panel["t"] = panel["round"].map(round_map)
    panel["state_code"] = pd.Categorical(panel["state_canon"]).codes

    return panel


# ── Estimation ─────────────────────────────────────────────────────────────────

def pick(m, key):
    if key in m.params.index:
        return m.params[key], m.bse[key], m.pvalues[key]
    cands = [k for k in m.params.index if key in k]
    if not cands:
        return np.nan, np.nan, np.nan
    return m.params[cands[-1]], m.bse[cands[-1]], m.pvalues[cands[-1]]


def stars(p):
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def run_twfe(df, outcome, regressor, rounds=None):
    sub = df[df[outcome].notna() & df[regressor].notna()].copy()
    if rounds:
        sub = sub[sub["round"].isin(rounds)]
    formula = f"{outcome} ~ {regressor} + C(state_code) + C(t)"
    m = smf.ols(formula, data=sub).fit(
        cov_type="cluster", cov_kwds={"groups": sub["state_code"]}
    )
    b, se, p = pick(m, regressor)
    return {"b": b, "se": se, "p": p, "n": len(sub),
            "n_states": sub["state_canon"].nunique(), "r2": m.rsquared}


# ── Main ───────────────────────────────────────────────────────────────────────

OUTCOMES = {
    "bank_account_use": "Women with bank account they use (%)",
    "mobile_use":       "Women with mobile phone they use (%)",
    "decisions":        "Women participating in decisions (%)",
    "child_marriage":   "Women married before 18 (%)",
    "literacy":         "Women's literacy rate (%)",
}


def main():
    print("Building 3-round state panel...")
    panel = build_panel()

    # Coverage summary
    for rnd in ["NFHS-3", "NFHS-4", "NFHS-5"]:
        sub = panel[panel["round"] == rnd]
        n_states = sub["state_canon"].nunique()
        n_banking = sub["deposits_pc"].notna().sum()
        print(f"  {rnd}: {n_states} states, banking coverage = {n_banking}/{len(sub)}")
    print()

    # Pre-post means across rounds
    print("=== Outcome means by NFHS round (Total area, all states) ===")
    print(f"  {'Outcome':<44} {'NFHS-3':>8} {'NFHS-4':>8} {'NFHS-5':>8}")
    print("-" * 72)
    for col, label in OUTCOMES.items():
        m3 = panel[panel["round"] == "NFHS-3"][col].mean()
        m4 = panel[panel["round"] == "NFHS-4"][col].mean()
        m5 = panel[panel["round"] == "NFHS-5"][col].mean()
        print(f"  {label:<44} {m3:>8.1f} {m4:>8.1f} {m5:>8.1f}")
    print()

    # ── TABLE 1: TWFE — all 3 rounds, log deposits per capita ────────────────
    print("=" * 76)
    print("TABLE 1: TWFE panel — log(deposits per capita) and women's outcomes")
    print("(3 rounds: NFHS-3/4/5; state FE + round FE; SE clustered at state)")
    print(f"  {'Outcome':<44} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>5} {'States':>7}")
    print("-" * 76)

    rows = []
    for col, label in OUTCOMES.items():
        r = run_twfe(panel, col, "log_deposits_pc_std")
        sig = stars(r["p"])
        print(f"  {label:<44} {r['b']:>+10.3f}{sig:<4} {r['se']:>8.3f} "
              f"{r['p']:>7.3f} {r['n']:>5} {r['n_states']:>7}")
        rows.append({"outcome": col, "regressor": "log_deposits_pc_3round", **r})
    print()

    # ── TABLE 2: TWFE — NFHS-4 and NFHS-5 only (2015-16 data available) ─────
    print("=" * 76)
    print("TABLE 2: TWFE panel — NFHS-4 → NFHS-5 only (cleaner banking data)")
    print("(2 rounds; log deposits per capita 2015-16 vs 2019-20; state + round FE)")
    print(f"  {'Outcome':<44} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>5}")
    print("-" * 76)

    for col, label in OUTCOMES.items():
        r = run_twfe(panel, col, "log_deposits_pc_std", rounds=["NFHS-4", "NFHS-5"])
        sig = stars(r["p"])
        print(f"  {label:<44} {r['b']:>+10.3f}{sig:<4} {r['se']:>8.3f} "
              f"{r['p']:>7.3f} {r['n']:>5}")
        rows.append({"outcome": col, "regressor": "log_deposits_pc_2round", **r})
    print()

    # ── TABLE 3: TWFE — branch density (2013 vs 2020) ────────────────────────
    print("=" * 76)
    print("TABLE 3: TWFE panel — log(branch density) and women's outcomes")
    print("(2 rounds: NFHS-4/5; branch density 2013 vs 2019-20 Q4)")
    print(f"  {'Outcome':<44} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>5}")
    print("-" * 76)

    for col, label in OUTCOMES.items():
        r = run_twfe(panel, col, "log_branch_std", rounds=["NFHS-4", "NFHS-5"])
        sig = stars(r["p"])
        print(f"  {label:<44} {r['b']:>+10.3f}{sig:<4} {r['se']:>8.3f} "
              f"{r['p']:>7.3f} {r['n']:>5}")
        rows.append({"outcome": col, "regressor": "log_branch_density_2round", **r})
    print()

    # ── Banking growth by state ───────────────────────────────────────────────
    print("=" * 76)
    print("Banking expansion 2015-16 → 2019-20 by state (% change in deposits per capita)")
    p4 = panel[panel["round"] == "NFHS-4"][["state_canon", "deposits_pc"]].rename(
        columns={"deposits_pc": "dep_pc_4"})
    p5 = panel[panel["round"] == "NFHS-5"][["state_canon", "deposits_pc"]].rename(
        columns={"deposits_pc": "dep_pc_5"})
    growth = p4.merge(p5, on="state_canon").dropna()
    growth["pct_change"] = (growth["dep_pc_5"] - growth["dep_pc_4"]) / growth["dep_pc_4"] * 100
    growth = growth.sort_values("pct_change", ascending=False)
    print(growth[["state_canon", "dep_pc_4", "dep_pc_5", "pct_change"]]
          .rename(columns={"dep_pc_4": "dep_pc_NFHS4", "dep_pc_5": "dep_pc_NFHS5"})
          .to_string(index=False))
    print()

    # Save
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "study_a_state_panel_results.csv", index=False)
    panel.to_csv(RESULTS_DIR / "study_a_state_panel_data.csv", index=False)
    print("Saved → results/tables/study_a_state_panel_results.csv")
    print("Done.")


if __name__ == "__main__":
    main()
