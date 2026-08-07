# Referee Report

**Manuscript:** Density-Based Dynamic Ensemble Learning Algorithm via Gaussian Mixture
Model Clustering for Enhanced Predictive Analytics (DDEL-GMM)
**Venue:** IEEE Transactions on Emerging Topics in Computational Intelligence
**Status:** Revised resubmission following rejection with major concerns from three referees
**Reviewed from:** `document.tex` (677 lines) and a freshly compiled 22-page PDF, plus the
eleven `\input`-ed table files that render into it. No project code or result files were
consulted.

---

## 1. Summary of the Submission

The paper proposes DDEL-GMM, a dynamic ensemble method in which a Gaussian mixture model
partitions the training set into `K` overlapping subsets, a base classifier is trained on
each, and predictions on a test instance are combined by weights derived from that
instance's density under each mixture component. The method is evaluated on UCI HAR
(10,299 instances, 157 principal components) against four internal aggregation variants
(DensityE, DistE, AvgE, MaxE), against published dynamic ensemble selection methods
(DELAK, META-DES, KNORA-U, KNORA-E, FH-DES), against classic non-clustering ensembles,
under simulated concept drift, and on an additional medical dataset.

## 2. Overall Assessment

**Recommendation: Major Revision.**

This revision is substantially more serious than the version the original three referees
rejected. Five of the gaps that drove that rejection are now closed with real experiments
rather than argument, and §4.4 in particular is written to a standard I rarely see: the
authors state plainly that their method is *not* statistically separated from a single
logistic regression on this dataset, quantify the 25x cost of the accuracy it does not
significantly gain, and redirect the reader to the ablations where the design choices
actually earn their place. That paragraph is the strongest evidence in the paper that the
authors are reporting rather than advocating.

The problem is that the manuscript is now travelling at two speeds. The sections written
for this revision (§4.3-§4.6) are rigorous and candid. The sections carried over from the
original submission (§4.1, §4.2, and the Conclusion) have not been brought into line with
them, and they contain numerical statements that contradict the paper's own tables. A
referee who reads §4.1 against Table I will find four consecutive mismatches, and one who
reads the medical case study against Table VIII will find the prose asserting a result the
table refutes. These are not presentational blemishes; they are claims the evidence in the
same document does not support, and they must be fixed before the paper can be accepted.

None of the defects I found is fatal to the method. All are fixable by correcting prose to
match existing tables, naming a dataset, and adding reproducibility detail. I recommend
major revision rather than minor because the numerical inconsistencies are systematic
rather than isolated, and because the central empirical justification for GMM over K-means
(§5) needs to be reconciled with the paper's own high-dimensional ablation.

## 3. Status of the Original Referees' Concerns

| # | Original concern | Status | Evidence |
|---|---|---|---|
| a | No conclusion section | **Closed with reservations** | §Conclusion now exists; lacks a limitations paragraph (M4) |
| b | No empirical DELAK / FH-DES comparison | **Closed** | Table VII gives head-to-head on identical protocol; DELAK 0.9534, FH-DES 0.9571, DDEL-GMM 0.9724 |
| c | No non-spherical / overlapping cluster experiment | **Closed** | §4.3 factorial sweep over overlap and dimension, three seeds, ARI and accuracy reported |
| d | No bagging / boosting comparison | **Closed** | Table VI: bagging, RF, AdaBoost, gradient boosting, single LR, single SVM |
| e | Literature review flow, undefined abbreviations | **Closed** | DSOC *is* defined at first use (line 106, "Dynamic Selection on Complexity (DSOC)"); no references used as sentence subjects remain |
| f | Positioning recap before contributions | **Partially closed** | Positioning block present in §1; still reads as an inserted block rather than integrated prose |
| g | Methodology re-litigating related work | **Partially closed** | Some comparative framing remains in §3 ("unlike hard, distance-based partitions") |
| h | Typos, e.g. "compete9nce" | **Closed** | No occurrence remains in the source |
| i | Figure/table ordering and placement | **Closed** | Every float now lands at or after its first textual mention; Fig. 3/4 no longer transposed |
| j | No concept drift experiment | **Closed** | §4.6, Table IX, Fig. 11; ten drift windows |
| k | GMM inefficiency in high dimensions | **Partially closed** | §4.3 Result 2 confronts it directly and honestly, but §5 and the Conclusion do not absorb the consequence (M7) |
| l | No real-world case study | **Partially closed** | §4.5 exists, but the dataset is never named (M2) and its prose contradicts its table (M3) |

## 4. Major Points

**M1. The prose in §4.1 disagrees with Table I in four consecutive statements.**
Lines 359-361 state that DensityE with logistic regression "attains a mean score of 0.973,
closely followed by the support vector machine base learner with a mean score of 0.969,"
and that KNN achieves "0.958"; the decision tree is said to peak at "0.841" under DistE.
Table I reports 0.978, 0.973, 0.963 and 0.843 respectively. Every value in the text is
displaced from the table, and the LR/SVM figures quoted in the text are exactly the table's
SVM/KNN rows — the prose appears to have been written against an earlier version of the
table and never updated. As it stands the paper misreports its own headline internal
result by half a point and misidentifies which base learner is best.
*Fix: rewrite lines 359-361 against the current Table I. Reanalysis is not required; the
table is internally consistent.*

**M2. The medical case study never names its dataset.**
§4.5 reports accuracy 0.968, F 0.969, AUC 0.995 on "a real-world medical classification
dataset," and Table VIII carries the literal string `medical` in its Dataset column for
every row. No source, size, class balance, feature count, or citation is given. A referee
cannot judge whether the result is meaningful, and a reader cannot reproduce it. Since this
experiment exists specifically to answer Referee 3's request for a real-world case study,
an unnamed dataset does not discharge that request.
*Fix: name the dataset, cite it, and state n, feature count, class prevalence. If it cannot
be named for licensing reasons, say so explicitly and characterise it quantitatively.*

**M3. The case-study prose asserts a result its own table contradicts.**
Line 612 states DDEL-GMM "wins all ten folds against each baseline" and that improvements
are significant "at the attainable two-sided floor (p = 0.002 at n = 10), except for
META-DES where p = 0.014." Table VIII reports p = 0.004 against DELAK and p = 0.014 against
META-DES. These are mutually exclusive: winning all ten folds forces the exact two-sided
Wilcoxon signed-rank p to 2/2^10 = 0.00195, which rounds to 0.002. A p of 0.004 corresponds
to nine wins and one loss; p = 0.014 to a weaker pattern still. So either the fold counts or
the p-values are wrong, and the text's blanket "wins all ten folds against each baseline" is
false for at least two of the four baselines.
*Fix: recheck the per-fold outcomes and correct whichever of the two is wrong. Note that
the paper handles this same point correctly in §4.4, where p = 0.002 is explicitly
described as the attainable floor for ten folds — §4.5 should match that care.*

**M4. The Conclusion does not meet the standard the Results section sets.**
The added Conclusion is more candid than the original referees might have feared — it does
concede that DDEL-GMM is "statistically indistinguishable from bagging and from strong
single linear models on this dataset." But it contains no limitations paragraph, never
mentions computational cost, and closes by claiming the work "advances the state-of-the-art
in dynamic ensemble learning" on the basis of one benchmark and one unnamed dataset. The
§4.4 cost analysis (81.1 s vs 13.9 s per fold, 25x once nested selection is included) and
the §4.3 dimensional limitation are the two most useful things a practitioner could take
from this paper, and neither survives into the Conclusion.
*Fix: add an explicit limitations paragraph carrying forward the cost finding, the
single-benchmark scope, and the dimensional bound from §4.3 Result 2.*

**M5. Reproducibility detail is insufficient for independent replication.**
The paper does not state: random seeds for the main HAR experiments (three seeds are stated
for the synthetic sweep only); EM initialisation strategy and convergence tolerance; the
covariance parameterisation used in the main experiments — significant, given §4.3 shows
the four parameterisations behave very differently at p = 157; base-learner
hyperparameters (LR penalty and solver, SVM C and kernel, KNN k, tree depth); and the
DELAK/META-DES/KNORA settings beyond "DESlib defaults." Two configuration choices *are*
documented with exemplary care (SVM trained to convergence, AdaBoost at depth 3, both
justified explicitly as avoiding a flattering comparison) — the rest of the setup deserves
the same treatment.
*Fix: add a configuration table. No new experiments needed if the settings are on record.*

**M6. The GMM-over-K-means justification is in tension with the paper's own ablation.**
§4.3 Result 2 reports honestly that the full-covariance advantage over K-means is bounded
by dimensionality and disappears by d = 157. The main HAR experiments run at exactly
p = 157. The paper nonetheless reports a +1.1-point clustering contribution at that
dimension and treats it in §5 and the Conclusion as vindication of the mixture model's
covariance flexibility. If the ablation is right, that +1.1 points cannot be attributable
to the mechanism the paper credits; soft assignment or implicit regularisation is the more
plausible explanation. The paper should not be penalised for running the experiment that
exposed this — but it must draw the consequence rather than leave the two claims side by
side.
*Fix: reconcile explicitly in §5 and the Conclusion. This is an interpretation change, not
a new experiment.*

**M7. Empirical scope remains narrow for the generality claimed.**
Substantive evaluation rests on one benchmark (UCI HAR) plus one unnamed medical dataset.
HAR is, as the authors themselves note, close to saturated for linear models at ~0.972
macro F — which is precisely why the non-clustering comparison cannot separate the methods.
A claim to advance dynamic ensemble learning generally needs datasets where the ceiling is
lower and the cluster structure is genuinely anisotropic, ideally at p < 50 where §4.3
predicts the GMM advantage should be largest.
*Fix: this one does require new experiments — three to five additional benchmarks, chosen
where the method's own theory predicts it should win.*

**M8. Table XI (`tab:nonspherical`) is compiled into the document but never referenced.**
The `nonspherical.tex` table is present in the table set and typeset, but no `\ref` to it
exists anywhere in `document.tex`. It appears in the PDF as an orphan.
*Fix: either cite it in §4.3, where it is directly relevant, or remove it.*

## 5. Minor Points

1. `T` (responsibility temperature) first appears in the §4.4 model-selection grid; it is
   never defined in the Methodology, where it belongs.
2. Line 583 explains that absolute values are not comparable across tables because
   protocols differ (0.9791 in Table VI vs 0.972 in Table V). This is correct and
   commendable, but the differing figures for the same method will still confuse readers —
   consider a footnote on each affected table rather than one explanation in the text.
3. The Fig. 5 caption ("Training phase of proposed model") and Fig. 6 caption
   ("Generalization phase of proposed model") are not self-contained; neither describes
   what the diagram shows.
4. Abstract: "degrades 3.6x less than DELAK" is ambiguous phrasing. The underlying numbers
   (0.0074 vs 0.0263 vs 0.0647 F-score loss) are unambiguous and would read better stated.
5. The decision-tree base learner collapses to 0.834-0.843 across all four aggregation
   schemes while linear learners reach 0.96+. The text calls this "significantly lower
   performance"; it is closer to a failure mode and deserves a sentence on why the
   framework depends on base-learner stability.
6. `\greenhighlight` and `\markfordelete` macros remain defined in the preamble (currently
   no-ops). Strip them before final submission.
7. Bibliography: entry `arco_probabilistic_2023` contains a UTF-8 sequence that survives
   into `document.bbl` as U+FFFD and prints as a missing glyph in the reference list.
8. Four overfull hboxes remain (compile log lines 861, 982, 1235, 1345); the one at 53.1 pt
   is visible in the PDF.
9. Times font shapes (`TU/ptm`) fall back under the Unicode engine. Harmless for review,
   but IEEE production will want it resolved.
10. Tense alternates between present and past across §3 and §4.

## 6. What I Verified, and What I Could Not

Checks I performed and passed:
- **Nemenyi critical difference.** The paper states CD = 2.85 for k = 7, N = 10. Recomputed:
  q(0.05, 7) = 2.949, CD = 2.949 * sqrt(7*8/(6*10)) = **2.849**. Correct.
- **Friedman omnibus.** chi-squared = 50.40 on df = 6 giving p = 3.9e-9 is consistent.
- **Wilcoxon floor.** The claim that p = 0.002 is the attainable two-sided minimum at
  n = 10 is correct (exact value 0.00195), and the paper is right to flag it as a floor
  rather than an effect size.
- **The 14-fold dispersion claim** (SD 0.003 for DensityE vs 0.043 for DistE) matches
  Table I.
- **Concept-drift figures** in the abstract (3.6x, 8.7x) match Table IX exactly.
- **Float placement.** Every figure and table lands at or after its first mention.
- **Cross-references.** Zero undefined citations or references in the compile log.

What I could not verify, and no referee could: whether any reported number was actually
produced by the experiment described. This review establishes internal consistency and
correctness of interpretation only. The mismatches in M1 and M3 are visible precisely
because they are internal contradictions; a number that is wrong *consistently* across
text and table would be invisible to me.

I also note three criticisms that a less careful reading would produce and that I checked
and **reject**: the abstract does *not* overclaim significance (it says "while matching the
strongest linear and bagged baselines on stationary data," which is accurate); DSOC *is*
defined at first use; and "compete9nce" has been fixed. The authors should not be asked to
address these.

## 7. Revision Triage

**Requires only rewriting (no new computation):** M1, M2 (assuming the dataset identity is
on record), M3 (assuming per-fold outcomes are on record), M4, M6, M8, and all minor points.
This is the bulk of the report and could be turned around quickly.

**Requires reanalysis of existing runs:** M5 — the configuration details should already
exist in the experiment scripts; they need extracting and tabulating, not re-running.

**Requires new experiments:** M7 alone. Additional benchmark datasets, ideally
lower-dimensional with anisotropic cluster structure, chosen where §4.3's own theory
predicts the method should show its largest advantage.

The distinction matters for scheduling: everything that makes this paper *incorrect* as
opposed to *narrow* is in the first category.
