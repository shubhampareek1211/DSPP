"""Build a district-quarter panel from a local PhonePe Pulse repository clone.

The public Pulse JSON contains aggregate activity for all PhonePe users. It is
not gender-disaggregated and must not be interpreted as women's transactions or
as the complete UPI market.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PULSE_DIR = PROJECT_ROOT / "data" / "raw" / "phonepe_pulse"
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "phonepe"
    / "phonepe_district_quarter.csv"
)


def normalize_name(value: str) -> str:
    """Return a conservative lowercase geographic join key."""
    value = str(value).lower().replace("&", " and ")
    value = re.sub(r"\bdistrict\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def available_quarters(metric_root: Path) -> list[tuple[str, int, int, Path]]:
    """Enumerate state/year/quarter JSON files under a Pulse metric root."""
    records: list[tuple[str, int, int, Path]] = []
    if not metric_root.exists():
        return records
    for state_dir in sorted(path for path in metric_root.iterdir() if path.is_dir()):
        for year_dir in sorted(path for path in state_dir.iterdir() if path.is_dir()):
            if not year_dir.name.isdigit():
                continue
            for json_path in sorted(year_dir.glob("*.json")):
                if json_path.stem.isdigit():
                    records.append(
                        (state_dir.name, int(year_dir.name), int(json_path.stem), json_path)
                    )
    return records


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not payload.get("success") or "data" not in payload:
        raise ValueError(f"Unexpected PhonePe Pulse payload: {path}")
    return payload["data"]


def load_transactions(pulse_dir: Path) -> pd.DataFrame:
    root = pulse_dir / "data" / "map" / "transaction" / "hover" / "country" / "india" / "state"
    rows: list[dict] = []
    for state, year, quarter, path in available_quarters(root):
        for district in read_json(path).get("hoverDataList", []):
            metrics = district.get("metric") or []
            total = next((item for item in metrics if item.get("type") == "TOTAL"), None)
            if total is None:
                continue
            rows.append(
                {
                    "state": state,
                    "district": district["name"],
                    "year": year,
                    "quarter": quarter,
                    "transaction_count": total.get("count"),
                    "transaction_amount": total.get("amount"),
                }
            )
    return pd.DataFrame(rows)


def load_registered_counts(pulse_dir: Path, metric: str) -> pd.DataFrame:
    root = pulse_dir / "data" / "map" / metric / "hover" / "country" / "india" / "state"
    column = "registered_users" if metric == "user" else "registered_merchants"
    rows: list[dict] = []
    for state, year, quarter, path in available_quarters(root):
        for district, values in read_json(path).get("hoverData", {}).items():
            rows.append(
                {
                    "state": state,
                    "district": district,
                    "year": year,
                    "quarter": quarter,
                    column: values.get("registeredCount"),
                }
            )
    return pd.DataFrame(rows)


def build_panel(pulse_dir: Path) -> pd.DataFrame:
    transactions = load_transactions(pulse_dir)
    if transactions.empty:
        raise FileNotFoundError(
            f"No district transaction JSON found under {pulse_dir}. "
            "Clone https://github.com/PhonePe/pulse to this location first."
        )

    key = ["state", "district", "year", "quarter"]
    panel = transactions.merge(load_registered_counts(pulse_dir, "user"), on=key, how="left")
    panel = panel.merge(load_registered_counts(pulse_dir, "merchant"), on=key, how="left")
    panel["state_key"] = panel["state"].map(normalize_name)
    panel["district_key"] = panel["district"].map(normalize_name)
    panel["period"] = panel["year"].astype(str) + "Q" + panel["quarter"].astype(str)
    panel["source"] = "PhonePe Pulse"
    return panel.sort_values(["state_key", "district_key", "year", "quarter"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pulse-dir", type=Path, default=DEFAULT_PULSE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    panel = build_panel(args.pulse_dir.resolve())
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(output, index=False)
    print(
        f"Saved {len(panel):,} district-quarter rows "
        f"({panel['period'].min()} to {panel['period'].max()}) to {output}"
    )


if __name__ == "__main__":
    main()
