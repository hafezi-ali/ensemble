# DDEL-GMM — Complete Pipeline Specification

How the model works end to end, traced from the source in `code/`.
Every statement below is read off the code, not inferred from the manuscript.

## 0. The two-stage split (and what "phi" means in each)

The pipeline is split across **two scripts that run at different times and do
different jobs**:

| | `codes/base_train.py` | `codes/evaluation.py` |
|---|---|---|
| Job | **Hyperparameter search** per cluster | **Fit + measure** on CV folds |
| Data split | one 80/20 `train_test_split` | `RepeatedKFold(5x4)` = 20 folds |
| Grid | `phi` 0.1..0.9 x `n_c` 2..6 (45 configs) | `phi` 0.1..0.9 x `n_c` 2..3 (as committed) |
| What it emits | tuned **hyperparameters** per cluster | per-fold F-scores, the reported numbers |
| Output | `Results/df_single_resampling_res_grid_*.pkl` | `Results/finall_res*.pkl` |

**What carries over between them is only hyperparameters, not fitted weights.**
`evaluation.py` retrieves the tuned estimator objects and immediately refits
them on the fold's own subsets (line 191):

```python
single_model = copy.deepcopy(signed_base_classifires_dict[single_model_name][l])
signed_base_classifires_dict[single_model_name][l] = single_model.fit(x_re_cluster, y_re_clusters)
```

So the two `phi` play genuinely different roles: in Stage A `phi` shapes the
subsets that `GridSearchCV` tunes on; in Stage B `phi` shapes the subsets the
base learners are actually **fitted** on and that the ensemble predicts from.

**One caveat on "completely independent".** In the code as committed the two
values are *locked to each other* by the lookup at line 158:

```python
df_out = df_single_resampling_res_grid[
    (df_single_resampling_res_grid.phi == phi) & (df_single_resampling_res_grid.n_c == n_c)]
```

Evaluating at `phi = 0.5` retrieves the hyperparameters that were tuned on
Stage A's `phi = 0.5` subsets. The roles are independent; the *values* are
tied by this line. To make them truly independent you would index `df_out`
with a separate `phi_train` variable.

---

## 1. Data

`Data/UCI_HAR_Dataset/data_uci_handled.csv` — UCI HAR, 561 engineered
time/frequency features from waist-mounted smartphone IMU, 6 activity classes.

```python
uci['Activity'] = uci['Activity'] + 1              # shift labels to 1..6
X = uci.drop(['Activity','ActivityName','subject'], axis=1)   # 561 features
y = uci['ActivityName']                                        # string labels
```

The `subject` column is dropped, so splits are **record-wise, not
subject-wise** — the same participant can appear in train and test.

## 2. Preprocessing — `Funcs/Functions.py :: single_preprocessing`

Fitted **inside** each training split, applied to test:

1. `StandardScaler(with_mean=True, with_std=True)` fit on `X_train` only.
2. PCA. With `n_components='auto'`: fit full PCA, take the cumulative
   explained-variance curve, choose the smallest number of components reaching
   **0.95** variance. On HAR this yields **157 components**.
3. Stage B pins `n_components` to Stage A's component count so the two stages
   share a feature space of identical width.

## 3. Partitioning — where `phi` acts

### 3.1 Clustering — `Functions.py :: sampling`

Dispatches on the estimator type; the paper's path is GMM:

```python
elif isinstance(cluster_model, GaussianMixture):
    cluster_model.fit(xtr)
    cluster_assignments = cluster_model.predict(xtr)   # hard argmax labels
    cluster_centers = cluster_model.means_             # mu_k
```

`KMeans` and `DBSCAN` branches exist and are what the GMM-vs-K-means ablation
switches between. Note `random_state=None` — GMM is refit unseeded on every
fold, so cluster identity is not stable across folds. This is why Stage B has
to match centroids (Sec. 4.3).

### 3.2 Subset selection — `Functions.py :: up_memberc`

**This is the definition of `phi`, and it is not what the algorithm box in the
paper describes.**

```python
k = round(phi * num_data_points)          # fraction of the ENTIRE training set
distances = np.linalg.norm(X_train - centroid, axis=1)
closest_indices = np.argsort(distances)[:k]
```

For each of the K centroids, take the `k` **nearest points of the whole
training set** — not points assigned to that cluster, and not a fraction of
the cluster. Consequences:

- Every subset has exactly `k = phi*N` rows regardless of cluster size.
- Subsets **overlap by construction**, and overlap grows with `phi`.
- Selection is by **Euclidean distance to the mean**, not by GMM
  responsibility. The covariance `Sigma_k` plays no role here — it enters only
  at prediction time (Sec. 5.4).
- At `phi = 0.9` every base learner sees 90% of all training rows, so the K
  training sets are near-identical. Measured on HAR at K=5: mean pairwise
  Jaccard overlap 0.842, base-learner disagreement 0.008
  (`data/diversity_diagnostic.csv`).

The manuscript's Algorithm 1 says *"select int(m x phi) instances with the
highest responsibilities"* — responsibility-ranked, within-component. The code
does distance-ranked, over the full set. **These are different algorithms and
the text should be corrected to match the code.**

### 3.3 Cleanup — `Functions.py :: remove_minority`, then `resampling`

Within each subset, drop any class holding `< 1%` of that subset's rows, then
shuffle (`random_state=42`). Base learners can therefore end up with different
`classes_`; the ensemble repairs this by inserting zero columns for absent
classes before aggregation.

`resampling()` wraps `sampling()` + `remove_minority()` and returns
`rm_cluster_samples`, `rm_cluster_samples_labels`, `cluster_centers`,
`min_distances`, `cluster_assignments`, `cluster_model`.

## 4. Stage A — `codes/base_train.py`

1. 80/20 `train_test_split(random_state=42)`, then `single_preprocessing`.
2. `resampling_grid` over `phi_list = np.arange(0.1, 1, 0.1)` x
   `n_c_list = np.arange(2, 7)` -> **45 configurations**, each producing K
   subsets.
3. `grid_train_base_models` runs `GridSearchCV` **per subset per model family**:

   | model | grid |
   |---|---|
   | `svm` | C {0.1,1,10,100} x kernel {linear,poly,rbf,sigmoid} x gamma {scale,auto} |
   | `lr` | C {0.1,1,10} x solver {lbfgs,liblinear,saga} |
   | `knn` | k {3,5,7,9} x weights {uniform,distance} x algorithm {auto,ball_tree,kd_tree} |
   | `dt` | criterion x splitter x max_depth x min_samples_split x min_samples_leaf |
   | `sgd` | alpha {1e-4,1e-3,1e-2}, loss log_loss |

4. `cv_results_` sorted by `mean_test_score`, duplicate scores dropped, top
   parameter set applied via `set_params` to a fresh **unfitted** estimator ->
   `best_models_clusters`.
5. Pickled with the resampling results.

Base pool — `Model_functions.py :: get_models`:
```python
models['sgd'] = SGDClassifier(loss='log', n_jobs=-1)
models['svm'] = SVC(max_iter=1000, probability=True, C=1, kernel='linear')
models['lr']  = LogisticRegression(solver='lbfgs', max_iter=1000)
models['knn'] = KNeighborsClassifier(n_jobs=-1)
models['dt']  = DecisionTreeClassifier()
```
`gn` (GaussianNB) is popped in both stages. **`SVC(max_iter=1000)` is a hard
iteration cap** — on ~9.3k training rows the linear solver does not converge
and macro F falls from 0.972 to 0.886. Any SVM baseline must be run uncapped
or it is understated.

## 5. Stage B — `codes/evaluation.py`

`RepeatedKFold(n_splits=5, n_repeats=4, random_state=42)` -> 20 folds. Per
fold, per `(phi, n_c)`:

### 5.1 Fold preprocessing
`single_preprocessing` refit on the fold's training rows, `n_components` pinned
to Stage A's width.

### 5.2 Single-model baselines
Each model in the pool is fit on the **full** fold training set and scored —
this is the `single_*` reference the ensemble is measured against.

### 5.3 Fold partitioning
A fresh `GaussianMixture(n_components=n_c, random_state=None)` is fit on the
fold's training data, then `resampling(..., phi=phi, ...)` builds that fold's
K subsets.

### 5.4 Centroid matching — the bridge between stages
Stage A's centroids and this fold's centroids are in arbitrary order, so they
are paired by nearest neighbour:

```python
differences = centers_1[:, np.newaxis, :] - centers_2[np.newaxis, :, :]
distances   = np.linalg.norm(differences, axis=2)
ordered_centers_indexes = np.argmin(distances, axis=1)
```

This is a greedy `argmin` **without a uniqueness constraint** — two fold
centroids can map to the same Stage A centroid, in which case one tuned
configuration is used twice and another is dropped. Not checked in the code.

### 5.5 Fit and predict
Matched estimators are refit on the fold's subsets, wrapped in `MainModel`
(an `nn.Module` shell around `Ensemble`), and `forward()` calls
`Ensemble.predict_sample`, which produces all aggregation rules in one pass.
`use_ensemble = {'diste':True,'avge':True,'acce':False,'maxe':True,'densitye':True}`.

## 6. Aggregation rules — `Model_functions.py :: Ensemble.predict_sample`

Each base learner k emits `P_k(x) in R^C` from `predict_proba`. Missing classes
are zero-filled first. `nan` -> 0 via `np.nan_to_num`.

**AvgE** — unweighted mean, the no-competence control:
```python
final = np.mean(X_pred_for_clusters, axis=0)
```

**MaxE** — hard winner-take-all on peak confidence; the single most confident
(learner, class) pair wins and the output is one-hot. This discards all
probability mass, which is why MaxE collapses (~0.508 for lr).

**DistE** — inverse Euclidean distance to centroids, with a radius gate:
```python
distances   = np.linalg.norm(cluster_centers[:, None] - X, axis=2)
thresholds  = 2 * np.array([min_dist[-1] for min_dist in min_distances])  # 2x subset radius
distances_filtered = np.where(distances <= thresholds[:, None], distances, np.inf)
inv = 1 / (distances_filtered + 1e-20)
w   = inv / inv.sum(axis=0, keepdims=True)
final = np.sum(w[..., None] * X_pred_for_clusters, axis=0)
```
`min_dist[-1]` is the distance of the farthest retained point, i.e. the subset
radius. Learners whose region is more than 2 radii away are gated out; if a
point falls outside every region, the nearest one is reinstated.

**DensityE — the method of the paper.** Weights are the **GMM posterior
responsibilities** of the test point:
```python
gamma = self.cluster_model.predict_proba(X)        # gamma_k(x), sums to 1 over k
final = np.sum(gamma.transpose(1,0,2) * X_pred_for_clusters, axis=0)
```
i.e.

    P(y|x) = sum_k gamma_k(x) P_k(y|x),
    gamma_k(x) = pi_k N(x | mu_k, Sigma_k) / sum_j pi_j N(x | mu_j, Sigma_j)

This is the one place the full covariance `Sigma_k` is used, and it is the
entire formal difference from a K-means/distance scheme: `gamma_k` is a
normalised likelihood under an anisotropic Gaussian, whereas DistE's weight is
an isotropic inverse distance. That is the empirical basis of the GMM-over-
K-means claim, and it lives at *prediction* time, not at partitioning time.

**Diagnostics computed alongside** (both have caveats):
```python
oracle_acc = |union of indices any base learner gets right| / N     # ceiling
dissagreement = mean_i corr(X_pred_for_clusters[0][i], X_pred_for_clusters[1][i])
```
The disagreement statistic uses **only clusters 0 and 1**, ignoring the rest,
and it is a Pearson *correlation* — higher means more agreement. Do not cite it
as a diversity measure without restating it over all K(K-1)/2 pairs.

## 7. What the manuscript reports

Reported configuration is **`n_c = 6`, `phi = 0.5`** (Sec. IV-B, Table I,
Fig. `boxplot_comparison`). From the Stage A grid, DensityE at `n_c=6`:

| phi | 0.1 | 0.2 | 0.3 | 0.4 | **0.5** | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|---|---|---|---|---|
| lr | .9256 | .9588 | .9665 | .9719 | **.9733** | .9726 | .9726 | .9718 | .9726 |
| svm | .9399 | .9596 | .9638 | .9672 | **.9688** | .9629 | .9638 | .9626 | .9657 |
| knn | .8636 | .9350 | .9481 | .9554 | .9579 | .9581 | .9588 | .9586 | **.9590** |
| dt | .7213 | .7808 | .8079 | .8168 | .8212 | .8216 | .8201 | .8205 | **.8223** |

The curve rises steeply to ~0.4-0.5 and is **flat thereafter** —
`phi = 0.9` is 0.0007 below `phi = 0.5` for lr, well inside the fold std
(0.0024). Higher `phi` does not cost accuracy.

What it does cost is the ensemble's reason to exist. At K=5
(`data/diversity_diagnostic.csv`):

| phi | overlap | disagreement | oracle | achieved | headroom | train s |
|---|---|---|---|---|---|---|
| 0.2 | 0.113 | 0.706 | 0.981 | 0.950 | 0.031 | 6.4 |
| 0.4 | 0.289 | 0.643 | 0.991 | 0.974 | 0.017 | 16.7 |
| 0.6 | 0.478 | 0.199 | 0.987 | 0.971 | 0.016 | 36.0 |
| 0.9 | 0.842 | 0.008 | 0.973 | 0.972 | 0.001 | 65.9 |

At `phi = 0.9` the oracle ceiling has fallen to the achieved score: no combiner,
however good, could improve on these base learners, and training costs 4x more
than at `phi = 0.4`. Measured on the same protocol a single logistic regression
scores 0.9734 (Wilcoxon p = 0.50, 5/10 wins) — parity.

**The defensible claim is about diversity and cost, not accuracy.**

## 8. Known defects to fix before resubmission

1. **Algorithm 1 does not match `up_memberc`.** Text says responsibility-ranked
   within-component; code is distance-ranked over the full training set. Fix
   the text.
2. **Fig. 1(c) caption says "the originally published phi = 0.9".** Wrong — the
   published configuration is `phi = 0.5`. (My error; needs correcting.)
3. **Sec. IV-E claims F-score "improves for all base learners" as phi rises.**
   The sweep plateaus after 0.5; lr and svm peak at 0.5 and decline slightly.
4. **`SVC(max_iter=1000)`** caps the solver; any SVM number from the default
   pool is understated unless refit uncapped.
5. **Centroid matching has no uniqueness constraint** — possible duplicate
   assignment of tuned configurations.
6. **Disagreement statistic covers only clusters 0 and 1** and is a
   correlation, not a disagreement.
7. **`subject` is dropped before splitting** — record-wise CV on HAR leaks
   participants across folds. Standard practice for this dataset is
   subject-wise splitting; a referee may raise it.

## 9. Reproduction order

```
codes/base_train.py                  # Stage A: 45-config hyperparameter search
codes/evaluation.py                  # Stage B: 20-fold fit + score
codes/diagnose_diversity.py          # overlap / disagreement / oracle -> data/diversity_diagnostic.csv
codes/confirm_phi_K.py               # paired Wilcoxon vs Single LR -> data/phi_K_confirmation.csv
codes/tier4_item19_gmm_vs_kmeans.py  # GMM vs K-means ablation
codes/tier4_item20_*.py              # non-clustering baselines
```

Both stage scripts begin with `os.chdir('/content/drive/MyDrive/Thp')` and
`from Lib.lib import *` — they are Colab artifacts and will not run here
unmodified.
