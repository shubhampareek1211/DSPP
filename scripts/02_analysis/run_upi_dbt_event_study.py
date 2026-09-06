"""
UPI adoption event study — women's DBT program launches and digital payment activity.

Design
------
State × month balanced panel, April 2023 – December 2025 (32 months, missing Oct 2024).
Unit: state s in month t.

Outcome: log(UPI volume per capita) — number of UPI transactions per person per month.
         log(UPI value per capita)  — Rs. value of UPI transactions per person per month.

Treatment events (new state women-directed DBT program launches within sample period):
    CHHATTISGARH  — Mahtari Vandan Yojana, first payment Feb 2024
    MAHARASHTRA   — Mukhyamantri Majhi Ladki Bahin Yojana, first payment Aug 2024
    JHARKHAND     — Mukhyamantri Maiya Samman Yojana, first payment Nov 2024

Excluded from treated (no clean pre-period in panel):
    MADHYA PRADESH — Ladli Behna launched March 2023, first UPI month is April 2023.

Already treated before panel starts (serve as controls alongside other states):
    WEST BENGAL — Lakshmir Bhandar, 2021
    ASSAM       — Orunodoi, 2020

Estimators
----------
1. Two-way fixed effects (TWFE): log_outcome ~ state_FE + ym_FE + treated_post
2. Event study: TWFE with relative-time dummies (−8 to +8 around treatment month)
   Reference period: t = −1 (month before launch)
3. Stacked DiD: clean cohort-based estimate for each treatment event separately

Standard errors: clustered at state level (37 clusters).
"""

from __future__ import annotations
from pathlib import Path
import os, re

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ── State name crosswalk ───────────────────────────────────────────────────────

UPI_TO_CENSUS = {
    "ANDAMAN & NICOBAR":                    "ANDAMAN AND NICOBAR ISLANDS",
    "ANDAMAN AND NICOBAR":                  "ANDAMAN AND NICOBAR ISLANDS",
    "DADRA & NAGAR HAVELI & DAMAN & DIU":   "DADRA AND NAGAR HAVELI & DAMAN AND DIU",
    "JAMMU AND KASHMIR":                    "JAMMU AND KASHMIR",   # includes Ladakh
    "J&K":                                  "JAMMU AND KASHMIR",
}

# Approximate 2011-equivalent populations for states not in Census 2011 as separate
APPROX_POP = {
    "TELANGANA":                    35003674,   # ~2014 split from AP
    "LADAKH":                        274289,    # ~2019 split from J&K
    "DADRA AND NAGAR HAVELI & DAMAN AND DIU": 586956,  # merged 2020
}

# Treatment events: state → first treatment month (YYYY-MM)
TREATMENT_EVENTS = {
    "CHHATTISGARH": "2024-02",    # Mahtari Vandan Yojana
    "MAHARASHTRA":  "2024-08",    # Ladki Bahin Yojana
    "JHARKHAND":    "2024-11",    # Maiya Samman Yojana
}


# ── Load UPI panel ─────────────────────────────────────────────────────────────

def load_upi_panel() -> pd.DataFrame:
    upi_dir = PROJECT_ROOT / "data" / "raw" / "upi_support" / "UPI_Statewise"
    records = []

    for root, _, files in os.walk(upi_dir):
        for f in sorted(files):
            if f.startswith("."): continue
            path = os.path.join(root, f)

            if f.endswith(".csv"):
                yr, m = "2023", "Apr"
                df = pd.read_csv(path)
            elif f.endswith(".xlsx"):
                mm = re.search(r"(\d{4})-([\w]+)", f)
                if not mm: continue
                yr, m = mm.group(1), mm.group(2)
                df = pd.read_excel(path, header=1)
            else:
                continue

            df.columns = [str(c).strip() for c in df.columns]
            state_col = next((c for c in df.columns if "state" in c.lower() or "union" in c.lower()), None)
            vol_col   = next((c for c in df.columns if "volume" in c.lower() and "mn" in c.lower()), None) or \
                        next((c for c in df.columns if "volume" in c.lower()), None)
            val_col   = next((c for c in df.columns if "value" in c.lower() and "cr" in c.lower()), None) or \
                        next((c for c in df.columns if "value" in c.lower()), None)
            if not state_col or not vol_col or not val_col: continue

            df = df[[state_col, vol_col, val_col]].copy()
            df.columns = ["state", "volume_mn", "value_cr"]
            df = df.dropna(subset=["state"])
            df["state"] = df["state"].astype(str).str.strip().str.upper()
            df = df[~df["state"].str.match(r"^(SR\.|TOTAL|STATE|UNNAMED|\d+$)", na=False)]
            df = df[df["state"].str.len() > 2]

            for col in ["volume_mn", "value_cr"]:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "").str.replace("%", "").str.strip(),
                    errors="coerce",
                )
            df = df.dropna(subset=["volume_mn"])

            mmap = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06",
                    "Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
            df["ym"] = f"{yr}-{mmap.get(m,'04')}"
            records.append(df)

    panel = pd.concat(records, ignore_index=True)

    # Drop "UNCLASSIFIED" rows
    panel = panel[~panel["state"].str.contains("UNCLASSIFIED", na=False)]
    return panel


def load_population() -> pd.DataFrame:
    census = pd.read_csv(
        PROJECT_ROOT / "data" / "processed" / "census" / "census2011_district_population.csv"
    )
    state_pop = (
        census.groupby("state_name_census_clean")["population_total_2011"]
        .sum()
        .reset_index()
    )
    state_pop.columns = ["state_census", "pop_2011"]
    state_pop["state_census"] = state_pop["state_census"].str.upper()

    # Add states not in Census 2011 as separate
    extras = pd.DataFrame([
        {"state_census": k, "pop_2011": v}
        for k, v in APPROX_POP.items()
    ])
    state_pop = pd.concat([state_pop, extras], ignore_index=True)
    return state_pop


def build_panel() -> pd.DataFrame:
    panel = load_upi_panel()
    state_pop = load_population()

    # Normalize UPI state names to census names
    panel["state_norm"] = panel["state"].replace(UPI_TO_CENSUS)

    panel = panel.merge(
        state_pop.rename(columns={"state_census": "state_norm"}),
        on="state_norm",
        how="left",
    )

    missing_pop = panel[panel["pop_2011"].isna()]["state_norm"].unique()
    if len(missing_pop):
        print(f"  WARNING: No population for: {missing_pop}")

    # UPI volume is in millions; population in persons
    # volume_per_capita = transactions per person per month
    panel["vol_pc"]   = (panel["volume_mn"] * 1e6) / panel["pop_2011"]
    # value_cr is crores of rupees; per capita in rupees
    panel["val_pc"]   = (panel["value_cr"] * 1e7) / panel["pop_2011"]

    panel["log_vol_pc"] = np.log(panel["vol_pc"].replace(0, np.nan))
    panel["log_val_pc"] = np.log(panel["val_pc"].replace(0, np.nan))

    # Date features
    panel["period"] = pd.to_datetime(panel["ym"] + "-01")
    panel["t"]      = panel.groupby("state_norm")["period"].rank(method="dense").astype(int)

    # Treatment assignment
    panel["treated"]   = panel["state_norm"].isin(TREATMENT_EVENTS.keys()).astype(int)
    panel["treat_date"] = panel["state_norm"].map(TREATMENT_EVENTS)
    panel["treat_period"] = pd.to_datetime(
        panel["treat_date"].fillna("2099-01") + "-01"
    )
    panel["post"] = (panel["period"] >= panel["treat_period"]).astype(int)
    panel["did"]  = panel["treated"] * panel["post"]

    # Relative time (months since treatment, reference = -1)
    panel["rel_t"] = (
        (panel["period"].dt.year * 12 + panel["period"].dt.month)
        - (panel["treat_period"].dt.year * 12 + panel["treat_period"].dt.month)
    )
    # For never-treated, rel_t is meaningless — set to large negative
    panel.loc[panel["treated"] == 0, "rel_t"] = -99

    # State and month FE codes
    panel["state_code"] = pd.Categorical(panel["state_norm"]).codes
    panel["month_code"] = pd.Categorical(panel["ym"]).codes

    return panel


# ── Estimation ─────────────────────────────────────────────────────────────────

def pick(m, key):
    params = m.params
    if key in params.index:
        return params[key], m.bse[key], m.pvalues[key]
    parts = key.split(":")
    cands = [k for k in params.index if all(p in k for p in parts)]
    exact = [k for k in cands if len(k.split(":")) == len(parts)]
    chosen = exact or cands
    if not chosen: return np.nan, np.nan, np.nan
    k = chosen[-1]
    return params[k], m.bse[k], m.pvalues[k]


def stars(p):
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def run_twfe(df, outcome):
    sub = df[df[outcome].notna()].copy()
    formula = f"{outcome} ~ did + C(state_code) + C(month_code)"
    m = smf.ols(formula, data=sub).fit(
        cov_type="cluster", cov_kwds={"groups": sub["state_code"]}
    )
    b, se, p = pick(m, "did")
    return {"model": m, "b": b, "se": se, "p": p, "n": len(sub),
            "n_states": sub["state_norm"].nunique()}


def run_per_cohort(df, state, outcome):
    """Clean 2×2 DiD: treated state vs never-treated controls, −12m to +12m around launch."""
    t0 = pd.to_datetime(TREATMENT_EVENTS[state] + "-01")
    window_start = t0 - pd.DateOffset(months=12)
    window_end   = t0 + pd.DateOffset(months=12)

    controls = df[df["treated"] == 0]["state_norm"].unique()
    sub = df[
        (df["state_norm"].isin([state] + list(controls))) &
        (df["period"] >= window_start) &
        (df["period"] <= window_end) &
        df[outcome].notna()
    ].copy()

    sub["treat_i"]  = (sub["state_norm"] == state).astype(int)
    sub["post_t"]   = (sub["period"] >= t0).astype(int)
    sub["did_clean"] = sub["treat_i"] * sub["post_t"]

    formula = f"{outcome} ~ did_clean + C(state_code) + C(month_code)"
    m = smf.ols(formula, data=sub).fit(
        cov_type="cluster", cov_kwds={"groups": sub["state_code"]}
    )
    b, se, p = pick(m, "did_clean")
    n_pre  = sub[(sub["state_norm"] == state) & (sub["post_t"] == 0)]["ym"].nunique()
    n_post = sub[(sub["state_norm"] == state) & (sub["post_t"] == 1)]["ym"].nunique()
    return {"b": b, "se": se, "p": p, "n_pre": n_pre, "n_post": n_post,
            "n_control_states": len(controls)}


def run_event_study(df, state, outcome, window=8):
    """Event study coefficients for a single treated state vs never-treated controls."""
    t0 = pd.to_datetime(TREATMENT_EVENTS[state] + "-01")
    window_start = t0 - pd.DateOffset(months=window + 1)
    window_end   = t0 + pd.DateOffset(months=window)

    controls = df[df["treated"] == 0]["state_norm"].unique()
    sub = df[
        (df["state_norm"].isin([state] + list(controls))) &
        (df["period"] >= window_start) &
        (df["period"] <= window_end) &
        df[outcome].notna()
    ].copy()

    sub["treat_i"] = (sub["state_norm"] == state).astype(int)
    sub["rel_t_here"] = (
        (sub["period"].dt.year * 12 + sub["period"].dt.month)
        - (t0.year * 12 + t0.month)
    )
    sub.loc[sub["treat_i"] == 0, "rel_t_here"] = -99

    # Create relative time dummies, reference = -1
    # Use safe names: dm6 for -6, dp1 for +1, d0 for 0
    def dname(rt):
        if rt < 0: return f"dm{abs(rt)}"
        elif rt == 0: return "d0"
        else: return f"dp{rt}"

    valid_rt = [r for r in range(-window, window + 1) if r != -1]
    for rt in valid_rt:
        sub[dname(rt)] = ((sub["treat_i"] == 1) & (sub["rel_t_here"] == rt)).astype(int)

    d_terms = " + ".join([dname(rt) for rt in valid_rt])
    formula = f"{outcome} ~ {d_terms} + C(state_code) + C(month_code)"
    m = smf.ols(formula, data=sub).fit(
        cov_type="cluster", cov_kwds={"groups": sub["state_code"]}
    )

    results = []
    for rt in range(-window, window + 1):
        if rt == -1:
            results.append({"rel_t": rt, "b": 0.0, "se": 0.0, "p": 1.0})
        else:
            b, se, p = pick(m, dname(rt))
            results.append({"rel_t": rt, "b": b, "se": se, "p": p})
    return pd.DataFrame(results)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("Building UPI panel...")
    panel = build_panel()
    n_states = panel["state_norm"].nunique()
    n_months = panel["ym"].nunique()
    print(f"  Panel: {n_states} states × {n_months} months = {len(panel)} rows")
    print(f"  Treatment cohorts: {list(TREATMENT_EVENTS.keys())}")
    print(f"  Date range: {panel['ym'].min()} – {panel['ym'].max()}")
    print()

    # Descriptive: UPI growth over time
    print("=== UPI Growth: National Aggregate ===")
    national = panel.groupby("ym").agg(
        vol_mn_total=("volume_mn","sum"),
        val_cr_total=("value_cr","sum"),
    ).reset_index()
    national["period"] = pd.to_datetime(national["ym"] + "-01")
    national = national.sort_values("period")
    # Show quarterly averages
    print(f"  {'Period':<12} {'Vol (Mn txns)':>16} {'Val (Rs Cr)':>14}")
    for _, r in national.iterrows():
        if r["ym"] in ["2023-04","2023-10","2024-04","2024-10","2025-04","2025-10","2025-12"]:
            print(f"  {r['ym']:<12} {r['vol_mn_total']:>16,.0f} {r['val_cr_total']:>14,.0f}")
    print()

    # Treated vs control pre-trends (raw log vol pc)
    print("=== Treated vs Control States: Mean log(vol per capita) ===")
    pre_period = panel[panel["period"] < pd.to_datetime("2024-02-01")]
    for grp, label in [(1,"Treated (CG/MH/JH)"),(0,"Control (never-treated)")]:
        subset = pre_period[pre_period["treated"]==grp]
        m = subset["log_vol_pc"].mean()
        print(f"  {label:<35}: mean log_vol_pc = {m:.4f}")
    print()

    # ── TABLE 1: Pooled TWFE ─────────────────────────────────────────────────
    print("=" * 75)
    print("TABLE 1: Pooled TWFE DiD — effect of women DBT launch on UPI activity")
    print("(State + month FE; 3 treated states: CG Feb-2024, MH Aug-2024, JH Nov-2024)")
    print(f"  {'Outcome':<40} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>7}")
    print("-" * 75)

    twfe_rows = []
    for outcome, label in [
        ("log_vol_pc", "log(UPI transactions per capita)"),
        ("log_val_pc", "log(UPI value per capita, Rs.)"),
    ]:
        r = run_twfe(panel, outcome)
        sig = stars(r["p"])
        print(f"  {label:<40} {r['b']:>+10.4f}{sig:<4} {r['se']:>8.4f} {r['p']:>7.3f} {r['n']:>7,}")
        twfe_rows.append({"outcome": outcome, **{k: r[k] for k in ("b","se","p","n")}})
    print()

    # ── TABLE 2: Per-cohort 2×2 DiD ─────────────────────────────────────────
    print("=" * 75)
    print("TABLE 2: Per-cohort 2×2 DiD — clean comparison (±12 months around launch)")
    print(f"  {'State / Program':<36} {'Launch':>8} {'Coeff':>10} {'SE':>8} {'p':>7} {'pre':>5} {'post':>5}")
    print("-" * 75)

    cohort_rows = []
    programs = {
        "CHHATTISGARH":  "Mahtari Vandan",
        "MAHARASHTRA":   "Ladki Bahin",
        "JHARKHAND":     "Maiya Samman",
    }
    for state, prog in programs.items():
        r = run_per_cohort(panel, state, "log_vol_pc")
        sig = stars(r["p"])
        label = f"{state.title()} ({prog})"
        print(f"  {label:<36} {TREATMENT_EVENTS[state]:>8} "
              f"{r['b']:>+10.4f}{sig:<4} {r['se']:>8.4f} {r['p']:>7.3f} "
              f"{r['n_pre']:>5} {r['n_post']:>5}")
        cohort_rows.append({"state": state, "program": prog,
                             "launch": TREATMENT_EVENTS[state], "outcome": "log_vol_pc", **r})

    print()
    for state, prog in programs.items():
        r = run_per_cohort(panel, state, "log_val_pc")
        sig = stars(r["p"])
        label = f"{state.title()} — value"
        print(f"  {label:<36} {TREATMENT_EVENTS[state]:>8} "
              f"{r['b']:>+10.4f}{sig:<4} {r['se']:>8.4f} {r['p']:>7.3f} "
              f"{r['n_pre']:>5} {r['n_post']:>5}")
        cohort_rows.append({"state": state, "program": prog,
                             "launch": TREATMENT_EVENTS[state], "outcome": "log_val_pc", **r})
    print()

    # ── TABLE 3: Event study coefficients ───────────────────────────────────
    print("=" * 75)
    print("TABLE 3: Event study — log(vol per capita), relative to month of launch (t=0)")
    print("(Reference period: t = −1; treated state vs never-treated controls)")
    print()

    all_es = {}
    for state, prog in programs.items():
        es = run_event_study(panel, state, "log_vol_pc", window=6)
        all_es[state] = es
        print(f"  === {state.title()} — {prog} (launch: {TREATMENT_EVENTS[state]}) ===")
        print(f"  {'rel_t':>6} {'coeff':>10} {'SE':>8} {'p':>7} {'sig':>4}")
        for _, row in es.iterrows():
            sig = stars(row["p"])
            print(f"  {int(row['rel_t']):>6} {row['b']:>+10.4f} {row['se']:>8.4f} {row['p']:>7.3f} {sig:>4}")
        print()

    # ── Save ─────────────────────────────────────────────────────────────────
    pd.DataFrame(twfe_rows).to_csv(RESULTS_DIR / "upi_dbt_twfe.csv", index=False)
    pd.DataFrame(cohort_rows).to_csv(RESULTS_DIR / "upi_dbt_cohort_did.csv", index=False)
    es_all = pd.concat(
        [df.assign(state=s) for s, df in all_es.items()], ignore_index=True
    )
    es_all.to_csv(RESULTS_DIR / "upi_dbt_event_study.csv", index=False)

    # Save cleaned panel for plotting
    panel.to_csv(RESULTS_DIR / "upi_dbt_panel.csv", index=False)
    print("Results saved → results/tables/upi_dbt_*.csv")
    print("Done.")


if __name__ == "__main__":
    main()
