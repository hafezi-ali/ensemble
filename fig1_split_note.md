# Figure 1 rework: split into two vector figures

## What changed

The single composite `fig1_final.pdf` is replaced by two figures, each placed
next to the text that references it:

| file | label | placement | contents |
|---|---|---|---|
| `fig1_pipeline.pdf` | `fig:overview` | Sec. III, p6 | FIT / SELECT / WEIGHT schematic |
| `fig2_diagnostics.pdf` | `fig:diagnostics` | Sec. IV, p12 | (a) aggregation (b) diversity (c) oracle headroom |

Panel letters renumbered: old (b)(c)(d) are now (a)(b)(c) of Fig. 2. The one
in-text reference to `fig:overview`(b) was retargeted to `fig:diagnostics`(a).

## Why it was split

The schematic is referenced from the Methodology and the three results panels
from Section IV. A single float cannot sit near both, and as one object it was
7.16 x 9.7 in -- essentially a full page, pushing the manuscript from 19 to 22
pages. Split, both figures land on the page after their first reference and the
manuscript is 20 pages.

## Defects fixed across four review rounds

1. **Sample count `n=9528`** in the caption matched neither the dataset
   (10,299 rows in `code/Data/UCI_HAR_Dataset/data_uci_handled.csv`) nor the
   per-fold training size stated at line 71. Removed; the caption now states
   10,299, verified against the file.
2. **Clipped bars.** Panel (b) had `ylim` floor 0.70 while MaxE measures 0.508
   (lr) and 0.410 (dt) -- the two points that support the caption's own claim of
   sharp degradation were invisible. The floor is now computed from the data:
   `min(mean - sd) - 0.06`.
3. **Inverted claim.** The oracle panel's caption asserted the ensemble was
   already at its ceiling at the published operating point. Measured headroom is
   1.54 pp at phi=0.5, closing to 0.48 pp at phi=0.9 -- the opposite reading.
   Caption rewritten to the measured direction.
4. **Double-scaled shading.** `oracle_vals` was already x100 when
   `fill_between` multiplied it by 100 again, so the shaded band's upper bound
   was ~9750 against a [96,100] axis: it flooded the panel instead of showing
   the gap. Fixed.
5. **Clipping reintroduced.** The oracle panel then used floor 96.0 while the
   achieved score at phi=0.2 is 95.49 -- same defect, new panel. Limits are now
   derived from the data with a fixed pad.
6. **Raster output.** `make_fig1.py` rendered four PNGs, composed them with PIL
   (`Image.paste` after per-panel `.resize()`, which distorts aspect ratios
   independently), and called `canvas.save(...pdf)` -- a PIL image saved as PDF
   can only be a bitmap. The delivered file was a single 2148x2910 JPEG with no
   embedded fonts. Rewritten as matplotlib figures saved with `fig.savefig`.
7. **Mismatched dual axes.** The diversity panel had left axis 0-100 and right
   0-80 for two quantities both in percent, making curve heights
   non-comparable. Both now share one axis.

## Verification

    pdffonts  fig1_pipeline.pdf     -> 5 embedded fonts
    pdfimages -list fig1_pipeline.pdf   -> empty (no raster)
    pdffonts  fig2_diagnostics.pdf  -> 3 embedded fonts
    pdfimages -list fig2_diagnostics.pdf -> empty
    document.pdf                    -> 20 pages, 0 undefined refs
    document_tier4_highlighted.pdf  -> 20 pages, 0 undefined refs

## Measured values in the figures (K=6, rule=distance)

    phi        0.20    0.40    0.50    0.60    0.90
    overlap    16.3    34.8    42.5    53.0    87.7   %
    disagree   65.1    61.7    29.8     7.6     1.1   %
    oracle     98.74   99.51   98.83   98.25   97.38  %
    achieved   95.49   97.08   97.29   97.11   96.90  %
    headroom    3.25    2.43    1.54    1.14    0.48  pp

Source: `data/selection_rule_diagnostic.csv` and `code/best_ensemble_results.csv`,
read at render time. Regenerate with `python3 code/codes/make_fig1.py` from the
repository root.

## One caveat on the tracked-changes copy

`document_tier4_highlighted.tex` is generated from `document.tex` by wrapping
Tier-4 subsections in `{\tfourhighlight ...}`. The macro must be defined in the
generated file (it is injected before `\begin{document}`) and must be the
group-scoped form, not `\textcolor{...}{...}` -- the wrapped blocks span blank
lines and the argument form fails to compile.
