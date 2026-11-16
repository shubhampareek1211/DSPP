"""
Multi-state PMMVY district analysis — HP, Assam, Madhya Pradesh

Replicates the UP district DiD framework for 3 additional states with
newly added district-level PMMVY enrollment data.

Output:
  data/processed/multistate/ — merged analysis tables + crosswalks
  results/maps/              — spatial choropleths per state
  results/tables/            — DiD result CSVs

Design:
  - Treatment: PMMVY enrollment rate (beneficiaries / Census 2011 pop × 1000)
  - Outcomes:  bank_account_self_use, own_money_autonomy,
               decision_health_care, mobile_phone_self_use
  - Controls:  age, age², education, urban_rural, wealth_index
  - DiD:       repeated cross-section NFHS-4 (pre) vs NFHS-5 (post)
  - Triple interaction with pre-2013 RBI branch density
  - Cluster SEs at district level

States:
  HP    — 12 districts; spatial map only (too few for robust DiD)
  Assam — 33 districts; full DiD + banking amplification
  MP    — 51 districts; full DiD + banking amplification
"""
import warnings, os, re
from pathlib import Path
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LogNorm
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.chdir(PROJECT_ROOT)

os.makedirs("data/processed/multistate", exist_ok=True)
os.makedirs("results/maps", exist_ok=True)
os.makedirs("results/tables", exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. NFHS-4 district code → name crosswalk (from DHS DO file)
# ═══════════════════════════════════════════════════════════════════════════════

# Extracted from data/raw/nfhs4/IAIR74DT/IAIR74FL.DO label define SDISTRI
NFHS4_DISTRICT_LABELS = {
    # HP (23–34)
    23: "Chamba", 24: "Kangra", 25: "Lahul and Spiti", 26: "Kullu",
    27: "Mandi", 28: "Hamirpur", 29: "Una", 30: "Bilaspur",
    31: "Solan", 32: "Sirmaur", 33: "Shimla", 34: "Kinnaur",
    # Assam (300–326)
    300: "Kokrajhar", 301: "Dhubri", 302: "Goalpara", 303: "Barpeta",
    304: "Morigaon", 305: "Nagaon", 306: "Sonitpur", 307: "Lakhimpur",
    308: "Dhemaji", 309: "Tinsukia", 310: "Dibrugarh", 311: "Sivasagar",
    312: "Jorhat", 313: "Golaghat", 314: "Karbi Anglong", 315: "Dima Hasao",
    316: "Cachar", 317: "Karimganj", 318: "Hailakandi", 319: "Bongaigaon",
    320: "Chirang", 321: "Kamrup", 322: "Kamrup Metropolitan",
    323: "Nalbari", 324: "Baksa", 325: "Darrang", 326: "Udalguri",
    # MP (418–467)
    418: "Sheopur", 419: "Morena", 420: "Bhind", 421: "Gwalior",
    422: "Datia", 423: "Shivpuri", 424: "Tikamgarh", 425: "Chhatarpur",
    426: "Panna", 427: "Sagar", 428: "Damoh", 429: "Satna",
    430: "Rewa", 431: "Umaria", 432: "Neemuch", 433: "Mandsaur",
    434: "Ratlam", 435: "Ujjain", 436: "Shajapur", 437: "Dewas",
    438: "Dhar", 439: "Indore", 440: "Khargone", 441: "Barwani",
    442: "Rajgarh", 443: "Vidisha", 444: "Bhopal", 445: "Sehore",
    446: "Raisen", 447: "Betul", 448: "Harda", 449: "Hoshangabad",
    450: "Katni", 451: "Jabalpur", 452: "Narsinghpur", 453: "Dindori",
    454: "Mandla", 455: "Chhindwara", 456: "Seoni", 457: "Balaghat",
    458: "Guna", 459: "Ashoknagar", 460: "Shahdol", 461: "Anuppur",
    462: "Sidhi", 463: "Singrauli", 464: "Jhabua", 465: "Alirajpur",
    466: "Khandwa", 467: "Burhanpur",
    # West Bengal (327–345 NFHS-4)
    327: "Darjiling", 328: "Jalpaiguri", 329: "Koch Bihar",
    330: "Uttar Dinajpur", 331: "Dakshin Dinajpur", 332: "Maldah",
    333: "Murshidabad", 334: "Birbhum", 335: "Barddhaman",
    336: "Nadia", 337: "North Twenty Four Parganas", 338: "Hugli",
    339: "Bankura", 340: "Puruliya", 341: "Haora",
    342: "Kolkata", 343: "South Twenty Four Parganas",
    344: "Paschim Medinipur", 345: "Purba Medinipur",
    # NFHS-5 new districts (post-2011 splits)
    # Assam: 6 new districts created 2015–2016
    810: "Biswanath", 811: "Charaideo", 812: "Hojai", 813: "Majuli",
    814: "South Salmara Mancachar", 815: "West Karbi Anglong",
    816: "Bajali", 817: "Tamulpur", 818: "Bodoland",
    819: "Kamrup Rural", 820: "Biswanath Chariali", 821: "Hailakandi New",
    # MP: 2 new districts
    867: "Agar Malwa",   # split from Shajapur (Nov 2013)
    868: "Niwari",       # split from Tikamgarh (Oct 2018)
    # WB: Bardhaman split into 2 districts in 2017
    931: "Paschim Bardhaman",   # split from code 335 Barddhaman
    932: "Purba Bardhaman",     # split from code 335 Barddhaman
}

def normalise(s):
    if not isinstance(s, str):
        return ""
    s = s.upper().strip()
    s = re.sub(r"\s+", " ", s)
    for old, new in [
        ("KHARGONE (WEST NIMAR)", "KHARGONE"),
        ("KHANDWA (EAST NIMAR)", "KHANDWA"),
        ("HOSHANGABAD", "NARMADAPURAM"),
        ("KAMRUP METROPOLITAN", "KAMRUP METRO"),
        ("KAMRUP RURAL", "KAMRUP"),
        # WB name normalisation: PMMVY → NFHS label equivalents
        ("24 PARAGANAS NORTH", "NORTH TWENTY FOUR PARGANAS"),
        ("24 PARAGANAS SOUTH", "SOUTH TWENTY FOUR PARGANAS"),
        ("DINAJPUR DAKSHIN", "DAKSHIN DINAJPUR"),
        ("DINAJPUR UTTAR", "UTTAR DINAJPUR"),
        ("MEDINIPUR EAST", "PURBA MEDINIPUR"),
        ("MEDINIPUR WEST", "PASCHIM MEDINIPUR"),
        ("HOOGHLY", "HUGLI"),
        ("HOWRAH", "HAORA"),
        ("DARJEELING", "DARJILING"),
        ("COOCHBEHAR", "KOCH BIHAR"),
        ("PURULIA", "PURULIYA"),
        ("PURBA BARDHAMAN", "PURBA BARDHAMAN"),
        ("PASCHIM BARDHAMAN", "PASCHIM BARDHAMAN"),
    ]:
        s = s.replace(old, new)
    return s

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Load & parse PMMVY files
# ═══════════════════════════════════════════════════════════════════════════════

def load_pmmvy():
    dfs = {}

    # HP
    hp = pd.read_csv("data/raw/pmmvy/himachal_pmmvy.csv")
    hp.columns = ["district_raw", "beneficiaries"]
    hp["state"] = "Himachal Pradesh"
    hp["district_norm"] = hp["district_raw"].apply(normalise)
    dfs["HP"] = hp

    # Assam (file also contains West Bengal rows — drop them)
    assam_raw = pd.read_csv("data/raw/pmmvy/assam_2022.csv")
    assam = assam_raw[assam_raw["State"] == "Assam"].copy()
    assam = assam.rename(columns={
        "Name of the District": "district_raw",
        "Total Beneficiary Enrolled since Inception of the Scheme and till 25.01.2022": "beneficiaries"
    })[["district_raw", "beneficiaries"]]
    assam["state"] = "Assam"
    assam["district_norm"] = assam["district_raw"].apply(normalise)
    dfs["Assam"] = assam

    # MP
    mp = pd.read_csv("data/raw/pmmvy/mp_data_pmmvy.csv")
    mp.columns = ["district_raw", "beneficiaries"]
    mp["state"] = "Madhya Pradesh"
    mp["district_norm"] = mp["district_raw"].apply(normalise)
    dfs["MP"] = mp

    # West Bengal — from the same file as Assam
    wb_raw = pd.read_csv("data/raw/pmmvy/assam_2022.csv")
    wb = wb_raw[wb_raw["State"] == "West Bengal"].copy()
    wb = wb.rename(columns={
        "Name of the District": "district_raw",
        "Total Beneficiary Enrolled since Inception of the Scheme and till 25.01.2022": "beneficiaries"
    })[["district_raw", "beneficiaries"]]
    wb["state"] = "West Bengal"
    wb["district_norm"] = wb["district_raw"].apply(normalise)
    # Barddhaman (NFHS-4 combined district) — aggregate Paschim + Purba for matching
    wb_combined = wb.copy()
    bardhaman_total = wb[wb["district_norm"].isin(
        ["PASCHIM BARDHAMAN", "PURBA BARDHAMAN"])]["beneficiaries"].sum()
    wb_barddhaman = pd.DataFrame([{
        "district_raw": "Barddhaman (combined)", "beneficiaries": bardhaman_total,
        "state": "West Bengal", "district_norm": "BARDDHAMAN"
    }])
    wb_combined = pd.concat([wb_combined, wb_barddhaman], ignore_index=True)
    dfs["WB"] = wb_combined

    for k, df in dfs.items():
        print(f"  {k}: {len(df)} districts, total beneficiaries={df['beneficiaries'].sum():,}")
    return dfs

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Load NFHS outcomes + build district-level aggregates
# ═══════════════════════════════════════════════════════════════════════════════

STATE_FILTERS = {
    "HP":    "himachal",
    "Assam": "assam",
    "MP":    "madhya",
    "WB":    "west bengal",
}

OUTCOMES = ["bank_account_self_use", "own_money_autonomy",
            "decision_health_care", "mobile_phone_self_use"]

CONTROLS = ["age", "education_level", "urban_rural", "wealth_index",
            "woman_weight", "survey_round", "district_code", "state_name"]

def load_nfhs():
    df = pd.read_parquet(
        "data/processed/nfhs/nfhs_individual_harmonized.parquet",
        columns=CONTROLS + OUTCOMES,
    )
    # Add district name from our label map
    df["district_name"] = df["district_code"].map(NFHS4_DISTRICT_LABELS)
    df["district_name_norm"] = df["district_name"].apply(normalise)
    df["post"] = (df["survey_round"] == "NFHS-5").astype(int)
    df["age_sq"] = df["age"] ** 2
    return df

def get_state_nfhs(df, state_key):
    keyword = STATE_FILTERS[state_key]
    sub = df[df["state_name"].str.lower().str.contains(keyword, na=False)].copy()
    # Keep only state-module women (have outcome data)
    sub = sub[sub["bank_account_self_use"].notna()].copy()
    print(f"  {state_key}: {len(sub):,} state-module women "
          f"(NFHS-4={( sub['post']==0).sum():,}, NFHS-5={(sub['post']==1).sum():,})")
    print(f"    Districts: {sub['district_code'].nunique()} with outcomes")
    return sub

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Load RBI baseline + Census population
# ═══════════════════════════════════════════════════════════════════════════════

def load_rbi_census():
    rbi = pd.read_csv("data/processed/rbi/rbi_district_baseline_dec_2013.csv")
    rbi["district_norm"] = rbi["district_name_clean"].apply(normalise)
    rbi["state_norm"]    = rbi["state_name_clean"].apply(normalise)

    census = pd.read_csv("data/processed/census/census2011_district_population.csv")
    census["district_norm"] = census["district_name_census_clean"].apply(normalise)
    census["state_norm"]    = census["state_name_census_clean"].apply(normalise)

    # Merge RBI + census on state+district
    baseline = rbi.merge(
        census[["state_norm", "district_norm", "population_total_2011"]],
        on=["state_norm", "district_norm"], how="left"
    )
    return baseline

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Build state analysis tables
# ═══════════════════════════════════════════════════════════════════════════════

STATE_BASELINE_KEY = {
    "HP":    "HIMACHAL PRADESH",
    "Assam": "ASSAM",
    "MP":    "MADHYA PRADESH",
    "WB":    "WEST BENGAL",
}

def build_state_table(state_key, pmmvy_df, nfhs_df, baseline_df):
    state_baseline_name = STATE_BASELINE_KEY[state_key]

    # RBI + Census for this state
    state_bl = baseline_df[
        baseline_df["state_norm"].str.upper() == state_baseline_name
    ].copy()

    # Compute branch density
    state_bl["branch_density_2013"] = (
        state_bl["reporting_offices_total"] / state_bl["population_total_2011"] * 1e5
    )
    state_bl["deposits_per_capita"] = (
        state_bl["deposits_total_crore_rs"] * 1e7 / state_bl["population_total_2011"]
    )

    # PMMVY enrollment rate: merge pmmvy + census population
    pmmvy = pmmvy_df.copy()
    pmmvy = pmmvy.merge(
        state_bl[["district_norm", "population_total_2011",
                  "branch_density_2013", "deposits_per_capita"]],
        on="district_norm", how="left"
    )
    pmmvy["enrollment_rate"] = pmmvy["beneficiaries"] / pmmvy["population_total_2011"] * 1000
    pmmvy["pmmvy_std"] = (
        (pmmvy["enrollment_rate"] - pmmvy["enrollment_rate"].mean())
        / pmmvy["enrollment_rate"].std()
    )

    print(f"  {state_key} PMMVY: {pmmvy['district_norm'].notna().sum()} districts, "
          f"{pmmvy['population_total_2011'].notna().sum()} with population match")

    # NFHS individual data — attach district-level PMMVY & banking
    nfhs = nfhs_df.copy()
    nfhs_agg = nfhs.groupby(["district_name_norm", "post"])[ OUTCOMES].mean().reset_index()

    # Merge individual NFHS rows with district-level treatment + banking
    merged_ind = nfhs.merge(
        pmmvy[["district_norm", "enrollment_rate", "pmmvy_std",
               "branch_density_2013", "deposits_per_capita", "population_total_2011"]],
        left_on="district_name_norm", right_on="district_norm", how="inner"
    )

    # Standardise banking within state
    bd_mean = merged_ind["branch_density_2013"].mean()
    bd_std  = merged_ind["branch_density_2013"].std()
    merged_ind["banking_std"] = (merged_ind["branch_density_2013"] - bd_mean) / bd_std

    matched = merged_ind["district_code"].nunique()
    total   = nfhs["district_code"].nunique()
    print(f"  {state_key} individual merge: {len(merged_ind):,} women, "
          f"{matched}/{total} districts matched to PMMVY")

    return pmmvy, merged_ind

# ═══════════════════════════════════════════════════════════════════════════════
# 6. DiD estimation
# ═══════════════════════════════════════════════════════════════════════════════

def run_did(merged, state_key, outcomes=None):
    if outcomes is None:
        outcomes = OUTCOMES

    results = []
    for outcome in outcomes:
        sub = merged[[outcome, "post", "pmmvy_std", "banking_std",
                      "age", "age_sq", "education_level", "urban_rural",
                      "wealth_index", "woman_weight", "district_name_norm"]].dropna()

        if len(sub) < 200:
            print(f"    {outcome}: skipped (n={len(sub)})")
            continue

        # Encode district FE
        sub = sub.copy()
        sub["district_fe"] = pd.Categorical(sub["district_name_norm"])

        try:
            # Main DiD: post × PMMVY (no triple yet)
            formula_main = (
                f"{outcome} ~ post*pmmvy_std + age + age_sq + "
                f"education_level + urban_rural + wealth_index + C(district_name_norm)"
            )
            m_main = smf.wls(formula_main, data=sub, weights=sub["woman_weight"]).fit(
                cov_type="cluster", cov_kwds={"groups": sub["district_name_norm"]}
            )

            # Triple interaction: post × PMMVY × banking
            formula_triple = (
                f"{outcome} ~ post*pmmvy_std*banking_std + age + age_sq + "
                f"education_level + urban_rural + wealth_index + C(district_name_norm)"
            )
            m_triple = smf.wls(formula_triple, data=sub, weights=sub["woman_weight"]).fit(
                cov_type="cluster", cov_kwds={"groups": sub["district_name_norm"]}
            )

            results.append({
                "state":       state_key,
                "outcome":     outcome,
                "n_women":     len(sub),
                "n_districts": sub["district_name_norm"].nunique(),
                # Main DiD
                "did_coef":    m_main.params.get("post:pmmvy_std", np.nan),
                "did_se":      m_main.bse.get("post:pmmvy_std", np.nan),
                "did_pval":    m_main.pvalues.get("post:pmmvy_std", np.nan),
                # Triple interaction
                "triple_coef": m_triple.params.get("post:pmmvy_std:banking_std", np.nan),
                "triple_se":   m_triple.bse.get("post:pmmvy_std:banking_std", np.nan),
                "triple_pval": m_triple.pvalues.get("post:pmmvy_std:banking_std", np.nan),
            })
            stars_did    = "***" if results[-1]["did_pval"] < 0.01 else \
                           "**"  if results[-1]["did_pval"] < 0.05 else \
                           "*"   if results[-1]["did_pval"] < 0.10 else ""
            stars_triple = "***" if results[-1]["triple_pval"] < 0.01 else \
                           "**"  if results[-1]["triple_pval"] < 0.05 else \
                           "*"   if results[-1]["triple_pval"] < 0.10 else ""
            print(f"    {outcome:<30} DiD={results[-1]['did_coef']:+.3f}{stars_did:<3} "
                  f"Triple={results[-1]['triple_coef']:+.3f}{stars_triple:<3} "
                  f"(n={len(sub):,})")
        except Exception as e:
            print(f"    {outcome}: ERROR — {e}")

    return pd.DataFrame(results)

# ═══════════════════════════════════════════════════════════════════════════════
# 7. Spatial maps
# ═══════════════════════════════════════════════════════════════════════════════

def fix_enc(s):
    if not isinstance(s, str): return s
    return s.replace(">", "A").replace("@", "U").replace("|", "I")

STATE_SHP_NAME = {
    "HP":    "HIMACHAL PRADESH",
    "Assam": "ASSAM",
    "MP":    "MADHYA PRADESH",
    "WB":    "WEST BENGAL",
}

Q_COLORS = ["#FEE5D9", "#FC9272", "#DE2D26", "#67000D"]

def load_state_shp(state_key):
    gdf = gpd.read_file("data/processed/shapefiles/DISTRICT_BOUNDARY.shp")
    gdf["state_clean"]    = gdf["STATE"].apply(fix_enc).apply(normalise)
    gdf["district_clean"] = gdf["District"].apply(fix_enc).apply(normalise)
    target = STATE_SHP_NAME[state_key]
    sub = gdf[gdf["state_clean"] == target].copy()
    return sub

def make_enrollment_map(state_key, pmmvy_df, state_shp):
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    bg = "#F4F1EC"
    fig.patch.set_facecolor(bg)

    # Panel 1: log-scale continuous
    ax = axes[0]
    ax.set_facecolor(bg)
    merged = state_shp.merge(
        pmmvy_df[["district_norm", "enrollment_rate"]],
        left_on="district_clean", right_on="district_norm", how="left"
    )
    data = merged["enrollment_rate"].dropna()
    if len(data) < 2:
        ax.set_title("No data"); ax.set_axis_off()
    else:
        norm = LogNorm(vmin=max(data.min(), 0.1), vmax=data.max())
        cmap = plt.get_cmap("YlOrRd")
        merged[merged["enrollment_rate"].isna()].plot(
            ax=ax, color="#CCCCCC", linewidth=0.3, edgecolor="white")
        merged[merged["enrollment_rate"].notna()].plot(
            ax=ax, column="enrollment_rate", cmap=cmap, norm=norm,
            linewidth=0.3, edgecolor="white")
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, aspect=28)
        cbar.set_label("PMMVY beneficiaries per 1,000 pop (log)", fontsize=9)
        for _, row in merged.nlargest(5, "enrollment_rate").iterrows():
            if row.geometry is None: continue
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.annotate(row["district_clean"].title() + f"\n{row['enrollment_rate']:.1f}",
                        (cx, cy), fontsize=6, ha="center", va="center",
                        color="#1B2A4A", fontweight="bold")
        ax.set_title(f"PMMVY Enrollment Rate (log scale)\n{pmmvy_df['state'].iloc[0]}",
                     fontsize=11, fontweight="bold", color="#1B2A4A")
        ax.set_axis_off()

    # Panel 2: quartile status
    ax = axes[1]
    ax.set_facecolor(bg)
    merged2 = state_shp.merge(
        pmmvy_df[["district_norm", "enrollment_rate"]],
        left_on="district_clean", right_on="district_norm", how="left"
    )
    data2 = merged2["enrollment_rate"].dropna()
    if len(data2) >= 4:
        merged2["quartile"] = pd.qcut(
            data2.rank(method="first"), q=4,
            labels=["Q1 Low", "Q2 Med-Low", "Q3 Med-High", "Q4 High"]
        )
        q_map = dict(zip(["Q1 Low","Q2 Med-Low","Q3 Med-High","Q4 High"], Q_COLORS))
        merged2[merged2["enrollment_rate"].isna()].plot(
            ax=ax, color="#CCCCCC", linewidth=0.3, edgecolor="white")
        for q_label, color in q_map.items():
            sub = merged2[merged2["quartile"].astype(str) == q_label]
            if len(sub): sub.plot(ax=ax, color=color, linewidth=0.3, edgecolor="white")
        for _, row in merged2.iterrows():
            if row.geometry is None or pd.isna(row.get("enrollment_rate")): continue
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.annotate(row["district_clean"].title(), (cx, cy),
                        fontsize=5.5, ha="center", va="center", color="#2C2C2C")
        patches = [mpatches.Patch(color=c, label=l)
                   for l, c in q_map.items()]
        patches.append(mpatches.Patch(color="#CCCCCC", label="No data"))
        ax.legend(handles=patches, loc="lower left", fontsize=8, framealpha=0.9,
                  title="Enrollment quartile", title_fontsize=8)
    ax.set_title(f"PMMVY Enrollment Status — Quartile\n{pmmvy_df['state'].iloc[0]}",
                 fontsize=11, fontweight="bold", color="#1B2A4A")
    ax.set_axis_off()

    fname = f"results/maps/map_{state_key.lower()}_pmmvy_enrollment.png"
    plt.tight_layout()
    plt.savefig(fname, dpi=160, bbox_inches="tight", facecolor=bg)
    plt.close()
    print(f"  Saved → {fname}")

# ═══════════════════════════════════════════════════════════════════════════════
# 8. DiD results map — coef by district (post × PMMVY direction)
# ═══════════════════════════════════════════════════════════════════════════════

def make_outcomes_map(state_key, merged_ind, state_shp):
    """NFHS-5 vs NFHS-4 mean outcome change by district."""
    change = (
        merged_ind.groupby(["district_name_norm", "post"])["bank_account_self_use"]
        .mean().unstack("post")
    )
    change.columns = ["nfhs4", "nfhs5"]
    change["change_pp"] = (change["nfhs5"] - change["nfhs4"]) * 100
    change = change.reset_index()

    fig, ax = plt.subplots(figsize=(11, 12))
    bg = "#F4F1EC"
    ax.set_facecolor(bg)
    fig.patch.set_facecolor(bg)

    merged = state_shp.merge(
        change, left_on="district_clean", right_on="district_name_norm", how="left"
    )
    data = merged["change_pp"].dropna()
    if len(data) < 2:
        ax.set_title("No data"); ax.set_axis_off()
        plt.tight_layout()
        fname = f"results/maps/map_{state_key.lower()}_bank_change.png"
        plt.savefig(fname, dpi=150, bbox_inches="tight", facecolor=bg)
        plt.close()
        return

    from matplotlib.colors import TwoSlopeNorm
    vmin, vmax = data.quantile(0.02), data.quantile(0.98)
    vcenter = 0 if vmin < 0 < vmax else data.median()
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    cmap = plt.get_cmap("RdYlGn")

    merged[merged["change_pp"].isna()].plot(
        ax=ax, color="#CCCCCC", linewidth=0.3, edgecolor="white")
    merged[merged["change_pp"].notna()].plot(
        ax=ax, column="change_pp", cmap=cmap, norm=norm,
        linewidth=0.3, edgecolor="white")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, aspect=28)
    cbar.set_label("Change in bank account use (pp)", fontsize=10)

    for _, row in merged.nlargest(5, "change_pp").iterrows():
        if row.geometry is None: continue
        cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
        ax.annotate(row["district_clean"].title() + f"\n+{row['change_pp']:.1f}pp",
                    (cx, cy), fontsize=6, ha="center", va="center",
                    color="#1B2A4A", fontweight="bold")

    ax.set_title(
        f"Change in Women's Bank Account Use\nNFHS-4 → NFHS-5 (percentage points) · {state_key}",
        fontsize=12, fontweight="bold", color="#1B2A4A", pad=12)
    ax.set_axis_off()
    plt.tight_layout()
    fname = f"results/maps/map_{state_key.lower()}_bank_change.png"
    plt.savefig(fname, dpi=160, bbox_inches="tight", facecolor=bg)
    plt.close()
    print(f"  Saved → {fname}")

# ═══════════════════════════════════════════════════════════════════════════════
# 9. Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("Multi-state PMMVY district analysis")
    print("=" * 65)

    print("\n[1] Loading PMMVY files...")
    pmmvy_all = load_pmmvy()

    print("\n[2] Loading NFHS harmonized data...")
    nfhs_all = load_nfhs()
    state_nfhs = {}
    for k in ["HP", "Assam", "MP", "WB"]:
        state_nfhs[k] = get_state_nfhs(nfhs_all, k)

    print("\n[3] Loading RBI baseline + Census population...")
    baseline = load_rbi_census()

    print("\n[4] Building state analysis tables...")
    analysis_tables = {}
    for state_key in ["HP", "Assam", "MP", "WB"]:
        print(f"\n  --- {state_key} ---")
        pmmvy_df, merged_ind = build_state_table(
            state_key, pmmvy_all[state_key], state_nfhs[state_key], baseline
        )
        analysis_tables[state_key] = (pmmvy_df, merged_ind)

        # Save
        pmmvy_df.to_csv(f"data/processed/multistate/{state_key.lower()}_pmmvy_district.csv",
                        index=False)
        merged_ind.to_parquet(
            f"data/processed/multistate/{state_key.lower()}_analysis_dataset.parquet"
        )

    print("\n[5] Running DiD estimations...")
    all_results = []
    for state_key in ["HP", "Assam", "MP", "WB"]:
        print(f"\n  === {state_key} DiD ===")
        _, merged = analysis_tables[state_key]
        n_dist = merged["district_name_norm"].nunique()
        if n_dist < 8:
            print(f"  Skipping — only {n_dist} districts (minimum 8 required)")
            continue
        if n_dist < 15:
            print(f"  Note: small sample ({n_dist} districts) — interpret SEs with caution")
        res = run_did(merged, state_key)
        all_results.append(res)
        res.to_csv(f"results/tables/multistate_{state_key.lower()}_did_results.csv", index=False)

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        combined.to_csv("results/tables/multistate_did_combined.csv", index=False)
        print("\n  Combined results saved → results/tables/multistate_did_combined.csv")

    print("\n[6] Producing spatial maps...")
    for state_key in ["HP", "Assam", "MP", "WB"]:
        print(f"\n  --- {state_key} ---")
        shp = load_state_shp(state_key)
        pmmvy_df, merged_ind = analysis_tables[state_key]
        make_enrollment_map(state_key, pmmvy_df, shp)
        if len(merged_ind) > 0:
            make_outcomes_map(state_key, merged_ind, shp)

    print("\n[7] Summary table...")
    if all_results:
        combined = pd.concat(all_results)
        print("\n" + "=" * 80)
        print(f"{'State':<8} {'Outcome':<32} {'DiD coef':>10} {'p':>6} {'Triple':>10} {'p':>6} {'N':>7}")
        print("-" * 80)
        for _, r in combined.iterrows():
            s_did    = "***" if r["did_pval"]    < 0.01 else "**" if r["did_pval"]    < 0.05 else "*" if r["did_pval"]    < 0.10 else ""
            s_triple = "***" if r["triple_pval"] < 0.01 else "**" if r["triple_pval"] < 0.05 else "*" if r["triple_pval"] < 0.10 else ""
            print(f"{r['state']:<8} {r['outcome']:<32} {r['did_coef']:>+8.3f}{s_did:<2} "
                  f"{r['did_pval']:>6.3f} {r['triple_coef']:>+8.3f}{s_triple:<2} "
                  f"{r['triple_pval']:>6.3f} {int(r['n_women']):>7,}")
        print("=" * 80)

    print("\nDone.")


if __name__ == "__main__":
    main()
