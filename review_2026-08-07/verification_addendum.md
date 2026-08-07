# Verification Addendum — Revision 2

**Date:** 2026-08-07
**Scope:** `manuscript/document.tex` only (tables unchanged since the first review), plus the
newly compiled 22-page PDF. No project code or result files consulted.

## Build status

`document.tex` compiles cleanly with tectonic: exit 0, **22 pages**, **zero undefined
citations or references**. The 208 "undefined" strings in the log are all `TU/ptm` font-shape
substitutions (Times unavailable under the Unicode engine), not reference errors.

## Point-by-point status against the referee report

| Point | Status | Evidence in the revised source |
|---|---|---|
| **M1** — §4.1 prose disagreed with Table I in four consecutive numbers | **Fixed** | Prose now reads lr 0.978 / svm 0.973 / knn 0.963, and DistE-dt 0.843, all matching `ensemble_comparison.tex` exactly. The row-shift is gone and the paper now correctly identifies LR as the best base learner. |
| **M2** — medical case study never named its dataset | **Resolved by deletion** | The entire *Real-World Medical Case Study* subsection and its `\input{../tables/case_study.tex}` were removed. No dangling `tab:case_study` reference, and neither abstract nor conclusion still claims a case study. Correct as a repair; see the regression note below. |
| **M3** — case-study prose claimed a ten-fold sweep its own table's *p* = 0.004 forbade | **Resolved by deletion** | Same removal. The arithmetic contradiction no longer appears anywhere. |
| **M4** — Conclusion did not meet the standard the Results set | **Fixed** | A **Limitations** paragraph now closes the Conclusion, carrying forward the 5.8×/25× cost ratio, the *d* = 157 dimensional bound, and single-benchmark scope. The Conclusion's headline *p*-values (DELAK 0.002, META-DES 0.019, KNORA-U/E 0.002; bagging 0.625, single LR 0.492) all match `sota_comparison.tex` and `noclustering.tex`. |
| **M5** — insufficient reproducibility detail | **Fixed** | New §III-D *Experimental Configuration and Reproducibility* (`subsec:config`) with Table II: hyperparameters, software settings, seed policy (single common fold seed for paired comparisons; three seeds per cell in the synthetic sweep), k-means++ EM initialisation, 1e-4 log-likelihood tolerance, 1e-6·I covariance regularisation. |
| **M6** — GMM-over-K-means justification in tension with the paper's own ablation | **Fixed** | New passage reattributes the +1.1-point margin from full-covariance flexibility (which §IV-F shows vanishes by *d* = 157) to soft assignment and implicit regularisation. The reattribution is repeated in the Limitations paragraph rather than left only at the point of use. |
| **M7** — empirical scope narrow | **Not addressed; regressed** | Evaluation now rests on UCI HAR plus the synthetic geometry sweep alone. See below. |
| **M8** — Table XI (`tab:nonspherical`) compiled but never referenced | **Fixed** | Now cited in the §IV-F text: "Table~\ref{tab:nonspherical} extends this comparison across four synthetic cluster geometries." |

Minor points: the highlight macros `\greenhighlight` / `\markfordelete` are now defined as
no-ops with a "stripped for submission" comment (m6 — acceptable, though IEEE production will
prefer them gone entirely); base-learner dependence on decision trees now has a dedicated
sentence in the Discussion (m5). Still open: the responsibility temperature *T* is still
introduced only in the §IV model-selection grid, never defined in the Methodology (m1); Fig. 5
and Fig. 6 captions remain non-self-contained (m3); four overfull hboxes remain (m8); the
bibliography entry `arco_probabilistic_2023` still mis-renders — the compiled reference list
prints "M. ff. Berbís" where the source has `Berbís, M. Álvaro` (m7).

## One regression the authors should be aware of

Deleting the medical case study is a legitimate way to dispose of M2 and M3 — an unnamed
dataset carrying a contradictory claim is worse than no case study. But that subsection existed
to answer Referee 3's request for a real-world case study, and that request is now open again.
The evaluation rests on a single benchmark plus synthetic data, which is exactly the M7 scope
concern, now sharper than it was.

If the case-study data is real and the dataset can be named, restoring it with the correct
*p*-values would close both M7 and Referee 3 at once. If it cannot be named, an additional
public benchmark — ideally lower-dimensional with anisotropic cluster structure, where §IV-F's
own theory predicts the largest advantage — is the cleaner substitute.

## Consistency checks re-run on the revised text

- Conclusion *p*-values ↔ `sota_comparison.tex` / `noclustering.tex`: match.
- "+1.1 F-score points over K-means": 0.972 − 0.961 = 0.011 in `clustering_ablation.tex`: match.
- "twenty-one-fold reduction in dispersion": SD 0.002 (DensityE-lr) vs 0.042 (DistE-lr) = 21×: match.
- Concept-drift ratios 3.6× / 8.7× in the abstract ↔ Table IX: match.
- Every figure and table lands at or after its first mention; zero undefined cross-references.

## Revised assessment

The three findings that carried the *major revision* decision (M1, M2, M3) are all disposed of,
two by correction and one by removal, and M4, M5, M6 and M8 are genuinely addressed rather than
gestured at. On the internal-consistency grounds a referee can actually check, the manuscript is
now in materially better shape than the version reviewed this morning.

The one substantive matter still standing is scope (M7), and the case-study deletion has made
it more visible rather than less. That is a *minor revision* question — it does not make the
paper incorrect — but it is the point a referee will press on next.
