# ensemble

DDEL-GMM manuscript revision (IEEE TETCI resubmission).

## Putting your own results into the paper

```bash
python3 make_results.py --status     # what still needs numbers
                                     # edit a CSV in results/
python3 make_results.py              # rebuild tables + figures
                                     # recompile manuscript/document.tex
```

**Documentation: [`docs/`](docs/README.md)** — start with
[docs/1-EDITING-RESULTS.md](docs/1-EDITING-RESULTS.md).

## Layout

| Path | Contents |
|---|---|
| `results/` | Hand-editable CSVs — the single source of truth for every number |
| `tables/` | Generated LaTeX tables (do not hand-edit) |
| `figures_out/` | Generated figures (do not hand-edit) |
| `manuscript/` | `document.tex`, published figures, pristine backups |
| `docs/` | Results-pipeline documentation |
| `notes/` | Manuscript revision material: reviewer triage, rebuttal notes |
| `reproduce/` | Reproduction package for the experiments |
