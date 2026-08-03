# Results workflow

Every number printed in the paper comes from a CSV in `results/`. You edit the CSV,
run one command, and the LaTeX tables and figure PDFs are rebuilt from it.

```
results/*.csv   ->   make_results.py   ->   tables/*.tex  +  figures_out/*.pdf
                                                  |
                                       document.tex \input's them
```

You never hand-edit `tables/*.tex` or the figure files. They are generated and are
overwritten on every build.

## The one command

```bash
cd /home/ali/Documents/ensemble
python3 make_results.py
```

Then recompile `manuscript/document.tex` as usual.

Useful variants:

| Command | What it does |
|---|---|
| `python3 make_results.py` | Rebuild everything (tables + figures) |
| `python3 make_results.py --tables` | Tables only (fast) |
| `python3 make_results.py --figures` | Figures only |
| `python3 make_results.py --verify` | Check the six original tables still match the submitted paper |

## What `--verify` is for

It re-renders the six tables that already existed in the submitted manuscript and
compares them **byte for byte** against the original text, which is preserved in
`manuscript/original_backup/document_ORIGINAL_20260730.tex`.

- Before you change anything: all six report `PASS byte-identical`. That is the
  proof that the generator reproduces the paper exactly and has not silently
  altered a number, a `\cite` key, or the bolding.
- After you paste new Colab numbers: the tables you edited will report `FAIL` and
  print `paper:` vs `render:` lines. **This is expected** — it is showing you the
  difference between the submitted number and your new one. Read those lines as a
  changelog of what your edit changed.

The four new reviewer tables are excluded from `--verify`; they have no original
in the paper to compare against.

## Which CSV drives what

### Tables that exist in the submitted paper

| CSV in `results/` | Generates | Appears in paper as |
|---|---|---|
| `table_selection_rule.csv` | `tables/selection_rule.tex` | `tab:selection_rule` |
| `table_ensemble_comparison.csv` | `tables/ensemble_comparison.tex` | `tab:ensemble_comparison` |
| `table_diversity_cost.csv` | `tables/diversity_cost.tex` | `tab:diversity_cost` |
| `table_sota_comparison.csv` | `tables/sota_comparison.tex` | `tab:sota_comparison` |
| `table_clustering_ablation.csv` | `tables/clustering_ablation.tex` | `tab:clustering_ablation` |
| `table_noclustering.csv` | `tables/noclustering.tex` | `tab:noclustering` |

### New tables for the reviewer-requested experiments

These are wired up and generate every build. While a CSV is empty the table prints
`---` in each cell (the same marker the paper already uses for "not applicable"),
so you can see the slot in the compiled PDF. Paste numbers in and the table fills.

| CSV in `results/` | Generates | Addresses |
|---|---|---|
| `table_delak_fhdes.csv` | `tables/delak_fhdes.tex` | All 3 referees: no empirical DELAK / FH-DES comparison |
| `table_nonspherical.csv` | `tables/nonspherical.tex` | GMM vs K-means on non-spherical / overlapping clusters |
| `table_bagging_boosting.csv` | `tables/bagging_boosting.tex` | No comparison against bagging / boosting without clustering |
| `table_case_study.csv` | `tables/case_study.tex` | Referee 3: real-world (medical) case study |

### Figures

| CSV(s) in `results/` | Generates (`figures_out/`) |
|---|---|
| `figure_fscore_vs_phi.csv` | `fscore_vs_phi.pdf` / `.png` |
| `figure_fscore_vs_clusters.csv` | `fscore_vs_clusters.pdf` / `.png` |
| `figure_boxplot_perfold.csv`, `figure_boxplot_stats.csv`, `table_best_ensemble_results.csv` | `boxplot_comparison_v2.pdf` |
| `table_diversity_cost.csv`, `table_ensemble_comparison.csv` | `fig2_diagnostics.pdf` |
| `figure_sota_perfold.csv` | `sota_comparison.pdf` |
| `figure_gmm_vs_kmeans_sweep.csv`, `figure_gmm_vs_kmeans_covtype.csv`, `figure_gmm_vs_kmeans_perfold.csv` | `gmm_vs_kmeans_synthetic.pdf` |
| `figure_noclustering_perfold.csv` | `noclustering_comparison.pdf` |
| `figure_concept_drift.csv` | `concept_drift.pdf` — Referee 2: simulated concept drift |
| `table_delak_fhdes.csv` | `delak_fhdes.pdf` |
| `table_nonspherical.csv` | `nonspherical.pdf` |
| `table_case_study.csv` | `case_study.pdf` |

Note that the last three figures read the **same CSV as the corresponding table**.
Fill the table CSV once and both the table and its figure update.

## Slots that still need data

Run a build and read the console: anything not yet filled announces itself.

- `results/figure_fscore_vs_clusters.csv` — **empty**. The published figure shows a
  full sweep over K for all four base learners; that raw sweep was never saved to
  the repository, only the exported PDF from the original 2024 run. Until you paste
  it, the build prints a placeholder rather than a blank axes.
- `results/figure_fscore_vs_phi.csv` — **partial**: 3 of 9 φ values, LR only. The
  build warns `UNDER-POPULATED` and stamps a red `partial sweep` note on the figure
  so a thin plot cannot be mistaken for a complete one. Remove that note by filling
  the CSV.
- `results/figure_boxplot_perfold.csv` — empty. The boxplot falls back to the
  summary statistics in `figure_boxplot_stats.csv` and draws no outlier markers.
  Fill the per-fold file to get true boxes with fliers.
- The four reviewer CSVs listed above — empty, awaiting the new experiments.

The published `fscore_vs_phi.pdf` and `fscore_vs_clusters.pdf` currently in
`manuscript/` are the originals and are **not** overwritten by the build; the
generator writes to `figures_out/`. `document.tex` has a `\graphicspath` that
prefers `figures_out/`, so a regenerated figure takes precedence once it exists.

## Editing rules

1. **Do not change a header row or add/remove columns.** The generator matches the
   paper's column order by name; a renamed column is silently dropped from the table.
2. **Keep the number of significant digits you want printed.** The formatter
   preserves what the paper used per column (e.g. 4 decimals for accuracy, 3 for
   AUC). Writing `0.98` where the paper printed `0.9800` still prints `0.9800`.
3. **Bolding is automatic** — the best value per merit column is bolded, and the
   direction (max for accuracy/F/AUC, min for rank/std/time) is fixed per table to
   match the paper. If your new numbers change who wins, the bold moves with them.
4. **`---` means "not applicable"** and is passed through untouched. Use it, not a
   blank, where the paper prints a dash (e.g. DDEL-GMM's own `p` value).
5. **`(ours)`, `\cite{...}` keys, captions and labels live in the generator**, not
   in the CSV. They survive every rebuild.

## If you need to undo the `document.tex` rewiring

`patch_document.py` replaced six inline table floats with `\input{...}` lines and
kept a timestamped backup:

```bash
python3 patch_document.py --revert     # restore the inline tables
python3 patch_document.py --dry-run    # preview the patch without writing
```

The pristine submitted manuscript is at
`manuscript/original_backup/document_ORIGINAL_20260730.tex`. Do not edit that file —
the table generator reads it as its template source, which is how `--verify` works.
