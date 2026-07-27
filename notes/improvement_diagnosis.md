# How to improve DDEL-GMM: measured diagnosis and options

All numbers below are MEASURED on real UCI HAR (10,299x561 -> 157 PCs, seed 42).
Diagnostics on fold 1; the confirmation run is all 10 folds, paired, identical folds.

## Diagnosis: the tie with Single LR is a diversity failure, not an accuracy ceiling

Two defects in the current configuration, both measured:

### 1. phi=0.9 destroys base-learner diversity
With K=5 and phi=0.9 each of the 5 learners trains on 90% of the rows. Measured mean
pairwise subset overlap (Jaccard) = 0.842, and the 5 learners disagree on only 0.8% of
test points. Averaging 5 near-identical classifiers returns that classifier. This is the
arithmetic reason DDEL-GMM = 0.9734 = Single LR to four decimals.

    K  phi   overlap  disagree  oracle   F       vs SingleLR
    5  0.2   0.113    0.706     0.9806   0.9497  -0.0193
    5  0.4   0.289    0.643     0.9913   0.9737  +0.0047
    5  0.6   0.477    0.199     0.9874   0.9711  +0.0021
    5  0.9   0.842    0.008     0.9728   0.9723  +0.0033   <- current
    8  0.4   0.359    0.572     0.9951   0.9739  +0.0049
    8  0.9   0.860    0.007     0.9738   0.9700  +0.0010

`oracle` = accuracy if an omniscient combiner picked the best base learner per test
point. It is the CEILING for any weighting rule. At K=8/phi=0.4 the oracle is 0.9951
while the aggregator delivers 0.9739: 2.1 points of headroom the weighting misses.
At phi=0.9 the oracle itself falls to 0.9728 - the diversity needed to beat a single
model is not in the ensemble at all, so no weighting rule could recover it.

### 2. The GMM posteriors are numerically HARD, not soft
Normalised posterior entropy H(W) = 0.005 at K=5 and 0.003 at K=8 (0 = one-hot,
1 = uniform). At 157 dimensions component log-densities differ by hundreds of nats, so
the posterior softmax saturates: every test point gets weight ~1 on one component.
DENSITYE is therefore behaving as HARD cluster selection - structurally what DELAK does.
The manuscript's claim that soft responsibilities distinguish it from hard assignment is
not what the code does at this dimensionality. This is a correctness issue for the
narrative independent of any accuracy gain.

## What was tried, and what it bought

### Temperature on the posterior: +0.001, keeps the mechanism honest
W = softmax(log p / T). T>1 softens. Note this runs AGAINST the usual DES advice to
sharpen competence weights - the measurement says sharpening is already saturated, so
the untried direction was softening.

    T        H(W)    F        vs SingleLR
    1        0.003   0.9739   +0.0049
    20       0.124   0.9739   +0.0049
    80       0.399   0.9749   +0.0059
    300      0.603   0.9749   +0.0059
    1e9      1.000   0.9379   -0.0311   <- uniform weights == AvgE

The T=1e9 row is worth keeping: with uniform weights the ensemble collapses to 0.9379.
Density weighting IS doing real work versus plain averaging - a useful ablation for the
paper even though the accuracy gain over T=1 is small.

### Heterogeneous base learners (LR/SVM/tree/KNN per component): -0.035, REJECTED
Measured 0.9342 at T=1 against 0.9690 for Single LR. The weaker families drag the
weighted average down because a saturated posterior cannot route around a bad learner.
Do not pursue: it makes things worse, and the measurement says why.

### 10-fold confirmation of the phi/K correction

    Configuration              mean F     SD       vs SingleLR   Wilcoxon p   wins
    K=5 phi=0.9 (current)      0.97341    0.00554  +0.00006      -            -
    K=8 phi=0.4                0.97506    0.00486  +0.00170      0.193        8/10
    K=8 phi=0.4 T=80           0.97555    0.00527  +0.00220      0.106        8/10

Consistent in direction (8/10 folds both times) but NOT statistically significant at
n=10 folds. Do not claim significance from this. It is also worth noting the SD drops
(0.00554 -> 0.00486), which is consistent with the dispersion-reduction story the paper
already tells.

## Recommendation

1. RETUNE and rerun: K=8, phi=0.4, T=80. Costs one measurement pass, gains +0.0022 F,
   lowers SD, and moves the mean above every non-clustering baseline. It will not make
   the Wilcoxon significant on HAR.
2. REPORT the temperature as a contribution, not a fix. 'High-dimensional GMM posteriors
   saturate; we introduce a temperature parameter that restores soft responsibility
   weighting' is a genuine methodological point, it explains the DELAK relationship
   mechanically, and the AvgE collapse (0.9379) is the ablation that justifies it.
3. DO NOT keep chasing HAR. Four methods sit within 0.001 F of each other; the dataset
   is saturated for regularised linear models on this representation and 10 folds cannot
   resolve a 0.002 gap. More tuning here buys nothing a referee will accept.
4. WHERE THE GAIN IS: move the headline evidence to data where the inductive bias pays -
   non-spherical/overlapping clusters (the GMM-vs-KMeans arm), concept drift, and class
   imbalance. On HAR the honest claim remains: decisive over tree ensembles, tied with
   strong linear baselines, with dispersion reduction as the mechanism.

## Files
- data/diversity_diagnostic.csv   - overlap/disagreement/oracle per (K, phi)
- data/weighting_improvement.csv  - temperature sweep x base-learner homogeneity
- data/phi_K_confirmation.csv     - 10-fold paired scores for the 3 DDEL variants + Single LR
- code/codes/diagnose_diversity.py, improve_weighting.py, confirm_phi_K.py