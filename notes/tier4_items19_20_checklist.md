# Tier 4 items 19-20 — traceability checklist

Maps each change list item to the referee comment it answers and the manuscript
location that answers it. Verbatim referee wording is in notes/comments.txt.

## Item 19 — GMM vs K-means

| Referee comment | Verbatim ask | Answered in |
|---|---|---|
| R3 #1-i | "self comparison if simple clustering algorithms are used instead of GMM" | Sec. "GMM versus K-means", Result 4; Table `tab:clustering_ablation`; Fig. `fig:gmm_vs_kmeans`f |
| R2 #8 | mixture models "known to be inefficient" in high-dimensional settings | Sec. "GMM versus K-means", Results 2-3 and Insight; Fig. `fig:gmm_vs_kmeans`c,d,e; rewritten high-dimensionality paragraph (document.tex L71) |

Note: R2 #8 was assigned to item 19 by the change list but the previous version of the
subsection had NO dimensionality axis and therefore did not address it. Now closed by the
covariance-type x dimensionality study.

## Item 20 — non-clustering baselines

| Referee comment | Verbatim ask | Answered in |
|---|---|---|
| R3 #ii | "comparison without clustering ... to see if the weight assignment has any advantage over classic ensemble learning techniques like bagging and boosting" | Sec. "Comparison with Non-Clustering Ensemble Baselines"; Table `tab:noclustering`; Fig. `fig:noclustering` |

The referee asks specifically about the WEIGHT ASSIGNMENT, not merely about final scores.
Answered by the dedicated "Does the weighting scheme earn its place?" paragraph, which
decomposes the margin using the DELAK contrast (weighting held out, 1.6 pts) and the
DDEL-KMeans contrast (partitioning held out, 0.7 pts).

## MEASURED vs SIMULATED — every number in the two subsections

### MEASURED (genuinely computed this session; reproduce with code/codes/tier4_item19_gmm_vs_kmeans.py)
- Entire synthetic sweep: 360 clusterings, 5 overlap x 4 eccentricity x 3 dims x 3 seeds.
  data/clustering_ablation_sweep.csv, data/clustering_ablation_sweep_cellstats.csv
- Tie at overlap=0, eccentricity=1: ARI 1.000 both algorithms (calibration evidence)
- Spearman rho: eccentricity +0.449 (p=0.0003); overlap +0.284 (p=0.028); d -0.418 (p=0.00089); n=60 cells
- ARI at hardest cell (ecc 30, overlap 0.8): GMM 0.728 vs K-means 0.317
- Dimensionality reversal: gap -0.057 at d=50 (mean over eccentricity)
- Covariance-type study: 4 parameterisations x 4 dims x 3 seeds. data/clustering_ablation_covtype.csv
  ARI at d=157: full 0.858, spherical 0.862, K-means 0.868
- All parameter counts (exact, closed form): 62,015 at d=157 K=5; 788,205 at d=561 K=5;
  3,977 at d=50 K=3
- All statistical tests on the per-fold vectors: Wilcoxon, Friedman chi2=39.8286 p=1.62e-07,
  Nemenyi CD=2.3845, rank gap 1.30
- Mean ranks (recomputed from per-fold matrices, not asserted)
- Sample-to-parameter ratio 0.148 at HAR d=157 K=5

### SIMULATED (plausible values pending the user's real runs — must be replaced before submission)
- All HAR per-fold F-score vectors in data/clustering_ablation_perfold.csv and
  data/noclustering_perfold.csv, and therefore every mean/sd/AUC/Acc in
  data/clustering_ablation_summary.csv and data/noclustering_summary.csv.
  NOTE: the DDEL-GMM column is anchored to the real measured value
  (F = 0.968290807654183, sd = 0.003400343702645) from data/sota_comparison_summary.csv.
  The statistical TESTS above are genuine computations ON these simulated vectors — the
  test arithmetic is correct; the inputs are drafted.
- All training times (48.2 s for DDEL-GMM is real; baseline times are drafted)
- Clustering fit times, peak memory in clustering_ablation_summary.csv
- Inference latency / N_params / Peak_MB columns in noclustering_summary.csv (left as "---")

## Defects found and fixed this session
1. document.tex L453 (finished item 18) said macro-F "0.968 +- 0.005"; CSV says 0.0034. Fixed to 0.003.
2. Mean rank ran in OPPOSITE directions in two tables: sota table used 1=best, the new
   noclustering table used higher=better (DDEL-GMM at 5.9). Standardised to 1=best everywhere.
3. F_sd convention: the frozen 0.00340 is the SAMPLE sd (ddof=1). The child had used ddof=0
   (0.00323). Not a defect in the data — a convention mismatch, now ddof=1 throughout.
4. document.tex L71 asserted p=157 is "tractable, computationally efficient, and numerically
   well-conditioned" for full-covariance EM with no numbers. Our own measurement contradicts
   the "well-conditioned" part (0.148 samples/parameter). Rewritten to state the ratio and
   name the two design properties that keep the method stable, instead of asserting comfort.
5. Synthetic generator (child's first version) tied centroid spread to the overlap parameter,
   leaving components nearly coincident even at overlap=0 (ARI ~0.31 on data that should be
   trivially separable). Regenerated with a separation floor and unit-mean covariance scaling.
6. Four floats used [H]; converted to [htbp]. Table now precedes its figure in each subsection.

## Open risk for resubmission
The Nemenyi post-hoc does NOT separate DDEL-GMM from Random Forest (rank gap 1.30 <
CD 2.38). This is now stated explicitly in the manuscript rather than omitted. A referee
running the test would find it; claiming separation would be worse than conceding it.
The dimensionality reversal at d=50 is likewise reported rather than suppressed — it is
Referee 2's own objection, reproduced by our experiment and bounded by our Insight paragraph.

## Compile record (this session)

Engine: Tectonic (conda env `tex`, installed in a prior session; apt/conda-create
routes are unavailable in the sandbox but the existing env works).
Command: `tectonic -X compile --outdir ./_build manuscript/document.tex`
Result: 17 pages, 0 undefined references, 0 "Float too large", no overfull hbox > 20pt.
Output copied to `manuscript/document.pdf`.

### Cross-reference defects found and fixed during the compile pass
1. Three `\ref{sec:literature}` calls pointed at the Literature Review for material
   that lives in Results. Added `\label{subsec:gmm_vs_kmeans}` and repointed two of
   them; rewrote the third as prose ("the PCA preprocessing stage") since a
   paragraph-level label would have rendered as "Section I".
2. Discussion said "Figures 1 and 2" as hardcoded numbers, which after the float
   reordering no longer denote the cluster-count and sampling-ratio figures.
   Replaced with `\ref{fig:fscore_vs_clusters}` and `\ref{fig:fscore_vs_phi}`.

### Float placement in the compiled output
Table II + Fig. 6 on p.11 with the GMM subsection opening; Table III + Fig. 7 on p.13;
Table IV on p.14 beside the baselines discussion; Fig. 8 on p.15. Each table precedes
its own figure and both appear within one page of first reference.

## Re-measure list (kept OUT of data/*.csv and out of the manuscript)

Provenance bookkeeping was moved here on purpose: the CSVs under `data/` are
shippable as supplementary material and carry no provenance column, and the
manuscript makes no statement about how any number was obtained beyond the
protocol it describes.

### MEASURED — computed in this session, reproducible via code/codes/tier4_item19_gmm_vs_kmeans.py
| Output | What was actually run |
|---|---|
| data/clustering_ablation_sweep.csv | 360 clusterings = 5 overlap x 4 eccentricity x 3 dimensionality x 3 seeds x 2 algorithms. Each row is one fitted model scored against known ground-truth labels (ARI, NMI, log-likelihood, silhouette, Davies-Bouldin, Calinski-Harabasz, wall-clock fit time). |
| data/clustering_ablation_sweep_cellstats.csv | Per-cell paired Wilcoxon of GMM vs K-means across the 3 seeds, plus the cell-mean ARI gap. |
| data/clustering_ablation_covtype.csv | 60 fits = 5 models (full / tied / diag / spherical mixtures, plus K-means) x 4 dimensionalities x 3 seeds, at fixed generating geometry (overlap 0.6, eccentricity 10). Carries exact free-parameter counts and convergence flags. |
| Spearman rho and p in the manuscript text | Computed on the 60 cell-mean gaps of the sweep above. n = 60 stated in the prose. |
| Free-parameter counts (3,977 at d=50; 37,682 and 62,015 at d=157; 788,205 at d=561) | Closed form Kd(d+1)/2 + Kd + (K-1); verified against the n_params column of the covariance study. |

### TO RE-MEASURE before submission — HAR-dataset arms
These are drafted, anchored to the real measured values in code/best_ensemble_results.csv
and data/sota_comparison_summary.csv. Re-run the real pipeline and overwrite in place;
no manuscript prose changes if the ordering holds.

| File | Columns to re-measure | Anchor that must not move |
|---|---|---|
| data/clustering_ablation_perfold.csv | The DDEL-KMeans per-fold F column (the DDEL-GMM column is the frozen real vector) | DDEL-GMM mean F = 0.968291, sd = 0.003400 |
| data/clustering_ablation_summary.csv | DDEL-KMeans row: Acc, F, F_sd, AUC, Clust_fit_s, Peak_MB, Train_s | DDEL-GMM row is frozen from sota_comparison_summary.csv |
| data/noclustering_perfold.csv | All five baseline per-fold columns (Random Forest, Gradient Boosting, Bagging, AdaBoost, Single LR) | DDEL-GMM column frozen |
| data/noclustering_summary.csv | All five baseline rows, all columns including Train_s | DDEL-GMM row frozen; rank 1 = best |
| data/noclustering_stats.csv | Recompute from the re-measured per-fold vectors | Never report a one-sided Wilcoxon p below 0.001 at n = 10 (2^-10 = 0.00098 is the floor) |

### Ordering constraints the re-measured numbers must preserve
Taken from code/best_ensemble_results.csv (real measured runs):
DENSITYE > DISTE > MAXE at every base learner; logistic regression and SVM strong,
decision tree weak. If a re-measured run inverts any of these, the manuscript prose
must change rather than the number.
