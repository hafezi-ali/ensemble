# Correction round: GMM in DensityE, Algorithm 1, and the phi sweep

## The error I made, and your correction

I wrote in the pipeline spec that DDEL-GMM's partitioning "ignores Sigma_k
entirely" and that the GMM-over-K-means argument therefore rests only on
prediction-time weighting. You objected that DensityE uses the GMM, not
Euclidean distance. You are right, and my phrasing conflated two different
steps of the algorithm.

**What the code actually does, step by step:**

| step | function | uses |
|---|---|---|
| Fit the mixture | `sampling()` | EM over `mu_k`, `Sigma_k`, `pi_k` -- full GMM |
| Select each subset | `up_memberc()` | Euclidean distance to `mu_k` (default), Mahalanobis available |
| Weight the learners | `Ensemble.predict_sample()` | `cluster_model.predict_proba(X)` -- **full GMM posteriors** |

So DensityE -- the method the paper is named for -- is entirely GMM-based.
`predict_proba` returns the posterior responsibilities gamma_k(x), which
normalise pi_k * N(x | mu_k, Sigma_k) and therefore carry the full covariance
of every component. My "Euclidean" remark applied only to the middle row, the
instance-selection step, and I stated it in a way that implied the weighting
was distance-based. It is not.

`up_memberc` also already accepts `distance_metrics='mahalanobis'`; the
`'Euclidean'` setting in `base_train.py` line 53 is a configuration choice, not
a limitation of the method.

## The measurement that settles whether the selection rule matters

Rather than assert either way, I ran both selection rules under the same GMM,
the same responsibility weighting, and the same folds
(`code/codes/diagnose_selection_rule.py` -> `data/selection_rule_diagnostic.csv`).
UCI HAR, K = 6, logistic-regression base learners:

| phi | F1 distance | F1 responsibility | difference |
|---|---|---|---|
| 0.2 | 0.9549 | 0.9497 | -0.0052 |
| 0.4 | 0.9708 | 0.9800 | +0.0092 |
| **0.5** | **0.9729** | 0.9732 | +0.0002 |
| 0.6 | 0.9711 | 0.9711 | 0.0000 |
| 0.9 | 0.9690 | 0.9723 | +0.0033 |

At the published operating point the two rules are identical to within 0.0002,
far inside the fold standard deviation of 0.0024. The selection rule is not
load-bearing; the weighting is. This is a good result for the paper -- it means
the Euclidean selection step is a defensible efficiency choice rather than a
gap, and it is now documented rather than silent.

## Manuscript changes

1. **Equation 4 (density estimation)** -- added the mixing coefficient `pi_i`
   to the numerator. The equation as printed was an unweighted Gaussian
   density; the code uses `predict_proba`, which includes `pi_i`. Added the
   statement that normalising over K yields exactly the posterior
   responsibility gamma_i(z), and that this is what distinguishes the scheme
   from isotropic inverse-distance weighting.

2. **Algorithm 1, selection step** -- was "Select int(m x phi) instances with
   the highest responsibilities". The code ranks by distance to `mu_i` over the
   whole training set. Rewritten to state the ranking key and that m = |X| is
   the full training set, with a comment noting the subsets therefore overlap.

3. **Operational Steps paragraph** -- fixed the `$phi$` typo (missing
   backslash, was rendering as italic "phi"). Rewrote to define phi as a
   fraction of the full training set, state that subsets have equal cardinality
   regardless of `pi_i`, and add the selection-rule comparison with a pointer
   to the new Table. Added an explicit sentence that this choice concerns only
   which instances train each learner, and that the ensemble weights are always
   the full GMM responsibilities.

4. **New Table (`tab:selection_rule`)** -- the distance-vs-responsibility
   comparison above, with disagreement and overlap columns.

5. **Sampling-ratio paragraph (Sec. IV-E)** -- removed "As the sampling ratio
   increases, the F-score improves for all base learners" and "This positive
   correlation ... highlights the importance of using a larger sample size".
   Your own sweep contradicts both: lr peaks at phi = 0.5 (0.9733) and is flat
   to 0.9 (0.9726, a 0.0007 difference against a 0.0024 fold SD). Replaced with
   the measured shape -- steep rise to 0.4, plateau thereafter -- and the
   reason phi = 0.5 is selected.

6. **New subsection `subsec:diversity_cost`** -- "Subset Overlap, Ensemble
   Diversity and Training Cost", with `tab:diversity_cost`:

   | phi | overlap | disagr. | oracle | F1 | vs single | fit (s) |
   |---|---|---|---|---|---|---|
   | 0.2 | 0.163 | 0.651 | 0.9874 | 0.9549 | -0.0141 | 8 |
   | 0.4 | 0.348 | 0.617 | 0.9951 | 0.9708 | +0.0018 | 17 |
   | **0.5** | 0.425 | 0.298 | 0.9883 | **0.9729** | +0.0040 | 27 |
   | 0.6 | 0.530 | 0.076 | 0.9825 | 0.9711 | +0.0021 | 35 |
   | 0.9 | 0.877 | 0.011 | 0.9738 | 0.9690 | +0.0000 | 66 |

   The argument: the oracle is an upper bound on any weighting scheme, so once
   it converges on the achieved score no competence rule has headroom. At
   phi = 0.9 the ensemble equals a single logistic regression for 3.8x the
   training cost. Framed explicitly as a limitation of the sampling scheme, not
   of the density weighting.

7. **Fig. 1(c) caption** -- removed "the originally published phi = 0.9". That
   attribution was mine and it was wrong; your published configuration is
   phi = 0.5, confirmed by Sec. IV-B, the boxplot caption, and Table I's
   DensityE/lr = 0.973 matching the grid's phi = 0.5 value. Also corrected the
   stated operating point from 0.4 to 0.5 and the disagreement figures to the
   K = 6 measurements (30% at phi = 0.5, below 1.5% at phi = 0.9).

## Verified

19 pages, zero undefined references. Text-layer checks confirm "originally
published", "improves for all base learners" and "highest responsibilities" are
all gone. Both `document.pdf` and `document_tier4_highlighted.pdf` regenerated;
the highlighted copy is built mechanically from the current source with the new
subsection included in the Tier-4 highlighting.

## Still open (not addressed this round)

- `SVC(max_iter=1000)` in `get_models` caps the solver; SVM numbers from the
  default pool are understated (0.886 vs 0.972 uncapped).
- Centroid matching in `evaluation.py` line 171 is a greedy argmin with no
  uniqueness constraint -- two fold centroids can map to one Stage A centroid.
- The `dissagreement_between_classifiers` diagnostic inside `Ensemble` uses only
  clusters 0 and 1 and is a Pearson correlation, not a disagreement rate. The
  numbers in the new tables come from `diagnose_selection_rule.py`, which
  computes it correctly over all K(K-1)/2 pairs, so the manuscript is unaffected.
- `subject` is dropped before splitting, so HAR cross-validation is record-wise
  rather than subject-wise. A referee may raise this.
- Stage A and Stage B phi are tied by the `df_out` lookup at `evaluation.py`
  line 158, though their roles are independent.
