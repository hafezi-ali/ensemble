# DDEL-GMM — Required Changes Ranked by Difficulty (TETCI-2024-1262)

Based on the edited `comments.txt`. Note: item R1#15 (explicit DELAK/FH-DES comparison) was removed and
R1#16 softened to a generic "state-of-the-art comparison" — but an external-baseline comparison is still
required by R1#16, R2#7, and R3#1.

## Tier 1 — Trivial (minutes, pure text)
1. "compete9nce" typo (R1#8) — already fixed; confirm none remain.
2. Rename DDELA-GMM -> DDEL-GMM (R2#3) — already done in .tex.
3. Reference-as-sentence-subject -> "Guo et al." style (R1#5) — one leftover: "B. et al." line 109 (fixed -> "Sowkarthika et al.").
4. Define "DSOC" on first use (R1#4) — already done.
5. Fix ambiguous "This method shows the potential..." sentence (R2#5 / R1#3) — delete dangling recap.

## Tier 2 — Easy (under ~1 hour each, localized)
6. Swap Figure 3/4 (R1#13) — labels are cross-wired in .tex (fscore_vs_phi block has label fig:fscore_vs_clusters and vice-versa).
7. Add PCA statement to abstract (R2#1) — "157 PCs retain 95% variance."
8. Define the four ensemble methods at start of Results (R1#10) — partly done.
9. State metrics up front in Results (R1#14) — partly done.
10. Place Table 1 where referenced; use \ref{} not hardcoded "Table 1" (R1#11).
11. Paper-structure outline at end of intro (R1#2) — already added.
12. Remove duplicated paragraph (Methodology lines 121 & 132 identical) — not a referee item, free fix.

## Tier 3 — Moderate rewriting (~half day, restructuring, no new data)
13. DES-limitations recap + numbered contributions list before the contribution, in intro (R1#1, #6).
14. Reorganize Literature Review: tighten II.E redundancy, drop irrelevant threads (R2#6); close each subsection before recap (R1#3).
15. Move "how we differ from X" out of Methodology into Lit Review (R1#7, R3#iii); trim GMM/E-M derivation to a citation (R3#iii).
16. Redraw Figure 1 to show the GMM sampling step (R1#9).
17. Add paragraph defending GMM in high dimensions via the PCA-to-157-dims step (R2#8).

## Tier 4 — Hard (new experiments + compute; the actual rejection drivers)
18. External state-of-the-art comparison (R1#16, R2#7, R3#1-ii) — run >=1 competing published method (DELAK is the natural choice).
19. GMM vs K-means self-comparison (R3#1-i, R2#8) — ideally on non-spherical/overlapping data.
20. Comparison without clustering vs bagging/boosting (R3#ii).
21. Concept-drift / data-stream experiment (R2#2, #4) — largest single new build.
22. Real-world case study, e.g. medical (R3#v) — second dataset, different domain.
23. Justify each addressed limitation with results evidence; rewrite Results as rationale->result->insight (R3#iv, R3#ii#i) — depends on 18-22.

## Bottom line
Tiers 1-2 are done or a couple hours of editing. Tier 3 is a focused rewrite day. Tier 4 is what caused the
rejection: all three referees demanded external baselines, but the manuscript compares only internal variants
(DensityE/DistE/AvgE/MaxE) of its own method. No Tier 1-3 fix changes the resubmission outcome if Tier 4 is empty.
