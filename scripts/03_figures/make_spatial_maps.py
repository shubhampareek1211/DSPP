"""
Spatial choropleth maps — Women's financial inclusion and earnings
Datasets: IIPS district-level model estimates (NFHS-4/5)
Shapefile: India district boundary 2022 (Kaggle: ankitgaikar1995)
"""
import warnings
warnings.filterwarnings("ignore")

import re
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import BoundaryNorm
from matplotlib import cm
from rapidfuzz import process, fuzz
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.chdir(PROJECT_ROOT)
os.makedirs("results/maps", exist_ok=True)

# ── 1. Load and clean shapefile ───────────────────────────────────────────────

def fix_encoding(s):
    """Shapefile has encoding corruption: '>' = 'A', '@' = 'U'."""
    if not isinstance(s, str):
        return s
    return s.replace('>', 'A').replace('@', 'U')

def load_shapefile():
    gdf = gpd.read_file("data/processed/shapefiles/DISTRICT_BOUNDARY.shp")
    gdf["district_shp"] = gdf["District"].apply(fix_encoding).str.upper().str.strip()
    gdf["state_shp"]    = gdf["STATE"].apply(fix_encoding).str.upper().str.strip()
    # Drop disputed/null geometry rows
    gdf = gdf[gdf["district_shp"].notna() & ~gdf["district_shp"].str.startswith("DISPUTED")].copy()
    return gdf


# ── 2. District name normalisation ───────────────────────────────────────────

MANUAL_MAP = {
    # IIPS name → shapefile name (both upper)
    "NICOBARS":                          "NICOBAR",
    "NORTH & MIDDLE ANDAMAN":            "NORTH AND MIDDLE ANDAMAN",
    "SOUTH ANDAMANS":                    "SOUTH ANDAMAN",
    "Y.S.R.":                            "Y S R KADAPA",
    "SRI POTTI SRIRAMULU NELLORE":       "NELLORE",
    "KAIMUR (BHABUA)":                   "KAIMUR",
    "PASHCHIM CHAMPARAN":                "WEST CHAMPARAN",
    "PURBA CHAMPARAN":                   "EAST CHAMPARAN",
    "PURNIA":                            "PURNEA",
    "BUXAR":                             "BUXAR",
    "DAKSHIN DINAJPUR":                  "DAKSHIN DINAJPUR",
    "UTTAR DINAJPUR":                    "UTTAR DINAJPUR",
    "PASCHIM MEDINIPUR":                 "PASCHIM MEDINIPUR",
    "PURBA MEDINIPUR":                   "PURBA MEDINIPUR",
    "KAMRUP METROPOLITAN":               "KAMRUP METRO",
    "DIMA HASAO":                        "DIMA HASAO",
    "RIBHOI":                            "RI BHOI",
    "EAST KHASI HILLS":                  "EAST KHASI HILLS",
    "SANT KABIR NAGAR":                  "SANT KABIR NAGAR",
    "SAHARANPUR":                        "SAHARANPUR",
    "MUZAFFARNAGAR":                     "MUZAFFARNAGAR",
    "SHAHJAHANPUR":                      "SHAHJAHANPUR",
    "PRAYAGRAJ":                         "PRAYAGRAJ",
    "KUSHI NAGAR":                       "KUSHINAGAR",
    "SIDDHARTH NAGAR":                   "SIDDHARTHNAGAR",
    "MAHARAJGANJ":                       "MAHARAJGANJ",
    "SHRAWASTI":                         "SHRAVASTI",
    "BALARAMPUR":                        "BALRAMPUR",
    "BALRAMPUR":                         "BALRAMPUR",
    "GONDA":                             "GONDA",
    "BADAUN":                            "BUDAUN",
    "SAMBHAL":                           "SAMBHAL",
    "HAPUR":                             "HAPUR",
    "GAUTAM BUDDHA NAGAR":               "GAUTAM BUDDHA NAGAR",
    "AMROHA":                            "AMROHA",
    "BAGHPAT":                           "BAGHPAT",
    "BULANDSHAHR":                       "BULANDSHAHR",
    "MUZAFFARPUR":                       "MUZAFFARPUR",
    "LAHUL & SPITI":                     "LAHAUL AND SPITI",
    "KANGRA":                            "KANGRA",
    "KULLU":                             "KULLU",
    "SIRMAUR":                           "SIRMAUR",
    "BILASPUR":                          "BILASPUR",
    "UNA":                               "UNA",
    "HAMIRPUR":                          "HAMIRPUR",
    "CHAMBA":                            "CHAMBA",
    "KINNAUR":                           "KINNAUR",
    "SOLAN":                             "SOLAN",
    "MANDI":                             "MANDI",
    "SHIMLA":                            "SHIMLA",
    "NORTH GARO HILLS":                  "NORTH GARO HILLS",
    "SOUTH GARO HILLS":                  "SOUTH GARO HILLS",
    "EAST GARO HILLS":                   "EAST GARO HILLS",
    "WEST GARO HILLS":                   "WEST GARO HILLS",
    "SOUTH WEST GARO HILLS":             "SOUTH WEST GARO HILLS",
    "DIBANG VALLEY":                     "DIBANG VALLEY",
    "LOWER DIBANG VALLEY":               "LOWER DIBANG VALLEY",
    "TAWANG":                            "TAWANG",
    "WEST KAMENG":                       "WEST KAMENG",
    "EAST KAMENG":                       "EAST KAMENG",
    "PAPUM PARE":                        "PAPUM PARE",
    "UPPER SIANG":                       "UPPER SIANG",
    "WEST SIANG":                        "WEST SIANG",
    "EAST SIANG":                        "EAST SIANG",
    "LOWER SUBANSIRI":                   "LOWER SUBANSIRI",
    "UPPER SUBANSIRI":                   "UPPER SUBANSIRI",
    "KURUNG KUMEY":                      "KURUNG KUMEY",
    "LOHIT":                             "LOHIT",
    "TIRAP":                             "TIRAP",
    "CHANGLANG":                         "CHANGLANG",
    "ANJAW":                             "ANJAW",
    "NAMSAI":                            "NAMSAI",
    "LONGDING":                          "LONGDING",
    "PAKKE KESSANG":                     "PAKKE KESSANG",
    "LEPA RADA":                         "LEPA RADA",
    "SHI YOMI":                          "SHI YOMI",
}

def normalise(s):
    if not isinstance(s, str):
        return ""
    s = s.upper().strip()
    s = re.sub(r'\s+', ' ', s)
    return s

def fuzzy_match(iips_dist, shp_districts, threshold=75):
    """Return best shapefile district match for an IIPS district name."""
    # Manual map first
    key = normalise(iips_dist)
    if key in MANUAL_MAP:
        return MANUAL_MAP[key]
    # Fuzzy match
    result = process.extractOne(key, shp_districts, scorer=fuzz.token_sort_ratio)
    if result and result[1] >= threshold:
        return result[0]
    return None

def build_crosswalk(iips_df, gdf):
    shp_districts = gdf["district_shp"].tolist()
    mapping = {}
    unmatched = []
    iips_keys = iips_df[["state", "district"]].drop_duplicates()
    for _, row in iips_keys.iterrows():
        key = normalise(row["district"])
        match = fuzzy_match(key, shp_districts)
        if match:
            mapping[key] = match
        else:
            unmatched.append((row["state"], row["district"]))
    return mapping, unmatched


# ── 3. Merge IIPS data into GeoDataFrame ─────────────────────────────────────

def merge_data(gdf, iips_df, mapping):
    iips_df = iips_df.copy()
    iips_df["district_key"] = iips_df["district"].apply(normalise)
    iips_df["district_shp"] = iips_df["district_key"].map(mapping)
    # Use direct match as fallback
    iips_df["district_shp"] = iips_df.apply(
        lambda r: r["district_shp"] if pd.notna(r["district_shp"])
                  else normalise(r["district"]),
        axis=1
    )
    merged = gdf.merge(iips_df, on="district_shp", how="left")
    return merged


# ── 4. Choropleth helper ──────────────────────────────────────────────────────

def choropleth(gdf_merged, col, title, label, cmap_name, output_path,
               vmin=None, vmax=None, diverging=False, n_bins=7):
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    ax.set_facecolor("#F5F5F0")
    fig.patch.set_facecolor("#F5F5F0")

    data = gdf_merged[col].dropna()
    if vmin is None:
        vmin = np.percentile(data, 2) if len(data) else 0
    if vmax is None:
        vmax = np.percentile(data, 98) if len(data) else 100

    cmap = plt.get_cmap(cmap_name)
    if diverging:
        bounds = np.linspace(vmin, vmax, n_bins + 1)
    else:
        bounds = np.linspace(vmin, vmax, n_bins + 1)
    norm = BoundaryNorm(bounds, cmap.N)

    # Missing districts in grey
    gdf_merged[gdf_merged[col].isna()].plot(
        ax=ax, color="#CCCCCC", linewidth=0.2, edgecolor="white"
    )
    gdf_merged[gdf_merged[col].notna()].plot(
        ax=ax, column=col, cmap=cmap, norm=norm,
        linewidth=0.2, edgecolor="white"
    )

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.025, pad=0.02, aspect=30)
    cbar.set_label(label, fontsize=11, labelpad=10)
    cbar.ax.tick_params(labelsize=9)

    # Labels
    ax.set_title(title, fontsize=15, fontweight="bold", pad=16,
                 color="#1B2A4A")
    ax.set_axis_off()

    # Grey = no data patch
    grey_patch = mpatches.Patch(color="#CCCCCC", label="No data")
    ax.legend(handles=[grey_patch], loc="lower left", fontsize=9,
              framealpha=0.8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")


# ── 5. Timeline comparison — bar chart ───────────────────────────────────────

def make_nfhs_comparison_chart(fin_df, output_path):
    """Grouped bar: national mean of 3 indicators, NFHS-4 vs NFHS-5."""
    indicators = {
        "Bank account\nownership": ("bank_nfhs4", "bank_nfhs5"),
        "Microcredit\nknowledge": ("micro_know_nfhs4", "micro_know_nfhs5"),
        "Microcredit\nuse": ("micro_use_nfhs4", "micro_use_nfhs5"),
    }
    x = np.arange(len(indicators))
    width = 0.35
    n4_vals = [fin_df[v[0]].mean() for v in indicators.values()]
    n5_vals = [fin_df[v[0]].mean() if v[0] == "bank_nfhs4" else fin_df[v[1]].mean()
               for v in indicators.values()]
    n4_vals = [fin_df[v[0]].mean() for v in indicators.values()]
    n5_vals = [fin_df[v[1]].mean() for v in indicators.values()]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor("#F9F9F7")
    fig.patch.set_facecolor("#F9F9F7")

    b1 = ax.bar(x - width/2, n4_vals, width, label="NFHS-4 (2015–16)",
                color="#4A7BA7", alpha=0.88)
    b2 = ax.bar(x + width/2, n5_vals, width, label="NFHS-5 (2019–21)",
                color="#E8A838", alpha=0.88)

    # Value labels
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.5,
                f'{h:.1f}%', ha='center', va='bottom', fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(indicators.keys(), fontsize=11)
    ax.set_ylabel("National average (%)", fontsize=11)
    ax.set_title("Women's Financial Inclusion Indicators\nNFHS-4 (2015–16) vs NFHS-5 (2019–21)",
                 fontsize=13, fontweight="bold", color="#1B2A4A")
    ax.legend(fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_ylim(0, max(n4_vals + n5_vals) * 1.18)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")


# ── 6. Distribution violin — change NFHS4→5 ──────────────────────────────────

def make_change_violin(fin_df, output_path):
    """Violin plot of district-level change for each indicator."""
    cols = {
        "Bank account": "bank_change",
        "Microcredit knowledge": "micro_know_change",
        "Microcredit use": "micro_use_change",
    }
    data = [fin_df[c].dropna().values for c in cols.values()]
    labels = list(cols.keys())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor("#F9F9F7")
    fig.patch.set_facecolor("#F9F9F7")

    parts = ax.violinplot(data, positions=range(1, len(data)+1),
                          showmedians=True, showextrema=True)
    colors = ["#4A7BA7", "#E8A838", "#6BAF72"]
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.75)
    parts['cmedians'].set_color("#1B2A4A")
    parts['cbars'].set_color("#555")
    parts['cmins'].set_color("#555")
    parts['cmaxes'].set_color("#555")

    ax.axhline(0, color="#CC3333", linewidth=1, linestyle="--", alpha=0.6)
    ax.set_xticks(range(1, len(data)+1))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Change NFHS-4 → NFHS-5 (percentage points)", fontsize=10)
    ax.set_title("District-Level Distribution of Change in Women's Financial Indicators\n(NFHS-4 to NFHS-5)",
                 fontsize=13, fontweight="bold", color="#1B2A4A")
    ax.spines[['top', 'right']].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved → {output_path}")


# ── 7. Main ───────────────────────────────────────────────────────────────────

def main():
    print("Loading shapefile...")
    gdf = load_shapefile()
    print(f"  {len(gdf)} districts in shapefile")

    print("\nLoading IIPS CSVs...")
    fin_df  = pd.read_csv("data/processed/iips_financial_inclusion.csv")
    earn_df = pd.read_csv("data/processed/iips_women_earnings.csv")
    print(f"  Financial inclusion: {len(fin_df)} districts")
    print(f"  Women earnings: {len(earn_df)} districts")

    print("\nBuilding district name crosswalk...")
    mapping, unmatched = build_crosswalk(fin_df, gdf)
    print(f"  Matched: {len(mapping)}  Unmatched: {len(unmatched)}")
    if unmatched[:5]:
        print("  Sample unmatched:", unmatched[:5])

    # ── A. Financial inclusion maps ───────────────────────────────────────────
    print("\n--- Financial Inclusion Maps ---")
    gdf_fin = merge_data(gdf, fin_df, mapping)

    make_nfhs_comparison_chart(fin_df, "results/maps/fin_inclusion_bar_nfhs4_vs_nfhs5.png")
    make_change_violin(fin_df, "results/maps/fin_inclusion_violin_change.png")

    choropleth(gdf_fin, "bank_nfhs5",
               "Women with Bank/Savings Account They Use\nNFHS-5 (2019–21)",
               "% of women", "YlGnBu",
               "results/maps/map_bank_account_nfhs5.png",
               vmin=20, vmax=100)

    choropleth(gdf_fin, "bank_change",
               "Change in Bank Account Ownership\nNFHS-4 (2015–16) → NFHS-5 (2019–21)",
               "Percentage point change", "RdYlGn",
               "results/maps/map_bank_account_change.png",
               vmin=-5, vmax=55, diverging=True)

    choropleth(gdf_fin, "bank_nfhs4",
               "Women with Bank/Savings Account They Use\nNFHS-4 (2015–16)",
               "% of women", "YlGnBu",
               "results/maps/map_bank_account_nfhs4.png",
               vmin=20, vmax=100)

    choropleth(gdf_fin, "micro_know_nfhs5",
               "Women with Knowledge of Microcredit Programme\nNFHS-5 (2019–21)",
               "% of women", "PuBuGn",
               "results/maps/map_micro_knowledge_nfhs5.png")

    choropleth(gdf_fin, "micro_use_nfhs5",
               "Women Who Used Microcredit Programme\nNFHS-5 (2019–21)",
               "% of women", "BuPu",
               "results/maps/map_micro_use_nfhs5.png")

    # ── B. Women earnings maps ────────────────────────────────────────────────
    print("\n--- Women Earnings Maps ---")
    mapping_earn, _ = build_crosswalk(earn_df, gdf)
    gdf_earn = merge_data(gdf, earn_df, mapping_earn)

    choropleth(gdf_earn, "worked_12m",
               "Women Who Worked in Past 12 Months\nNFHS-5 (2019–21)",
               "% of women", "YlOrRd",
               "results/maps/map_women_worked_12m.png",
               vmin=5, vmax=65)

    choropleth(gdf_earn, "self_employed",
               "Women Who Were Self-Employed\nNFHS-5 (2019–21)",
               "% of women", "OrRd",
               "results/maps/map_women_self_employed.png",
               vmin=0, vmax=25)

    choropleth(gdf_earn, "earned_cash",
               "Women Who Earned Cash\nNFHS-5 (2019–21)",
               "% of women", "YlOrBr",
               "results/maps/map_women_earned_cash.png",
               vmin=5, vmax=60)

    # ── C. Summary stats ──────────────────────────────────────────────────────
    print("\n--- National Summary ---")
    print("Financial inclusion (district means):")
    for col, label in [("bank_nfhs4","Bank acc NFHS4"), ("bank_nfhs5","Bank acc NFHS5"),
                        ("bank_change","Change"), ("micro_know_nfhs5","Micro know NFHS5"),
                        ("micro_use_nfhs5","Micro use NFHS5")]:
        print(f"  {label:<25} {fin_df[col].mean():.1f}%")

    print("\nWomen earnings (district means):")
    for col, label in [("worked_12m","Worked 12m"), ("self_employed","Self-employed"),
                        ("earned_cash","Earned cash")]:
        print(f"  {label:<25} {earn_df[col].mean():.1f}%")

    print(f"\nAll maps saved to results/maps/")


if __name__ == "__main__":
    main()
