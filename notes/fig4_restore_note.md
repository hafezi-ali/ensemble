# Restoring Fig. 4 (boxplot_comparison) and correcting Table I

## What I got wrong

I removed your boxplot figure on two stated grounds. The notebook
`code/Main_Thp.ipynb` disproves both.

1. I claimed the per-fold data existed only in Colab and could not be
   redrawn. The notebook's *stored cell outputs* contain the rendered figure
   (cell 21) and the printed per-configuration statistics for all 45
   configurations (cell 12). The pickles are absent from this machine, but the
   rendered figure is a faithful record and the statistics validate any
   extraction from it.
2. I claimed the figure spread over the 45-config grid, which is why it
   disagreed with the table. It does not. Cell 17 is
   `df_results_sorted.query('n_c==6 and phi==0.5')` -- a single configuration,
   the same one Table I reports. The disagreement had a different cause (below).

## The real error: Table I DistE rows

I audited all 16 rows of Table I against the notebook's printed statistics for
n_c=6, phi=0.5. Twelve match exactly. All four DistE rows were wrong in the
manuscript, systematically low:

| method | learner | was (mean/std/max) | now (mean/std/max) |
|--------|---------|--------------------|--------------------|
| DistE  | lr      | 0.911 / 0.048 / 0.958 | 0.962 / 0.043 / 0.977 |
| DistE  | svm     | 0.904 / 0.045 / 0.951 | 0.959 / 0.040 / 0.974 |
| DistE  | knn     | 0.885 / 0.037 / 0.929 | 0.948 / 0.031 / 0.966 |
| DistE  | dt      | 0.838 / 0.019 / 0.860 | 0.841 / 0.016 / 0.864 |

The corrected values agree with three independent sources: the notebook's
printed output, `code/best_ensemble_results.csv` (DistE/lr = 0.962), and your
figure itself. The manuscript was already self-contradictory before this fix --
Section IV-B used 0.841 and the discussion in Sec. IV-F used std 0.043, both
correct, while the table said 0.838 and 0.048.

## Consequence for the claim

The old numbers supported "DistE trails DensityE by roughly six points". That
claim is not true. The measured gap is ~1 point (0.962 vs 0.973 for lr), and
the per-fold distributions overlap. The defensible claim, now in the text, is
about *dispersion*: DensityE std 0.003 vs DistE 0.043 for lr -- a 14-fold
reduction -- with no low-side outlier folds. This is the same claim Sec. IV-F
already made, so the paper is now internally consistent.

Prose rewritten at Sec. IV-B (the six-point paragraph) and extended at the end
of Sec. IV-C to reference the figure.

## How the figure was rebuilt

Box statistics were measured from the pixels of your rendered figure
(`nb_cell21.png`, extracted from notebook cell 21): axes calibrated on the
frame at y=0.98/0.89, boxes located by Set2 fill colour, quartiles from box
extent, medians/whiskers from black runs, means from the red crosses. Every
recovered mean matches the notebook's printed value to <= 4e-4 (see
`boxplot_stats_measured.csv`). Nothing was invented; the redraw is a
re-rendering of your measurements at journal size.

Deliberate changes from your original: AvgE/MaxE and the dt learner stay
excluded (your `query(...)` excluded them -- I kept that and now say so in the
caption); y-range unchanged at 0.89-0.98; figure sized for a two-column float
instead of 25x25 inches.

## Do not revert

- Do not restore the old Table I DistE values. They contradict the CSV, the
  notebook, and the figure.
- Do not restore `manuscript/boxplot_comparison.pdf` (the pre-existing file,
  now also kept as `boxplot_comparison_OLD.pdf`). It is NOT your figure -- it
  draws DistE near 0.90 with whiskers below 0.86, i.e. it encodes the erroneous
  table values. The manuscript now includes `boxplot_comparison_v2.pdf`.
- Do not reinstate "roughly six points below" or any equivalent margin claim.

## Files

- `manuscript/boxplot_comparison_v2.pdf` / `.png` -- rebuilt figure (Fig. 4, p10)
- `boxplot_stats_measured.csv` -- the seven boxes' statistics with validation
- `table2_audit.csv` -- all 16 Table I rows, manuscript vs notebook
