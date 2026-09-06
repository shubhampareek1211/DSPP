"""Build the public working-paper PDF from the authoritative Markdown source."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT_ROOT / "results" / "findings" / "paper_consolidated.md"
OUTPUT_DIR = PROJECT_ROOT / "output" / "pdf"
OUTPUT = OUTPUT_DIR / "cash_transfers_banking_womens_financial_empowerment_india.pdf"
TEMP_DIR = PROJECT_ROOT / "tmp" / "pdfs"
TEMP_SOURCE = TEMP_DIR / "working_paper_source.md"


FIGURES = [
    ("Raw autonomy change by PMMVY-intensity tercile",
     PROJECT_ROOT / "results" / "figures" / "paper" / "fig1_autonomy_tercile.png"),
    ("PMMVY-autonomy interaction by banking depth",
     PROJECT_ROOT / "results" / "figures" / "paper" / "fig2_banking_bonus.png"),
    ("Older banking stock compared with recent expansion",
     PROJECT_ROOT / "results" / "figures" / "paper" / "fig3_branches_vs_growth.png"),
    ("State banking depth and women's account ownership",
     PROJECT_ROOT / "results" / "figures" / "paper" / "fig4_panel_banking_v3.png"),
]


def require_program(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise SystemExit(
            f"Required program '{name}' was not found. Install Pandoc and a LaTeX distribution, "
            "then rerun `make paper`."
        )
    return executable


def build_source() -> str:
    body = SOURCE.read_text(encoding="utf-8")
    title_line = "# Cash Transfers, Banking Infrastructure, and Women's Financial Empowerment in India"
    body = body.replace(title_line, "", 1).lstrip()
    body = body.replace("⚠️", "Caution:").replace("₹", "Rs.")

    figures = [
        "\n```{=latex}\n\\newpage\n```\n",
        "## Selected Figures\n",
    ]
    for caption, path in FIGURES:
        if not path.exists():
            raise SystemExit(f"Missing figure: {path}")
        figures.extend([
            f"\n![{caption}]({path.as_posix()}){{ width=100% }}\n",
            "\n```{=latex}\n\\newpage\n```\n",
        ])

    appendix_marker = "## Appendix A: Spatial Maps and Supplementary Analysis"
    figure_block = "".join(figures)
    if appendix_marker in body:
        body = body.replace(appendix_marker, figure_block + "\n" + appendix_marker, 1)
    else:
        body += figure_block

    metadata = """---
title: "Cash Transfers, Banking Infrastructure, and Women's Financial Empowerment in India"
subtitle: "Evidence from PMMVY, NFHS, RBI Banking Data, and Digital Payments"
author: "Shubham Pareek"
date: "September 2026"
papersize: "a4"
fontsize: "10pt"
geometry:
  - margin=24mm
---

"""
    return metadata + body


def main() -> None:
    pandoc = require_program("pandoc")
    lualatex = require_program("lualatex")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_SOURCE.write_text(build_source(), encoding="utf-8")

    command = [
        pandoc,
        str(TEMP_SOURCE),
        "--from=markdown+yaml_metadata_block+raw_attribute+pipe_tables",
        f"--pdf-engine={lualatex}",
        "--standalone",
        "--toc",
        "--variable=mainfont:Times New Roman",
        "--variable=papersize:a4",
        "--variable=geometry:margin=24mm",
        "--resource-path",
        str(PROJECT_ROOT),
        "--metadata",
        "link-citations=true",
        "--output",
        str(OUTPUT),
    ]
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    print(f"Built {OUTPUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
