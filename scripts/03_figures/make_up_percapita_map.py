"""
UP district per capita maps — RBI banking data aligned to PMMVY enrollment window

Extracts two RBI Statement 4a snapshots that bracket the PMMVY 2017-19 window:
  - 2017-18 Q4 (March 2018): mid-enrollment
  - 2018-19 Q4 (March 2019): end of enrollment period

Computes per capita: deposits, credit, branches (per 100k population)
using Census 2011 district population.

Produces side-by-side choropleths alongside PMMVY enrollment intensity.
"""
import warnings
warnings.filterwarnings("ignore")

import re
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LogNorm, BoundaryNorm
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.chdir(PROJECT_ROOT)
os.makedirs("results/maps", exist_ok=True)

# ── Quarter → starting column index (branches, deposits, credit) ──────────────
QUARTER_COLS = {
    "2018-19:Q4": 49,
    "2017-18:Q4": 61,
}

# ── Encoding + normalisation ──────────────────────────────────────────────────

def fix_encoding(s):
    if not isinstance(s, str):
        return s
    return s.replace(">", "A").replace("@", "U").replace("|", "I")

def norm(s):
    if not isinstance(s, str):
        return ""
    return re.sub(r"\s+", " ", s.upper().strip())

# Shapefile district → dataset district_name_norm
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

# RBI district names → normalised dataset names (uppercase RBI → lowercase data)
RBI_TO_DATA = {
    "ALLAHABAD":            "prayagraj",
    "KANPUR NAGAR":         "kanpur nagar",
    "KANPUR DEHAT":         "kanpur dehat",
    "FAIZABAD":             "ayodhya",
    "GAUTAM BUDDHA NAGAR":  "gautam buddha nagar",
    "SANT KABIR NAGAR":     "sant kabeer nagar",
    "KUSHI NAGAR":          "kushi nagar",
    "SHRAVASTI":            "shravasti",
    "SIDDHARTH NAGAR":      "siddharth nagar",
    "AMBEDKAR NAGAR":       "ambedkar nagar",
    "RAE BARELI":           "rae bareli",
    "BUDAUN":               "budaun",
    "BADAUN":               "budaun",
    "MAHARAJGANJ":          "maharajganj",
    "MAHAMAYA NAGAR":       "hathras",
    "J.P. NAGAR":           "amroha",
    "KASHIRAM NAGAR":       "kasganj",
    "BARA BANKI":           "barabanki",
    "KANAUJ":               "kannauj",
    "RAI BARELI":           "rae bareli",
    "SANT RAVIDAS NAGAR":   "bhadohi",
    "SIDHARTHANAGAR":       "siddharth nagar",
    "BASTI":                "basti",
    "GHAZIPUR":             "ghazipur",
}

# ── 1. Parse RBI Statement 4a for UP ─────────────────────────────────────────

def parse_rbi_4a():
    xl = pd.ExcelFile(
        "data/raw/rbi/rbi_statement_4a_district_reporting_offices_deposits_credit_2017_2022.xlsx"
    )
    raw = xl.parse(xl.sheet_names[0], header=None)

    # Data rows start at row index 7; state col = 2, district col = 3
    data = raw.iloc[7:].copy()
    data = data[data.iloc[:, 2].astype(str).str.upper().str.strip() == "UTTAR PRADESH"].copy()
    data = data[data.iloc[:, 3].notna()].copy()

    records = []
    for _, row in data.iterrows():
        district_rbi = str(row.iloc[3]).strip().upper()
        # Resolve district name
        data_key = RBI_TO_DATA.get(district_rbi, district_rbi.lower())

        for quarter, col_start in QUARTER_COLS.items():
            branches = pd.to_numeric(row.iloc[col_start],     errors="coerce")
            deposits = pd.to_numeric(row.iloc[col_start + 1], errors="coerce")
            credit   = pd.to_numeric(row.iloc[col_start + 2], errors="coerce")
            records.append({
                "district_rbi":  district_rbi,
                "district_key":  data_key,
                "quarter":       quarter,
                "branches":      branches,
                "deposits_crore":deposits,
                "credit_crore":  credit,
            })

    df = pd.DataFrame(records)
    print(f"  RBI 4a UP rows extracted: {len(df)} ({len(df['district_rbi'].unique())} districts × {len(QUARTER_COLS)} quarters)")
    return df

# ── 2. Load census population + PMMVY enrollment ─────────────────────────────

def load_district_data():
    panel = pd.read_parquet("data/processed/up/up_analysis_dataset.parquet")
    district_data = (
        panel.groupby("district_name_norm", as_index=False)
        .agg(
            population_2011        =("population_2011",         "first"),
            beneficiaries_2017_2019=("beneficiaries_2017_2019", "first"),
        )
    )
    district_data["enrollment_rate"] = (
        district_data["beneficiaries_2017_2019"] / district_data["population_2011"] * 1000
    )
    district_data["pmmvy_quartile"] = pd.qcut(
        district_data["enrollment_rate"], q=4,
        labels=["Q1 Low", "Q2 Med-Low", "Q3 Med-High", "Q4 High"]
    )
    print(f"  District panel rows: {len(district_data)}")
    return district_data

# ── 3. Merge RBI + population → per capita ────────────────────────────────────

def build_percapita(rbi_df, district_data):
    merged = rbi_df.merge(
        district_data[["district_name_norm", "population_2011",
                        "enrollment_rate", "pmmvy_quartile"]],
        left_on="district_key",
        right_on="district_name_norm",
        how="left",
    )
    pop = merged["population_2011"]
    merged["deposits_per_capita"]  = merged["deposits_crore"]  * 1e7 / pop   # Rs
    merged["credit_per_capita"]    = merged["credit_crore"]    * 1e7 / pop   # Rs
    merged["branches_per_100k"]    = merged["branches"] / pop * 1e5

    unmatched = merged[merged["population_2011"].isna()]["district_rbi"].unique()
    if len(unmatched):
        print(f"  RBI districts without population match: {unmatched}")

    return merged

# ── 4. Load UP shapefile ──────────────────────────────────────────────────────

def load_up_shp():
    gdf = gpd.read_file("data/processed/shapefiles/DISTRICT_BOUNDARY.shp")
    gdf["state_clean"]    = gdf["STATE"].apply(fix_encoding).apply(norm)
    gdf["district_clean"] = gdf["District"].apply(fix_encoding).apply(norm)
    up = gdf[gdf["state_clean"] == "UTTAR PRADESH"].copy()
    up["data_key"] = up["district_clean"].apply(
        lambda d: SHP_TO_DATA.get(d, d.lower())
    )
    return up

# ── 5. Merge shapefile + per capita data ─────────────────────────────────────

def merge_for_map(up_shp, percap_df, quarter):
    sub = percap_df[percap_df["quarter"] == quarter].copy()
    merged = up_shp.merge(sub, left_on="data_key", right_on="district_key", how="left")
    matched = merged["deposits_per_capita"].notna().sum()
    print(f"  [{quarter}] Matched: {matched} / {len(up_shp)}")
    return merged

# ── 6. Choropleth helper ──────────────────────────────────────────────────────

def choropleth(gdf, col, title, cbar_label, cmap_name, output_path,
               log=True, annotate_n=5):
    fig, ax = plt.subplots(figsize=(11, 12))
    bg = "#F4F1EC"
    ax.set_facecolor(bg)
    fig.patch.set_facecolor(bg)

    data = gdf[col].dropna()
    if log:
        norm_obj = LogNorm(vmin=max(data.min(), 1), vmax=data.max())
    else:
        norm_obj = BoundaryNorm(
            np.linspace(data.quantile(0.02), data.quantile(0.98), 8),
            plt.get_cmap(cmap_name).N
        )

    cmap = plt.get_cmap(cmap_name)

    gdf[gdf[col].isna()].plot(ax=ax, color="#CCCCCC", linewidth=0.3, edgecolor="white")
    gdf[gdf[col].notna()].plot(
        ax=ax, column=col, cmap=cmap, norm=norm_obj,
        linewidth=0.3, edgecolor="white"
    )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_obj)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, aspect=28)
    cbar.set_label(cbar_label, fontsize=10, labelpad=8)
    cbar.ax.tick_params(labelsize=8)

    if annotate_n:
        for _, row in gdf.nlargest(annotate_n, col).iterrows():
            if row.geometry is None:
                continue
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.annotate(
                row["district_clean"].title(),
                (cx, cy), fontsize=6.0, ha="center", va="center",
                color="#1B2A4A", fontweight="bold",
            )

    ax.set_title(title, fontsize=13, fontweight="bold", pad=14, color="#1B2A4A")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")

# ── 7. 2×2 panel: deposits + credit × two quarters ───────────────────────────

def panel_2x2(up_shp, percap_df, output_path):
    quarters = ["2017-18:Q4", "2018-19:Q4"]
    metrics  = [
        ("deposits_per_capita", "Deposits per capita (₹)", "YlGnBu"),
        ("credit_per_capita",   "Credit per capita (₹)",   "YlOrRd"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(20, 22))
    bg = "#F4F1EC"
    fig.patch.set_facecolor(bg)

    for col_i, (metric, mlabel, cmap_name) in enumerate(metrics):
        all_vals = percap_df[metric].dropna()
        norm_obj = LogNorm(vmin=max(all_vals.min(), 1), vmax=all_vals.max())
        cmap = plt.get_cmap(cmap_name)

        for row_i, quarter in enumerate(quarters):
            ax = axes[row_i][col_i]
            ax.set_facecolor(bg)

            sub = percap_df[percap_df["quarter"] == quarter]
            gdf = up_shp.merge(sub, left_on="data_key", right_on="district_key", how="left")

            gdf[gdf[metric].isna()].plot(ax=ax, color="#CCCCCC", linewidth=0.3, edgecolor="white")
            gdf[gdf[metric].notna()].plot(
                ax=ax, column=metric, cmap=cmap, norm=norm_obj,
                linewidth=0.3, edgecolor="white"
            )

            for _, row in gdf.nlargest(5, metric).iterrows():
                if row.geometry is None:
                    continue
                cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
                ax.annotate(
                    row["district_clean"].title(),
                    (cx, cy), fontsize=5.5, ha="center", va="center",
                    color="#1B2A4A", fontweight="bold",
                )

            q_label = "March 2018" if quarter == "2017-18:Q4" else "March 2019"
            ax.set_title(f"{mlabel}\n{q_label}", fontsize=11, fontweight="bold",
                         color="#1B2A4A", pad=8)
            ax.set_axis_off()

            if row_i == 0:
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_obj)
                sm.set_array([])
                cbar = fig.colorbar(sm, ax=axes[:, col_i], fraction=0.025,
                                    pad=0.02, aspect=40, shrink=0.8)
                cbar.set_label(mlabel + " (log scale)", fontsize=9, labelpad=8)
                cbar.ax.tick_params(labelsize=8)

    fig.suptitle(
        "UP District Banking Metrics — Aligned to PMMVY Enrollment Window (2017–19)\n"
        "Source: RBI Statement 4a · Census 2011 population",
        fontsize=14, fontweight="bold", color="#1B2A4A", y=1.01,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=160, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")

# ── 8. 1×2 panel: enrollment vs deposits (2018-19 Q4) ────────────────────────

def panel_enrollment_vs_banking(up_shp, percap_df, district_data, output_path):
    sub = percap_df[percap_df["quarter"] == "2018-19:Q4"]
    gdf_rbi    = up_shp.merge(sub, left_on="data_key", right_on="district_key", how="left")
    gdf_pmmvy  = up_shp.merge(district_data, left_on="data_key",
                               right_on="district_name_norm", how="left")

    fig, axes = plt.subplots(1, 2, figsize=(22, 12))
    bg = "#F4F1EC"
    fig.patch.set_facecolor(bg)

    panels = [
        (axes[0], gdf_pmmvy,  "enrollment_rate", "YlOrRd",
         "PMMVY Enrollment Rate\n(beneficiaries / 1,000 population · 2017–19)"),
        (axes[1], gdf_rbi,    "deposits_per_capita", "YlGnBu",
         "Bank Deposits per Capita (₹)\nRBI Statement 4a · March 2019"),
    ]

    for ax, gdf, col, cmap_name, title in panels:
        ax.set_facecolor(bg)
        data = gdf[col].dropna()
        norm_obj = LogNorm(vmin=max(data.min(), 0.1), vmax=data.max())
        cmap = plt.get_cmap(cmap_name)

        gdf[gdf[col].isna()].plot(ax=ax, color="#CCCCCC", linewidth=0.4, edgecolor="white")
        gdf[gdf[col].notna()].plot(
            ax=ax, column=col, cmap=cmap, norm=norm_obj,
            linewidth=0.4, edgecolor="white"
        )

        for _, row in gdf.nlargest(6, col).iterrows():
            if row.geometry is None:
                continue
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.annotate(
                row["district_clean"].title(),
                (cx, cy), fontsize=6.2, ha="center", va="center",
                color="#1B2A4A", fontweight="bold",
            )

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_obj)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, aspect=28)
        cbar.set_label("Log scale", fontsize=9, labelpad=6)
        cbar.ax.tick_params(labelsize=8)

        ax.set_title(title, fontsize=12, fontweight="bold", color="#1B2A4A", pad=10)
        ax.set_axis_off()

    fig.suptitle(
        "PMMVY Enrollment vs Banking Depth — Uttar Pradesh Districts",
        fontsize=15, fontweight="bold", color="#1B2A4A", y=1.02,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=160, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")

# ── 9. Main ───────────────────────────────────────────────────────────────────

def main():
    print("Parsing RBI Statement 4a (UP districts)...")
    rbi_df = parse_rbi_4a()

    print("Loading district population + PMMVY data...")
    district_data = load_district_data()

    print("Computing per capita metrics...")
    percap_df = build_percapita(rbi_df, district_data)

    print("Loading UP shapefile...")
    up_shp = load_up_shp()

    print("\nPlotting 2×2 banking panel (deposits + credit × 2 quarters)...")
    panel_2x2(up_shp, percap_df, "results/maps/map_up_banking_percapita_panel.png")

    print("Plotting enrollment vs deposits side-by-side...")
    panel_enrollment_vs_banking(
        up_shp, percap_df, district_data,
        "results/maps/map_up_enrollment_vs_banking.png"
    )

    print("\nSummary (2018-19:Q4):")
    q4 = percap_df[percap_df["quarter"] == "2018-19:Q4"].dropna(subset=["deposits_per_capita"])
    for col, label in [
        ("deposits_per_capita", "Deposits/capita (₹)"),
        ("credit_per_capita",   "Credit/capita (₹)"),
        ("branches_per_100k",   "Branches/100k pop"),
    ]:
        print(f"  {label:<28} min={q4[col].min():>12,.0f}  "
              f"median={q4[col].median():>12,.0f}  "
              f"max={q4[col].max():>12,.0f}")


if __name__ == "__main__":
    main()
