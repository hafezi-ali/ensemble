# How to put your own results into the paper

Everything printed in the paper comes from a CSV in `results/`. You edit a CSV,
run one command, recompile. You never touch a `.tex` table or a figure file.

---

## The loop (this is the whole thing)

```bash
cd /home/ali/Documents/ensemble

python3 make_results.py --status     # 1. what still needs numbers?
                                     # 2. open a CSV, paste your numbers, save
python3 make_results.py              # 3. rebuild tables + figures
                                     # 4. recompile document.tex
```

That's it. Steps 1 and 3 are the only commands you need.

---

## Step 1 — see what needs filling

```bash
python3 make_results.py --status
```

It sorts every file into **NEEDS DATA**, **PARTIAL**, and **COMPLETE**, so you
always know where you stand. Right now six files are waiting on you:

| File | What it feeds |
|---|---|
| `table_delak_fhdes.csv` | DELAK / FH-DES table **and** figure |
| `table_nonspherical.csv` | GMM vs K-means table **and** figure |
| `table_bagging_boosting.csv` | bagging/boosting table |
| `table_case_study.csv` | medical case-study table **and** figure |
| `figure_concept_drift.csv` | concept-drift figure |
| `figure_fscore_vs_clusters.csv` | F-score vs K figure |
| `figure_boxplot_perfold.csv` | outlier circles on the boxplot |

Note the first, second and fourth feed **both** a table and a figure. Fill the
CSV once; both update.

---

## Step 2 — paste your numbers

Open the CSV in Excel, LibreOffice, or any text editor. The scaffold is already
there with the right rows and columns — you are only filling blanks.

### Worked example: the DELAK / FH-DES comparison

`results/table_delak_fhdes.csv` looks like this now:

```
method,accuracy,mean_f_score,auc,rank,p_value,time_seconds
DDEL-GMM,,,,,---,
DELAK,,,,,,
FH-DES,,,,,,
```

Paste your Colab numbers into the blanks:

```
method,accuracy,mean_f_score,auc,rank,p_value,time_seconds
DDEL-GMM,0.9683,0.9691,0.994,1.2,---,48.2
DELAK,0.9502,0.9521,0.986,2.4,0.002,39.6
FH-DES,0.9558,0.9573,0.989,2.4,0.014,52.7
```

Rebuild, and you get a finished IEEE table with the best value in each column
bolded, `(ours)` on your method, and a matching bar chart — from that one edit.

### Worked example: the φ sweep (a partially filled file)

`results/figure_fscore_vs_phi.csv` has 3 of 36 values — LR only, at φ = 0.4,
0.5, 0.9. The published figure had all four learners across all nine φ values.
Fill the grid:

```
phi,lr_fscore,svm_fscore,knn_fscore,dt_fscore
0.1,0.9702,0.9688,0.9601,0.8402
0.2,0.9711,0.9695,0.9622,0.8433
...
0.9,0.9726,0.9701,0.9635,0.8447
```

Leave a cell blank if you don't have that measurement — the line simply skips
that point. It will **not** shift the remaining points onto wrong x-positions
(that was a bug; it's fixed and tested).

---

## Step 3 — rebuild

```bash
python3 make_results.py
```

Read the console output. It reports every table and figure, and it *warns you*
about anything thin:

```
! figure_fscore_vs_phi is UNDER-POPULATED: no data for SVM, KNN, DT | LR has 3/9 phi points
  -> paste the full sweep into results/figure_fscore_vs_phi.csv
```

A sparse figure also gets a red **"partial sweep"** note stamped on the axes, so
you cannot accidentally submit a half-empty plot thinking it's complete. Fill
the CSV and both the warning and the red note disappear.

Faster variants while iterating:

```bash
python3 make_results.py --tables     # tables only, ~1 second
python3 make_results.py --figures    # figures only
```

---

## Step 4 — recompile

Compile `manuscript/document.tex` exactly as you always have. It already
`\input`s the generated tables and picks up figures from `figures_out/`, so
there is no LaTeX edit to make. New numbers just appear.

---

## Rules for editing the CSVs

1. **Never rename or reorder a column, and never add one.** The generator
   matches columns by name. A renamed column is silently dropped from the table.
2. **Never rename the row labels** (`DDEL-GMM`, `DELAK`, `Bagging`, ...). Bolding
   and the `(ours)` suffix key off those exact strings.
3. **Write `---`, not a blank, where a value is genuinely not applicable** —
   e.g. DDEL-GMM's `p_value` against itself. Blank means "not measured yet";
   `---` means "does not apply" and prints as a dash in the paper.
4. **Don't worry about decimal places.** Each column has a fixed precision
   matching the paper. Typing `0.98` where the paper printed `0.9800` still
   prints `0.9800`.
5. **Don't bold anything yourself.** The winner in each merit column is bolded
   automatically, in the right direction (highest accuracy/F/AUC, lowest
   rank/std/time). Change the numbers and the bold moves.
6. **Captions, `\cite{...}` keys and labels live in the generator**, not in the
   CSV. They survive every rebuild — you cannot lose a citation by editing data.
7. **Save as plain CSV.** If you edit in Excel, use *Save As → CSV*, not .xlsx.

---

## The safety net: `--verify`

```bash
python3 make_results.py --verify
```

This re-renders the six tables that were in your submitted paper and compares
them **byte for byte** against the original, preserved at
`manuscript/original_backup/document_ORIGINAL_20260730.tex`.

- **Right now: all six PASS.** That is the proof the pipeline reproduces your
  submitted paper exactly — no number, citation, or bold has drifted.
- **After you paste new numbers: the tables you edited will FAIL**, and print
  `paper:` vs `render:` lines.

**A FAIL after you edit is not an error.** It is the tool showing you precisely
what changed against the submitted version — read it as a changelog. Use it to
confirm you changed what you meant to change and nothing else.

The four new reviewer tables are excluded from `--verify`; they have no original
in the paper to compare against.

---

## If something goes wrong

**A number didn't change in the PDF.** You edited the CSV but didn't rerun
`make_results.py`, or LaTeX used a cached table. Rerun the build, then recompile.

**A whole column vanished from a table.** You renamed or added a column header.
Restore the original header spelling.

**A row lost its bold or its `(ours)`.** You changed a row label. Restore the
exact original string.

**You want the original tables back inline in `document.tex`:**

```bash
python3 patch_document.py --revert
```

A pre-patch backup is kept at
`manuscript/original_backup/document_prepatch_20260802_224414.tex`, and the
pristine submitted manuscript at `document_ORIGINAL_20260730.tex`. **Never edit
that second file** — the generator reads it as its template, which is what makes
`--verify` possible.

---

## One thing needing a decision, not a paste

The boxplot caption claims outlier circles beyond 1.5×IQR and states that
DensityE produces no low-side outlier folds. Only five-number summaries survive
in the repository, so the figure cannot draw those circles. Either:

- paste per-fold F-scores into `results/figure_boxplot_perfold.csv`
  (columns: `method,learner,fold,fscore`) and the fliers appear automatically, or
- delete those two sentences from the caption.

As it stands the caption asserts something the figure does not show — a referee
may notice.
