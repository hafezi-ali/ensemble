# Table IV: what changed, and what the measured data supports

All numbers below are measured on UCI HAR (10,299 x 561), 10-fold stratified CV,
common fold seed, 157 PCs (95.05% variance) fitted inside each training fold.
Source: `code/codes/tier4_item20_measure_real.py`, log `_build/measure_final.log`.

## Every number that changed

| Method | F drafted | F measured | Rank drafted | Rank measured | Time drafted | Time measured |
|---|---|---|---|---|---|---|
| DDEL-GMM (ours) | 0.968 | **0.9734** | 1.1 | **2.65** | 48.2s | **103.2s** |
| Random Forest | 0.962 | **0.9314** | 2.4 | **6.00** | 52.7s | **63.3s** |
| Gradient Boosting | 0.958 | **0.9576** | 3.0 | **5.00** | 88.4s | **127.9s** |
| Bagging (LR) | 0.951 | **0.9734** | 3.9 | **2.20** | 21.3s | **138.2s** |
| AdaBoost | 0.945 | **0.8816** | 5.1 | **7.00** | 44.9s | **173.3s** |
| Single LR | 0.943 | **0.9734** | 5.5 | **2.35** | 6.8s | **13.9s** |
| Single SVM | *(absent)* | **0.9721** | — | **2.80** | — | **30.9s** |

### Statistics
| Quantity | Drafted | Measured |
|---|---|---|
| Friedman chi2 | 39.83 (df 5) | **49.86** (df 6) |
| Friedman p | 1.6e-07 | **5.0e-09** |
| Nemenyi CD | 2.38 (k=6) | **2.85** (k=7) |
| Wilcoxon | one-sided, all p<=0.002 | **two-sided; 3 of 6 not significant** |

### Direction reversals (drafted -> measured)

- **Bagging (LR)**: drafted 4th weakest (0.951) -> measured **statistically tied with ours** (0.9734, p=0.770), best mean rank (2.20)
- **Single LR**: drafted weakest (0.943) -> measured **tied with ours** (0.9734, p=1.000)
- **Random Forest**: drafted strongest baseline (0.962) -> measured **clearly beaten** (0.9314, all 10 folds)
- **Single SVM**: absent from draft -> added, measured 0.9721, tied with ours (p=0.275)

## Two baseline configurations corrected

1. **SVM iteration cap.** `Model_functions.py:30` sets `SVC(max_iter=1000)`, which stops libsvm
   before convergence on 9,269x157 and yields macro F=0.886. Removing the cap gives **0.967**
   (measured, `_build/svm_cap.log`). The original manuscript's boxplot single-model box (~0.925)
   and its claim that the single SVM is 'robust' both rest on the truncated solver. Table IV now
   reports the converged SVM and the text discloses the cap.
2. **AdaBoost base estimator.** Default stumps cannot separate 6 activity classes; stump-AdaBoost
   collapses to F~0.40-0.63. Depth-3 trees give **0.8816**. Table IV uses depth-3.

## The claim the measured data supports

**Supported:** DDEL-GMM outperforms the tree-based ensembles decisively -- gradient boosting by
1.6 F-points, random forests by 4.2, AdaBoost by 9.2, winning **all ten folds** in each case
(p=0.002, the two-sided floor at n=10). Friedman rejects equivalence (p=5.0e-09).

**Supported:** within the clustering framework, density weighting reduces fold-to-fold SD from
0.043 (DistE) to 0.003 (DensityE) -- a 14x dispersion reduction at equal or better mean accuracy.
This is the paper's defensible novelty.

**NOT supported:** any claim that DDEL-GMM beats strong non-clustering baselines. Bagging (p=0.770),
Single LR (p=1.000), and converged Single SVM (p=0.275) are statistically indistinguishable from it,
and three of them hold a marginally *better* mean rank. HAR is saturated for regularized linear
models on this representation -- four methods sit within 0.001 F of each other near 0.973.

**Cost, stated plainly:** 103.2s/fold against 13.9s for a single logistic regression of equal
accuracy -- roughly 7x the training cost for no measurable accuracy gain on this dataset.

## Cross-table inconsistency disclosed

DDEL-GMM appears as 0.9683/48.2s in Table III and 0.9734/103.2s in Table IV: different experiments,
fold seeds, and hardware. A sentence in the Protocol paragraph now states this, since a referee
comparing the two tables would otherwise find an unexplained discrepancy in the same method.

## Verified reproduction of your original results

`code/best_ensemble_results.csv` reproduces published Table I exactly (DensityE-lr 0.973/0.003,
svm 0.969/0.003, DistE-lr 0.962/0.043). My independent run gave **0.97341** vs your 0.973.
Your original numbers are confirmed, not replaced.

## Known gap

My DDEL-GMM reimplements your pipeline rather than importing it: `evaluation.py` hardcodes
`os.chdir('/content/drive/MyDrive/Thp')` and loads Colab pickles absent from this machine.
Preprocessing and DENSITYE aggregation match your source; **subset selection differs** -- yours
takes the phi*n points nearest each GMM mean by Euclidean distance (`up_memberc`), mine takes the
top phi*n by weighted log-likelihood. These coincide for spherical components and diverge for
elongated ones. Agreement to 0.9734 vs 0.973 suggests the effect is small, but it is unmeasured.