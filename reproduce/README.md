# DDEL-GMM — reproduction package

The scripts that produce the manuscript's results and figures. No figure holds
a hardcoded number: each reads its values from a CSV in `data/` at render time.

**Not everything here is measured.** Most of `data/` is written by a script in
`scripts/`, but two result sets are not, and one of them is the paper's most
requested comparison. Read [Provenance](#provenance) before citing any number
from this folder.

    ./run_all.sh figures     # redraw all figures from the shipped CSVs   (~30 s)
    ./run_all.sh diag        # rerun the diagnostics                      (~40 min)
    ./run_all.sh             # everything, including the slow measurements (~3 h)

Requires Python 3.9+ and the packages in `requirements.txt`
(`pip install -r requirements.txt`).

## The dataset

Scripts read the UCI HAR feature matrix — 10,299 rows, 561 features, six
activity classes — from

    ../code/Data/UCI_HAR_Dataset/data_uci_handled.csv

If you move this folder away from the repository, point the scripts at the file:

    export DDEL_DATASET=/path/to/data_uci_handled.csv

Every script calls `require_dataset()` on import and exits with that message if
the file is missing, rather than failing partway through a two-hour run.

## Layout

    reproduce/
      run_all.sh              driver; writes per-script logs to logs/
      requirements.txt
      lib/
        ddel_paths.py         the only place any path is defined
        Functions.py          author's original modules, copied verbatim
        Model_functions.py      (sampling, preprocessing, Ensemble, DENSITYE)
        Plot_functions.py
        lib_original.py
      scripts/                one script per result; see the table below
        figures/              one script per figure
      data/                   CSVs: inputs to the figures, outputs of the scripts
      figures/                PDFs and PNGs
      logs/                   stdout of the last run

`lib/ddel_paths.py` resolves everything relative to its own location, so the
folder can be moved, copied, or cloned anywhere without editing a script.

## What produces what

### Experiments

| script | runtime | writes | answers |
|---|---|---|---|
| `exp1_gmm_vs_kmeans.py` | ~25 min | `clustering_ablation_{sweep,covtype}.csv` | Does GMM beat K-means on non-spherical, overlapping clusters? |
| `exp2_noclustering_measure.py` | ~2 h | `noclustering_{perfold,summary}.csv` | Does DDEL-GMM beat bagging, boosting, RF, AdaBoost? |
| `exp2_noclustering_stats.py` | seconds | `noclustering_stats.csv` | Wilcoxon / Friedman / Nemenyi on those per-fold vectors |
| `exp3_table4_nested.py` | ~45 min | `ddel_nested_perfold.csv` | Table IV under nested hyperparameter selection |

`exp2_noclustering_measure.py` gives each baseline the representation that suits
it — tree ensembles get the raw 561 features, AdaBoost gets depth-3 trees rather
than sklearn's default stumps, linear models and DDEL-GMM get 157 PCs fitted
inside each fold. All methods see identical folds. This is deliberate: a
baseline that has been handicapped by preprocessing proves nothing.

### Diagnostics

| script | writes | answers |
|---|---|---|
| `diag_selection_rule.py` | `selection_rule_diagnostic.csv` | Distance-ranked vs responsibility-ranked selection; the phi sweep behind Fig. 7 |
| `diag_diversity.py` | `diversity_diagnostic.csv` | How subset overlap and learner disagreement vary with phi and K |
| `diag_confirm_phi_K.py` | `phi_K_confirmation.csv` | 10-fold confirmation of the chosen operating point |
| `diag_weighting.py` | `weighting_improvement.csv` | Two candidate mechanisms for closing the oracle gap |
| `check_svm_cap.py` | prints | Is single-SVM 0.925 a property of SVM or of `max_iter=1000`? |
| `check_user_funcs.py` | prints | Do the author's own `Funcs/` modules reproduce the measured numbers? |

### Figures

| script | manuscript figure | reads |
|---|---|---|
| `figures/fig1_and_fig7.py` | Fig. 1 pipeline schematic, Fig. 7 diagnostics (a)(b)(c) | `selection_rule_diagnostic.csv`, `best_ensemble_results.csv` |
| `figures/fig5_boxplot.py` | Fig. 5 per-fold F1 boxplot | `boxplot_stats_measured.csv`, `best_ensemble_results.csv` |
| `figures/fig8_sota.py` | Fig. 8 vs published DES methods | `sota_perfold_fscores.csv` **(not measured)** |
| `figures/fig10_noclustering.py` | Fig. 10 vs non-clustering ensembles | `noclustering_perfold.csv` |

Figures write both PDF (for LaTeX) and PNG (for inspection) into `figures/`.
To use them in the manuscript, copy the PDFs into `../manuscript/`.

`fig8_sota.py` recomputes its Wilcoxon p-values from the per-fold vectors
instead of reading them from the summary CSV, so the annotations cannot drift
from the data they describe.

## Three results that are easy to misread

**φ = 0.9 is not the best operating point, even though its oracle gap is
smallest.** The oracle is not a fixed target — it is the ceiling available from
the pool of learners you actually built, so it moves with φ. At φ = 0.9 the six
subsets overlap 87.7% and the learners disagree on 1.1% of predictions; six
near-identical learners give a combiner nothing to choose between, so the
ceiling itself falls to 97.38%. The decisive comparison: the entire oracle
ceiling at φ = 0.9 (97.38%) is below what DDEL-GMM actually delivers at
φ = 0.5 (97.29%) by 0.09 pp. Measured, K = 6, distance rule:

    phi        0.20    0.40    0.50    0.60    0.90
    overlap    16.3    34.8    42.5    53.0    87.7   %
    disagree   65.1    61.7    29.8     7.6     1.1   %
    oracle     98.74   99.51   98.83   98.25   97.38  %
    achieved   95.49   97.08   97.29   97.11   96.90  %
    headroom    3.25    2.43    1.54    1.14    0.48  pp

φ = 0.5 wins on achieved score and costs 27 s against 66 s. The accuracy margin
over φ = 0.9 is 0.39 pp against a fold SD of 0.3 pp — about 1.3 σ, so state it
as a preference, not a significant difference. The cost and non-degeneracy
arguments are the strong ones.

**The DensityE-vs-DistE claim is about dispersion, and it is not visible in the
box widths.** DistE's IQR is actually *tighter* (0.0022 vs 0.0040 for logistic
regression). The claim rests on the fold standard deviation — 0.003 vs 0.043, a
14-fold reduction — which is driven by a few low outlier folds. Their signature
in Fig. 5 is the mean marker sitting well below the median for every DistE box
(−0.0093 for lr) while DensityE means sit on their medians (−0.0003).
`fig5_boxplot.py` annotates the standard deviations for this reason. An earlier
version of this figure encoded DistE means that were systematically low and
supported a "DistE trails by six points" claim; the measured gap is about one
point and the distributions overlap. Do not restore it.

**1.54 pp of headroom at φ = 0.5 is a result, not a shortfall.** It is the
margin a better weighting rule could still recover, and it exists only at
moderate φ. At φ = 0.9 there is 0.48 pp left because the ensemble has collapsed
into a single classifier.

## Provenance

### Two result sets in `data/` were never computed from data

**`sota_perfold_fscores.csv` and `sota_comparison_summary.csv`** — the
comparison against META-DES, DELAK, KNORA-U and KNORA-E behind Table III and
Fig. 8. No code in this folder or the parent project produces them; grep for
META-DES, KNORA or deslib across the source tree returns nothing. They are
internally consistent — the per-fold vectors reproduce the summary means, SDs,
ranks, win counts and p-values exactly — so an internal consistency check does
**not** detect the problem.

This is the highest-priority open item in the project: all three referees asked
for the DELAK comparison specifically, so the table that answers the most-cited
review gap is currently the one with no measurement behind it. It is measurable
here. META-DES, KNORA-U and KNORA-E ship in DESlib 0.3.7, which installs
cleanly (`pip install deslib`). DELAK (K-means DES, Guo et al. 2021) is not in
DESlib and must be implemented; the DDEL-KMeans variant inside
`exp1_gmm_vs_kmeans.py` is structurally close and is the place to start. Use
`StratifiedKFold(10, shuffle=True, random_state=42)` so the folds match every
other experiment here. `fig8_sota.py` needs no edit once the CSV is real — it
recomputes its p-values from whatever vectors it is given.

**`clustering_ablation_summary.csv`** — its HAR arm is simulated, which its own
`Provenance` column states (`HAR SIMULATED / synthetic MEASURED`). The synthetic
sweep in the same experiment *is* measured and is the load-bearing part: the
ARI advantage of GMM over K-means on eccentric, overlapping components
(0.702 vs 0.235) comes from `clustering_ablation_sweep.csv`, which
`exp1_gmm_vs_kmeans.py` writes. Only the HAR row is unmeasured.

Everything else in `data/` is written by a script here, except the two files
below.

### Extracted from the original notebook

`data/boxplot_stats_measured.csv` and `data/best_ensemble_results.csv` were
extracted from the stored cell outputs of `../code/Main_Thp.ipynb` — cell 12
holds the printed per-configuration statistics for the full 45-configuration
grid, cell 17 selects `n_c==6 and phi==0.5`. The original pickles are not on
this machine, but the notebook's own printed output is the record, and the
figures agree with it. Everything else in `data/` was produced by the scripts
here.

`scripts/base_train_original.py` and `scripts/evaluation_original.py` are the
author's original training and evaluation code, kept verbatim for reference.
They contain Colab paths (`/content/drive/...`) and are not wired into
`run_all.sh`; `check_user_funcs.py` is the script that exercises the author's
`Funcs/` modules against the measured numbers.
