# Origin Figure Package

This folder is the handoff bundle for rebuilding the paper's statistical figures
in Origin or OriginPro. It is intentionally smaller than the full
`../NumericalStudy/generated/` directory and focuses on the figures that are
most likely to survive into a journal submission.

## Structure

- `data/`: curated CSV exports for the main manuscript figures.
- `reference_figures/`: current PDF figure previews from the BRA submission
  pipeline. These are reference layouts only, not final Origin exports.
- `figure_manifest.csv`: mapping from manuscript figure to source CSVs, columns,
  and recommended chart type.

## Recommended Figure Priorities

Main text:
- `BRA-F1`: cross-VM overview
- `BRA-F2`: cross-VM dependence summary
- `BRA-F5`: normalization errors
- `BRA-F6`: popcount CDF
- `BRA-F7`: popcount QQ panels
- `BRA-F8`: tail-probability panels
- `BRA-F9`: repeated-sequence ACF

Appendix or supplementary material:
- `BRA-F3`: bit-wise uniformity panels
- `BRA-F4`: pairwise similarity distributions
- `BRA-F10`: repeated-sequence lag-1 scatter

## Origin Styling Notes

- Export final figures as vector PDF or SVG.
- Use a journal-safe font stack such as Arial or Helvetica at 8--9 pt unless a
  target template requires something else.
- Prefer line widths around 1.2--1.6 pt and marker sizes that still print
  clearly when the figure is scaled to one-column width.
- Avoid saturated rainbow palettes. Use a restrained, colorblind-safe palette
  and preserve a grayscale-readable backup through line types or marker shapes.
- Remove chart borders and heavy gridlines. Keep only light horizontal guides
  when they materially improve reading.
- For multi-panel figures, lock axis ranges across panels wherever comparison is
  the point of the figure.
- For QQ, CDF, and tail plots, keep the theoretical reference curve visually
  distinct but secondary to the empirical series.

## PicDoc Note

PicDoc can still be useful for a graphical abstract or a conceptual
cross-VM-architecture illustration. It is not recommended for the core
statistical figures in this paper, where precise scales and reproducible
encodings matter.
