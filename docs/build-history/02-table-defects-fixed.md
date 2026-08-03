# Critical Defects Found in Phase 1 Table Renderer

## Summary
The verifier only checked numeric values, missing 6 LaTeX markup defects that prevent compilation and lose content.

## Defects by Severity

### (1) *** WILL NOT COMPILE *** \mathbf in text mode
**Issue**: Bare `\mathbf{0.966}` outside `$...$` causes "Missing $ inserted" error.

**Current Problem**: make_tables.py emits `\mathbf{...}` for ALL bold cells.

**Fix Required**: 
- Use `\textbf{...}` in text-mode table cells
- Use `\mathbf{...}` ONLY when cell is already inside `$...$` (selection_rule and diversity_cost have exactly 1 each)

**Test**: No bare `\mathbf{...}` outside `$...$` in any generated .tex

---

### (2) *** \cite KEYS DROPPED *** Content regression
**Issue**: Bibliography citations vanish from tables.

**Current State**:
- sota_comparison: has 4 \cite in manuscript (META-DES, DELAK, KNORA-U, KNORA-E), generated has 0
- noclustering: has 4 \cite in manuscript, generated has 0

**Root Cause**: cite_key column added to CSVs but render logic never outputs it.

**Fix Required**:
- When cite_key is non-empty: emit `<method> \cite{<cite_key>}`
- When cite_key is empty: emit bare method name (DDEL-GMM, Single SVM)

**Test**: sota_comparison and noclustering each have exactly 4 `\cite{...}` calls

---

### (3) *** HEADER ROW LOST ITS BOLD ***
**Issue**: Original header cells are `\textbf{Method} & \textbf{Acc.} & ...` ; generated are bare.

**Current State**:
- selection_rule: 0 textbf in header (CORRECT - manuscript has NO bold header)
- diversity_cost: 0 textbf in header (CORRECT - no bold header)
- ensemble_comparison: 0 textbf generated (WRONG - needs per-column check)
- sota_comparison: 0 textbf generated (WRONG - manuscript header is `\textbf{Method} & \textbf{Acc.} & ...`)
- clustering_ablation: 0 textbf generated (WRONG)
- noclustering: 0 textbf generated (WRONG)

**Pattern in Manuscript**:
- selection_rule: NO header bold (0 textbf)
- diversity_cost: NO header bold (0 textbf)
- ensemble_comparison: YES header bold (all 9 columns)
- sota_comparison: YES header bold (all 7 columns)
- clustering_ablation: YES header bold (all 8 columns)
- noclustering: YES header bold (all 8 columns)

**Fix Required**: Per-table config specifying which tables have bold headers.

**Test**: Verify textbf count in header row matches manuscript per table

---

### (4) *** \hline STRUCTURE FLATTENED ***
**Issue**: Emits 3 \hline everywhere; manuscript has table-specific patterns.

**Current State**: All tables get `[before_header, after_header, end]` (3 hlines)

**Actual Pattern in Manuscript**:
- selection_rule: 3 hlines + special `\cline{2-3}\cline{4-5}`
- diversity_cost: 3 hlines
- ensemble_comparison: 5 hlines (rules between every method group)
- clustering_ablation: 4 hlines
- sota_comparison: 7 hlines (rules after own-method and between EACH baseline)
- noclustering: 9 hlines (rules between EVERY row)

**Fix Required**: Extract exact hline positions per table and reproduce precisely.

**Test**: Count and compare \hline positions cell-by-cell

---

### (5) *** CAPTION NOT BYTE-FOR-BYTE ***
**Issue**: Stripped spaces around inline math. 

**Example**:
- Manuscript: `"Best value in each column in bold; $p$ is the one-sided Wilcoxon..."`
- Generated: `"bold;$p$is the one-sided"` (spaces lost)

**Fix Required**: Extract caption from document.tex as raw text with NO normalization.

**Test**: Diff each generated caption against manuscript string until identical.

---

### (6) *** OVER-BOLDING ***
**Issue**: Bolds cells the paper doesn't. Merit-direction automation inappropriate for all columns.

**Example**: sota_comparison Time column
- Generated: Bolds KNORA-U's 33.1 (minimum) as a "win"
- Manuscript: Bolding is blank (time is not presented as a merit claim)

**Pattern**: Paper only bolds where the metric is a merit claim. Some columns (Time, Disagreement, etc.) are informational only.

**Fix Required**: Audit every column per table. Where paper bolds nothing, set column config to `bold=None` (never bold).

**Test**: Verify bold PATTERN matches paper cell-for-cell, not internal consistency.

---

## Extended Verifier Requirements

The verifier must check:

1. **No bare \mathbf outside $...$ **: Regex check per table
2. **\cite key count**: Verify sota_comparison=4, noclustering=4, others=0
3. **\textbf cell positions**: Extract and compare per row type (header, own-method, baseline)
4. **\hline count and positions**: Count and compare per table
5. **Caption byte-for-byte**: Diff against manuscript with zero normalization
6. **Bold pattern**: Which cells have \textbf{...}; match against manuscript

## TeX Toolchain Status

`which pdflatex` returned: NO TeX TOOLCHAIN INSTALLED

Therefore: **Cannot compile-test locally.** Fixes must be validated via markup analysis only.

---

## Next Steps

1. Rewrite make_tables.py with:
   - Proper `\textbf` vs `\mathbf` logic
   - cite_key rendering logic
   - Per-table header bold config
   - Per-table hline pattern config
   - Byte-for-byte caption extraction
   - No over-bolding (set merit=NONE for non-merit columns)

2. Build extended verifier checking all 6 categories

3. Run verification and report per-table PASS/FAIL
