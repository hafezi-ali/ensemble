# DDEL-GMM Project Organization

## Structure
```
ensemble/
├── manuscript/                 # TeX source, PDFs, BibTeX (ACTIVE EDITING)
│   ├── document.tex           # Latest source
│   ├── document_tier4_highlighted.tex  # Final submission version
│   ├── document.pdf
│   ├── document_tier4_highlighted.pdf  # PUBLISHED VERSION
│   └── references.bib
│
├── figures/
│   ├── comparison/            # Ablation vs no-clustering vs SOTA comparison plots
│   │   ├── *_comparison.png
│   │   ├── *_comparison.pdf
│   │   └── boxplot_comparison.*
│   ├── diagrams/              # Phase diagrams (training, generalization, etc)
│   │   ├── *_phase_diagram.eps
│   │   ├── *_phase_diagram.pdf
│   │   └── fscore_vs_*.pdf
│   └── supplementary/         # Additional plots (if any)
│
├── experiments/
│   ├── ablation/              # GMM clustering ablation study
│   │   ├── clustering_ablation_*.csv
│   │   ├── noclustering_*.csv
│   │   └── _syn_*.npy (synthetic data arrays)
│   ├── sota/                  # External SOTA baseline comparisons
│   │   └── sota_comparison_*.csv
│   └── synthetic/             # Synthetic dataset runs
│
├── archive/
│   ├── old_versions/          # Superseded PDFs (tier2, tier3, prior revisions)
│   └── plans/                 # Historic work plans (plan_*.json)
│
├── notes/                     # Rebuttal notes, change logs, revision tracking
│   ├── changes_by_difficulty.md
│   ├── step18_rebuttal_note.md
│   ├── step19_20_rebuttal_note.md
│   └── revision_triage.md
│
├── data/                      # Raw experimental outputs (CSV + arrays)
│   ├── *_perfold_fscores.csv  # Per-fold metrics
│   ├── *_summary.csv          # Aggregate statistics
│   └── _syn_*.npy             # Synthetic data (X, y, GMM labels, KM labels)
│
├── _build/                    # Tectonic compile artifacts (ignore)
│   ├── document.pdf (stale)
│   ├── *.aux, *.bbl, *.log
│   └── *.png (screenshots)
│
└── code/                      # Python scripts (controlled access)
```

## Quick Reference

### For Manuscript Edits
- **Edit**: `manuscript/document.tex`
- **Compile**: `tectonic -X compile --outdir ./_build manuscript/document.tex`
- **Copy output**: `cp _build/document.pdf manuscript/document.pdf`
- **Final PDF**: `manuscript/document_tier4_highlighted.pdf`

### For Figure Updates
- Place new comparison plots in `figures/comparison/`
- Place new diagrams in `figures/diagrams/`
- Update `manuscript/document.tex` with `\includegraphics` paths relative to the TEX root

### For Experimental Data
- Ablation results → `experiments/ablation/`
- SOTA comparisons → `experiments/sota/`
- Synthetic validation → `experiments/synthetic/`

### For Rebuttal Tracking
- Current status → `notes/step19_20_rebuttal_note.md`
- Revision tiers → `notes/changes_by_difficulty.md`
- Old versions → `archive/old_versions/` (for reference)

## Storage Usage
- **Manuscript** (PDF + TEX + refs): 1.8 MB
- **Figures** (PNGs + PDFs + EPSs): ~3.5 MB
- **Experiments** (CSVs + numpy): 84 KB
- **Build artifacts**: 3.2 MB (safe to clear)
- **Total**: ~8.6 MB

