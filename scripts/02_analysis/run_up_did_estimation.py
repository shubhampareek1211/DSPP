"""
UP district-level DiD estimation.

Design
------
Repeated cross-section: NFHS-4 (2015-16, pre-treatment) vs NFHS-5 (2019-21, post-treatment).
Unit of observation: individual woman i in district d, survey round t.

Base specification (district FE):
    Y_idt = alpha_d + beta*post_t + gamma*(post_t x treat_d) + X_i'delta + e_idt

    gamma = DiD coefficient: differential change in outcome for districts with
            higher PMMVY exposure, absorbing time-invariant district confounders.

Heterogeneity specification:
    Adds post_t x treat_d x banking_d to test whether pre-treatment banking
    infrastructure moderates the PMMVY effect.

Treatment variable: pmmvy_per_1000 = beneficiaries_total / (population_2011 / 1000)

Outcomes:
    bank_account_self_use, mobile_phone_self_use, worked_last_12_months,
    own_money_autonomy, decision_any_say (recoded), loan_program_knowledge

Standard errors clustered on the 73 harmonized district units matched across rounds.
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


# ── Load and prepare data ─────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    path = PROJECT_ROOT / "data" / "processed" / "up" / "up_analysis_dataset.parquet"
    df = pd.read_parquet(path)

    # ── Outcome recoding ──────────────────────────────────────────────────────
    # Decision outcomes: 1=alone, 2=jointly → woman has any say; 4/5/6 → no say.
    for col in ["decision_health_care", "decision_large_purchases"]:
        df[col.replace("decision_", "decision_any_say_")] = (
            df[col].isin([1.0, 2.0]).astype(float)
        )
        df.loc[df[col].isna(), col.replace("decision_", "decision_any_say_")] = np.nan

    # Composite decision index (mean of the two recoded items)
    dc = "decision_any_say_health_care"
    dl = "decision_any_say_large_purchases"
    df["decision_index"] = df[[dc, dl]].mean(axis=1)

    # ── Treatment variables ───────────────────────────────────────────────────
    df["pmmvy_per_1000"] = df["beneficiaries_total"] / (df["population_2011"] / 1000)
    df["pmmvy_per_1000_std"] = (
        (df["pmmvy_per_1000"] - df["pmmvy_per_1000"].mean())
        / df["pmmvy_per_1000"].std()
    )
    df["log_pmmvy"] = np.log(df["beneficiaries_total"])

    # ── Banking heterogeneity ─────────────────────────────────────────────────
    median_bd = df["branch_density_2013"].median()
    df["high_banking"] = (df["branch_density_2013"] > median_bd).astype(int)
    df["branch_density_std"] = (
        (df["branch_density_2013"] - df["branch_density_2013"].mean())
        / df["branch_density_2013"].std()
    )

    # ── Controls ──────────────────────────────────────────────────────────────
    df["age_sq"] = df["age"] ** 2
    df["edu"] = df["education_level"].fillna(0).astype(float)
    df["urban"] = (df["urban_rural"] == 1).astype(float)

    return df


# ── Estimation helpers ────────────────────────────────────────────────────────

def run_did(
    df: pd.DataFrame,
    outcome: str,
    treat_var: str = "pmmvy_per_1000_std",
    district_fe: bool = True,
    controls: bool = True,
    weight_col: str | None = "state_module_weight",
) -> dict:
    sub = df[df[outcome].notna()].copy()

    ctrl = "+ age + age_sq + edu + urban + wealth_index" if controls else ""

    if district_fe:
        formula = f"{outcome} ~ post + post:{treat_var} {ctrl} + C({DISTRICT_ID})"
    else:
        formula = f"{outcome} ~ post + {treat_var} + post:{treat_var} {ctrl}"

    weights = sub[weight_col] if weight_col else None

    model = smf.wls(formula, data=sub, weights=weights).fit(
        cov_type="cluster",
        cov_kwds={"groups": sub[DISTRICT_ID]},
    )
    return {"model": model, "n": len(sub), "n_districts": sub[DISTRICT_ID].nunique()}


def run_heterogeneity(
    df: pd.DataFrame,
    outcome: str,
    treat_var: str = "pmmvy_per_1000_std",
    moderator: str = "branch_density_std",
    weight_col: str | None = "state_module_weight",
) -> dict:
    sub = df[df[outcome].notna()].copy()

    formula = (
        f"{outcome} ~ post + post:{treat_var} + post:{moderator}"
        f" + post:{treat_var}:{moderator}"
        f" + age + age_sq + edu + urban + wealth_index"
        f" + C({DISTRICT_ID})"
    )
    weights = sub[weight_col] if weight_col else None
    model = smf.wls(formula, data=sub, weights=weights).fit(
        cov_type="cluster",
        cov_kwds={"groups": sub[DISTRICT_ID]},
    )
    return {"model": model, "n": len(sub), "n_districts": sub[DISTRICT_ID].nunique()}


def run_subgroup(
    df: pd.DataFrame,
    outcome: str,
    treat_var: str = "pmmvy_per_1000_std",
    weight_col: str | None = "state_module_weight",
) -> tuple[dict, dict]:
    low = df[df["high_banking"] == 0]
    high = df[df["high_banking"] == 1]
    return (
        run_did(low, outcome, treat_var, weight_col=weight_col),
        run_did(high, outcome, treat_var, weight_col=weight_col),
    )


# ── Result formatting ────────────────────────────────────────────────────────

def extract_coef(result: dict, coef_pattern: str) -> tuple[float, float, float]:
    model = result["model"]
    params = model.params
    pvals = model.pvalues
    bses = model.bse
    if coef_pattern in params.index:
        return params[coef_pattern], bses[coef_pattern], pvals[coef_pattern]
    matches = [k for k in params.index if coef_pattern in k]
    if not matches:
        return np.nan, np.nan, np.nan
    k = matches[-1]
    return params[k], bses[k], pvals[k]


def stars(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def format_coef(b: float, se: float, p: float) -> str:
    if np.isnan(b):
        return "—"
    return f"{b:.4f}{stars(p)}\n({se:.4f})"


# ── Main ──────────────────────────────────────────────────────────────────────

OUTCOMES = {
    "bank_account_self_use":          "Bank account self-use",
    "mobile_phone_self_use":          "Mobile phone self-use",
    "worked_last_12_months":          "Worked last 12 months",
    "own_money_autonomy":             "Own money autonomy",
    "decision_any_say_health_care":   "Any say: health care",
    "decision_any_say_large_purchases": "Any say: large purchases",
    "loan_program_knowledge":         "Loan programme knowledge",
}


def main() -> None:
    print("Loading data...")
    df = load_data()
    sub = df[df["bank_account_self_use"].notna()].copy()
    print(f"  Estimation sample: {len(sub):,} women, {sub[DISTRICT_ID].nunique()} matched districts")
    print(f"  NFHS-4: {(sub['post']==0).sum():,}   NFHS-5: {(sub['post']==1).sum():,}")
    print(f"  Treatment (pmmvy_per_1000): mean={sub['pmmvy_per_1000'].mean():.1f}, "
          f"sd={sub['pmmvy_per_1000'].std():.1f}, "
          f"min={sub['pmmvy_per_1000'].min():.1f}, max={sub['pmmvy_per_1000'].max():.1f}")
    print(f"  Branch density: median={df['branch_density_2013'].median():.2f}, "
          f"high-banking districts: {sub[sub['high_banking']==1][DISTRICT_ID].nunique()}")
    print()

    # ── Table 1: Main DiD results ──────────────────────────────────────────────
    print("=" * 80)
    print("TABLE 1: Main DiD Results (district FE, weighted, clustered SE at district)")
    print("Outcome                             coef(post x treat)    SE        p     N")
    print("-" * 80)

    main_results = {}
    for outcome, label in OUTCOMES.items():
        r = run_did(df, outcome)
        b, se, p = extract_coef(r, "post:pmmvy_per_1000_std")
        main_results[outcome] = r
        print(f"  {label:<36} {b:+.4f}{stars(p):<4}  ({se:.4f})  {p:.3f}  {r['n']:,}")

    # ── Table 2: Heterogeneity — above vs below median branch density ──────────
    print()
    print("=" * 80)
    print("TABLE 2: Subgroup by pre-treatment banking (branch density 2013)")
    print(f"  Low banking: ≤ median ({df['branch_density_2013'].median():.2f} per 100k)")
    print(f"  High banking: > median")
    print()
    print(f"  {'Outcome':<36} {'Low banking':>16} {'High banking':>16}")
    print("-" * 80)

    for outcome, label in OUTCOMES.items():
        r_low, r_high = run_subgroup(df, outcome)
        b_lo, se_lo, p_lo = extract_coef(r_low, "post:pmmvy_per_1000_std")
        b_hi, se_hi, p_hi = extract_coef(r_high, "post:pmmvy_per_1000_std")
        lo_str = f"{b_lo:+.4f}{stars(p_lo)}" if not np.isnan(b_lo) else "—"
        hi_str = f"{b_hi:+.4f}{stars(p_hi)}" if not np.isnan(b_hi) else "—"
        print(f"  {label:<36} {lo_str:>16} {hi_str:>16}")

    # ── Table 3: Triple interaction (continuous moderator) ─────────────────────
    print()
    print("=" * 80)
    print("TABLE 3: Triple interaction — post x treat x branch_density (standardised)")
    print("Outcome                             post:treat   post:banking  post:treat:banking")
    print("-" * 80)

    heterogeneity_rows = []
    for outcome, label in OUTCOMES.items():
        r = run_heterogeneity(df, outcome)
        b1, se1, p1 = extract_coef(r, "post:pmmvy_per_1000_std")
        b2, se2, p2 = extract_coef(r, "post:branch_density_std")
        b3, se3, p3 = extract_coef(r, "post:pmmvy_per_1000_std:branch_density_std")
        s1 = f"{b1:+.4f}{stars(p1)}" if not np.isnan(b1) else "—"
        s2 = f"{b2:+.4f}{stars(p2)}" if not np.isnan(b2) else "—"
        s3 = f"{b3:+.4f}{stars(p3)}" if not np.isnan(b3) else "—"
        print(f"  {label:<36} {s1:>14} {s2:>14} {s3:>20}")
        heterogeneity_rows.append({
            "outcome": outcome,
            "label": label,
            "post_pmmvy": b1,
            "post_pmmvy_se": se1,
            "post_pmmvy_pval": p1,
            "post_banking": b2,
            "post_banking_se": se2,
            "post_banking_pval": p2,
            "triple_coef": b3,
            "triple_se": se3,
            "triple_pval": p3,
            "n": r["n"],
            "n_districts": r["n_districts"],
        })

    # ── Table 4: Pre-post means by district banking tercile ────────────────────
    print()
    print("=" * 80)
    print("TABLE 4: Raw pre-post means (NFHS-4 vs NFHS-5) by banking group")

    df["banking_tercile"] = pd.qcut(df["branch_density_2013"], 3,
                                    labels=["Low", "Mid", "High"])
    means = (
        df[df["bank_account_self_use"].notna()]
        .groupby(["banking_tercile", "survey_round"])[list(OUTCOMES.keys())]
        .mean()
        .round(3)
    )
    print(means.to_string())

    # ── Save summary CSV ───────────────────────────────────────────────────────
    rows = []
    for outcome, label in OUTCOMES.items():
        r = main_results[outcome]
        b, se, p = extract_coef(r, "post:pmmvy_per_1000_std")
        rows.append({
            "outcome": outcome,
            "label": label,
            "coef_post_x_treat": b,
            "se": se,
            "pval": p,
            "n": r["n"],
            "n_districts": r["n_districts"],
        })
    results_df = pd.DataFrame(rows)
    out_path = RESULTS_DIR / "up_did_main_results.csv"
    results_df.to_csv(out_path, index=False)
    pd.DataFrame(heterogeneity_rows).to_csv(
        RESULTS_DIR / "table3_triple_interaction.csv", index=False
    )
    print(f"\nMain results saved → {out_path.name}")
    print("Interaction results saved → table3_triple_interaction.csv")
    print("\nDone.")


if __name__ == "__main__":
    main()
