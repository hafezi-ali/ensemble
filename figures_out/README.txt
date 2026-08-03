DDEL-GMM Regenerated Figures
=============================

These figures are generated automatically from hand-editable CSVs in
results/*.csv by running make_figures.py from the repository root:

    python make_figures.py

DO NOT HAND-EDIT any PDF or PNG files in this directory.
Every time results/*.csv changes, regenerate these figures by running
the command above. The renderer reads from results/ ONLY (never from
reproduce/data or manuscript/).

Figure Mapping
==============

Data-driven figures (7):
  - fscore_vs_phi.pdf          F-score vs sampling ratio phi (4 learners)
  - fscore_vs_clusters.pdf     F-score vs number of clusters K (4 learners)
  - boxplot_comparison_v2.pdf  Distribution of F-scores by method & learner
  - fig2_diagnostics.pdf       3-panel diagnostics (aggregation, diversity, oracle)
  - sota_comparison.pdf        State-of-the-art method comparison
  - gmm_vs_kmeans_synthetic.pdf 6-panel synthetic clustering ablation
  - noclustering_comparison.pdf No-clustering baseline comparison

Reviewer-requested placeholder figures (4):
  - concept_drift.pdf          Concept drift simulation (awaiting data)
  - delak_fhdes.pdf            DELAK & FH-DES comparison (awaiting data)
  - nonspherical.pdf           Non-spherical cluster comparison (awaiting data)
  - case_study.pdf             Medical case study (awaiting data)

Data Sources (in results/):
  - table_ensemble_comparison.csv       16 rows: ensemble method × learner combinations
  - table_diversity_cost.csv            5 rows: phi sweep with overlap/disagreement/oracle
  - table_noclustering.csv              7 rows: non-clustering baselines
  - table_sota_comparison.csv           5 rows: state-of-the-art methods
  - figure_noclustering_perfold.csv     10 rows: per-fold F-scores for noclustering comparison
  - figure_sota_perfold.csv             10 rows: per-fold F-scores for SOTA comparison
  - figure_gmm_vs_kmeans_sweep.csv      sweep data for synthetic clustering ablation

All figures output both PDF (for LaTeX \includegraphics) and PNG (300 dpi for preview).

Generated: 2026-07-30
Status: Ready for manuscript integration
