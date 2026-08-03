# Documentation

Everything about putting your own results into the paper. Start with the first file.

| File | Read it when |
|---|---|
| **[1-EDITING-RESULTS.md](1-EDITING-RESULTS.md)** | **Start here.** How to paste your Colab numbers in and rebuild. Worked examples, editing rules, troubleshooting. |
| [2-CSV-TO-OUTPUT-MAP.md](2-CSV-TO-OUTPUT-MAP.md) | You want to know which CSV produces a particular table or figure. |
| [3-CSV-SCHEMA.md](3-CSV-SCHEMA.md) | You need column-level detail: units, precision, merit direction, derived columns. |
| [build-history/](build-history/) | Archive of how the pipeline was built and which defects were fixed. Not needed for day-to-day work. |

## The 30-second version

```bash
cd /home/ali/Documents/ensemble

python3 make_results.py --status     # what still needs numbers?
                                     # edit a CSV in results/
python3 make_results.py              # rebuild tables + figures
                                     # recompile manuscript/document.tex
```

You never hand-edit `tables/*.tex` or the files in `figures_out/` — they are
generated and overwritten on every build. Edit CSVs in `results/` only.

## Commands

| Command | What it does |
|---|---|
| `python3 make_results.py` | Rebuild everything |
| `python3 make_results.py --status` | Show which CSVs still need your numbers |
| `python3 make_results.py --tables` | Tables only (fast) |
| `python3 make_results.py --figures` | Figures only |
| `python3 make_results.py --verify` | Check the six original tables still match the submitted paper |
| `python3 patch_document.py --revert` | Undo the `\input` rewiring of `document.tex` |

## Not in this folder

`../notes/` holds the manuscript revision material — reviewer triage, rebuttal
notes, figure rework notes. That is about the *content* of the paper; this folder
is about the *results pipeline*. They are kept separate on purpose.
