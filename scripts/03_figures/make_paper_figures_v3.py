"""
Revised figures v3:
  Fig 1 – raw autonomy change by PMMVY-intensity tercile
  Fig 2 – bar chart: banking bonus gap per state (drop slope chart)
  Fig 3 – legend moved outside the plot to the right
  Fig 4 – only label the 5 study states (UP, Assam, MP, WB, HP)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from scipy import stats
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE = str(PROJECT_ROOT / "results" / "tables") + "/"
OUTDIR = str(PROJECT_ROOT / "results" / "figures" / "paper") + "/"
Path(OUTDIR).mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

SIG   = "#2171b5"
INSIG = "#bdbdbd"

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1  —  Raw own-money-autonomy change by PMMVY-intensity tercile
# ═══════════════════════════════════════════════════════════════════════════════
terciles = pd.read_csv(BASE + "pmmvy_tercile_raw_changes.csv")
terciles = terciles.set_index("tercile").reindex(["Low", "Mid", "High"]).reset_index()
labels = [
    f"{row.tercile} tercile\n(avg {row.intensity_mean:.1f}/1,000)"
    for row in terciles.itertuples()
]
autonomy = terciles["money_autonomy"].to_numpy()
colors = ["#c6dbef", "#6baed6", "#2171b5"]

fig, ax = plt.subplots(figsize=(6.5, 4.5))
bars = ax.bar(range(3), autonomy, color=colors, width=0.55,
              zorder=3, edgecolor="white")
for bar, val in zip(bars, autonomy):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
            f"{val:+.1f} pp", ha="center", va="bottom", fontsize=11,
            fontweight="bold", color=bar.get_facecolor())

ax.set_xticks(range(3))
ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel("NFHS-4 → NFHS-5 change in\nown money autonomy (percentage points)",
              fontsize=9.5)
ax.set_ylim(0, max(16, autonomy.max() + 3))
ax.yaxis.grid(True, zorder=0)
ax.set_axisbelow(True)
ax.set_title(
    "Figure 1  States with Higher PMMVY Enrollment Had Larger Raw Gains\n"
    "in Women's Financial Autonomy",
    fontsize=11, fontweight="bold", loc="left", pad=10)
ax.text(0, -0.2,
        "Own money autonomy = share of women who have personal money they control (NFHS).\n"
        "Descriptive state-tercile means; no controls and no causal interpretation.",
        transform=ax.transAxes, fontsize=7.5, color="#555", va="top")

plt.tight_layout()
plt.savefig(OUTDIR + "fig1_autonomy_tercile.png", bbox_inches="tight", dpi=180)
plt.close()
print("Saved fig1_autonomy_tercile.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2  —  Banking bonus bar chart (gap between high and low banking)
# ═══════════════════════════════════════════════════════════════════════════════
# Gap = (did + triple) – (did – triple) = 2 × triple_coef × 100  (in pp)
# Interpretation: extra gain in own money autonomy in high- vs low-banking district

mc  = pd.read_csv(BASE + "multistate_did_combined.csv")
aut = mc[mc["outcome"] == "own_money_autonomy"].copy()

# Add UP from the current harmonized-district interaction results.
up_results = pd.read_csv(BASE + "table3_triple_interaction.csv")
up_row = up_results.loc[up_results["outcome"] == "own_money_autonomy"].iloc[0]
up  = pd.DataFrame([{"state": "UP", "triple_coef": up_row["triple_coef"],
                      "triple_se": up_row["triple_se"],
                      "triple_pval": up_row["triple_pval"]}])
aut = pd.concat([up, aut[["state","triple_coef","triple_se","triple_pval"]]],
                ignore_index=True)

# Drop HP (unreliable: <30 clusters, negative direction)
aut = aut[aut["state"] != "HP"].copy()

aut["gap_pp"]    = aut["triple_coef"] * 2 * 100     # high minus low (pp)
aut["gap_se_pp"] = aut["triple_se"]   * 2 * 100
aut["sig"]       = aut["triple_pval"] < 0.05

full_names = {"UP": "Uttar Pradesh\n(73 matched districts, n=29,226)",
              "Assam": "Assam\n(24 districts, n=7,278)",
              "MP": "Madhya Pradesh\n(47 districts, n=15,768)",
              "WB": "West Bengal\n(17 districts, n=5,159)"}

# Sort by gap descending
aut = aut.sort_values("gap_pp", ascending=True).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(9, 5.2))

for i, row in aut.iterrows():
    col  = SIG if row["sig"] else INSIG
    yerr = row["gap_se_pp"] * 1.96
    bar  = ax.barh(i, row["gap_pp"], color=col, height=0.55,
                   xerr=yerr, error_kw=dict(lw=1.5, capsize=4, color="#555"),
                   zorder=3)

    # Value label
    label = f"{row['gap_pp']:.1f} pp"
    if not row["sig"]:
        label += "  (n.s.)"
    ax.text(row["gap_pp"] + yerr + 0.3, i, label,
            va="center", fontsize=9,
            color=col, fontweight="bold" if row["sig"] else "normal")

ax.set_yticks(range(len(aut)))
ax.set_yticklabels([full_names[s] for s in aut["state"]], fontsize=9.5)
ax.set_xlabel("Estimated difference in women's financial-autonomy change\n"
              "— high-banking districts vs low-banking districts (percentage points)",
              fontsize=9.5)
ax.axvline(0, color="#333", lw=1, zorder=2)
upper_limit = np.ceil((aut["gap_pp"] + 1.96 * aut["gap_se_pp"]).max() + 2)
ax.set_xlim(0, upper_limit)
ax.xaxis.grid(True, zorder=0)
ax.set_axisbelow(True)

sig_patch   = mpatches.Patch(color=SIG,   label="Significant (p < 0.05)")
insig_patch = mpatches.Patch(color=INSIG, label="Not significant")
ax.legend(handles=[sig_patch, insig_patch], fontsize=8.5,
          loc="lower right", framealpha=0.9)

ax.set_title(
    "Figure 2  Estimated PMMVY–Autonomy Association Is Larger Where Banking Is Deeper\n"
    "Difference between above-average and below-average banking coverage",
    fontsize=10.5, fontweight="bold", loc="left", pad=10)
ax.text(0, -0.22,
    "Each bar = estimated difference in the PMMVY–autonomy association between high-banking "
    "and low-banking districts within the same state.\n"
    "Estimated from triple-interaction DiD: Post × PMMVY intensity × Branch density (2013). CIs are 95%.",
    transform=ax.transAxes, fontsize=7.5, color="#555", va="top")

fig.subplots_adjust(left=0.25, right=0.97, top=0.80, bottom=0.29)
plt.savefig(OUTDIR + "fig2_banking_bonus.png", bbox_inches="tight", dpi=180)
plt.close()
print("Saved fig2_banking_bonus.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3  —  Paired bar chart, legend outside on the right
# ═══════════════════════════════════════════════════════════════════════════════
sb = pd.read_csv(BASE + "study_b_district_expansion_results.csv")

outcomes  = ["child_marriage", "teen_pregnancy", "schooling_10plus"]
out_labels = {
    "child_marriage":   "Child\nmarriage",
    "teen_pregnancy":   "Teen\npregnancy",
    "schooling_10plus": "Women completing\nhigher-secondary school",
}
regs = ["log_branch_2013", "log_branch_growth"]
reg_colors = {"log_branch_2013": "#2171b5", "log_branch_growth": "#bdbdbd"}

data = sb[sb["regressor"].isin(regs) & sb["outcome"].isin(outcomes)].copy()

fig, ax = plt.subplots(figsize=(9, 5))

x_centers = np.arange(len(outcomes)) * 1.4
bar_w     = 0.32

for ri, reg in enumerate(regs):
    sub     = data[data["regressor"] == reg].set_index("outcome").reindex(outcomes)
    offsets = x_centers + (ri - 0.5) * bar_w + bar_w / 2

    for oi, outcome in enumerate(outcomes):
        row    = sub.loc[outcome]
        c, se, p = row["b"], row["se"], row["p"]
        is_sig = p < 0.05
        col    = reg_colors[reg] if is_sig else "#d9d9d9"
        x      = offsets[oi]

        ax.bar(x, c, width=bar_w * 0.88, color=col, zorder=3, edgecolor="white")
        ax.errorbar(x, c, yerr=1.96 * se, fmt="none",
                    color="#444", capsize=3, lw=1.2, zorder=4)

        stars = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "n.s."))
        ypos  = (c + 1.96*se + 0.07) if c >= 0 else (c - 1.96*se - 0.2)
        ax.text(x, ypos, stars, ha="center", fontsize=8.5,
                color=col if is_sig else "#aaa",
                fontweight="bold" if is_sig else "normal")

ax.axhline(0, color="#333", lw=1.2, zorder=2)
ax.set_xticks(x_centers)
ax.set_xticklabels([out_labels[o] for o in outcomes], fontsize=10.5)
ax.set_ylabel("Regression coefficient for women's outcome\n(percentage points per SD)", fontsize=9.5)
ax.yaxis.grid(True, zorder=0)
ax.set_axisbelow(True)

# ── Legend OUTSIDE the plot, on the right ──
legend_handles = [
    mpatches.Patch(color="#2171b5",
                   label="Bank branches per capita in 2013\n(pre-existing coverage)"),
    mpatches.Patch(color="#d9d9d9",
                   label="New branches added 2013–2020\n(recent expansion)  — not significant"),
]
ax.legend(handles=legend_handles, fontsize=8.5,
          loc="upper left", bbox_to_anchor=(1.02, 1),
          framealpha=0.95, edgecolor="#ccc", borderpad=0.8)

ax.set_title(
    "Figure 3  Pre-Existing Banking Depth Is Associated with Women's Outcomes;\n"
    "Recent Branch-Expansion Estimates Are Imprecise",
    fontsize=10.5, fontweight="bold", loc="left", pad=10)
ax.text(0, -0.17,
    "OLS with state fixed effects, 514 districts. Controls: electricity access, clean cooking fuel, "
    "female school attendance. CIs are 95%.\n"
    "Downward bars = lower child marriage / teen pregnancy (better outcome).  "
    "Upward bar = more schooling (better outcome).",
    transform=ax.transAxes, fontsize=7.5, color="#555", va="top")

plt.tight_layout()
plt.savefig(OUTDIR + "fig3_branches_vs_growth.png",
            bbox_inches="tight", dpi=180)
plt.close()
print("Saved fig3_branches_vs_growth.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4  —  State panel scatter, only label 5 study states
# ═══════════════════════════════════════════════════════════════════════════════
panel = pd.read_csv(BASE + "study_a_state_panel_data.csv")
panel = panel[panel["state_canon"] != "INDIA"].dropna(
    subset=["log_deposits_pc", "bank_account_use", "round"]).copy()

STUDY_STATES = {
    "UTTAR PRADESH":    "Uttar Pradesh",
    "ASSAM":            "Assam",
    "MADHYA PRADESH":   "Madhya Pradesh",
    "WEST BENGAL":      "West Bengal",
    "HIMACHAL PRADESH": "Himachal Pradesh",
}

rounds       = ["NFHS-3", "NFHS-4", "NFHS-5"]
round_colors = {"NFHS-3": "#fdae6b", "NFHS-4": "#3182bd", "NFHS-5": "#006d2c"}
round_labels = {"NFHS-3": "NFHS-3 (2005–06)",
                "NFHS-4": "NFHS-4 (2015–16)",
                "NFHS-5": "NFHS-5 (2019–21)"}

fig, ax = plt.subplots(figsize=(9.5, 6))

for rnd in rounds:
    sub = panel[panel["round"] == rnd]
    col = round_colors[rnd]

    # All dots — no labels on non-study states
    ax.scatter(sub["log_deposits_pc"], sub["bank_account_use"],
               color=col, s=35, alpha=0.5, zorder=3)

    # Trend line
    xv = sub["log_deposits_pc"].values
    yv = sub["bank_account_use"].values
    m, b_int, *_ = stats.linregress(xv, yv)
    xl = np.linspace(xv.min(), xv.max(), 100)
    ax.plot(xl, m*xl + b_int, color=col, lw=2,
            linestyle="--" if rnd == "NFHS-3" else "-", alpha=0.85, zorder=2)

# Label only study states, NFHS-5 only — with offset to avoid overlap
nfhs5 = panel[panel["round"] == "NFHS-5"]
offsets = {
    "UTTAR PRADESH":    (-0.45, -3.5),
    "ASSAM":            (-0.5,   2.0),
    "MADHYA PRADESH":   ( 0.05,  2.0),
    "WEST BENGAL":      ( 0.05, -3.5),
    "HIMACHAL PRADESH": ( 0.05,  1.5),
}
for _, row in nfhs5.iterrows():
    if row["state_canon"] in STUDY_STATES:
        xo, yo = offsets[row["state_canon"]]
        ax.annotate(
            STUDY_STATES[row["state_canon"]],
            xy=(row["log_deposits_pc"], row["bank_account_use"]),
            xytext=(row["log_deposits_pc"] + xo, row["bank_account_use"] + yo),
            fontsize=9, color="#006d2c", fontweight="bold",
            arrowprops=dict(arrowstyle="-", color="#aaa", lw=0.9),
        )
        # Highlight dot
        ax.scatter([row["log_deposits_pc"]], [row["bank_account_use"]],
                   color="#006d2c", s=65, zorder=5, edgecolors="white", lw=1.2)

ax.set_xlabel("Banking depth — log deposits per capita (RBI, standardised)",
              fontsize=10)
ax.set_ylabel("Women with a bank account — self-use (%)", fontsize=10)

legend_handles = [
    mlines.Line2D([], [], color=round_colors[r], lw=2,
                  linestyle="--" if r == "NFHS-3" else "-",
                  marker="o", markersize=5, label=round_labels[r])
    for r in rounds
]
ax.legend(handles=legend_handles, fontsize=9, framealpha=0.9, loc="upper left")

ax.set_title(
    "Figure 4  States with Deeper Banking Often Have Higher Women's Account Ownership\n"
    "Descriptive state patterns across three survey rounds (2005–2021)",
    fontsize=10.5, fontweight="bold", loc="left", pad=10)
ax.text(0, -0.12,
    "Each dot = one state × survey round (34 states). Study states highlighted and labelled (NFHS-5). "
    "Dashed trend = NFHS-3; solid = NFHS-4 and NFHS-5.\n"
    "Source: NFHS state factsheets; RBI BSR-2 / Statement 4a.",
    transform=ax.transAxes, fontsize=7.5, color="#555", va="top")

plt.tight_layout()
plt.savefig(OUTDIR + "fig4_panel_banking_v3.png", bbox_inches="tight", dpi=180)
plt.close()
print("Saved fig4_panel_banking_v3.png")

print("\nAll four revised figures saved.")
