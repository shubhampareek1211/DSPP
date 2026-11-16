"""
UP district choropleth — PMMVY enrollment status
Enrollment intensity = beneficiaries per 1,000 population (Census 2011)
Classified into quartiles (Q1 Low → Q4 High) and shown in log scale.

Sources:
  - Shapefile:          processed/shapefiles/DISTRICT_BOUNDARY.shp
  - UP analysis panel:  processed/up/up_analysis_dataset.parquet
    (contains district-level population_2011 and beneficiaries_2017_2019)
"""
import warnings
warnings.filterwarnings("ignore")

import re
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import BoundaryNorm, LogNorm
from matplotlib import cm
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.chdir(PROJECT_ROOT)
os.makedirs("results/maps", exist_ok=True)

# ── 1. Encoding fix ───────────────────────────────────────────────────────────

def fix_encoding(s):
    """Shapefile encoding corruption: '>' = 'A', '@' = 'U', '|' = 'I'."""
    if not isinstance(s, str):
        return s
    return s.replace(">", "A").replace("@", "U").replace("|", "I")

def normalise(s):
    if not isinstance(s, str):
        return ""
    return re.sub(r"\s+", " ", s.upper().strip())

# ── 2. Shapefile → PMMVY district name crosswalk ──────────────────────────────
# Keys: normalised shapefile names (after encoding fix)
# Values: normalised district names as they appear in up_analysis_dataset

SHP_TO_DATA = {
    "AYODHYA":          "ayodhya",           # shapefile uses new name; so does dataset
    "KANPUR":           "kanpur nagar",
    "GAZIPUR":          "ghazipur",
    "RAIBEARELI":       "rae bareli",
    "GAUTAMBUDHNAGAR":  "gautam buddha nagar",
    "SANTKABIRNAGAR":   "sant kabeer nagar",  # dataset spells with double-e
    "KUSHINAGAR":       "kushi nagar",         # dataset uses space
    "SHRAWASTI":        "shravasti",
    "SIDDHARTHNAGAR":   "siddharth nagar",     # dataset uses space
    "AMBEDKARNAGAR":    "ambedkar nagar",
    "PRAYAGRAJ":        "prayagraj",
    # JHANSI and LALITPUR absent from dataset (no NFHS module overlap)
}

# ── 3. Load UP shapefile subset ───────────────────────────────────────────────

def load_up_shapefile():
    gdf = gpd.read_file("data/processed/shapefiles/DISTRICT_BOUNDARY.shp")
    gdf["state_clean"]    = gdf["STATE"].apply(fix_encoding).apply(normalise)
    gdf["district_clean"] = gdf["District"].apply(fix_encoding).apply(normalise)
    up = gdf[gdf["state_clean"] == "UTTAR PRADESH"].copy()
    print(f"  UP districts in shapefile: {len(up)}")
    return up

# ── 4. Build district-level enrollment intensity from panel ───────────────────

def build_district_enrollment():
    df = pd.read_parquet("data/processed/up/up_analysis_dataset.parquet")

    # Aggregate: one row per district (values are constant within district)
    agg = (
        df.groupby("district_name_norm", as_index=False)
        .agg(
            beneficiaries_2017_2019=("beneficiaries_2017_2019", "first"),
            beneficiaries_total    =("beneficiaries_total",     "first"),
            population_2011        =("population_2011",         "first"),
        )
    )

    agg["enrollment_rate"] = (
        agg["beneficiaries_2017_2019"] / agg["population_2011"] * 1000
    )

    # Quartile status label
    agg["quartile"] = pd.qcut(
        agg["enrollment_rate"], q=4,
        labels=["Q1  Low", "Q2  Medium-Low", "Q3  Medium-High", "Q4  High"]
    )

    print(f"  Districts with enrollment data: {len(agg)}")
    print(agg.groupby("quartile")["enrollment_rate"]
              .agg(["min", "max", "count"])
              .rename(columns={"min": "rate_min", "max": "rate_max"})
              .to_string())
    return agg

# ── 5. Merge shapefile + enrollment data ──────────────────────────────────────

def merge(up_gdf, enroll_df):
    up_gdf = up_gdf.copy()
    up_gdf["data_key"] = up_gdf["district_clean"].apply(
        lambda d: SHP_TO_DATA.get(d, d.lower())
    )
    # Normalise data keys to lowercase (match district_name_norm)
    up_gdf["data_key"] = up_gdf["data_key"].str.lower()

    merged = up_gdf.merge(
        enroll_df,
        left_on="data_key",
        right_on="district_name_norm",
        how="left",
    )
    matched = merged["enrollment_rate"].notna().sum()
    unmatched = merged.loc[merged["enrollment_rate"].isna(), "district_clean"].tolist()
    print(f"\n  Matched: {matched} / {len(up_gdf)}")
    if unmatched:
        print(f"  Unmatched: {unmatched}")
    return merged

# ── 6a. Continuous log-scale choropleth ──────────────────────────────────────

def plot_log_choropleth(merged, output_path):
    fig, ax = plt.subplots(figsize=(11, 12))
    bg = "#F4F1EC"
    ax.set_facecolor(bg)
    fig.patch.set_facecolor(bg)

    data = merged["enrollment_rate"].dropna()
    norm = LogNorm(vmin=data.min(), vmax=data.max())
    cmap = plt.get_cmap("YlOrRd")

    merged[merged["enrollment_rate"].isna()].plot(
        ax=ax, color="#CCCCCC", linewidth=0.3, edgecolor="white"
    )
    merged[merged["enrollment_rate"].notna()].plot(
        ax=ax, column="enrollment_rate",
        cmap=cmap, norm=norm,
        linewidth=0.3, edgecolor="white",
    )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, aspect=28)
    cbar.set_label("PMMVY beneficiaries per 1,000 population (log scale)",
                   fontsize=10, labelpad=10)

    ticks = [3, 5, 8, 12, 20, 30]
    ticks = [t for t in ticks if data.min() <= t <= data.max()]
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([str(t) for t in ticks])
    cbar.ax.tick_params(labelsize=9)

    # Annotate top-5 and bottom-5 districts
    for rank, subset, color in [
        ("top", merged.nlargest(5, "enrollment_rate"),  "#1B2A4A"),
        ("btm", merged.nsmallest(5, "enrollment_rate"), "#7B1F1F"),
    ]:
        for _, row in subset.iterrows():
            if row.geometry is None:
                continue
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            name = row["district_clean"].title()
            val  = row["enrollment_rate"]
            ax.annotate(
                f"{name}\n({val:.1f})",
                (cx, cy), fontsize=6.2, ha="center", va="center",
                color=color, fontweight="bold",
            )

    ax.set_title(
        "PMMVY Enrollment Intensity — Uttar Pradesh Districts\n"
        "Beneficiaries per 1,000 Population · 2017–19 (log scale)",
        fontsize=13, fontweight="bold", pad=14, color="#1B2A4A",
    )
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")

# ── 6b. Discrete quartile-status choropleth ───────────────────────────────────

QUARTILE_COLORS = {
    "Q1  Low":          "#FEE5D9",
    "Q2  Medium-Low":   "#FC9272",
    "Q3  Medium-High":  "#DE2D26",
    "Q4  High":         "#67000D",
}

def plot_quartile_choropleth(merged, enroll_df, output_path):
    fig, ax = plt.subplots(figsize=(11, 12))
    bg = "#F4F1EC"
    ax.set_facecolor(bg)
    fig.patch.set_facecolor(bg)

    # Grey for missing
    merged[merged["quartile"].isna()].plot(
        ax=ax, color="#CCCCCC", linewidth=0.3, edgecolor="white"
    )

    for label, color in QUARTILE_COLORS.items():
        subset = merged[merged["quartile"].astype(str) == label]
        if len(subset):
            subset.plot(ax=ax, color=color, linewidth=0.3, edgecolor="white")

    # District labels for all — small font
    for _, row in merged.iterrows():
        if row.geometry is None or pd.isna(row.get("enrollment_rate")):
            continue
        cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
        name = row["district_clean"].title()
        ax.annotate(
            name, (cx, cy),
            fontsize=5.5, ha="center", va="center", color="#2C2C2C",
        )

    # Legend
    patches = [
        mpatches.Patch(color=c, label=f"{lbl}  ({_quartile_range(enroll_df, lbl)})")
        for lbl, c in QUARTILE_COLORS.items()
    ]
    patches.append(mpatches.Patch(color="#CCCCCC", label="No data"))
    ax.legend(
        handles=patches, loc="lower left",
        fontsize=9, framealpha=0.9, title="Enrollment intensity",
        title_fontsize=9,
    )

    ax.set_title(
        "PMMVY Enrollment Status by District — Uttar Pradesh\n"
        "Quartile of beneficiaries per 1,000 population · 2017–19",
        fontsize=13, fontweight="bold", pad=14, color="#1B2A4A",
    )
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")

def _quartile_range(df, label):
    sub = df[df["quartile"].astype(str) == label]["enrollment_rate"]
    if sub.empty:
        return ""
    return f"{sub.min():.1f}–{sub.max():.1f}/1k"

# ── 7. Main ───────────────────────────────────────────────────────────────────

def main():
    print("Loading UP shapefile...")
    up_gdf = load_up_shapefile()

    print("Building district enrollment intensity...")
    enroll_df = build_district_enrollment()

    print("Merging...")
    merged = merge(up_gdf, enroll_df)

    print("\nPlotting continuous log-scale map...")
    plot_log_choropleth(merged, "results/maps/map_up_pmmvy_enrollment_log.png")

    print("Plotting quartile status map...")
    plot_quartile_choropleth(merged, enroll_df, "results/maps/map_up_pmmvy_enrollment_status.png")

    print("\nEnrollment summary (district level):")
    print(enroll_df[["district_name_norm", "enrollment_rate", "quartile"]]
          .sort_values("enrollment_rate", ascending=False)
          .head(10)
          .to_string(index=False))


if __name__ == "__main__":
    main()
