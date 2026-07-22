# DDEL-GMM — Reviewer Response Triage (TETCI-2024-1262)

Cross-checked against `document.tex` and `comments.txt`. Each row: what the referee asked, current status in the draft, and whether the fix needs **new experiments** or is **rewrite-only**.

## A. NEW EXPERIMENTS REQUIRED (acceptance-critical — all 3 referees converged here)

| ID | Experiment | Raised by | Current status | Notes |
|----|-----------|-----------|----------------|-------|
| E1 | Empirical comparison vs **DELAK** (K-means + distance weighting) | R1 #15,#16; R3 #1 | Discussed only in prose (lit review lines 101–113); never run | Core pitch is "GMM beats K-means" — must be shown, not asserted |
| E2 | Empirical comparison vs **FH-DES** | R1 #15,#16 | Not mentioned anywhere in manuscript | Explicitly demanded |
| E3 | **GMM vs K-means self-comparison** on non-spherical / overlapping clusters | R3 #1(i); R2 #8 | Not done | Justifies GMM choice empirically |
| E4 | Comparison vs **bagging / boosting** (no clustering) | R3 #2(ii) | Not done | Tests whether density weighting beats classic ensembles |
| E5 | **Concept-drift / data-stream** simulation | R2 #2,#4 | Claims "dynamic/adaptive" but never simulates changing environment | Needs streaming eval |
| E6 | **Real-world case study** (e.g., medical) | R3 #5(v) | Single HAR dataset only | Add a public medical dataset |

**Structural root cause:** the current "comparison" (DensityE vs DistE vs AvgE vs MaxE) is four *internal* weighting variants of the same method — no external published baseline is actually run. This is the single biggest driver of the rejection.

## B. REWRITE-ONLY (no compute)

| Referee item | Status | Action |
|---|---|---|
| R1 #17 Conclusion missing | Added | Verify it states quantified contributions |
| R1 #2 Paper-structure outline (end of intro) | Added | — |
| R1 #4 DSOC undefined | Fixed ("Dynamic Selection on Complexity") | — |
| R1 #5 Reference as sentence subject | Mostly fixed | Check "B. et al." (line 116) |
| R1 #6 Positioning in Lit Review | Added | — |
| R1 #10,#14 Define 4 methods + metrics in Results | Added | — |
| R1 #12 Lessons learned at end of Results/A | Added ("Key Insights") | — |
| R1 #8 "compete9nce" typo | Fixed | — |
| R1 #1 DES-limitations recap before contributions | Partial | Add explicit recap + numbered contributions list |
| R1 #7 / R3 #3 Methodology re-litigates related work | Still present (~line 140) | Move comparisons to Lit Review; trim GMM derivation to a citation |
| R1 #9 Fig 1 should show GMM | Not done | Revise training-phase diagram to depict GMM sampling |
| R1 #11 Table 1 placement | Hardcoded "Table 1" | Use `\ref{}`; confirm placement near reference |
| R1 #13 Fig 3/4 swap | **Labels cross-wired** (lines 444–453) | Fix label/caption/filename mapping |
| R2 #1 Abstract: how high-dim handled | Not done | State PCA (157 PCs / 95% variance) in abstract |
| R2 #3 Awkward name "DDELA-GMM" | Fixed (now DDEL-GMM throughout) | — |
| R2 #6 Lit-review organization / II.E repeats | Fuzzy Min-Max removed | Tighten II.E redundancy |
| R2 #8 GMM inefficiency in high-dim | PCA in body only | Add explicit paragraph defending GMM-after-PCA |
| R3 #4 Justify addressed limitations with evidence | Not done | Depends on E1–E6 |
| R3 #4(iv) Explain *why* each experiment designed | Not done | Restructure Results as rationale→result→insight |

## C. Additional issues found (not explicitly flagged by referees)

- **Duplicated paragraph:** lines 121 and 132 are identical (the "generalization phase" sentence appears twice in Methodology).
- **Figure label cross-wiring** confirmed: the block including `fscore_vs_phi` carries `\label{fig:fscore_vs_clusters}` and vice-versa, so in-text refs resolve to the wrong figures.

## Missing to run experiments
The folder contains only the manuscript, figures, and `references.bib` — no dataset or experiment code. To run E1–E6 I need either the original HAR feature matrix, or approval to reconstruct on public data (UCI HAR + a public medical set + synthetic non-spherical benchmarks for E3).
