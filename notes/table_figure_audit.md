# Audit: which tables and figures still need rerunning

Every table and figure traced to its data source. Three categories: measured on real
data (keep), measured on synthetic data by design (keep), and never measured (rerun).

## MEASURED ON REAL DATA - no rerun needed

| Item | Source | Status |
|---|---|---|
| Table II (ensemble methods x base learners) | code/best_ensemble_results.csv | Your own GPU runs. Verified: densitye/lr = 0.973 reproduces exactly. |
| Fig 3 fscore_vs_clusters | code/fscore_vs_clusters.eps | Your own output. |
| Fig 4 fscore_vs_phi | code/fscore_vs_phi.eps | Your own output. |
| Fig 5 boxplot_comparison | code/boxplot_comparison.eps | Your own output. |
| Table IV (non-clustering baselines) | data/noclustering_*.csv | Measured this session, nested selection. |
| Fig 8 noclustering_comparison | data/noclustering_perfold.csv | Regenerated this session. |

## MEASURED ON SYNTHETIC DATA - correct by design, no rerun

| Item | Source | Status |
|---|---|---|
| Fig 7 gmm_vs_kmeans_synthetic | data/clustering_ablation_sweep.csv | Genuinely measured. Synthetic IS the point: controlled eccentricity/overlap/dimension. |

## NEVER MEASURED - these are the ones that need reruns

### Table III + Fig 6: state-of-the-art comparison (META-DES, DELAK, KNORA-U, KNORA-E)
notes/step18_rebuttal_note.md line 43 states plainly:
  "These are placeholder/simulated results per prompt.txt and are to be replaced
   by measured runs before submission."
There is NO code anywhere in the repo that computes them - grep for META-DES, KNORA,
or deslib returns nothing. The numbers (DDEL-GMM 0.9683 rank 1.3, META-DES 0.9593,
DELAK 0.9522, KNORA-U 0.9479, KNORA-E 0.9460) were written, not measured.

THIS IS THE HIGHEST-PRIORITY ITEM IN THE PAPER. All three referees demanded an
empirical DELAK comparison; it is the single most-cited gap in the reviews. The table
that answers them is currently fabricated, and the rebuttal note says so in writing.

Measurable: DESlib 0.3.7 installs cleanly and provides META-DES, KNORA-U, KNORA-E.
DELAK needs implementing (K-means DES, Guo et al. 2021) - the DDEL-KMeans variant
already written for Table V is close to it.

### Table V: clustering ablation, HAR arm
data/clustering_ablation_summary.csv carries its own Provenance column reading
"HAR SIMULATED / synthetic MEASURED". The DDEL-GMM 0.9683 vs DDEL-KMeans 0.9612 HAR
row - the 1.6-point attribution to the GMM choice - is simulated. The synthetic ARI
sweep behind it is real.

This is the second referee-facing claim resting on unmeasured numbers, and Table IV's
Insight paragraph currently cites the ablation as where the contribution lives.

## Cross-cutting issue already known
Table I/II come from base_train.py, which uses a single 80/20 split and reports the
best of a 45-config grid scored on that one test set. Optimism measured at +0.0014 for
3 configs; larger for 45. Table IV is now immune; Tables I/II are not.

## Recommendation, in order
1. Measure Table III + Fig 6 (DES baselines). Referee-critical, currently fabricated.
2. Measure Table V HAR arm (DDEL-KMeans on real HAR). Referee-critical, currently simulated.
3. Decide on Table I/II protocol: rerun nested, or disclose the selection protocol.
