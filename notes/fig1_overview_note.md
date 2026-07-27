# Fig. 1 (overview) — what replaced the old boxplot figure, and why

## What was removed

`boxplot_comparison.pdf` (formerly Fig. 5, `fig:boxplot_comparison`) and its paragraph.
Reason: **it could not be regenerated and it contradicted Table II.**

1. The per-fold distributions behind it live only in the Colab notebook
   (`os.chdir('/content/drive/MyDrive/Thp')` + pickles), not in this repo. Redrawing it
   would have meant inventing the boxes.
2. It put DistE/lr at a mean near 0.905 with whiskers below 0.86, while
   `code/best_ensemble_results.csv` and Table II record DistE/lr at 0.962. The figure
   appears to spread over the whole 45-config grid; the table reports the best config's
   fold spread. A referee comparing the two would have asked which is real.
3. Its caption and prose discussed **AvgE** and described MaxE distributions, but neither
   AvgE nor MaxE appears anywhere in the figure.
4. Its "Single Model" box at 0.925 is the capped SVM, superseded by the converged
   SVM (0.9721) measured for Table IV.

The `boxplot_comparison.pdf` file is left on disk; it is no longer included.

## What replaced it

`manuscript/fig1_overview.pdf` — three panels, 180 mm wide, placed at the opening of
Section III (Methodology) as **Fig. 1**, referenced there and again in Section
IV-A. Every number in it comes from a file in this repo:

| Panel | Content | Source |
|---|---|---|
| (a) | Pipeline schematic: GMM with full $\Sigma_k$ on 157 PCs -> resample $\phi$ per component -> fit $f_k$ -> responsibility weighting at inference | no data; schematic only. Components drawn anisotropic and tilted deliberately — isotropic blobs would depict K-means, not the method |
| (b) | Mean F-score by base learner x aggregation rule, $\pm 1$ SD | `code/best_ensemble_results.csv` (your measured 45-config grid) |
| (c) | Subset overlap and base-learner disagreement vs $\phi$, at $K=5,8$ | `data/diversity_diagnostic.csv` |

Panels (b) and (c) are drawn from data already in the paper or already measured; no new
experiment was run for this figure.

## Panels that were cut before placement

A five-panel version was built and compiled first. Two panels were cut as duplicative:

- **ARI gap heatmap (GMM − K-means)** — same result as Fig. 7(c). Fig. 7 was kept because
  it additionally carries the dimensionality reversal, which is the evidence the honest
  limitation in Section IV-E rests on; the heatmap alone would have lost that.
- **Per-fold boxplot vs non-clustering baselines** — identical in content to Fig. 8.

Cutting them rather than cutting Figs. 7/8 avoids repeated panels, which Referee 3
already objected to on figure placement grounds.

## Prose changes

Replaced the removed paragraph in Section IV-A with a description of the measured
aggregation ordering. Three claims in it are new to the manuscript and all are read
off `best_ensemble_results.csv`:

- MaxE's SD reaches **0.143** (dt) against **0.010** for DensityE (dt) — the erratic
  degradation is quantified, not asserted.
- **The decision tree reverses the ordering**: DistE 0.841 > DensityE 0.821. The old
  prose claimed DensityE "sits clearly above DistE" without exception. It has one.
- MaxE retains a single learner per query, so it forfeits the ensemble — this is the
  mechanism reading, offered as interpretation and marked as such.

Panel (c)'s caption states plainly that at the **originally published $\phi = 0.9$**
disagreement is below 1% and the ensemble is effectively a single classifier, and that
the cross-validated $\phi = 0.4$ retains 63–65%. This is a limitation of the published
configuration, stated in the paper's own overview figure. Do not soften it.

## Also fixed

`\section{Results and Analysis}` had no `\label`; the new Methodology prose cites it, so
`\label{sec:results}` was added. Final compile reports zero undefined references.

## Build

`tectonic -X compile document.tex --outdir _build` (the `tex` environment; no pdflatex
on this machine), then `_build/document.pdf` copied to `manuscript/document.pdf`.
18 pages. Fig. 1 lands on page 6 with Fig. 2; figure numbering of everything downstream
shifted by one (old Fig. 1 -> Fig. 2, and so on; old Fig. 5 is gone, so the tail is
unchanged in count).
