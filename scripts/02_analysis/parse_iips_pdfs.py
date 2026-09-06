"""Parse IIPS district-level PDFs into clean CSVs."""
import re
import os
from pathlib import Path
import pdfplumber
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.chdir(PROJECT_ROOT)

# pattern: state district  val (lb,ub)  val (lb,ub)  val (lb,ub)  [optional 3 more for fin_inclusion]
EST_RE = re.compile(r'([\d.]+)\s*\(([\d.]+),([\d.]+)\)')


def parse_estimates(text):
    """Return list of (estimate, lb, ub) tuples found in text."""
    return [(float(m[1]), float(m[2]), float(m[3])) for m in EST_RE.finditer(text)]


def is_data_line(line):
    return bool(EST_RE.search(line)) and '(' in line and ',' in line


def split_state_district(prefix, known_states):
    """Given 'State District', split on first match of a known state name."""
    prefix = prefix.strip()
    for st in sorted(known_states, key=len, reverse=True):
        if prefix.upper().startswith(st.upper()):
            dist = prefix[len(st):].strip()
            if dist:
                return st, dist
    # fallback: first two words = state, rest = district
    parts = prefix.split()
    if len(parts) >= 2:
        return parts[0], ' '.join(parts[1:])
    return prefix, ''


# ── Financial Inclusion PDF ──────────────────────────────────────────────────

def parse_financial_inclusion():
    path = 'data/raw/iips/iips_district_financial_inclusion.pdf'
    rows = []
    known_states = set()

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split('\n'):
                if not is_data_line(line):
                    continue
                ests = parse_estimates(line)
                if len(ests) < 6:
                    continue  # need 6 triplets (NFHS4+5 × 3 indicators)
                # Remove all estimate strings to get state+district prefix
                prefix = EST_RE.sub('', line).strip()
                prefix = re.sub(r'\s+', ' ', prefix)
                rows.append({'prefix': prefix, 'ests': ests[:6]})

    # Collect known state names from prefixes for splitting
    # Use a heuristic: look for lines where prefix matches known Indian state
    indian_states = [
        'Andaman & Nicobar Islands', 'Andhra Pradesh', 'Arunachal Pradesh',
        'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh',
        'Dadra & Nagar Haveli and Daman & Diu', 'Dadra & Nagar Haveli',
        'Daman & Diu', 'Delhi', 'Goa', 'Gujarat', 'Haryana',
        'Himachal Pradesh', 'Jammu & Kashmir', 'Jharkhand', 'Karnataka',
        'Kerala', 'Ladakh', 'Lakshadweep', 'Madhya Pradesh', 'Maharashtra',
        'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha',
        'Puducherry', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
        'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    ]

    records = []
    for r in rows:
        prefix = r['prefix']
        ests = r['ests']
        state, district = split_state_district(prefix, indian_states)
        if not district:
            continue
        records.append({
            'state': state.strip(),
            'district': district.strip(),
            'bank_nfhs4': ests[0][0], 'bank_nfhs4_lb': ests[0][1], 'bank_nfhs4_ub': ests[0][2],
            'bank_nfhs5': ests[1][0], 'bank_nfhs5_lb': ests[1][1], 'bank_nfhs5_ub': ests[1][2],
            'micro_know_nfhs4': ests[2][0], 'micro_know_nfhs4_lb': ests[2][1], 'micro_know_nfhs4_ub': ests[2][2],
            'micro_know_nfhs5': ests[3][0], 'micro_know_nfhs5_lb': ests[3][1], 'micro_know_nfhs5_ub': ests[3][2],
            'micro_use_nfhs4': ests[4][0], 'micro_use_nfhs4_lb': ests[4][1], 'micro_use_nfhs4_ub': ests[4][2],
            'micro_use_nfhs5': ests[5][0], 'micro_use_nfhs5_lb': ests[5][1], 'micro_use_nfhs5_ub': ests[5][2],
        })

    df = pd.DataFrame(records)
    df['bank_change'] = df['bank_nfhs5'] - df['bank_nfhs4']
    df['micro_know_change'] = df['micro_know_nfhs5'] - df['micro_know_nfhs4']
    df['micro_use_change'] = df['micro_use_nfhs5'] - df['micro_use_nfhs4']
    return df


# ── Women Earnings PDF ────────────────────────────────────────────────────────

def parse_earnings():
    path = 'data/raw/iips/iips_district_women_worked_cash_earnings.pdf'
    rows = []
    indian_states = [
        'Andaman & Nicobar Islands', 'Andhra Pradesh', 'Arunachal Pradesh',
        'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh',
        'Dadra & Nagar Haveli and Daman & Diu', 'Dadra & Nagar Haveli',
        'Daman & Diu', 'Delhi', 'Goa', 'Gujarat', 'Haryana',
        'Himachal Pradesh', 'Jammu & Kashmir', 'Jharkhand', 'Karnataka',
        'Kerala', 'Ladakh', 'Lakshadweep', 'Madhya Pradesh', 'Maharashtra',
        'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha',
        'Puducherry', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
        'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    ]

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split('\n'):
                if not is_data_line(line):
                    continue
                ests = parse_estimates(line)
                if len(ests) < 3:
                    continue
                prefix = EST_RE.sub('', line).strip()
                prefix = re.sub(r'\s+', ' ', prefix)
                state, district = split_state_district(prefix, indian_states)
                if not district:
                    continue
                rows.append({
                    'state': state.strip(),
                    'district': district.strip(),
                    'worked_12m': ests[0][0], 'worked_12m_lb': ests[0][1], 'worked_12m_ub': ests[0][2],
                    'self_employed': ests[1][0], 'self_employed_lb': ests[1][1], 'self_employed_ub': ests[1][2],
                    'earned_cash': ests[2][0], 'earned_cash_lb': ests[2][1], 'earned_cash_ub': ests[2][2],
                })

    return pd.DataFrame(rows)


def main():
    print("Parsing financial inclusion PDF...")
    fin = parse_financial_inclusion()
    print(f"  Districts parsed: {len(fin)}")
    print(f"  Sample:\n{fin[['state','district','bank_nfhs4','bank_nfhs5','bank_change']].head(5).to_string()}")
    fin.to_csv('data/processed/iips_financial_inclusion.csv', index=False)
    print("  Saved → data/processed/iips_financial_inclusion.csv")

    print("\nParsing women earnings PDF...")
    earn = parse_earnings()
    print(f"  Districts parsed: {len(earn)}")
    print(f"  Sample:\n{earn[['state','district','worked_12m','self_employed','earned_cash']].head(5).to_string()}")
    earn.to_csv('data/processed/iips_women_earnings.csv', index=False)
    print("  Saved → data/processed/iips_women_earnings.csv")


if __name__ == '__main__':
    main()
