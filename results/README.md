# Results Layer — Hand-Editable CSV Directory

This directory contains the hand-editable CSV files that drive table and figure regeneration in the DDEL-GMM manuscript.

## What is This?

Instead of hardcoding table bodies in document.tex, all numeric results are stored here as CSV files. When numbers change (e.g., from re-running experiments or filling in new results), you edit the CSV, and downstream renderers regenerate the LaTeX tables and figures automatically.

## CSV Files (13 total)

**Six tables (filled from manuscript):**
- `table_selection_rule.csv` — instance-selection rule comparison (phi sweep)
- `table_ensemble_comparison.csv` — four ensemble methods × four base learners
- `table_diversity_cost.csv` — subset overlap, disagreement, oracle, cost vs phi
- `table_sota_comparison.csv` — DDEL-GMM vs published baselines (META-DES, DELAK, KNORA)
- `table_clustering_ablation.csv` — DDEL-GMM (GMM) vs DDEL-KMeans
- `table_noclustering.csv` — DDEL-GMM vs classic ensemble methods

**Two figures (partial fill + references):**
- `figure_fscore_vs_phi.csv` — F-score vs sampling ratio (partial: 3 LR values pre-filled; SVM/KNN/DT empty)
- `figure_fscore_vs_clusters.csv` — F-score vs number of clusters K (all empty; re-run sweep in Colab)
- Other figures (boxplot, diagnostics, sota, gmm_vs_kmeans, noclustering) are **references** to tables above

**Five reviewer-requested experiments (empty templates):**
- `table_delak_fhdes.csv` — DELAK vs FH-DES head-to-head
- `table_nonspherical.csv` — K-means vs GMM on non-spherical/overlapping synthetic data
- `table_bagging_boosting.csv` — classic bagging/boosting extension
- `figure_concept_drift.csv` — simulated concept drift over 10 time windows
- `table_case_study.csv` — real-world medical case study

## How to Use

1. **To update existing results**: Open a filled CSV (e.g., `table_ensemble_comparison.csv`), edit a numeric cell, save as CSV (keep no extra columns or comments).
2. **To fill in new results**: Open an empty-template CSV (e.g., `figure_concept_drift.csv`), type numbers into the metric columns, leave row-ID columns (method, learner, etc.) unchanged.
3. **To run the pipeline** (coming in Phase 2): `python make_results.py` will read these CSVs and regenerate all tables and figures in LaTeX format.

## Rules

- **Empty cells = missing**: Use empty string (not 0, "NA", "TODO") for values you'll fill later.
- **No LaTeX in cells**: Numbers only; renderers add formatting.
- **Cite keys in dedicated column**: Store "guo_dynamic_2021" (not \cite{guo_dynamic_2021}).
- **One row per method/dataset/sweep-point**: Keep rows flat and tidy.
- **Column names are lowercase snake_case**: Never edit column names; they are part of the contract with renderers.

## Schema Documentation

See `SCHEMA.md` for the full contract:
- Column definitions, units, precision rules
- Merit direction (higher_is_better vs. lower_is_better)
- Which columns are derived and never hand-typed (rank, bold, p_value aggregates, etc.)
- Formatting rules (p-value display, delta signs, bold-best rules)
- Provenance (where each value came from in the original Colab output)

## What Comes Next

- **Phase 1** (parallel sub-agents): Build `make_tables.py` and `make_figures.py` against this schema.
- **Phase 2**: Write `make_results.py` driver, patch document.tex to `\input` generated tables, document the workflow in `RESULTS_WORKFLOW.md`.

The CSVs are now the single source of truth. All renderers and the document will read from here.
