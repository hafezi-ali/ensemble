"""Fig. 5: per-fold F1 distribution at the published operating point.

Draws the boxplot from the measured five-number summaries in
data/boxplot_stats_measured.csv, which were extracted from the stored cell
outputs of code/Main_Thp.ipynb (cell 12, the printed per-configuration
statistics for n_c=6, phi=0.5 -- the same single configuration Table I
reports, not a spread over the 45-config grid).

The defensible claim is about DISPERSION, not mean gap: DensityE std 0.003 vs
DistE 0.043 for logistic regression (best_ensemble_results.csv), a 14-fold
reduction. An earlier version encoded DistE means that were systematically low
and supported a "DistE trails by six points" claim the data does not support.
Do not restore it.

CAUTION on reading this figure. The dispersion claim is NOT visible in the
box widths -- DistE's IQR is actually tighter than DensityE's (0.0022 vs
0.0040 for lr). It is driven by a small number of low outlier folds, whose
signature here is the mean marker sitting well below the median for every
DistE box (-0.0093 for lr) while the DensityE means sit on their medians
(-0.0003). The source file records five-number summaries only; individual
flier folds were not retained, so no flier circles can be drawn. Annotate the
standard deviations, never the IQRs.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'lib'))
from ddel_paths import ROOT, DATA, FIGS, DATASET, NPC, SEED, K_PUB, PHI_PUB

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STATS = os.path.join(DATA, "boxplot_stats_measured.csv")
s = pd.read_csv(STATS)

LABEL = {"lr": "LogReg", "svm": "SVM", "knn": "KNN", "single_svm": "Single SVM"}
COLOR = {"DensityE": "#E69F00", "DistE": "#56B4E9", "Single Model": "#BBBBBB"}

order = [("DensityE", "lr"), ("DistE", "lr"),
         ("DensityE", "svm"), ("DistE", "svm"),
         ("DensityE", "knn"), ("DistE", "knn"),
         ("Single Model", "single_svm")]

bxp, colors, ticks = [], [], []
for method, learner in order:
    r = s[(s.method == method) & (s.learner == learner)]
    assert len(r) == 1, "missing row: %s / %s" % (method, learner)
    r = r.iloc[0]
    bxp.append(dict(med=r["median"], q1=r["q1"], q3=r["q3"],
                    whislo=r["whislo"], whishi=r["whishi"],
                    mean=r["mean"], fliers=[], label=""))
    colors.append(COLOR[method])
    ticks.append(LABEL[learner] if method != "DistE" else "")

fig, ax = plt.subplots(figsize=(7.0, 3.6))
bp = ax.bxp(bxp, showmeans=True, patch_artist=True, widths=0.62,
            meanprops=dict(marker="x", markeredgecolor="crimson",
                           markersize=6, markeredgewidth=1.4),
            medianprops=dict(color="black", linewidth=1.2),
            boxprops=dict(linewidth=0.8),
            whiskerprops=dict(linewidth=0.8), capprops=dict(linewidth=0.8))
for patch, c in zip(bp["boxes"], colors):
    patch.set_facecolor(c)
    patch.set_alpha(0.85)

# group the paired boxes under one learner label
positions = [1.5, 3.5, 5.5, 7]
ax.set_xticks(positions)
ax.set_xticklabels(["LogReg", "SVM", "KNN", "Single SVM"])
ax.set_ylabel("weighted $F_1$-score")
ax.set_ylim(0.88, 0.99)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)
ax.set_axisbelow(True)

handles = [plt.Rectangle((0, 0), 1, 1, fc=COLOR[m], alpha=0.85, ec="black", lw=0.8)
           for m in ["DensityE", "DistE", "Single Model"]]
ax.legend(handles, ["DensityE", "DistE", "single-SVM reference"],
          loc="lower left", frameon=False, fontsize=8, ncol=3,
          bbox_to_anchor=(0.0, -0.30))

# Annotate the dispersion claim from the standard deviations, which is where
# it lives. Read from best_ensemble_results.csv so the figure cannot drift.
best = pd.read_csv(os.path.join(DATA, "best_ensemble_results.csv"))
def sd(method, learner):
    r = best[(best.ensemble_method == method) & (best.base_learner == learner)]
    assert len(r) == 1, "missing %s/%s in best_ensemble_results.csv" % (method, learner)
    return float(r.iloc[0]["std_score"])

sd_d, sd_x = sd("densitye", "lr"), sd("diste", "lr")
ax.annotate("LogReg fold SD:  DensityE $%.3f$   vs   DistE $%.3f$   (%.0f$\\times$ tighter)"
            % (sd_d, sd_x, sd_x / sd_d),
            xy=(0.5, 0.975), xycoords="axes fraction", ha="center",
            fontsize=8.5, color="#333333")

# the low outlier folds behind that SD show up as mean-below-median
d_lr = s[(s.method == "DensityE") & (s.learner == "lr")].iloc[0]
x_lr = s[(s.method == "DistE") & (s.learner == "lr")].iloc[0]
off_d = d_lr["mean"] - d_lr["median"]
off_x = x_lr["mean"] - x_lr["median"]

fig.tight_layout()
fig.savefig(os.path.join(FIGS, "boxplot_comparison_v2.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(FIGS, "boxplot_comparison_v2.png"), dpi=200, bbox_inches="tight")
print("wrote boxplot_comparison_v2.{pdf,png}")
print("lr fold SD    DensityE %.3f | DistE %.3f | %.0fx tighter" % (sd_d, sd_x, sd_x / sd_d))
print("lr mean-median  DensityE %+.4f | DistE %+.4f  (low outlier folds)" % (off_d, off_x))
print("lr IQR          DensityE %.4f | DistE %.4f  <- NOT the dispersion claim"
      % (d_lr["q3"] - d_lr["q1"], x_lr["q3"] - x_lr["q1"]))
