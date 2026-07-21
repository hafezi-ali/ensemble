# Graph Report - .  (2026-07-22)

## Corpus Check
- 12 files · ~74,680 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 86 nodes · 120 edges · 9 communities (8 shown, 1 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.8)
- Token cost: 159,825 input · 0 output

## Community Hubs (Navigation)
- Data Preprocessing & Training
- Ensemble Model Architecture
- Boxplot Comparison (v2)
- Boxplot Comparison (v1)
- Base Learner Ablation Charts
- F-score vs Phi Ratio
- F-score vs Cluster Count
- PyTorch Dataset Wrapper

## God Nodes (most connected - your core abstractions)
1. `Boxplot: F-score by Ensemble Method and Base Learner` - 8 edges
2. `F-score vs Number of Clusters (plot_n_clusters.pdf)` - 7 edges
3. `F-score vs Sampling Ratio (plot_phi_ratio.pdf)` - 7 edges
4. `Boxplot Comparison of Ensemble Methods by F-score` - 7 edges
5. `Base Learners (lr, svm, knn, dt)` - 6 edges
6. `F-score vs Phi Ratio (Base Learner Comparison Chart)` - 6 edges
7. `MyDataset` - 5 edges
8. `F-score vs Number of Clusters (Base Learner Comparison)` - 5 edges
9. `resampling()` - 4 edges
10. `generate_cols_IMU()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `resampling_grid()` --calls--> `resampling()`  [EXTRACTED]
  codes/base_train.py → Funcs/Functions.py
- `F-score vs Number of Clusters (plot_n_clusters.pdf)` --semantically_similar_to--> `F-score vs Sampling Ratio (plot_phi_ratio.pdf)`  [INFERRED] [semantically similar]
  Plots/plot_n_clusters.pdf → Plots/plot_phi_ratio.pdf
- `Number of Clusters (hyperparameter)` --semantically_similar_to--> `Sampling Ratio / Phi Ratio (hyperparameter)`  [INFERRED] [semantically similar]
  Plots/plot_n_clusters.pdf → Plots/plot_phi_ratio.pdf
- `F-score vs Sampling Ratio (plot_phi_ratio.pdf)` --references--> `Decision Tree (dt) Base Learner`  [EXTRACTED]
  Plots/plot_phi_ratio.pdf → Plots/plot_n_clusters.pdf
- `F-score vs Sampling Ratio (plot_phi_ratio.pdf)` --references--> `F-score Evaluation Metric`  [EXTRACTED]
  Plots/plot_phi_ratio.pdf → Plots/plot_n_clusters.pdf

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Base learners compared by F-score across cluster counts** — concept_svm, concept_logistic_regression, concept_knn, concept_decision_tree, concept_number_of_clusters, concept_fscore [INFERRED 0.85]
- **Base learners compared by F-score across sampling ratios** — concept_svm, concept_logistic_regression, concept_knn, concept_decision_tree, concept_sampling_ratio, concept_fscore [INFERRED 0.85]
- **Ensemble Method F-score Comparison Experiment** — boxplot_comparison_densitye, boxplot_comparison_avge, boxplot_comparison_maxe, boxplot_comparison_single_svm [INFERRED 0.85]
- **Stable, High-Performing Classification Methods** — boxplot_comparison_1_densitye, boxplot_comparison_1_diste, boxplot_comparison_1_single_svm [INFERRED 0.80]
- **Base Learner F-score Sensitivity to Phi Ratio** — fscore_vs_phi, fscore_vs_phi_svm, fscore_vs_phi_lr, fscore_vs_phi_knn, fscore_vs_phi_dt, fscore_vs_phi_phi_ratio [INFERRED 0.85]

## Communities (9 total, 1 thin omitted)

### Community 0 - "Data Preprocessing & Training"
Cohesion: 0.15
Nodes (14): resampling_grid(), check_missing(), fetch_null(), generate_cols_IMU(), generate_four_IMU(), generate_three_IMU(), handle_outlier(), load_IMU() (+6 more)

### Community 1 - "Ensemble Model Architecture"
Cohesion: 0.17
Nodes (9): confusion_mn(), Ensemble, f1_tuned_model(), grid_train_base_models(), MainModel, model_performance_report(), train(), train_main_model() (+1 more)

### Community 2 - "Boxplot Comparison (v2)"
Cohesion: 0.50
Nodes (9): Boxplot Comparison of Ensemble Methods by F-score, Average Ensemble Method (avge), Base Learners (lr, svm, knn, dt), Density-based Ensemble Method (densitye), Distance-based Ensemble Method (diste), F-score (%) Metric, Max Ensemble Method (maxe), Single SVM Baseline (+1 more)

### Community 3 - "Boxplot Comparison (v1)"
Cohesion: 0.28
Nodes (9): Average Ensemble Method (avge), Boxplot: F-score by Ensemble Method and Base Learner, Density Ensemble Method (densitye), Decision Tree Base Learner (dt), KNN Base Learner (knn), Logistic Regression Base Learner (lr), Max Ensemble Method (maxe), Single SVM Baseline (+1 more)

### Community 4 - "Base Learner Ablation Charts"
Cohesion: 0.39
Nodes (9): F-score vs Number of Clusters (plot_n_clusters.pdf), F-score vs Sampling Ratio (plot_phi_ratio.pdf), Decision Tree (dt) Base Learner, F-score Evaluation Metric, K-Nearest Neighbors (knn) Base Learner, Logistic Regression (lr) Base Learner, Number of Clusters (hyperparameter), Sampling Ratio / Phi Ratio (hyperparameter) (+1 more)

### Community 5 - "F-score vs Phi Ratio"
Cohesion: 0.38
Nodes (7): F-score vs Phi Ratio (Base Learner Comparison Chart), Decision Tree Base Learner (F-score vs Phi Ratio series), F-score (%) Metric (y-axis), KNN Base Learner (F-score vs Phi Ratio series), Logistic Regression Base Learner (F-score vs Phi Ratio series), Phi Ratio (experiment parameter, x-axis), SVM Base Learner (F-score vs Phi Ratio series)

### Community 6 - "F-score vs Cluster Count"
Cohesion: 0.33
Nodes (6): Decision Tree Base Learner, KNN Base Learner, Logistic Regression Base Learner, SVM Base Learner, Clustering-based Ensemble Sensitivity Experiment, F-score vs Number of Clusters (Base Learner Comparison)

## Knowledge Gaps
- **13 isolated node(s):** `Single SVM Baseline`, `Logistic Regression Base Learner (lr)`, `SVM Base Learner (svm)`, `KNN Base Learner (knn)`, `Decision Tree Base Learner (dt)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MyDataset` connect `PyTorch Dataset Wrapper` to `Data Preprocessing & Training`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **What connects `Single SVM Baseline`, `Logistic Regression Base Learner (lr)`, `SVM Base Learner (svm)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Data Preprocessing & Training` be split into smaller, more focused modules?**
  _Cohesion score 0.14761904761904762 - nodes in this community are weakly interconnected._