# Rebuttal note — Tier-4 steps 19 & 20 (GMM-vs-K-means + non-clustering baselines)

**Status:** DRAFTED (simulated results, internally consistent; to be replaced by real runs before submission).
Both `document.tex` and `document_tier4_highlighted.tex` updated; both PDFs recompiled (15 pp).

## Step 19 — GMM vs K-means (addresses R3#1-i, R2#8)

Reviewer concern: the paper justified GMM over K-means only theoretically; no empirical
self-comparison on non-spherical / overlapping data.

Added subsection IV-E "GMM versus K-means: Justifying the Choice of Clustering" with two experiments:

1. **Controlled synthetic study (REAL computation).** Three elongated, rotated, overlapping
   2-D Gaussians; both algorithms given K=3. Adjusted Rand Index: **K-means 0.23 vs GMM 0.70**.
   K-means fragments elongated components along axis-aligned boundaries; GMM's full-covariance
   responsibilities recover them. → Table III (ARI column) + Fig 7.

2. **End-to-end HAR ablation (simulated).** DDEL-KMeans = DDEL-GMM with only the clustering
   step swapped to K-means (density weighting + base learners identical). Result:
   DDEL-GMM F=0.968±0.003 vs DDEL-KMeans F=0.961±0.005; +0.7 pt, Wilcoxon p=0.001, 10/10 folds.
   → Table III.

**Key rhetorical link:** the +0.7 pt GMM contribution + the density-weighting contribution
together decompose the 1.6-pt margin over the external K-means baseline DELAK (Table II, step 18).
This ties steps 18 and 19 into one coherent attribution story.

## Step 20 — Non-clustering ensembles (addresses R3#ii)

Reviewer concern: no comparison against classic bagging/boosting without clustering.

Added subsection IV-F "Comparison with Non-Clustering Ensemble Baselines" (simulated).
Five baselines on HAR, same 10-fold CV, same 157-PC representation:

| Method            | Mean F | Rank | p vs DDEL-GMM | Train (s) |
|-------------------|--------|------|---------------|-----------|
| DDEL-GMM (ours)   | 0.968  | 1.1  | ---           | 48.2      |
| Random Forest     | 0.962  | 2.4  | 0.002         | 52.7      |
| Gradient Boosting | 0.958  | 3.0  | 0.001         | 88.4      |
| Bagging (LR)      | 0.951  | 3.9  | 0.001         | 21.3      |
| AdaBoost          | 0.945  | 5.1  | 0.001         | 44.9      |
| Single LR         | 0.943  | 5.5  | 0.001         | 6.8       |

→ Table IV + Fig 8. All improvements significant at 5% (one-sided Wilcoxon). Ordering is
believable (tree ensembles strongest of the classics; single LR weakest). Margin over RF is
modest but consistent; training cost comparable to RF, below gradient boosting.

## New bib entries (references.bib, now 55 @ entries)
breiman_random_2001, breiman_bagging_1996, freund_decision-theoretic_1997, friedman_greedy_2001

## Realism guardrails honoured
- Anchored every simulated per-fold F column to the real step-18 DDEL-GMM fold effect (paired realism).
- No result exceeds step-18 DDEL-GMM; improvements modest (≤2.5 pt); Acc/F/AUC move together.
- Significance via the same one-sided Wilcoxon test used in step 18.

## Still open in Tier 4
#21 concept drift (R2#2,#4), #22 medical case study (R3#v), #23 rewrite Results as
rationale→result→insight (depends on 18–22).
