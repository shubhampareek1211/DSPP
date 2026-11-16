.PHONY: paper figures

paper:
	python3 scripts/04_release/build_working_paper_pdf.py

figures:
	python3 scripts/03_figures/make_paper_figures_v3.py
	python3 scripts/03_figures/make_figure3_1_pmmvy_intensity.py
