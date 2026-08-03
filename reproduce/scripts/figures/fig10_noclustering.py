"""Figure: DDEL-GMM vs non-clustering ensembles, from MEASURED per-fold data."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'lib'))
from ddel_paths import ROOT, DATA, FIGS, DATASET, NPC, SEED, K_PUB, PHI_PUB, require_dataset
require_dataset()

import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import rankdata, studentized_range

pf = pd.read_csv(DATA+"noclustering_perfold.csv")
st = pd.read_csv(DATA+"noclustering_stats.csv")
ours = "DDEL-GMM (ours)"
order = pf.mean().sort_values(ascending=False).index.tolist()
n, k = len(pf), pf.shape[1]
R = np.vstack([rankdata(-pf.iloc[i].to_numpy()) for i in range(n)])
mr = pd.Series(R.mean(0), index=pf.columns)
CD = studentized_range.ppf(0.95, k, np.inf) / np.sqrt(2) * np.sqrt(k * (k + 1) / (6.0 * n))

fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.2, 4.3),
                               gridspec_kw={"width_ratios": [1.35, 1]})

# ---- left: per-fold F distributions ----------------------------------------
cols = ["#c0392b" if c == ours else "#7f8c8d" for c in order]
bp = axL.boxplot([pf[c] for c in order], patch_artist=True, widths=0.62,
                 medianprops=dict(color="black", lw=1.4),
                 flierprops=dict(marker="o", ms=3, mfc="0.4", mec="none"))
for patch, c in zip(bp["boxes"], cols):
    patch.set_facecolor(c); patch.set_alpha(.85); patch.set_edgecolor("black"); patch.set_lw(.8)
for i, c in enumerate(order, 1):
    axL.plot(i, pf[c].mean(), marker="D", ms=5, color="white",
             mec="black", mew=.9, zorder=5)
axL.set_xticks(range(1, len(order) + 1))
axL.set_xticklabels([c.replace(" (ours)", "\n(ours)").replace(" (LR)", "\n(LR)")
                     .replace("Gradient Boosting", "Gradient\nBoosting")
                     .replace("Random Forest", "Random\nForest")
                     for c in order], fontsize=8.5)
axL.set_ylabel("Macro F-score", fontsize=10)
axL.set_title(f"(a) Per-fold F-score, {n}-fold stratified CV", fontsize=10, loc="left")
axL.grid(axis="y", alpha=.3, lw=.6); axL.set_axisbelow(True)
axL.text(.99, .965, "white diamond = mean", transform=axL.transAxes,
         ha="right", va="top", fontsize=7.5, style="italic", color="0.35")

# ---- right: mean ranks with Nemenyi CD -------------------------------------
mro = mr[order]
ypos = np.arange(len(order))[::-1]
axR.barh(ypos, mro.values, color=cols, alpha=.85, edgecolor="black", lw=.8, height=.6)
axR.errorbar(mro[ours], ypos[order.index(ours)], xerr=CD / 2, color="black",
             capsize=4, lw=1.3, zorder=6)
axR.axvline(mro[ours] + CD, ls="--", lw=1.1, color="#c0392b")
axR.text(mro[ours] + CD, len(order) - .35, f"  CD={CD:.2f}", color="#c0392b",
         fontsize=8, va="top")
axR.set_yticks(ypos)
axR.set_yticklabels([c.replace(" (ours)", " (ours)") for c in order], fontsize=8.5)
axR.set_xlabel("Mean Friedman rank  (1 = best)", fontsize=9.5)
axR.set_title("(b) Mean rank and Nemenyi critical difference", fontsize=10, loc="left")
axR.grid(axis="x", alpha=.3, lw=.6); axR.set_axisbelow(True)
axR.set_xlim(0, k + .6)
for yv, c in zip(ypos, order):
    axR.text(mro[c] + .09, yv, f"{mro[c]:.2f}", va="center", fontsize=8)

fig.suptitle("DDEL-GMM vs non-clustering ensemble baselines on UCI HAR "
             f"(measured, {n} folds)", fontsize=11, y=1.0)
fig.tight_layout()
fig.savefig(FIGS+"noclustering_comparison.pdf", bbox_inches="tight")
fig.savefig(FIGS+"noclustering_comparison.png", dpi=150, bbox_inches="tight")
print(f"CD={CD:.3f}")
print(mro.round(2).to_string())
