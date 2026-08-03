# Results Data Schema

## Purpose

This directory contains hand-editable CSV files that drive table and figure generation in the DDEL-GMM manuscript (IEEE TETCI resubmission). Each CSV represents one experimental result; renderers will read these files and regenerate document.tex tables and figures without manual cell editing.

## Global Conventions

1. **Empty cells = missing values**: Use empty string (not 0, NA, "TODO", "MISSING") to indicate missing data that the user will fill from Colab output.
2. **No LaTeX in data cells**: Column values are plain numeric or text; LaTeX (mathbf, cite{}, etc.) is applied by renderers.
3. **Citation keys in dedicated column**: Where a method name carries a reference, store the bare cite key (e.g., "guo_dynamic_2021") in a `cite_key` column; renderers will format as \cite{}.
4. **Derived columns never hand-typed**: Bold, rank, wins, delta, mean_rank are computed downstream; CSVs contain only measured/reported values.
5. **No comments in rows**: Use header row + notes column (optional) instead.

## CSV Files

### Tables from Manuscript (Filled)

#### table_selection_rule.csv
- **Drives**: Table 1 (tab:selection_rule), line ~280 in document.tex
- **Manuscript float**: \ref{tab:selection_rule}
- **Dimensions**: 5 rows (phi sweep: 0.2, 0.4, 0.5, 0.6, 0.9) × 6 columns
- **Columns**:
  - `phi` (float, 0.0-1.0): sampling ratio
  - `f1_distance` (float, 4 decimals): Macro F₁ using distance-based ranking to μᵢ
  - `f1_responsibility` (float, 4 decimals): Macro F₁ using responsibility-based ranking γᵢ(x)
  - `disagreement_distance` (float, 3 decimals): base-learner pairwise disagreement with distance rule
  - `disagreement_responsibility` (float, 3 decimals): base-learner pairwise disagreement with responsibility rule
  - `overlap` (float, 3 decimals): mean pairwise Jaccard index of training subsets
- **Merit direction**: Higher F₁ is better, lower disagreement favors ensemble hypothesis, overlap is informational
- **Precision as printed**: 4 decimals (F₁), 3 decimals (disagreement, overlap)
- **Row order**: Ascending phi (0.2 → 0.9)
- **Status**: FILLED (extracted from document.tex lines 280–290)
- **Provenance**: Manuscript Table 1; no external CSV source (first author computed for configuration sweep)

#### table_ensemble_comparison.csv
- **Drives**: Table 2 (tab:ensemble_comparison), line ~397 in document.tex
- **Manuscript float**: \ref{tab:ensemble_comparison}
- **Dimensions**: 16 rows (4 ensemble methods × 4 base learners) × 5 columns
- **Columns**:
  - `ensemble_method` (string): DensityE, DistE, AvgE, MaxE
  - `base_learner` (string): lr, svm, knn, dt
  - `mean_score` (float, 3 decimals): mean macro F₁ over 10-fold CV
  - `std_score` (float, 3 decimals): standard deviation across folds
  - `max_score` (float, 3 decimals): best fold macro F₁
- **Merit direction**: higher_is_better for mean_score, max_score; lower_is_better for std_score
- **Precision**: 3 decimals throughout
- **Row order**: Method outer loop (DensityE, DistE, AvgE, MaxE), learner inner loop (lr, svm, knn, dt)
- **Status**: FILLED (extracted from document.tex lines 400–431)
- **Provenance**: Manuscript Table 2; corresponds to reproduce/data/best_ensemble_results.csv (summary only)

#### table_diversity_cost.csv
- **Drives**: Table 3 (tab:diversity_cost), line ~613 in document.tex
- **Manuscript float**: \ref{tab:diversity_cost}
- **Dimensions**: 5 rows (phi sweep: 0.2, 0.4, 0.5, 0.6, 0.9) × 7 columns
- **Columns**:
  - `phi` (float): sampling ratio
  - `overlap` (float, 3 decimals): mean pairwise Jaccard index of K=6 training subsets
  - `disagreement` (float, 3 decimals): mean pairwise fraction of test instances on which learners differ
  - `oracle` (float, 4 decimals): oracle accuracy (omniscient per-query selector)
  - `macro_f1` (float, 4 decimals): measured DDEL-GMM macro F₁ (DensityE aggregation)
  - `delta_single` (float, 4 decimals signed): F₁ improvement over single logistic-regression baseline
  - `fit_seconds` (integer): wall-clock training time for K=6 learners, first fold
- **Merit direction**: higher_is_better for oracle, macro_f1, delta_single; lower_is_better for fit_seconds; overlap/disagreement are analysis metrics
- **Precision**: 3 decimals (overlap, disagreement), 4 decimals (oracle, macro_f1, delta_single)
- **Special formatting**: delta_single printed with explicit sign (e.g., "+0.0040", "-0.0141")
- **Row order**: Ascending phi
- **Status**: FILLED (extracted from document.tex lines 613–622)
- **Provenance**: Manuscript Table 3; source is Section 4.2 / reproduce/data/diversity_diagnostic.csv (overlap, disagreement columns); oracle and F₁ computed in Colab experiment

#### table_sota_comparison.csv
- **Drives**: Table 4 (tab:sota_comparison), line ~643 in document.tex
- **Manuscript float**: \ref{tab:sota_comparison}
- **Dimensions**: 5 rows (DDEL-GMM, META-DES, DELAK, KNORA-U, KNORA-E) × 7 columns
- **Columns**:
  - `method` (string): method name; DDEL-GMM is the row with p_value = "---"
  - `accuracy` (float, 3 decimals): overall accuracy
  - `mean_f_score` (float, 3 decimals): macro F₁
  - `auc` (float, 3 decimals): area under ROC curve
  - `rank` (float, 1 decimal): mean Friedman rank across 10 folds
  - `p_value` (string or float): one-sided Wilcoxon signed-rank p-value vs. DDEL-GMM; "---" for DDEL-GMM row
  - `time_seconds` (float, 1 decimal): single-run training time
- **Cite keys**: `cite_key` column added in Phase 1 (renderer): METHOD → CITATION_KEY mapping:
  - DDEL-GMM → (empty)
  - META-DES → cruz_meta-oracle_2017
  - DELAK → guo_dynamic_2021
  - KNORA-U → ko_dynamic_2008
  - KNORA-E → ko_dynamic_2008
- **Merit direction**: higher_is_better for accuracy, mean_f_score, auc; lower_is_better for rank, p_value (smaller p = stronger evidence), time_seconds
- **Precision**: 3 decimals for accuracy/F₁/AUC, 1 decimal for rank/time, 3 decimals for p_value
- **Bold rule**: Best (highest) accuracy, F₁, AUC in each column; p_value = "---" never bolded
- **Row order**: DDEL-GMM first, then others in rank order (ascending rank number)
- **Status**: FILLED (extracted from document.tex lines 643–655)
- **Provenance**: Manuscript Table 4; source is reproduce/data/sota_perfold_fscores.csv (per-fold F₁ scores, aggregated and stats computed in Colab)

#### table_clustering_ablation.csv
- **Drives**: Table 5 (tab:clustering_ablation), line ~689 in document.tex
- **Manuscript float**: \ref{tab:clustering_ablation}
- **Dimensions**: 2 rows (DDEL-GMM, DDEL-KMeans) × 8 columns
- **Columns**:
  - `variant` (string): DDEL-GMM, DDEL-KMeans
  - `clustering` (string): GMM, K-means
  - `accuracy` (float, 3 decimals)
  - `mean_f_score` (float, 3 decimals)
  - `auc` (float, 3 decimals)
  - `rank` (float, 1 decimal): Friedman mean rank
  - `covariance_params` (integer): number of free parameters in clustering model at K=5, d=157
  - `ari` (float, 3 decimals): Adjusted Rand Index on synthetic data (hardest config: eccentricity 30, overlap 0.8)
- **Merit direction**: higher_is_better for accuracy, mean_f_score, auc, ari; lower_is_better for rank
- **Precision**: 3 decimals for F₁/AUC/ARI, 1 decimal for rank, no decimal for params (integer)
- **Row order**: DDEL-GMM first, DDEL-KMeans second
- **Status**: FILLED (extracted from document.tex lines 689–700)
- **Provenance**: Manuscript Table 5; accuracy/F₁/AUC from reproduce/data/clustering_ablation_summary.csv (HAR evaluation); ARI from reproduce/data/clustering_ablation_sweep.csv (synthetic experiment)

#### table_noclustering.csv
- **Drives**: Table 6 (tab:noclustering), line ~731 in document.tex
- **Manuscript float**: \ref{tab:noclustering}
- **Dimensions**: 7 rows (7 methods) × 8 columns
- **Columns**:
  - `method` (string): method name (may include cite key inline or separate)
  - `accuracy` (float, 4 decimals)
  - `mean_f_score` (float, 4 decimals)
  - `std_dev` (float, 4 decimals): standard deviation across folds
  - `auc` (float, 4 decimals)
  - `rank` (float, 2 decimals): Friedman mean rank (can be fractional)
  - `p_value` (string or float): two-sided Wilcoxon signed-rank p-value; "---" for DDEL-GMM
  - `time_seconds` (float, 1 decimal): per-fold wall-clock time
  - `cite_key` (string): added in Phase 1 (renderer); maps METHOD → CITATION_KEY:
    - DDEL-GMM → (empty)
    - Bagging (LR) → breiman_bagging_1996
    - Single LR → (empty)
    - Single SVM → (empty)
    - Gradient Boosting → friedman_greedy_2001
    - Random Forest → breiman_random_2001
    - AdaBoost → freund_decision-theoretic_1997
- **Merit direction**: higher_is_better for accuracy, mean_f_score, auc; lower_is_better for std_dev, rank, time
- **Precision**: 4 decimals for accuracy/F₁/std/AUC, 2 decimals for rank, 1 decimal for time, 3 decimals for p_value
- **Bold rule**: Best value in each column; "---" for p_value never bolded
- **Row order**: DDEL-GMM first, then others in ascending rank order
- **Special note**: Bagging (LR), Single LR, Single SVM are statistically indistinguishable from DDEL-GMM (p > 0.05); AdaBoost, Random Forest, Gradient Boosting are separated at p < 0.05
- **Status**: FILLED (extracted from document.tex lines 731–748)
- **Provenance**: Manuscript Table 6; source is reproduce/data/noclustering_perfold.csv (per-fold F₁ and per-method stats, nested CV results in reproduce/data/_partial_nested.csv); note discrepancy: noclustering_summary_MEASURED.csv exists but manuscript uses unnested results from noclustering_perfold.csv

### Figure Data (Partial Fill & References)

#### figure_fscore_vs_phi.csv
- **Drives**: Figure 2 (fig:fscore_vs_phi), line ~382 in document.tex
- **Dimensions**: 9 rows (phi sweep: 0.1–0.9) × 5 columns
- **Columns**:
  - `phi` (float, 1 decimal): sampling ratio 0.1 to 0.9
  - `lr_fscore` (float, 4 decimals): logistic regression macro F₁
  - `svm_fscore` (float, 4 decimals): SVM macro F₁
  - `knn_fscore` (float, 4 decimals): KNN macro F₁
  - `dt_fscore` (float, 4 decimals): decision tree macro F₁
- **Pre-filled values** (from manuscript text, line ~522):
  - phi=0.4, lr=0.9719
  - phi=0.5, lr=0.9733 (maximum)
  - phi=0.9, lr=0.9726
  - All other cells: EMPTY (user fills from Colab)
- **Merit direction**: higher_is_better
- **Precision**: 4 decimals
- **Row order**: Ascending phi
- **Status**: PARTIAL (pre-filled with 3 quoted values; rest empty)
- **Provenance**: The three quoted LR values are from Colab experiment (manuscript prose, line 522); they do not exist in any stored CSV. SVM/KNN/DT columns are empty because the Colab sweep output was not saved. User must re-run the phi sweep in Colab and fill all missing cells.

#### figure_fscore_vs_clusters.csv
- **Drives**: Figure 3 (fig:fscore_vs_clusters), line ~538 in document.tex
- **Dimensions**: 9 rows (K = 2–10) × 5 columns
- **Columns**:
  - `K` (integer): number of clusters
  - `lr_fscore` (float, 4 decimals)
  - `svm_fscore` (float, 4 decimals)
  - `knn_fscore` (float, 4 decimals)
  - `dt_fscore` (float, 4 decimals)
- **Status**: EMPTY_SLOT (no quoted values exist in manuscript)
- **Provenance**: No stored CSV data. The original .eps file dates from Sep 2024 Colab run; sweep results were not captured. User must re-run K sweep in Colab.

#### figure_boxplot_comparison_v2.csv
- **Drives**: Figure 4 (fig:boxplot_comparison), line ~522 in document.tex
- **Data source**: **Reference table_ensemble_comparison.csv** — renderer extracts per-fold distributions from ensemble comparison results
- **Panels**: Distribution of macro F₁ by ensemble method and base learner (10 folds per method-learner pair)
- **Status**: DATA_DRIVEN (computed from table_ensemble_comparison.csv; no separate CSV needed)

#### figure_diagnostics.csv
- **Drives**: Figure 5 (fig:diagnostics), line ~545 in document.tex (three panels a, b, c)
- **Data sources**:
  - Panel (a): table_ensemble_comparison.csv
  - Panel (b): table_diversity_cost.csv
  - Panel (c): table_diversity_cost.csv (oracle column)
- **Status**: DATA_DRIVEN (computed from existing tables)

#### figure_sota_comparison.csv
- **Drives**: Figure 6 (fig:sota_comparison), line ~668 in document.tex
- **Data source**: **Reference table_sota_comparison.csv**
- **Status**: DATA_DRIVEN (visualization of sota comparison table with error bars and significance markers)

#### figure_gmm_vs_kmeans_synthetic.csv
- **Drives**: Figure 7 (fig:gmm_vs_kmeans), line ~708 in document.tex (six panels a–f)
- **Data sources**:
  - Panels (a)–(e): reproduce/data/clustering_ablation_sweep.csv (synthetic mixture experiments across dimensionality, eccentricity, overlap)
  - Panel (f): reproduce/data/clustering_ablation_perfold.csv or Table 5 embedded (HAR DDEL-GMM vs DDEL-KMeans per-fold F₁)
- **Status**: DATA_DRIVEN (uses existing reproduce/data CSVs)

#### figure_noclustering_comparison.csv
- **Drives**: Figure 8 (fig:noclustering), line ~760 in document.tex (two panels a, b)
- **Data source**: **Reference table_noclustering.csv**
- **Status**: DATA_DRIVEN (visualization with error bars and Nemenyi critical difference)

### Reviewer-Requested Empty Slots (Unfilled)

These CSVs exist but contain only headers and empty metric columns. The author will fill them after running new experiments.

#### table_delak_fhdes.csv
- **Purpose**: Head-to-head comparison of DDEL-GMM vs. DELAK vs. FH-DES (Ref 1, Ref 2)
- **Dimensions**: 3 rows (3 methods) × 7 columns
- **Columns**: method, accuracy, mean_f_score, auc, rank, p_value, time_seconds
- **Status**: EMPTY_SLOT (will be filled after new experiment)
- **Provenance**: New experiment (not in current paper)

#### table_nonspherical.csv
- **Purpose**: Empirical validation of GMM advantage on non-spherical/overlapping synthetic data (Ref 2 comment)
- **Dimensions**: 8 rows (2 clustering types × 4 geometry types) × 5 columns
- **Columns**: clustering_type, data_geometry, accuracy, ari, silhouette
- **Geometry types**: spherical, overlapping, non-spherical, non-spherical+overlapping
- **Status**: EMPTY_SLOT
- **Provenance**: New experiment (extends existing synthetic comparison in Table 5, panel of fig:gmm_vs_kmeans)

#### table_bagging_boosting.csv
- **Purpose**: Comparison of DDEL-GMM against classic bagging and boosting with various base learners (Ref 3 comment)
- **Dimensions**: 11 rows (bagging 4 learners + boosting 4 learners + RF + AdaBoost + DDEL-GMM) × 6 columns
- **Columns**: method, base_learner, accuracy, mean_f_score, std_dev, auc, time_seconds
- **Status**: EMPTY_SLOT
- **Provenance**: New experiment (extends Table 6 / fig:noclustering)

#### figure_concept_drift.csv
- **Purpose**: Simulated concept drift: performance of DDEL-GMM, Single LR, DELAK across 10 time windows (Ref 2 comment)
- **Dimensions**: 10 rows (drift points / time windows) × 7 columns
- **Columns**: drift_point, ddel_accuracy, ddel_f_score, single_lr_accuracy, single_lr_f_score, delak_accuracy, delak_f_score
- **Status**: EMPTY_SLOT
- **Provenance**: New experiment (concept drift simulation not in current paper)

#### table_case_study.csv
- **Purpose**: Real-world medical case study (Ref 3 comment)
- **Dimensions**: 5 rows (5 methods on medical dataset) × 8 columns
- **Columns**: method, dataset, accuracy, mean_f_score, sensitivity, specificity, auc, p_value, time_seconds
- **Status**: EMPTY_SLOT
- **Provenance**: New experiment (case study not in current paper)

## Implementation Notes for Renderers

1. **Skip empty tables**: If a CSV has no filled metric columns (all rows empty except row IDs), skip rendering that table/figure and log a warning.
2. **Merge bold/rank rules**: Best values per column are bolded. Rank and p-value columns are not themselves bolded.
3. **Cite key handling**: If a method name contains a cite key (detected as underscore-separated words), convert bare cite key to \cite{key}. Example: "guo_dynamic_2021" → \cite{guo_dynamic_2021}.
4. **Delta columns**: delta_single in table_diversity_cost must be printed with explicit sign (+ or −).
5. **P-value formatting**:
   - "---" (three hyphens) for the method's own row (no self-comparison)
   - Floating-point values printed to 3 decimals (e.g., 0.019, 0.001)
   - Special case: smallest attainable p at 10 folds is 0.001 (one-sided) or 0.002 (two-sided)
6. **Cross-table consistency**: A value appearing in multiple CSVs (e.g., DDEL-GMM mean F₁ = 0.968 in both sota_comparison and noclustering) must be kept in sync.

#### figure_boxplot_perfold.csv (EMPTY SLOT - Phase 1 Regression Fix)
- **Drives**: Figure 3 (fig:boxplot_comparison_v2) per-fold data and flier circles
- **Manuscript float**: \\ref{fig:boxplot_comparison_v2}
- **Dimensions**: 10 rows per method/learner combination = 70 rows when filled (7 method/learner × 10 folds)
- **Columns**:
  - `method` (string): DensityE, DistE, Single Model (3 methods; empty slot uses DensityE only in caption)
  - `learner` (string): lr, svm, knn, single_svm (4 learners)
  - `fold` (int, 0-9): Outer 10-fold CV fold index
  - `fscore` (float, 4 decimals): Weighted macro F₁-score for this fold
- **Merit direction**: higher_is_better
- **Precision**: 4 decimals
- **Row order**: Method outer loop, learner inner loop, fold inner-most
- **Status**: EMPTY_SLOT
- **Provenance**: Colab Main_Thp.ipynb cell 12, outer 10-fold cross-validation per-fold scores
- **Renderer behavior**:
  1. **If filled**: Compute quartiles, median, whiskers, and TRUE flier circles from raw per-fold data via ax.boxplot()
  2. **If empty (current)**: Use precomputed 5-number summaries from figure_boxplot_stats.csv; flier circles will NOT appear
- **Caption dependencies**: The published caption states "circles are folds beyond 1.5×IQR" and claims DensityE "produces no low-side outlier folds". These claims cannot be verified from 5-number summaries alone and MUST be supported by per-fold data. Until this CSV is filled, the caption sentences about outliers are unsupported and the author must either (a) paste per-fold scores here or (b) trim those sentences from the caption.

---

## Known Discrepancies (Author Must Resolve)

- **noclustering_summary_MEASURED.csv vs. noclustering_perfold.csv**: Two versions exist. The paper uses unnested results from noclustering_perfold.csv (Table 6). The _MEASURED variant may reflect a different CV fold seed or measurement protocol. Clarify with author.
- **clustering_ablation_summary.csv provenance**: CSV header states "Provenance: HAR SIMULATED" but the manuscript reports it as measured results. Confirm with author whether this is synthetic or real HAR data.
- **Fig 1 pipeline, training_phase_diagram, generalization_phase_diagram**: Hand-drawn schematics (fig:overview, fig:training_phase_diagram, fig:generalization_phase_diagram). No CSV; do not edit.

## File Layout & Testing

Each CSV file includes:
- Real header row with column names (lowercase snake_case, no units in name)
- Data rows aligned to header
- No comment rows embedded

Test: Load each CSV in pandas/R, verify column count and data types, check for NaN patterns consistent with status (FILLED, PARTIAL, EMPTY_SLOT).

---

**Schema version**: Phase 0 contract  
**Last updated**: 2026-07-30  
**Status**: FROZEN (ready for Phase 1 renderer development)
