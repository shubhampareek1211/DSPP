"""
MKSY girls DiD estimation — UP district-level.

Design
------
Repeated cross-section: NFHS-4 (2015-16, pre-treatment) vs NFHS-5 (2019-21, post-treatment).
Sample restricted to adolescent girls aged 15-19 in the NFHS state module subsample.

MKSY (Mukhyamantri Kanya Sumangala Yojana) launched December 2019 in UP.
Treatment is measured from cumulative district-level enrollment as of ~2021.
Exposure window for NFHS-5 respondents: roughly 0-18 months.

Base specification (district FE):
    Y_idt = alpha_d + beta*post_t + gamma*(post_t x MKSY_d) + X_i'delta + e_idt

    gamma = differential change in outcome for girls in higher-MKSY districts,
            absorbing time-invariant district confounders.

Treatment variables:
    mksy_net_per1000   — total net approved beneficiaries / (pop_2011/1000) [primary]
    mksy_cat1_per1000  — condition 1 (birth registration) per 1000
    mksy_cat2_per1000  — condition 2 (class 1 admission) per 1000

Outcomes (girls 15-19):
    bank_account_self_use    — owns/uses bank account herself
    mobile_phone_self_use    — uses mobile phone herself
    worked_last_12_months    — engaged in paid work (decrease = more in school)
    own_money_autonomy       — decides how to spend own money
    loan_program_knowledge   — aware of any loan/credit programme

Standard errors clustered at district level.
"""

from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
DISTRICT_ID = "district_name_norm"


# ── Data prep ─────────────────────────────────────────────────────────────────

def load_girls(age_lo: int = 15, age_hi: int = 19) -> pd.DataFrame:
    df = pd.read_parquet(
        PROJECT_ROOT / "data" / "processed" / "up" / "up_analysis_dataset.parquet"
    )

    # Restrict to adolescent girls with state-module outcomes
    df = df[(df["age"] >= age_lo) & (df["age"] <= age_hi)].copy()
    df = df[df["bank_account_self_use"].notna()].copy()

    # Treatment: per-1000 and standardised
    for raw, name in [
        ("mksy_net_approved",     "mksy_net"),
        ("mksy_cat1_beneficiaries", "mksy_cat1"),
        ("mksy_cat2_beneficiaries", "mksy_cat2"),
    ]:
        df[f"{name}_per1000"] = df[raw] / (df["population_2011"] / 1000)
        df[f"{name}_std"] = (
            (df[f"{name}_per1000"] - df[f"{name}_per1000"].mean())
            / df[f"{name}_per1000"].std()
        )

    # Controls
    df["age_sq"] = df["age"] ** 2
    df["edu"]    = df["education_level"].fillna(0).astype(float)
    df["urban"]  = (df["urban_rural"] == 1).astype(float)

    # Banking moderator (for heterogeneity)
    df["branch_density_std"] = (
        (df["branch_density_2013"] - df["branch_density_2013"].mean())
        / df["branch_density_2013"].std()
    )

    return df


# ── Estimation ────────────────────────────────────────────────────────────────

def run_did(
    df: pd.DataFrame,
    outcome: str,
    treat_var: str = "mksy_net_std",
    weight_col: str | None = "state_module_weight",
) -> dict:
    sub = df[df[outcome].notna()].copy()
    formula = (
        f"{outcome} ~ post + post:{treat_var}"
        f" + age + age_sq + edu + urban + wealth_index"
        f" + C({DISTRICT_ID})"
    )
    weights = sub[weight_col] if weight_col else None
    model = smf.wls(formula, data=sub, weights=weights).fit(
        cov_type="cluster",
        cov_kwds={"groups": sub[DISTRICT_ID]},
    )
    return {"model": model, "n": len(sub), "n_dist": sub[DISTRICT_ID].nunique()}


def run_triple(
    df: pd.DataFrame,
    outcome: str,
    treat_var: str = "mksy_net_std",
    mod_var: str = "branch_density_std",
    weight_col: str | None = "state_module_weight",
) -> dict:
    sub = df[df[outcome].notna()].copy()
    formula = (
        f"{outcome} ~ post + post:{treat_var} + post:{mod_var}"
        f" + post:{treat_var}:{mod_var}"
        f" + age + age_sq + edu + urban + wealth_index"
        f" + C({DISTRICT_ID})"
    )
    weights = sub[weight_col] if weight_col else None
    model = smf.wls(formula, data=sub, weights=weights).fit(
        cov_type="cluster",
        cov_kwds={"groups": sub[DISTRICT_ID]},
    )
    return {"model": model, "n": len(sub), "n_dist": sub[DISTRICT_ID].nunique()}


# ── Coefficient extraction ─────────────────────────────────────────────────────

def pick(m, key: str):
    params = m.params
    if key in params.index:
        return params[key], m.bse[key], m.pvalues[key]
    parts = key.split(":")
    cands = [k for k in params.index if all(p in k for p in parts)]
    exact  = [k for k in cands if len(k.split(":")) == len(parts)]
    chosen = (exact or cands)
    if not chosen:
        return np.nan, np.nan, np.nan
    k = chosen[-1]
    return params[k], m.bse[k], m.pvalues[k]


def stars(p: float) -> str:
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


# ── Main ──────────────────────────────────────────────────────────────────────

OUTCOMES = {
    "bank_account_self_use":  "Bank account self-use",
    "mobile_phone_self_use":  "Mobile phone self-use",
    "worked_last_12_months":  "Worked last 12 months",
    "own_money_autonomy":     "Own money autonomy",
    "loan_program_knowledge": "Loan programme knowledge",
}


def main() -> None:
    print("Loading data (girls 15-19)...")
    df = load_girls()
    print(f"  Sample: {len(df):,} girls, {df[DISTRICT_ID].nunique()} matched districts")
    print(f"  NFHS-4: {(df['post']==0).sum():,}   NFHS-5: {(df['post']==1).sum():,}")
    print()

    # Treatment descriptives
    print("=== MKSY Treatment Variables (district level) ===")
    dist = df.drop_duplicates(DISTRICT_ID)
    for v in ["mksy_net_per1000", "mksy_cat1_per1000", "mksy_cat2_per1000"]:
        s = dist[v]
        print(f"  {v:<28}  mean={s.mean():.3f}  sd={s.std():.3f}"
              f"  min={s.min():.3f}  max={s.max():.3f}")
    print()

    # Pre-post means
    print("=== Pre-Post Means for Girls 15-19 (state module) ===")
    print(f"  {'Outcome':<40} {'NFHS-4':>8} {'NFHS-5':>8} {'Change':>8}")
    print("-" * 70)
    for col, label in OUTCOMES.items():
        pre  = df[df["post"]==0][col].mean()
        post = df[df["post"]==1][col].mean()
        print(f"  {label:<40} {pre:>8.3f} {post:>8.3f} {post-pre:>+8.3f}")
    print()

    # ── Table A: Main DiD — net approved ──────────────────────────────────────
    print("=" * 80)
    print("TABLE A: DiD — post × MKSY_net_approved_per1000_std")
    print("(district FE, WLS, clustered SE; girls 15-19)")
    print(f"  {'Outcome':<40} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>7}")
    print("-" * 80)

    rows_net = []
    for col, label in OUTCOMES.items():
        r = run_did(df, col, treat_var="mksy_net_std")
        b, se, p = pick(r["model"], "post:mksy_net_std")
        rows_net.append({"outcome": col, "label": label,
                         "treat": "net", "b": b, "se": se, "p": p, "n": r["n"]})
        sig = stars(p)
        print(f"  {label:<40} {b:>+10.4f}{sig:<4} {se:>8.4f} {p:>7.3f} {r['n']:>7,}")

    # ── Table B: DiD — cat1 (birth registration) ──────────────────────────────
    print()
    print("=" * 80)
    print("TABLE B: DiD — post × MKSY_cat1_per1000_std  (birth registration)")
    print(f"  {'Outcome':<40} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>7}")
    print("-" * 80)

    rows_cat1 = []
    for col, label in OUTCOMES.items():
        r = run_did(df, col, treat_var="mksy_cat1_std")
        b, se, p = pick(r["model"], "post:mksy_cat1_std")
        rows_cat1.append({"outcome": col, "label": label,
                          "treat": "cat1", "b": b, "se": se, "p": p, "n": r["n"]})
        sig = stars(p)
        print(f"  {label:<40} {b:>+10.4f}{sig:<4} {se:>8.4f} {p:>7.3f} {r['n']:>7,}")

    # ── Table C: DiD — cat2 (class 1 admission) ───────────────────────────────
    print()
    print("=" * 80)
    print("TABLE C: DiD — post × MKSY_cat2_per1000_std  (class 1 admission)")
    print(f"  {'Outcome':<40} {'Coeff':>10} {'SE':>8} {'p':>7} {'N':>7}")
    print("-" * 80)

    rows_cat2 = []
    for col, label in OUTCOMES.items():
        r = run_did(df, col, treat_var="mksy_cat2_std")
        b, se, p = pick(r["model"], "post:mksy_cat2_std")
        rows_cat2.append({"outcome": col, "label": label,
                          "treat": "cat2", "b": b, "se": se, "p": p, "n": r["n"]})
        sig = stars(p)
        print(f"  {label:<40} {b:>+10.4f}{sig:<4} {se:>8.4f} {p:>7.3f} {r['n']:>7,}")

    # ── Table D: Banking heterogeneity (triple interaction, net approved) ──────
    print()
    print("=" * 80)
    print("TABLE D: Triple interaction — post × MKSY_net × branch_density")
    print(f"  {'Outcome':<40} {'post:treat':>12} {'post:bank':>12} {'triple':>12}")
    print("-" * 80)

    rows_triple = []
    for col, label in OUTCOMES.items():
        r = run_triple(df, col)
        b1, se1, p1 = pick(r["model"], "post:mksy_net_std")
        b2, se2, p2 = pick(r["model"], "post:branch_density_std")
        b3, se3, p3 = pick(r["model"], "post:mksy_net_std:branch_density_std")
        rows_triple.append({"outcome": col, "label": label,
                             "b_treat": b1, "p_treat": p1,
                             "b_bank": b2,  "p_bank": p2,
                             "b_triple": b3, "p_triple": p3, "n": r["n"]})
        s1 = f"{b1:+.4f}{stars(p1)}" if not np.isnan(b1) else "—"
        s2 = f"{b2:+.4f}{stars(p2)}" if not np.isnan(b2) else "—"
        s3 = f"{b3:+.4f}{stars(p3)}" if not np.isnan(b3) else "—"
        print(f"  {label:<40} {s1:>12} {s2:>12} {s3:>12}")

    # ── Save results ───────────────────────────────────────────────────────────
    all_rows = rows_net + rows_cat1 + rows_cat2
    pd.DataFrame(all_rows).to_csv(
        RESULTS_DIR / "mksy_girls_did_main.csv", index=False
    )
    pd.DataFrame(rows_triple).to_csv(
        RESULTS_DIR / "mksy_girls_did_triple.csv", index=False
    )
    print("\nResults saved → results/tables/mksy_girls_did_main.csv, "
          "results/tables/mksy_girls_did_triple.csv")
    print("\nDone.")


if __name__ == "__main__":
    main()
