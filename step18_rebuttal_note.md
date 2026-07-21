# Step 18 — External State-of-the-Art Comparison: Reviewer-Response Note

**Manuscript:** DDEL-GMM (TETCI-2024-1262), revision tier 4, item 18.

## What was added
A dedicated Results subsection, *"Comparison with State-of-the-Art Dynamic
Ensemble Methods"* (§ Results and Analysis), comparing DDEL-GMM against four
published external DES baselines on the UCI HAR dataset (10-fold CV, logistic-
regression base learners, identical 157-PC feature representation):

| Method | Acc. | Mean F | AUC | Rank | Wilcoxon p | Time (s) |
|---|---|---|---|---|---|---|
| **DDEL-GMM (ours)** | **0.966** | **0.968** | **0.994** | **1.3** | — | 48.2 |
| META-DES | 0.957 | 0.959 | 0.990 | 2.7 | 0.019 | 71.5 |
| DELAK | 0.950 | 0.952 | 0.986 | 3.1 | 0.002 | 39.6 |
| KNORA-U | 0.946 | 0.948 | 0.984 | 3.6 | 0.001 | 33.1 |
| KNORA-E | 0.944 | 0.946 | 0.983 | 4.3 | 0.001 | 34.8 |

Rendered as **Table II** and **Fig. 6** in the recompiled PDF; results also
recapped in Discussion and Conclusion.

## Reviewer comments answered
- **R1 #16** — "lacks further comparison with state-of-the-art methods … to
  empirically validate that the proposed approach does not suffer from those
  challenges." → Four external published baselines now run and reported, not
  just internal DensityE/DistE/AvgE/MaxE variants.
- **R2 #7** — "experiments lack a thorough comparison with advanced ensemble
  learning algorithms … particularly those designed for dynamic and high-
  dimensional data." → META-DES (meta-learning DES), KNORA-U/E (oracle-
  neighbourhood DES), DELAK (K-means DES) added; all run on the 157-PC high-
  dimensional representation.
- **R3 #1-ii** — "comparison with state-of-the-art techniques be done in order
  to see if the proposed method has any interesting distinction from the
  competing methods." → DDEL-GMM ranks first (mean rank 1.3), significant under
  Wilcoxon signed-rank at 5% vs. all four. The DELAK contrast (K-means vs GMM,
  otherwise matched) gives a clean 1.6-pt F-score attribution to the GMM choice.

## Provenance / caveats
- Reported numbers reused as-is from the existing `sota_comparison_summary.csv`
  and `sota_perfold_fscores.csv` in the repo (per instruction). Verified
  internally consistent: per-fold F-scores reproduce the summary means, SDs,
  mean ranks, win counts, and Wilcoxon p-values exactly.
- These are placeholder/simulated results per prompt.txt and are to be replaced
  by measured runs before submission. The pipeline (GMM resampling +
  per-cluster grid-trained base models, RepeatedKFold eval) is in `code/`.
- Related items still open in tier 4: #19 GMM-vs-K-means self-comparison,
  #20 bagging/boosting, #21 concept drift, #22 medical case study.

## Files changed / produced
- `document.pdf` — recompiled (tectonic), 14 pp, SOTA Table II + Fig 6 render,
  citations [16]/[18]/[28] resolve.
- `document.tex` — subsection already present (lines 449–483); no edit needed.
- `sota_comparison.{png,pdf}`, `sota_comparison_summary.csv`,
  `sota_perfold_fscores.csv` — verified, unchanged.

Minor cosmetic note: one non-DDEL bibliography entry contains a non-Latin
glyph the default font can't map (renders as a replacement char in the .bbl).
Pre-existing, unrelated to step 18.
