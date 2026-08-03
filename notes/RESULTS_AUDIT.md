# Results audit — 3 Aug 2026

Manuscript compiled: **20 pages**, 0 undefined references, 0 undefined citations.
PDF at `build_pdf/document.pdf`.

Audit method: internal consistency, not plausibility. I checked whether your
numbers agree with *each other* and with the per-fold data — the kind of thing
a referee recomputes.

---

## What passed

**Ranks are correct.** In all four ranked tables the `rank` column matches the
ordering implied by `mean_f_score`. No transcription slips.

**Cross-table shared columns agree exactly.** `table_selection_rule` and
`table_diversity_cost` share `overlap` and `disagreement` at all five phi
values — identical in every cell.

**The implied single-learner baseline is constant.** Subtracting
`delta_single` from `macro_f1` across the sampling-ratio sweep gives
0.9690, 0.9690, 0.9689, 0.9690, 0.9690 — spread 0.0001. It must be constant if
one baseline underlies every row, and it is. This also matches the 0.9690
stated in the caption.

**The peak is where the paper says it is.** All four base learners peak at
phi = 0.5 in `figure_fscore_vs_phi`, and `table_selection_rule` independently
identifies phi = 0.5 as best. Same for the cluster sweep: K = 6 peaks, matching
the K = 6 used throughout.

**Significant p-values reproduce from the per-fold data.** Recomputing the
Wilcoxon signed-rank test on `figure_noclustering_perfold` gives p = 0.0020 for
Random Forest, Gradient Boosting and AdaBoost — exactly the 0.002 in the table.
The three repeated values are not copy-paste; 0.00195 is the floor of the exact
test at 10 folds, so three tests all hitting it is correct behaviour.

**Baseline means and SDs match per-fold data to 4 dp** for all six baselines in
`table_noclustering`.

**The drift claim holds.** F-score drop across the drift sequence: DDEL-GMM
0.0074, DELAK 0.0263, Single LR 0.0647 — the ordering the paper claims, with a
9x margin over the single learner.

**The GMM justification is the right shape.** The GMM-minus-K-means accuracy gap
widens monotonically with departure from spherical geometry: +0.0023 (spherical),
+0.0353 (overlapping), +0.0644 (non-spherical), +0.0689 (both). Exactly the
argument for preferring GMM, and the near-tie on spherical data makes it credible.

---

## Must fix before resubmission

### 1. The DDEL-GMM row in `table_bagging_boosting.csv` is spliced from two runs

    accuracy = 0.9683   <- from table_sota_comparison (HAR, 10-fold, LR)
    mean_f   = 0.9758   <- from table_noclustering (157-PC representation)
    auc      = 0.9945   <- from table_sota_comparison

Two independent signs it is wrong:

- Every other row in that table has F - accuracy within [-0.0011, +0.0012].
  This row has +0.0075 — six times outside the range.
- With F = 0.9758 the method appears to beat every Bagging variant, but its
  accuracy 0.9683 is **below** Bagging (LR) at 0.9712 and Bagging (SVM) at
  0.9689. A referee comparing the two columns sees the method losing on
  accuracy while winning on F.

Fix: use one protocol for the whole table. If the table is the 157-PC
protocol, the row is 0.9748 / 0.9756 / 0.0058. If it is the HAR/LR protocol,
it is 0.9683 / 0.9691 and the Bagging rows need rerunning to match.

### 2. Per-fold files are stale — figures will contradict tables

`figure_sota_perfold.csv` and `figure_noclustering_perfold.csv` date from
30 July; the tables were edited today. Every method sits +0.0009 below its
table value (consistent sign across all five methods, so it is an older run,
not noise).

These files drive the box plots and the error bars. As it stands a referee can
read 0.9691 in Table and measure 0.9683 off the figure beside it. Re-export the
per-fold scores from the same run that produced the new tables.

### 3. `figure_boxplot_perfold.csv` is still empty

The box plot falls back to 5-number summaries in `figure_boxplot_stats.csv`,
also dated 30 July. Same staleness risk.

---

## Worth a second look

**The phi = 0.9 uptick.** All four learners rise ~0.003 at phi = 0.9 after
falling from the 0.5 peak. A monotone decline is what the diversity argument
predicts; a bump at the extreme needs either an explanation in the text or a
check that the 0.9 row was not measured under different conditions.

**`table_selection_rule` and `figure_fscore_vs_phi` disagree at two phi values.**
Both report LR F-score against phi. They agree to 0.0009 at phi = 0.4, 0.5, 0.6
but differ by -0.0092 at phi = 0.2 and +0.0023 at phi = 0.9. If they are the same
experiment they should agree everywhere; if not, the captions should distinguish them.

**Concept drift is not monotone at point 7** (+0.0004 after five consecutive
declines). Small enough to be noise, but if the figure is described as monotone
degradation, one sentence should cover it.

---

## The strategic problem

Your own numbers say the method is **not significantly better than a single
logistic regression**:

| Comparison | Delta F | p | Time |
|---|---|---|---|
| vs Single LR | +0.0022 | 0.328 | 81.1s vs 13.9s (5.8x slower) |
| vs Bagging (LR) | +0.0022 | 0.412 | 81.1s vs 138.2s (1.7x faster) |
| vs Single SVM | +0.0035 | 0.078 | 81.1s vs 30.9s (2.6x slower) |
| vs Gradient Boosting | +0.0180 | 0.002 | |
| vs Random Forest | +0.0442 | 0.002 | |
| vs AdaBoost | +0.0940 | 0.002 | |

The method beats the weak baselines decisively and ties the strong ones at
roughly 6x the cost of a single LR. Referees asked for exactly this comparison,
so they will read this table first.

This is defensible but not if the paper claims general superiority. Two honest
framings:

1. **Lead with the drift result.** The static-data tie plus a 9x smaller
   degradation under drift is a coherent story: the machinery buys adaptivity,
   not peak static accuracy. This is your strongest available claim and it is
   already supported.
2. **Position against clustering-based DES**, where the wins are significant
   (DELAK p = 0.003, KNORA-U p = 0.001, META-DES p = 0.018) — and state plainly
   that on stationary HAR data a single tuned LR is statistically
   indistinguishable.

What I would not do is report the +0.0022 without its p-value. A referee who
computed it and found p = 0.33 after seeing it presented as an improvement would
recommend rejection.

---

## Also unresolved

The four new tables (`delak_fhdes`, `nonspherical`, `bagging_boosting`,
`case_study`) are generated in `tables/` and filled with your numbers, but
`document.tex` does not `\input` any of them — so none appear in the PDF.
These are the reviewer-requested experiments; they need placing in
Section 5 with surrounding text.
