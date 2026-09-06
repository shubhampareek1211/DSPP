"""
Generates Figure 3.1: PMMVY Enrollment Intensity by State
(Cumulative Beneficiaries per 1,000 Women)

Output: results/figures/paper/figure3_1_pmmvy_intensity.png
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "results" / "tables" / "pmmvy_state_intensity.csv"
OUTPUT_PATH = PROJECT_ROOT / "results" / "figures" / "paper" / "figure3_1_pmmvy_intensity.png"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── data ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH)

# Title-case state names
df["state"] = df["state_n"].str.title()

# Fix a few long names for display
name_map = {
    "Dadra And Nagar Haveli And Daman And Diu": "D&NH / Daman & Diu",
    "Andaman And Nicobar Islands": "Andaman & Nicobar",
    "Jammu And Kashmir": "Jammu & Kashmir",
    "Uttar Pradesh": "Uttar Pradesh",
}
df["state"] = df["state"].replace(name_map)

# Annotate special states
df["label"] = df["state"]
df.loc[df["state_n"] == "ODISHA",    "label"] = "Odisha †"
df.loc[df["state_n"] == "TELANGANA", "label"] = "Telangana †"
df.loc[df["state_n"] == "TAMIL NADU","label"] = "Tamil Nadu ‡"

# Sort descending by intensity
df = df.sort_values("pmmvy_intensity", ascending=True).reset_index(drop=True)

# ── colours ───────────────────────────────────────────────────────────────────
palette = {"Low": "#c6dbef", "Mid": "#6baed6", "High": "#2171b5"}
bar_colors = df["intensity_tercile"].map(palette)

# Non-participants get a distinct hatched grey
non_participant_mask = df["state_n"].isin(["ODISHA", "TELANGANA"])
bar_colors[non_participant_mask] = "#d9d9d9"

# ── plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 12))

bars = ax.barh(
    df["label"],
    df["pmmvy_intensity"],
    color=bar_colors,
    edgecolor="white",
    linewidth=0.5,
    height=0.75,
)

# Hatch non-participants
for bar, is_np in zip(bars, non_participant_mask):
    if is_np:
        bar.set_hatch("///")
        bar.set_edgecolor("#999999")

# Value labels on bars
for bar, val in zip(bars, df["pmmvy_intensity"]):
    x = bar.get_width()
    ax.text(
        x + 0.8,
        bar.get_y() + bar.get_height() / 2,
        f"{val:.1f}" if val > 0 else "0",
        va="center",
        ha="left",
        fontsize=7.5,
        color="#333333",
    )

# Reference lines
for xval, style in [(43.4, "--"), (62.0, ":")]:
    ax.axvline(xval, color="#666666", linewidth=0.8, linestyle=style, alpha=0.6)

ax.text(43.4 + 0.5, len(df) - 0.5, "Tamil Nadu\n(‡ state scheme)", fontsize=7,
        color="#555555", va="top")

# ── axes ──────────────────────────────────────────────────────────────────────
ax.set_xlabel("Cumulative PMMVY beneficiaries per 1,000 women (Census 2011 female population)",
              fontsize=9)
ax.set_xlim(0, 135)
ax.set_yticks(range(len(df)))
ax.set_yticklabels(df["label"], fontsize=8.5)
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(axis="x", labelsize=8)
ax.xaxis.grid(True, linestyle="--", alpha=0.4, color="#cccccc")
ax.set_axisbelow(True)

# ── legend ────────────────────────────────────────────────────────────────────
legend_handles = [
    mpatches.Patch(facecolor=palette["High"],  label="High tercile (≥ ~73/1,000)"),
    mpatches.Patch(facecolor=palette["Mid"],   label="Mid tercile"),
    mpatches.Patch(facecolor=palette["Low"],   label="Low tercile"),
    mpatches.Patch(facecolor="#d9d9d9", hatch="///", edgecolor="#999999",
                   label="Non-participant (†)"),
]
ax.legend(handles=legend_handles, loc="lower right", fontsize=8,
          framealpha=0.9, edgecolor="#cccccc")

# ── title & footnotes ─────────────────────────────────────────────────────────
ax.set_title(
    "Figure 3.1  PMMVY Enrollment Intensity by State\n"
    "Cumulative Beneficiaries per 1,000 Women",
    fontsize=11, fontweight="bold", pad=12, loc="left",
)

footnote = (
    "† Odisha and Telangana are full non-participants (own state schemes); coded zero in DiD specification.\n"
    "‡ Tamil Nadu enrolled at low intensity due to crowding-out by Dr. Muthulakshmi Reddy Maternity Benefit Scheme (₹18,000/birth).\n"
    "Source: MoWCD PMMVY cumulative beneficiary counts (November 2024); denominator: Census 2011 female population."
)
fig.text(0.02, -0.03, footnote, fontsize=7, color="#555555",
         va="top", wrap=True)

plt.tight_layout()
plt.savefig(OUTPUT_PATH,
            dpi=200, bbox_inches="tight")
print("Saved: results/figures/paper/figure3_1_pmmvy_intensity.png")
