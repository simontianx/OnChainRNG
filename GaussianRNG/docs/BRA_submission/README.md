Target venue: `Blockchain: Research and Applications`

This folder contains a venue-tuned manuscript draft based on the main combined
paper:
- [BRA_submission.tex](./BRA_submission.tex)

It keeps the shared figures and generated tables in the sibling
`../NumericalStudy/` directory and is intended as a separate submission-focused
workspace so the main draft can continue evolving independently.

This folder now also contains:
- [references.bib](./references.bib): bibliography for the BRA draft
- [origin_package](./origin_package): curated CSVs and figure references for
  rebuilding the manuscript plots in Origin/OriginPro

Build from this folder with:

```bash
Rscript plot_publication_figures.R
latexmk -pdf -interaction=nonstopmode -halt-on-error BRA_submission.tex
```

To regenerate the tables and CSVs first (deterministic, seed `20260415`):

```bash
python3 ../NumericalStudy/generate_study_artifacts.py
python3 ../NumericalStudy/generate_cross_vm_artifacts.py
```

The gas numbers in the on-chain implications section come from the Foundry
project in `../../benchmarks` (`forge test -vvvv --match-test testGasProfile`).

Review history:
- [paper_review_2026-04-24.md](./paper_review_2026-04-24.md): editorial/storytelling pass (applied)
- [paper_review_2026-09-08.md](./paper_review_2026-09-08.md): technical/statistical pass (applied)
