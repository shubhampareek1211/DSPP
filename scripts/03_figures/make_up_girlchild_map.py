"""
UP district comparison maps — PMMVY (first child) vs MKSY (girl child)

Three-panel choropleth:
  Panel 1: PMMVY enrollment rate (beneficiaries / 1,000 population · 2017-19)
  Panel 2: MKSY girl-child birth benefit (cat1 beneficiaries / 1,000 population)
  Panel 3: MKSY administrative approval rate (net_approved / total_applications %)

Plus a standalone scatter: district-level PMMVY vs MKSY cat1 rate with quartile colouring.

Sources:
  - processed/up/up_analysis_dataset.parquet   (PMMVY enrollment + population)
  - processed/up/mksy_up_district_labeled.csv  (MKSY district metrics)
  - processed/shapefiles/DISTRICT_BOUNDARY.shp
"""
import warnings
warnings.filterwarnings("ignore")

import re
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import BoundaryNorm
from matplotlib.lines import Line2D
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.chdir(PROJECT_ROOT)
os.makedirs("results/maps", exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def fix_encoding(s):
    if not isinstance(s, str):
        return s
    return s.replace(">", "A").replace("@", "U").replace("|", "I")

def normalise(s):
    if not isinstance(s, str):
        return ""
    return re.sub(r"\s+", " ", s.upper().strip())

SHP_TO_DATA = {
    "AYODHYA":         "ayodhya",
    "KANPUR":          "kanpur nagar",
    "GAZIPUR":         "ghazipur",
    "RAIBEARELI":      "rae bareli",
    "GAUTAMBUDHNAGAR": "gautam buddha nagar",
    "SANTKABIRNAGAR":  "sant kabeer nagar",
    "KUSHINAGAR":      "kushi nagar",
    "SHRAWASTI":       "shravasti",
    "SIDDHARTHNAGAR":  "siddharth nagar",
    "AMBEDKARNAGAR":   "ambedkar nagar",
    "PRAYAGRAJ":       "prayagraj",
}

# ── 1. Load shapefile ─────────────────────────────────────────────────────────

def load_up_shp():
    gdf = gpd.read_file("data/processed/shapefiles/DISTRICT_BOUNDARY.shp")
    gdf["state_clean"]    = gdf["STATE"].apply(fix_encoding).apply(normalise)
    gdf["district_clean"] = gdf["District"].apply(fix_encoding).apply(normalise)
    up = gdf[gdf["state_clean"] == "UTTAR PRADESH"].copy()
    up["data_key"] = up["district_clean"].apply(
        lambda d: SHP_TO_DATA.get(d, d.lower())
    )
    return up

# ── 2. Build analysis table ───────────────────────────────────────────────────

def build_data():
    panel = pd.read_parquet("data/processed/up/up_analysis_dataset.parquet")
    pmmvy = (
        panel.groupby("district_name_norm", as_index=False)
        .agg(
            population_2011        =("population_2011",         "first"),
            beneficiaries_2017_2019=("beneficiaries_2017_2019", "first"),
        )
    )
    pmmvy["pmmvy_rate"] = pmmvy["beneficiaries_2017_2019"] / pmmvy["population_2011"] * 1000

    mksy = pd.read_csv("data/processed/up/mksy_up_district_labeled.csv")
    mksy = mksy[["district_name_norm", "total_applications",
                 "net_approved", "pending_applications",
                 "cat1_beneficiaries", "cat2_beneficiaries"]]

    df = pmmvy.merge(mksy, on="district_name_norm", how="outer")
    df["mksy_cat1_rate"]    = df["cat1_beneficiaries"] / df["population_2011"] * 1000
    df["mksy_cat2_rate"]    = df["cat2_beneficiaries"] / df["population_2011"] * 1000
    df["mksy_approval_pct"] = df["net_approved"] / df["total_applications"] * 100
    df["mksy_pending_pct"]  = df["pending_applications"] / df["total_applications"] * 100

    # Quartile labels for each metric
    for col, label in [("pmmvy_rate", "pmmvy_q"), ("mksy_cat1_rate", "mksy_q")]:
        df[label] = pd.qcut(df[col].rank(method="first"), q=4,
                            labels=["Q1 Low", "Q2 Med-Low", "Q3 Med-High", "Q4 High"])

    print(f"  Districts built: {len(df)}")
    print(f"  PMMVY rate  — min:{df['pmmvy_rate'].min():.2f}  "
          f"median:{df['pmmvy_rate'].median():.2f}  max:{df['pmmvy_rate'].max():.2f}")
    print(f"  MKSY cat1 rate — min:{df['mksy_cat1_rate'].min():.3f}  "
          f"median:{df['mksy_cat1_rate'].median():.3f}  max:{df['mksy_cat1_rate'].max():.3f}")
    print(f"  MKSY approval% — min:{df['mksy_approval_pct'].min():.1f}  "
          f"median:{df['mksy_approval_pct'].median():.1f}  max:{df['mksy_approval_pct'].max():.1f}")
    return df

# ── 3. Merge to shapefile ─────────────────────────────────────────────────────

def merge(up_shp, df):
    gdf = up_shp.merge(df, left_on="data_key", right_on="district_name_norm", how="left")
    print(f"  Shapefile merge — matched: {gdf['pmmvy_rate'].notna().sum()} / {len(up_shp)}")
    return gdf

# ── 4. Quartile choropleth (discrete colours) ─────────────────────────────────

Q_COLORS = {
    "Q1 Low":      "#FEE5D9",
    "Q2 Med-Low":  "#FC9272",
    "Q3 Med-High": "#DE2D26",
    "Q4 High":     "#67000D",
}

APPROVAL_COLORS = ["#EDF8E9", "#BAE4B3", "#74C476", "#238B45"]  # green for good admin

def _quartile_range(df, col, label):
    q = pd.qcut(df[col].rank(method="first"), q=4,
                labels=["Q1 Low", "Q2 Med-Low", "Q3 Med-High", "Q4 High"])
    sub = df[q.astype(str) == label][col]
    return f"{sub.min():.2f}–{sub.max():.2f}" if not sub.empty else ""

def plot_discrete(ax, gdf, col, title, cmap_colors, unit="", bg="#F4F1EC",
                  label_all=False, label_top=6):
    ax.set_facecolor(bg)
    data = gdf[col].dropna()
    q = pd.qcut(data.rank(method="first"), q=4,
                labels=["Q1 Low", "Q2 Med-Low", "Q3 Med-High", "Q4 High"])
    gdf = gdf.copy()
    gdf["_q"] = np.nan
    gdf.loc[data.index, "_q"] = q.values

    gdf[gdf[col].isna()].plot(ax=ax, color="#CCCCCC", linewidth=0.3, edgecolor="white")
    for i, (label, color) in enumerate(cmap_colors.items()):
        subset = gdf[gdf["_q"].astype(str) == label]
        if len(subset):
            subset.plot(ax=ax, color=color, linewidth=0.3, edgecolor="white")

    # District labels
    if label_all:
        for _, row in gdf.iterrows():
            if row.geometry is None or pd.isna(row.get(col)):
                continue
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.annotate(row["district_clean"].title(), (cx, cy),
                        fontsize=4.8, ha="center", va="center", color="#2C2C2C")
    elif label_top:
        for _, row in gdf.nlargest(label_top, col).iterrows():
            if row.geometry is None:
                continue
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            val = row[col]
            ax.annotate(
                f"{row['district_clean'].title()}\n{val:.2f}{unit}",
                (cx, cy), fontsize=5.8, ha="center", va="center",
                color="#1B2A4A", fontweight="bold",
            )

    ax.set_title(title, fontsize=10.5, fontweight="bold", color="#1B2A4A", pad=7)
    ax.set_axis_off()

def approval_legend(ax, gdf, col, colors):
    """Continuous 4-bin approval-rate choropleth using green palette."""
    data = gdf[col].dropna()
    bins = np.percentile(data, [0, 25, 50, 75, 100])
    bins = np.unique(bins)
    labels = ["Q1", "Q2", "Q3", "Q4"][:len(bins)-1]
    cmap_colors = dict(zip(labels, colors[:len(labels)]))

    q = pd.cut(data, bins=bins, labels=labels, include_lowest=True)
    gdf = gdf.copy()
    gdf["_q"] = np.nan
    gdf.loc[data.index, "_q"] = q.values

    gdf[gdf[col].isna()].plot(ax=ax, color="#CCCCCC", linewidth=0.3, edgecolor="white")
    for label, color in cmap_colors.items():
        subset = gdf[gdf["_q"].astype(str) == label]
        if len(subset):
            subset.plot(ax=ax, color=color, linewidth=0.3, edgecolor="white")

    for _, row in gdf.nlargest(5, col).iterrows():
        if row.geometry is None:
            continue
        cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
        ax.annotate(
            f"{row['district_clean'].title()}\n{row[col]:.1f}%",
            (cx, cy), fontsize=5.8, ha="center", va="center",
            color="#1B2A4A", fontweight="bold",
        )

    ax.set_title("MKSY Administrative Efficiency\nApproval rate (net approved / total applications %)",
                 fontsize=10.5, fontweight="bold", color="#1B2A4A", pad=7)
    ax.set_axis_off()

# ── 5. Three-panel figure ─────────────────────────────────────────────────────

def make_three_panel(gdf, df, output_path):
    fig = plt.figure(figsize=(28, 12))
    bg = "#F4F1EC"
    fig.patch.set_facecolor(bg)
    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.04)

    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]

    # Panel 1 — PMMVY
    plot_discrete(
        axes[0], gdf, "pmmvy_rate",
        "PMMVY Enrollment\nBeneficiaries per 1,000 pop · 2017–19",
        Q_COLORS, unit="/1k", label_all=True,
    )

    # Panel 2 — MKSY cat1 (girl birth benefit)
    mksy_colors = {
        "Q1 Low":      "#FFF7FB",
        "Q2 Med-Low":  "#C994C7",
        "Q3 Med-High": "#DF65B0",
        "Q4 High":     "#67001F",
    }
    plot_discrete(
        axes[1], gdf, "mksy_cat1_rate",
        "MKSY Girl Child Birth Benefit\nCat-1 beneficiaries per 1,000 pop",
        mksy_colors, unit="/1k", label_all=True,
    )

    # Panel 3 — MKSY approval rate
    approval_legend(axes[2], gdf, "mksy_approval_pct", APPROVAL_COLORS)

    # Shared legend for Q colours
    q_patches = [mpatches.Patch(color=c, label=l) for l, c in Q_COLORS.items()]
    q_patches.append(mpatches.Patch(color="#CCCCCC", label="No data"))
    axes[0].legend(handles=q_patches, loc="lower left", fontsize=7.5,
                   framealpha=0.9, title="Quartile", title_fontsize=7.5)

    mksy_patches = [mpatches.Patch(color=c, label=l) for l, c in mksy_colors.items()]
    mksy_patches.append(mpatches.Patch(color="#CCCCCC", label="No data"))
    axes[1].legend(handles=mksy_patches, loc="lower left", fontsize=7.5,
                   framealpha=0.9, title="Quartile", title_fontsize=7.5)

    app_labels = ["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]
    app_patches = [mpatches.Patch(color=c, label=l)
                   for c, l in zip(APPROVAL_COLORS, app_labels)]
    axes[2].legend(handles=app_patches, loc="lower left", fontsize=7.5,
                   framealpha=0.9, title="Approval quartile", title_fontsize=7.5)

    fig.suptitle(
        "Girl-Child Scheme Coverage — Uttar Pradesh Districts\n"
        "PMMVY (first child, all) vs MKSY (girl child at birth)",
        fontsize=15, fontweight="bold", color="#1B2A4A", y=1.01,
    )
    plt.savefig(output_path, dpi=160, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")

# ── 6. Scatter: PMMVY rate vs MKSY cat1 rate ─────────────────────────────────

def make_scatter(df, output_path):
    fig, ax = plt.subplots(figsize=(10, 8))
    bg = "#F9F8F5"
    ax.set_facecolor(bg)
    fig.patch.set_facecolor(bg)

    q_color_map = {
        "Q1 Low":      "#FEE5D9",
        "Q2 Med-Low":  "#FC9272",
        "Q3 Med-High": "#DE2D26",
        "Q4 High":     "#67000D",
    }
    # PMMVY quartile colouring
    pmmvy_q = pd.qcut(df["pmmvy_rate"].rank(method="first"), q=4,
                      labels=list(q_color_map.keys()))

    for q_label, color in q_color_map.items():
        sub = df[pmmvy_q.astype(str) == q_label]
        ax.scatter(
            sub["pmmvy_rate"], sub["mksy_cat1_rate"],
            c=color, edgecolors="#333333", linewidths=0.5,
            s=80, label=f"PMMVY {q_label}", zorder=3,
        )

    # Annotate top-5 by MKSY cat1
    for _, row in df.nlargest(5, "mksy_cat1_rate").iterrows():
        ax.annotate(
            row["district_name_norm"].title(),
            (row["pmmvy_rate"], row["mksy_cat1_rate"]),
            textcoords="offset points", xytext=(6, 4),
            fontsize=8, color="#1B2A4A",
        )

    # Trend line
    valid = df[["pmmvy_rate", "mksy_cat1_rate"]].dropna()
    m, b = np.polyfit(valid["pmmvy_rate"], valid["mksy_cat1_rate"], 1)
    x_line = np.linspace(valid["pmmvy_rate"].min(), valid["pmmvy_rate"].max(), 100)
    ax.plot(x_line, m * x_line + b, color="#555555", linewidth=1.2,
            linestyle="--", alpha=0.7, label=f"Trend (slope={m:.4f})")

    corr = valid["pmmvy_rate"].corr(valid["mksy_cat1_rate"])
    ax.text(0.97, 0.05, f"r = {corr:.3f}", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=11, color="#333333",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

    ax.set_xlabel("PMMVY enrollment rate (per 1,000 population · 2017–19)",
                  fontsize=11, labelpad=8)
    ax.set_ylabel("MKSY cat-1 girl birth beneficiaries (per 1,000 population)",
                  fontsize=11, labelpad=8)
    ax.set_title(
        "District-Level PMMVY vs MKSY Girl-Child Birth Benefit\nUttar Pradesh (73 districts)",
        fontsize=13, fontweight="bold", color="#1B2A4A", pad=12,
    )
    ax.legend(fontsize=8.5, framealpha=0.9, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=160, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")

# ── 7. Side-by-side: PMMVY quartile vs MKSY quartile ─────────────────────────

def make_side_by_side(gdf, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(22, 12))
    bg = "#F4F1EC"
    fig.patch.set_facecolor(bg)
    for ax in axes:
        ax.set_facecolor(bg)

    mksy_colors = {
        "Q1 Low":      "#FFF7FB",
        "Q2 Med-Low":  "#C994C7",
        "Q3 Med-High": "#DF65B0",
        "Q4 High":     "#67001F",
    }

    plot_discrete(
        axes[0], gdf, "pmmvy_rate",
        "PMMVY First-Child Enrollment\n(per 1,000 pop · 2017–19)",
        Q_COLORS, unit="/1k", label_all=True,
    )
    plot_discrete(
        axes[1], gdf, "mksy_cat1_rate",
        "MKSY Girl-Child Birth Benefit (Cat-1)\n(per 1,000 pop)",
        mksy_colors, unit="/1k", label_all=True,
    )

    # Legends
    for ax, colors, title in [
        (axes[0], Q_COLORS,    "PMMVY quartile"),
        (axes[1], mksy_colors, "MKSY quartile"),
    ]:
        patches = [mpatches.Patch(color=c, label=l) for l, c in colors.items()]
        patches.append(mpatches.Patch(color="#CCCCCC", label="No data"))
        ax.legend(handles=patches, loc="lower left", fontsize=8.5,
                  framealpha=0.9, title=title, title_fontsize=8.5)

    fig.suptitle(
        "PMMVY (All First Births) vs MKSY (Girl Births Only) — Uttar Pradesh Districts\n"
        "MKSY targets girl children; PMMVY targets first live births regardless of sex",
        fontsize=14, fontweight="bold", color="#1B2A4A", y=1.01,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=160, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")

# ── 8. Main ───────────────────────────────────────────────────────────────────

def main():
    print("Loading UP shapefile...")
    up_shp = load_up_shp()

    print("Building analysis table...")
    df = build_data()

    print("Merging to shapefile...")
    gdf = merge(up_shp, df)

    print("\nPlotting three-panel map (PMMVY + MKSY cat1 + approval rate)...")
    make_three_panel(gdf, df, "results/maps/map_up_girlchild_threepanel.png")

    print("Plotting side-by-side PMMVY vs MKSY...")
    make_side_by_side(gdf, "results/maps/map_up_pmmvy_vs_mksy.png")

    print("Plotting scatter: PMMVY rate vs MKSY cat1 rate...")
    make_scatter(df, "results/maps/scatter_up_pmmvy_vs_mksy.png")

    print("\nDistrict-level summary (top 10 by MKSY cat1 rate):")
    top = df.nlargest(10, "mksy_cat1_rate")[
        ["district_name_norm", "pmmvy_rate", "mksy_cat1_rate",
         "mksy_approval_pct", "pmmvy_q", "mksy_q"]
    ]
    print(top.to_string(index=False))

    print("\nCorrelation matrix:")
    print(df[["pmmvy_rate", "mksy_cat1_rate", "mksy_approval_pct"]].corr().round(3).to_string())


if __name__ == "__main__":
    main()
