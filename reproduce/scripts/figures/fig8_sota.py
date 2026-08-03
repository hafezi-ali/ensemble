"""Fig. 8: DDEL-GMM against published dynamic ensemble selection methods.

=============================================================================
PROVENANCE WARNING -- THE INPUT VECTORS ARE NOT MEASURED.

data/sota_perfold_fscores.csv and data/sota_comparison_summary.csv were
never computed from data. No code in this repository or the parent project
produces them: grep for META-DES, KNORA or deslib across the source tree
returns nothing. They are internally consistent (the per-fold vectors
reproduce the summary means, SDs, ranks, win counts and p-values exactly),
which makes the inconsistency check useless as a provenance check.

This script therefore renders a figure whose inputs are unverified. It is
kept because the plotting logic is correct and will be reused unchanged once
the measurement exists -- swap the CSV, rerun, done.

TO MEASURE IT (this is the highest-priority open item in the project; all
three referees asked for the DELAK comparison specifically):
  * META-DES, KNORA-U and KNORA-E come from DESlib 0.3.7, which installs
    into this environment cleanly (pip install deslib).
  * DELAK (K-means DES, Guo et al. 2021) is not in DESlib and must be
    implemented. The DDEL-KMeans variant in exp1_gmm_vs_kmeans.py is
    structurally close and is the place to start.
  * Use StratifiedKFold(10, shuffle=True, random_state=42) on the HAR
    matrix so the folds match every other experiment here, then write the
    per-fold macro F of each method as a column of sota_perfold_fscores.csv.
=============================================================================

Bars are means, error bars +-1 SD over the ten folds, annotations the
one-sided Wilcoxon signed-rank p-value of DDEL-GMM against each baseline.
The p-values are RECOMPUTED here from the per-fold vectors rather than read
from the summary, so the figure cannot drift from its input file.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'lib'))
from ddel_paths import ROOT, DATA, FIGS

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

per = pd.read_csv(os.path.join(DATA, "sota_perfold_fscores.csv"))
OURS = "DDEL-GMM (ours)"
assert OURS in per.columns, per.columns.tolist()
baselines = [c for c in per.columns if c != OURS]

rows = []
for m in [OURS] + baselines:
    v = per[m].to_numpy(float)
    if m == OURS:
        p = np.nan
    else:
        p = wilcoxon(per[OURS].to_numpy(float), v, alternative="greater").pvalue
    rows.append((m, v.mean(), v.std(ddof=1), p))
res = pd.DataFrame(rows, columns=["method", "mean", "sd", "p"])

fig, ax = plt.subplots(figsize=(6.4, 3.4))
x = np.arange(len(res))
colors = ["#E69F00"] + ["#56B4E9"] * len(baselines)
ax.bar(x, res["mean"], yerr=res["sd"], capsize=4, color=colors,
       edgecolor="black", linewidth=0.7, width=0.62,
       error_kw=dict(elinewidth=0.9, ecolor="#333333"))

lo = float((res["mean"] - res["sd"]).min())
hi = float((res["mean"] + res["sd"]).max())
pad = 0.25 * (hi - lo)
ax.set_ylim(max(0.0, lo - pad), hi + pad * 1.6)

for i, r in res.iterrows():
    ax.text(i, r["mean"] + r["sd"] + 0.1 * pad, "%.4f" % r["mean"],
            ha="center", fontsize=8)
    if not np.isnan(r["p"]):
        star = "*" if r["p"] < 0.05 else ""
        ax.text(i, r["mean"] + r["sd"] + 0.45 * pad,
                "$p=%.3f$%s" % (r["p"], star), ha="center", fontsize=7.5,
                color="#B22222" if r["p"] < 0.05 else "#555555")

ax.set_xticks(x)
ax.set_xticklabels(res["method"], rotation=15, ha="right", fontsize=8.5)
ax.set_ylabel("mean macro F-score")
ax.grid(axis="y", alpha=0.3, linewidth=0.5)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "sota_comparison.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(FIGS, "sota_comparison.png"), dpi=200, bbox_inches="tight")
print(res.to_string(index=False, float_format=lambda v: "%.4f" % v))
print()
print("!! sota_perfold_fscores.csv is NOT measured -- see this script's docstring.")
print("!! The figure is rendered so the pipeline is ready; the numbers are not evidence.")
