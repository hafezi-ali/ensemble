# Verification Addendum 3 — Revision Round 3

**Manuscript:** DDEL-GMM (IEEE TETCI resubmission)
**Source checked:** `manuscript/document.tex` as of this round, plus the eleven
`\input`-ed table files and `references.bib`
**Build:** `document_compiled_rev3_2026-08-07.pdf` — 22 pages, 11 tables (I–XI),
11 figures (1–11), compiled clean apart from the items below
**Scope:** `.tex` and compiled PDF only, per the standing instruction. No project
code or result files were consulted.

---

## 1. What changed since the previous build

Four edits, all aimed at the minor points left open in the previous addendum.

| # | Edit | Location | Verdict |
|---|------|----------|---------|
| 1 | New **"Responsibility temperature"** paragraph defining `T > 0`, with tempered-weight equation `eq:temperature` | §III, lines 310–316 | **Effective, with one defect** — see 2.1 |
| 2 | `\emergencystretch=1em` added to the preamble | line 17–19 | **No effect** — see 2.2 |
| 3 | Fig. 2 (diagnostics) caption expanded to be self-contained | line 507–519 | **Effective** |
| 4 | Fig. 5 (SOTA comparison) caption expanded to be self-contained | line 584 | **Effective** |

No table file changed in this round; all eleven are byte-identical to the previous build.

### On edits 3 and 4

Both captions now stand alone. Fig. 5's caption names the method in full, names all
four baselines it is plotted against (DELAK, META-DES, KNORA-U, KNORA-E), states the
dataset with its size and class count, states that all methods share the same ten-fold
stratified splits and base-learner pool, defines the error bars, and defines the
significance annotation. That is what a self-contained caption looks like; the minor
point that raised it is closed. Fig. 2's caption similarly now names the dataset,
dimensionality, cluster count, base-learner count, the meaning of `φ`, and the fold count
behind the error bars.

---

## 2. Defects found in this round

### 2.1 Broken cross-reference — the one blocking item

The new temperature paragraph closes with:

> "The value of `T` is selected by nested cross-validation alongside `K` and `φ`
> (Section `\ref{subsec:noclustering}`)."

**`subsec:noclustering` is not defined anywhere in the document.** I enumerated every
`\label{...}` in the source; the label does not exist. The compiler agrees — the log
carries exactly one undefined-reference warning, on page 8, and the rendered PDF prints
**"(Section ??)"** at that point. This is a visible defect in the typeset output and would
be flagged immediately at desk check.

The subsection that actually describes the `T` selection protocol is
**"Comparison with Non-Clustering Ensemble Baselines"** (line 626), whose
"Model selection" paragraph (line 632) states that `K`, `φ`, and `T` are selected by
nested cross-validation. That subsection carries no label.

**One-line fix.** Add the label to that heading:

```latex
\subsection{Comparison with Non-Clustering Ensemble Baselines}\label{subsec:noclustering}
```

The alternative — repointing the reference at `subsec:config`, which does exist — is
defensible but weaker, because Table I in that subsection does not currently state the
`T` grid (see 2.3).

### 2.2 The overfull-hbox fix did not take, and cannot

`\emergencystretch=1em` was added with the comment "Prevent overfull hbox warnings by
allowing extra inter-word stretch." The build after the edit still reports the **same four
overfull boxes, at the same widths**:

| Location | Overfull by |
|---|---|
| `tables/noclustering.tex` | 53.1 pt |
| `document.tex` line 392 (Table I, configuration) | 25.9 pt |
| `tables/sota_comparison.tex` | 6.7 pt |
| `tables/ensemble_comparison.tex` | 4.7 pt |

The reason is structural, not a matter of tuning the value: `\emergencystretch` adds
stretch to *paragraph* line-breaking. All four boxes are **tabular rows**, where TeX has
no inter-word stretch to exploit — the row is as wide as its columns make it. Raising the
value will not change the outcome.

What does work, in order of preference: shorten the offending cell text (the 53 pt
overrun in `noclustering.tex` is the one worth attacking first, and is large enough to be
visible as text intruding into the column gutter), reduce `\tabcolsep`, wrap the table in
`\resizebox{\columnwidth}{!}{...}`, or move the widest column to a `p{}` specification so
its contents can wrap. The two small overruns (4.7 pt and 6.7 pt) are below the threshold
where anything is visible on the page and can be left alone.

### 2.3 `T` is defined but still absent from the reproducibility table

The new paragraph defines `T` and the results text says it is tuned by nested CV, but
**Table I** — the configuration and reproducibility table, which lists the `K` value, the
`φ` value, the EM initialisation and tolerance, the covariance regularisation and type,
and the full hyperparameter grid for every base learner — does not list `T` at all.
Neither the searched grid nor the selected value appears anywhere in the manuscript.

A reader cannot reproduce the method without it. Add a row to Table I giving the grid and
the selected value, in the same style as the `C ∈ {0.01, 0.1, 1, 10}` entries already
there. This is a one-row edit against numbers the authors already have.

### 2.4 Not a defect: the UTF-8 warnings

The build log emits `Invalid UTF-8 byte or sequence at line 11 replaced by U+FFFD` three
times. I traced it: the file is **`algorithm.sty:11`** — a package from the TeX
distribution's own bundle, not manuscript source. Every manuscript file passes a strict
UTF-8 validation (`document.tex`, `references.bib`, and all eleven table files). The
warning has no effect on the output and **requires no action from the authors**; I record
it only so nobody spends time hunting for it.

---

## 3. Status of the report's findings after this round

| Finding | Status |
|---|---|
| M1–M6 (major points) | Closed in earlier rounds; unchanged and still closed |
| `T` undefined in methodology | **Closed** — now defined with an equation |
| `T` missing from reproducibility table | **Open** — 2.3 |
| Figure captions not self-contained | **Closed** — 2.1's table, edits 3 and 4 |
| Overfull hboxes | **Open** — 2.2; previous fix attempt was structurally unable to work |
| Undefined cross-reference | **New this round** — 2.1; introduced by the temperature edit |
| Medical case study removed | **Still open from Addendum 2** — the subsection that answered Referee 3's real-world-domain request remains deleted rather than repaired |

---

## 4. Recommendation

Unchanged: **Major Revision**, and the substance of that recommendation now rests almost
entirely on the case-study removal noted in the previous addendum rather than on anything
in this round. The three items above are small:

1. Add `\label{subsec:noclustering}` to the non-clustering subsection heading — one line, closes the visible `??` in the PDF.
2. Add a `T` row to Table I — one row.
3. Shorten the widest cell in `noclustering.tex`, or wrap that table in `\resizebox` — one table.

None requires new computation. All three can be done and recompiled in a single pass.

---

## 5. What this check does and does not establish

It establishes that the source compiles, that the edits made this round do what their
authors intended in three cases out of four, and that one of them introduced a reference
that does not resolve. It establishes nothing about whether any reported number was
produced by the experiment described — that is outside what any referee working from the
`.tex` and PDF can determine, and it remains outside what I have checked.
