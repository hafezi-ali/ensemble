"""Fig. 1 pipeline schematic + Fig. 7 diagnostics panels"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'lib'))
from ddel_paths import ROOT, DATA, FIGS, DATASET, NPC, SEED, K_PUB, PHI_PUB, require_dataset
require_dataset()

#!/usr/bin/env python3
"""
Generate the DDEL-GMM overview figures.

Outputs two vector PDFs into manuscript/, both with embedded fonts and no
raster content:

  fig1_pipeline.pdf     the FIT / SELECT / WEIGHT schematic  (Sec. III)
  fig2_diagnostics.pdf  (a) aggregation comparison
                        (b) subset overlap vs base-learner disagreement
                        (c) oracle ceiling and remaining headroom   (Sec. IV)

Every number is read from CSV at run time. Nothing is hardcoded.

  data sources
    code/best_ensemble_results.csv          panel 2(a)
    data/selection_rule_diagnostic.csv      panels 2(b), 2(c)   [K=6, rule=distance]

Usage:  python3 code/codes/make_fig1.py     (run from the repository root)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse

# ---------------------------------------------------------------- paths ----
OUT = FIGS.rstrip(os.sep)
BEST = os.path.join(DATA, "best_ensemble_results.csv")
SEL = os.path.join(DATA, "selection_rule_diagnostic.csv")

K_PUB, PHI_PUB = 6, 0.5

# ----------------------------------------------------------------- data ----
best = pd.read_csv(BEST)
sel = pd.read_csv(SEL)
pub = sel[(sel["K"] == K_PUB) & (sel["rule"] == "distance")].sort_values("phi").copy()
assert len(pub) >= 5, f"expected the phi sweep at K={K_PUB}, got {len(pub)} rows"

phi = pub["phi"].to_numpy()
overlap = pub["overlap"].to_numpy() * 100
disagree = pub["disagree"].to_numpy() * 100
oracle = pub["oracle"].to_numpy() * 100
achieved = pub["ddel_F"].to_numpy() * 100
headroom = oracle - achieved

i_pub = int(np.argmin(np.abs(phi - PHI_PUB)))
i_top = int(np.argmax(phi))

# Okabe-Ito, colourblind-safe
ORANGE, SKY, MAUVE, BLUE, GREEN = "#E69F00", "#56B4E9", "#CC79A7", "#0072B2", "#009E73"
GREY = "#555555"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.labelsize": 8, "axes.titlesize": 8.5, "axes.titleweight": "bold",
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7,
    "axes.linewidth": 0.7, "xtick.major.width": 0.7, "ytick.major.width": 0.7,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})


def panel_tag(ax, s, dx=-0.30, dy=1.16):
    ax.text(dx, dy, s, transform=ax.transAxes, fontsize=10,
            fontweight="bold", ha="left", va="top")


# ======================================================== FIGURE 1: pipeline
fig1, ax = plt.subplots(figsize=(7.16, 2.75))
ax.set_xlim(0, 100)
ax.set_ylim(0, 40)
ax.axis("off")

# --- row 1: the three stages -------------------------------------------
STAGE_Y, STAGE_H, BW, GAP = 23.0, 14.5, 29.0, 5.5
X0 = 2.0
stages = [
    ("1.  FIT", GREEN,
     "Gaussian mixture,\nfull covariances\n"
     r"EM over 157 PCs $\rightarrow$ $\mu_k$, $\Sigma_k$, $\pi_k$"),
    ("2.  SELECT", ORANGE,
     "Rank all $m$ training rows\n"
     r"by distance to $\mu_k$; keep" "\n"
     r"the nearest $\phi m$ of them"),
    ("3.  WEIGHT", BLUE,
     "Mixture posterior of query $x^*$\n"
     r"$\gamma_k(x^*)\propto\pi_k\,\mathcal{N}(x^*\!\mid\!\mu_k,\Sigma_k)$" "\n"
     r"— carries the full $\Sigma_k$"),
]
centres = []
for i, (title, colour, body) in enumerate(stages):
    x = X0 + i * (BW + GAP)
    centres.append(x + BW / 2)
    ax.add_patch(FancyBboxPatch((x, STAGE_Y), BW, STAGE_H,
                                boxstyle="round,pad=0.35,rounding_size=1.2",
                                facecolor=colour, alpha=0.13,
                                edgecolor=colour, linewidth=1.3))
    ax.text(x + BW / 2, STAGE_Y + STAGE_H - 1.6, title, ha="center", va="top",
            fontsize=9, fontweight="bold", color=colour)
    ax.text(x + BW / 2, STAGE_Y + STAGE_H - 5.4, body, ha="center", va="top",
            fontsize=6.8, linespacing=1.65)

ymid = STAGE_Y + STAGE_H / 2
for i in range(2):
    x0 = X0 + i * (BW + GAP) + BW + 0.5
    ax.add_patch(FancyArrowPatch((x0, ymid), (x0 + GAP - 1.0, ymid),
                                 arrowstyle="-|>", mutation_scale=12,
                                 linewidth=1.3, color=GREY))

ax.text(X0 + BW / 2, STAGE_Y + STAGE_H + 2.4, "training data $X$", ha="center",
        va="bottom", fontsize=7.4, color=GREY, style="italic")
ax.text(centres[2], STAGE_Y + STAGE_H + 2.4, r"prediction $P(y \mid x^*)$", ha="center",
        va="bottom", fontsize=7.4, color=GREY, style="italic")

# --- row 2: the overlapping subsets, measured at the published phi ------
ov_pub = overlap[i_pub]
cx, cy = centres[1], 9.0
for j in range(6):
    a = 2 * np.pi * j / 6 + np.pi / 6
    ax.add_patch(Ellipse((cx + 4.6 * np.cos(a), cy + 2.3 * np.sin(a)), 12.4, 8.2,
                         facecolor=ORANGE, alpha=0.16, edgecolor=ORANGE, linewidth=0.8))
ax.text(cx, cy, r"$S_1\!\ldots\!S_6$", ha="center", va="center", fontsize=7.2,
        fontweight="bold", color="#8a5a00")
ax.add_patch(FancyArrowPatch((centres[1], STAGE_Y - 0.6), (centres[1], cy + 6.6),
                             arrowstyle="-|>", mutation_scale=11,
                             linewidth=1.1, color=GREY))
ax.text(cx - 13.0, cy, "six overlapping\ntraining subsets\n"
        + f"({ov_pub:.0f}% pairwise\noverlap at " + rf"$\phi={PHI_PUB:.1f}$)",
        ha="right", va="center", fontsize=6.8, color=GREY, linespacing=1.5)
ax.text(cx + 13.0, cy, r"one base learner $f_k$ per subset" "\n"
                       r"$P(y|x^*)=\sum_k \gamma_k(x^*)\,P_k(y|x^*)$",
        ha="left", va="center", fontsize=7.0, linespacing=1.7,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#f4f4f4",
                  edgecolor="#bbbbbb", linewidth=0.7))

fig1.savefig(os.path.join(OUT, "fig1_pipeline.pdf"), bbox_inches="tight", pad_inches=0.02)
fig1.savefig(os.path.join(OUT, "fig1_pipeline.png"), dpi=200, bbox_inches="tight", pad_inches=0.02)

# ==================================================== FIGURE 2: diagnostics
fig2, (axb, axc, axd) = plt.subplots(1, 3, figsize=(7.16, 3.15))
fig2.subplots_adjust(left=0.075, right=0.985, bottom=0.30, top=0.87, wspace=0.40)

# ---- 2(a) aggregation --------------------------------------------------
learners = ["lr", "svm", "knn", "dt"]
llab = {"lr": "LogReg", "svm": "SVM", "knn": "KNN", "dt": "DTree"}
methods = ["densitye", "diste", "maxe"]
mlab = {"densitye": "DensityE", "diste": "DistE", "maxe": "MaxE"}
mcol = {"densitye": ORANGE, "diste": SKY, "maxe": MAUVE}

pos, w = np.arange(len(learners)), 0.26
lo = 1.0
for i, meth in enumerate(methods):
    mu, sd = [], []
    for lr_ in learners:
        r = best[(best.base_learner == lr_) & (best.ensemble_method == meth)]
        mu.append(float(r.mean_score.iloc[0]) if len(r) else np.nan)
        sd.append(float(r.std_score.iloc[0]) if len(r) else 0.0)
    mu, sd = np.array(mu), np.array(sd)
    lo = min(lo, np.nanmin(mu - sd))
    axb.bar(pos + (i - 1) * w, mu, w, yerr=sd, capsize=2,
            color=mcol[meth], edgecolor="black", linewidth=0.5,
            error_kw=dict(elinewidth=0.8, capthick=0.8), label=mlab[meth])

axb.set_ylim(max(0.0, lo - 0.06), 1.0)          # floor below the smallest measured bar
axb.set_xticks(pos)
axb.set_xticklabels([llab[x] for x in learners])
axb.tick_params(axis="x", pad=1.5)
axb.set_ylabel("Macro F-score")
axb.set_title("Aggregation rule")
axb.legend(loc="upper center", bbox_to_anchor=(0.5, -0.185), ncol=3,
           frameon=False, handlelength=1.0, columnspacing=1.0, handletextpad=0.4)
axb.grid(axis="y", alpha=0.25, linewidth=0.6)
axb.set_axisbelow(True)
for s in ("top", "right"):
    axb.spines[s].set_visible(False)
panel_tag(axb, "(a)")

# ---- 2(b) overlap vs disagreement --------------------------------------
axc.plot(phi, overlap, marker="o", ms=4, lw=1.6, color=ORANGE, label="subset overlap")
axc.plot(phi, disagree, marker="s", ms=4, lw=1.6, color=MAUVE, label="learner disagreement")
axc.fill_between(phi, disagree, overlap, where=overlap >= disagree,
                 color=GREY, alpha=0.07, linewidth=0)
axc.axvline(PHI_PUB, color="black", ls="--", lw=0.9, alpha=0.55)
axc.text(PHI_PUB - 0.015, 97, r"published $\phi=%.1f$" % PHI_PUB, rotation=90,
         ha="right", va="top", fontsize=6.8, color="black")
axc.annotate(f"{disagree[i_top]:.1f}%",
             xy=(phi[i_top], disagree[i_top]), xytext=(phi[i_top] - 0.13, 17),
             fontsize=6.8, color=MAUVE,
             arrowprops=dict(arrowstyle="->", lw=0.7, color=MAUVE))
axc.set_xlim(phi.min() - 0.04, phi.max() + 0.04)
axc.set_ylim(0, 100)
axc.set_xlabel(r"sampling ratio $\phi$")
axc.set_ylabel("percent (%)")
axc.set_title("Diversity")
axc.legend(loc="upper center", bbox_to_anchor=(0.5, -0.185), ncol=1,
           frameon=False, handlelength=1.2, labelspacing=0.25)
axc.grid(alpha=0.25, linewidth=0.6)
axc.set_axisbelow(True)
for s in ("top", "right"):
    axc.spines[s].set_visible(False)
panel_tag(axc, "(b)")

# ---- 2(c) oracle ceiling and headroom ----------------------------------
axd.fill_between(phi, achieved, oracle, color=SKY, alpha=0.30, linewidth=0,
                 label="headroom")
axd.plot(phi, oracle, marker="D", ms=4, lw=1.6, color=BLUE, label="oracle ceiling")
axd.plot(phi, achieved, marker="o", ms=4, lw=1.6, color=ORANGE, label="DDEL-GMM achieved")
axd.axvline(PHI_PUB, color="black", ls="--", lw=0.9, alpha=0.55)

axd.annotate(f"{headroom[i_pub]:.2f} pp", xy=(phi[i_pub], (oracle[i_pub] + achieved[i_pub]) / 2),
             xytext=(phi[i_pub] - 0.24, 96.55), fontsize=7, color=BLUE, fontweight="bold",
             arrowprops=dict(arrowstyle="->", lw=0.7, color=BLUE))
axd.annotate(f"{headroom[i_top]:.2f} pp", xy=(phi[i_top], (oracle[i_top] + achieved[i_top]) / 2),
             xytext=(phi[i_top] - 0.30, 99.25), fontsize=7, color=BLUE, fontweight="bold",
             arrowprops=dict(arrowstyle="->", lw=0.7, color=BLUE))

pad = 0.35
axd.set_ylim(min(achieved.min(), oracle.min()) - pad, oracle.max() + pad)
axd.set_xlim(phi.min() - 0.04, phi.max() + 0.04)
axd.set_xlabel(r"sampling ratio $\phi$")
axd.set_ylabel("Macro F-score (%)")
axd.set_title("Oracle headroom")
axd.legend(loc="upper center", bbox_to_anchor=(0.5, -0.185), ncol=1,
           frameon=False, handlelength=1.2, labelspacing=0.22)
axd.grid(alpha=0.25, linewidth=0.6)
axd.set_axisbelow(True)
for s in ("top", "right"):
    axd.spines[s].set_visible(False)
panel_tag(axd, "(c)")

fig2.savefig(os.path.join(OUT, "fig2_diagnostics.pdf"), bbox_inches="tight", pad_inches=0.02)
fig2.savefig(os.path.join(OUT, "fig2_diagnostics.png"), dpi=200, bbox_inches="tight", pad_inches=0.02)

print("phi      ", np.round(phi, 2))
print("overlap  ", np.round(overlap, 1))
print("disagree ", np.round(disagree, 1))
print("oracle   ", np.round(oracle, 2))
print("achieved ", np.round(achieved, 2))
print("headroom ", np.round(headroom, 2))
print("panel-a bar floor", round(max(0.0, lo - 0.06), 3))
