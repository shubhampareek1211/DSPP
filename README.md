# Cash Transfers, Banking Infrastructure, and Women's Financial Empowerment in India

This repository studies how women-directed direct benefit transfer programs interact with financial infrastructure to shape women's financial inclusion and household empowerment in India.

## Working paper

[Download the current working paper (PDF)](output/pdf/cash_transfers_banking_womens_financial_empowerment_india.pdf)

The PDF is generated from the authoritative paper source and current figures with `make paper`.

The analysis combines NFHS-4 (2015-16) and NFHS-5 (2019-21), PMMVY administrative records, RBI banking statistics, Census 2011 population, state women-directed transfer data, and a supplementary state-level UPI panel.

## Research question

Did PMMVY and related women-directed cash-transfer programs improve women's financial inclusion and empowerment, and were the gains larger where formal banking infrastructure was more deeply established?

## Main findings

- At the national level, PMMVY enrollment intensity is positively associated with changes in women's bank-account use and own-money autonomy, but the latest estimates are not statistically significant: +2.1 percentage points for bank-account use (`p = 0.18`) and +1.2 points for autonomy (`p = 0.31`).
- In Uttar Pradesh, the PMMVY-intensity association with women's participation in health-care decisions is larger where pre-existing banking infrastructure is denser (+0.062, `p = 0.009`). Average UP associations are mostly insignificant; own-money autonomy is negative (−3.9 points, `p = 0.041`).
- District-level replications in Assam and Madhya Pradesh also show positive banking-amplification estimates for own-money autonomy. Himachal Pradesh is underpowered and West Bengal is statistically inconclusive.
- Across 544 districts, greater 2013 branch density is associated with lower child marriage, lower teen pregnancy, and more women completing at least ten years of schooling. These are cross-sectional associations, not fully identified causal effects.
- The historical banking stock predicts women's later outcomes more consistently than banking expansion between 2013 and 2020.
- State-level aggregate UPI activity does not show a robust response to the launch of contemporary women-directed DBT programs. This extension cannot identify women's transactions directly.

## Interpretation

The evidence is consistent with cash transfers and financial infrastructure acting as complements. However, program intensity is not randomly assigned, several analyses are observational, and residual differences in district development trajectories may affect the estimates. The results should not be interpreted as definitive causal effects unless a specification explicitly supports that claim.

## Repository structure

```text
data/
  raw/             local source downloads; restricted and large files are ignored
  processed/       public aggregates, crosswalks, and local restricted extracts
docs/
  data_docs/       source inventory and variable documentation
  planning/        historical project notes; not the authoritative results
results/
  tables/          regression outputs and analysis datasets safe for release
  figures/paper/   final paper figures
  maps/            appendix maps
  findings/        study write-ups and consolidated paper
scripts/
  01_build/        source cleaning and harmonization
  02_analysis/     statistical analyses
  03_figures/      final figures and spatial outputs
```

## Reproducing the analysis

See [REPLICATION.md](REPLICATION.md) for the execution order and [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md) for source-access requirements.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

All commands should be run from the repository root. Scripts resolve paths relative to their own location and do not require machine-specific absolute paths.

To rebuild the downloadable working paper, install [Pandoc](https://pandoc.org/installing.html) and a LaTeX distribution that provides LuaLaTeX, then run:

```bash
make paper
```

## Data policy

NFHS/DHS respondent-level microdata and respondent-level derived files are not distributed in this repository. Users must obtain their own authorized copies. Public aggregate outputs and geographic crosswalks are retained where appropriate.

PhonePe Pulse may be used as a district-level measure of the surrounding digital-payment ecosystem. It is platform-specific, aggregated, and not gender-disaggregated; it must not be described as women's individual PhonePe activity or as the complete UPI market.

## Authoritative outputs

- Working paper: `results/findings/paper_consolidated.md`
- National PMMVY estimates: `results/tables/pmmvy_national_did_results.csv`
- UP interaction results: `results/tables/table3_triple_interaction.csv`
- Multi-state results: `results/tables/multistate_did_combined.csv`
- National district results: `results/tables/national_crosssection_results.csv`

When a historical planning note or component write-up conflicts with the current tables, the current regression table and consolidated paper control.

## License and citation

Code is released under the MIT License. Source datasets retain their original providers' terms and licenses. Citation metadata are provided in `CITATION.cff`.
