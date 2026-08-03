#!/usr/bin/env python3
"""
DDEL-GMM Figure Renderer
========================

Regenerates all seven data-driven figures from hand-editable CSVs in results/.
Each figure reads ONLY from results/*.csv (never from reproduce/data), writes
PDF (for LaTeX \includegraphics) and PNG (for quick inspection) to figures_out/.

Figures:
  1. fscore_vs_phi         - F-score vs sampling ratio phi (4 learners)
  2. fscore_vs_clusters    - F-score vs number of clusters K (4 learners)
  3. boxplot_comparison_v2 - Distribution of macro F1 by method and learner
  4. fig2_diagnostics      - 3-panel diagnostics (aggregation, diversity, oracle)
  5. sota_comparison       - State-of-the-art comparison with error bars
  6. gmm_vs_kmeans_synthetic - 6-panel synthetic clustering ablation
  7. noclustering_comparison - No-clustering baseline comparison

Plus 4 stubs for reviewer-requested figures (will auto-populate when CSVs filled):
  - concept_drift
  - delak_fhdes
  - nonspherical
  - case_study

Usage:
  python make_figures.py           # generates all figures to figures_out/
  from make_figures import *; figure_fscore_vs_phi()  # call individual function
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.stats import wilcoxon
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# Configuration & Constants
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "figures_out")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Publication-grade color scheme (Okabe-Ito, colorblind-safe)
COLORS = {
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "mauve": "#CC79A7",
    "blue": "#0072B2",
    "green": "#009E73",
    "grey": "#555555",
    "light_grey": "#CCCCCC",
}

# Font and style configuration
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "axes.titleweight": "bold",
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def apply_figure_style(fig, axes=None):
    """
    Apply publication-grade styling to a figure.
    
    Based on figure-style skill conventions:
    - Clean spines (no top/right)
    - Consistent typography and sizing
    - Proper axis padding and label economy
    - Frameless legends in whitespace
    """
    if axes is None:
        axes = fig.get_axes()
    elif not isinstance(axes, list):
        axes = [axes]
    
    for ax in axes:
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Grid styling
        ax.grid(True, alpha=0.25, linewidth=0.6, axis='y')
        ax.set_axisbelow(True)
        
        # Tick styling
        ax.tick_params(axis='both', which='major', labelsize=7.5, length=3, width=0.7)
        
    return fig

def save_figure(fig, name):
    """Save figure as both PDF and PNG at 300 dpi."""
    ensure_output_dir()
    pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
    png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    
    # Apply styling before saving
    apply_figure_style(fig)
    
    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(png_path, dpi=300, bbox_inches="tight", pad_inches=0.02)
    return pdf_path

def is_empty(df):
    """Check if a DataFrame has no filled metric values (all rows empty except ID cols)."""
    metric_cols = [c for c in df.columns if c not in ['phi', 'K', 'drift_point', 'method', 'base_learner', 'clustering_type', 'data_geometry', 'dataset']]
    if not metric_cols:
        return True
    return df[metric_cols].isna().all().all() and df[metric_cols].eq('').all().all()

def add_panel_letter(ax, letter, x=-0.30, y=1.16, fontsize=10):
    """Add a panel letter (a, b, c, etc.) to an axes in publication style."""
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontsize=fontsize,
            fontweight="bold", ha="left", va="top")

def placeholder_figure(title, width_mm=177, height_mm=100):
    """Create a placeholder figure for empty data."""
    fig, ax = plt.subplots(figsize=(width_mm/25.4, height_mm/25.4))
    ax.text(0.5, 0.5, title, ha='center', va='center', fontsize=12, fontweight='bold',
            transform=ax.transAxes)
    ax.text(0.5, 0.3, "awaiting data", ha='center', va='center', fontsize=10, style='italic',
            transform=ax.transAxes, color=COLORS['grey'])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    return fig

# ============================================================================
# Figure 1: F-score vs phi (sampling ratio)
# ============================================================================

def figure_fscore_vs_phi():
    """
    Figure 1: F-score vs phi for 4 base learners.
    
    Data: results/figure_fscore_vs_phi.csv
    Status: PARTIAL - only 3 LR values known (0.4, 0.5, 0.9)
    """
    csv_path = os.path.join(RESULTS_DIR, "figure_fscore_vs_phi.csv")
    df = pd.read_csv(csv_path)
    
    if is_empty(df):
        fig = placeholder_figure("fscore_vs_phi - awaiting sweep data", width_mm=140, height_mm=100)
        return fig
    
    # Plot data
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    
    learners = ["lr_fscore", "svm_fscore", "knn_fscore", "dt_fscore"]
    learner_labels = {"lr_fscore": "LogReg", "svm_fscore": "SVM", "knn_fscore": "KNN", "dt_fscore": "DTree"}
    learner_colors = {
        "lr_fscore": COLORS["orange"],
        "svm_fscore": COLORS["sky"],
        "knn_fscore": COLORS["mauve"],
        "dt_fscore": COLORS["blue"],
    }
    
    for learner in learners:
        # Filter to rows with data in this column
        data = df[df[learner].notna() & (df[learner] != "")].copy()
        if len(data) > 0:
            data[learner] = pd.to_numeric(data[learner], errors='coerce')
            data = data.dropna(subset=[learner])
            if len(data) > 0:
                ax.plot(data["phi"], data[learner], marker="o", ms=4, lw=1.6,
                       color=learner_colors[learner], label=learner_labels[learner])
    
    ax.set_xlabel(r"sampling ratio $\phi$")
    ax.set_ylabel("Macro F-score")
    ax.set_title("F-score vs sampling ratio")
    ax.set_xlim(0.05, 0.95)
    ax.set_ylim(0.95, 1.0)
    ax.grid(alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="best", frameon=False, fontsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    
    fig.tight_layout()
    save_figure(fig, "fscore_vs_phi")
    plt.close(fig)
    return fig

# ============================================================================
# Figure 2: F-score vs K (number of clusters)
# ============================================================================

def figure_fscore_vs_clusters():
    """
    Figure 2: F-score vs number of clusters K.
    
    Data: results/figure_fscore_vs_clusters.csv
    Status: EMPTY - no sweep data available
    """
    csv_path = os.path.join(RESULTS_DIR, "figure_fscore_vs_clusters.csv")
    df = pd.read_csv(csv_path)
    
    if is_empty(df):
        fig = placeholder_figure("fscore_vs_clusters - awaiting K sweep data", width_mm=140, height_mm=100)
        save_figure(fig, "fscore_vs_clusters")
        plt.close(fig)
        return fig
    
    # Plot data
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    
    learners = ["lr_fscore", "svm_fscore", "knn_fscore", "dt_fscore"]
    learner_labels = {"lr_fscore": "LogReg", "svm_fscore": "SVM", "knn_fscore": "KNN", "dt_fscore": "DTree"}
    learner_colors = {
        "lr_fscore": COLORS["orange"],
        "svm_fscore": COLORS["sky"],
        "knn_fscore": COLORS["mauve"],
        "dt_fscore": COLORS["blue"],
    }
    
    for learner in learners:
        data = df[df[learner].notna() & (df[learner] != "")].copy()
        if len(data) > 0:
            data[learner] = pd.to_numeric(data[learner], errors='coerce')
            data = data.dropna(subset=[learner])
            if len(data) > 0:
                ax.plot(data["K"], data[learner], marker="s", ms=4, lw=1.6,
                       color=learner_colors[learner], label=learner_labels[learner])
    
    ax.set_xlabel("Number of clusters $K$")
    ax.set_ylabel("Macro F-score")
    ax.set_title("F-score vs number of clusters")
    ax.set_xlim(1, 11)
    ax.set_ylim(0.95, 1.0)
    ax.grid(alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="best", frameon=False, fontsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    
    fig.tight_layout()
    save_figure(fig, "fscore_vs_clusters")
    plt.close(fig)
    return fig

# ============================================================================
# Figure 3: Boxplot comparison (per-fold distribution)
# ============================================================================

def figure_boxplot_comparison():
    """
    Figure 3: Boxplot of macro F1 distribution by method and learner.
    
    This is a data-driven figure computed from table_ensemble_comparison.csv.
    For now, a stub that will be enhanced when per-fold data becomes available.
    """
    csv_path = os.path.join(RESULTS_DIR, "table_ensemble_comparison.csv")
    df = pd.read_csv(csv_path)
    
    if is_empty(df):
        fig = placeholder_figure("boxplot_comparison - awaiting per-fold data", width_mm=177, height_mm=130)
        save_figure(fig, "boxplot_comparison_v2")
        plt.close(fig)
        return fig
    
    # For now, show a simple bar plot of the means from table_ensemble_comparison
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    
    methods = df["ensemble_method"].unique()
    learners = ["lr", "svm", "knn", "dt"]
    learner_labels = {"lr": "LogReg", "svm": "SVM", "knn": "KNN", "dt": "DTree"}
    
    method_colors = {
        "DensityE": COLORS["orange"],
        "DistE": COLORS["sky"],
        "MaxE": COLORS["mauve"],
    }
    
    x_pos = 0
    positions = []
    colors = []
    means = []
    
    for learner in learners:
        for method in ["DensityE", "DistE", "MaxE"]:
            row = df[(df["ensemble_method"] == method) & (df["base_learner"] == learner)]
            if len(row) > 0:
                means.append(float(row["mean_score"].iloc[0]))
                colors.append(method_colors.get(method, COLORS["grey"]))
                positions.append(x_pos)
                x_pos += 0.3
        x_pos += 0.5  # gap between learner groups
    
    if means:
        ax.bar(positions, means, width=0.25, color=colors, edgecolor="black", linewidth=0.5, alpha=0.85)
        ax.set_ylim(0.88, 1.0)
        ax.set_ylabel("weighted $F_1$-score")
        ax.set_title("Aggregation method comparison")
        ax.grid(axis="y", alpha=0.3, linewidth=0.5)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    
    fig.tight_layout()
    save_figure(fig, "boxplot_comparison_v2")
    plt.close(fig)
    return fig

# ============================================================================
# Figure 4: Diagnostics (3 panels)
# ============================================================================

def figure_diagnostics():
    """
    Figure 4: 3-panel diagnostics.
    
    Panel (a): Aggregation rule comparison (DensityE, DistE, MaxE)
    Panel (b): Overlap vs learner disagreement
    Panel (c): Oracle ceiling and headroom
    
    Data: table_ensemble_comparison.csv, table_diversity_cost.csv
    """
    best_csv = os.path.join(RESULTS_DIR, "table_ensemble_comparison.csv")
    div_csv = os.path.join(RESULTS_DIR, "table_diversity_cost.csv")
    
    best = pd.read_csv(best_csv)
    div = pd.read_csv(div_csv)
    
    if is_empty(best) or is_empty(div):
        fig = placeholder_figure("fig2_diagnostics - awaiting data", width_mm=177, height_mm=110)
        save_figure(fig, "fig2_diagnostics")
        plt.close(fig)
        return fig
    
    fig, (axb, axc, axd) = plt.subplots(1, 3, figsize=(7.16, 3.15))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.30, top=0.87, wspace=0.40)
    
    learners = ["lr", "svm", "knn", "dt"]
    llab = {"lr": "LogReg", "svm": "SVM", "knn": "KNN", "dt": "DTree"}
    methods = ["DensityE", "DistE", "MaxE"]
    mlab = {"DensityE": "DensityE", "DistE": "DistE", "MaxE": "MaxE"}
    mcol = {"DensityE": COLORS["orange"], "DistE": COLORS["sky"], "MaxE": COLORS["mauve"]}
    
    # Panel (a): Aggregation
    pos, w = np.arange(len(learners)), 0.26
    lo = 1.0
    for i, meth in enumerate(methods):
        mu, sd = [], []
        for lr_ in learners:
            r = best[(best.base_learner == lr_) & (best.ensemble_method == meth)]
            if len(r) > 0:
                mu.append(float(r.mean_score.iloc[0]))
                sd.append(float(r.std_score.iloc[0]))
            else:
                mu.append(np.nan)
                sd.append(0.0)
        mu, sd = np.array(mu), np.array(sd)
        lo = min(lo, np.nanmin(mu - sd))
        axb.bar(pos + (i - 1) * w, mu, w, yerr=sd, capsize=2,
                color=mcol[meth], edgecolor="black", linewidth=0.5,
                error_kw=dict(elinewidth=0.8, capthick=0.8), label=mlab[meth])
    
    axb.set_ylim(max(0.0, lo - 0.06), 1.0)
    axb.set_xticks(pos)
    axb.set_xticklabels([llab[x] for x in learners])
    axb.tick_params(axis="x", pad=1.5)
    axb.set_ylabel("Macro F-score")
    axb.set_title("Aggregation rule", fontsize=8.5, fontweight="bold")
    axb.legend(loc="upper center", bbox_to_anchor=(0.5, -0.185), ncol=3,
               frameon=False, handlelength=1.0, columnspacing=1.0, handletextpad=0.4, fontsize=7)
    axb.grid(axis="y", alpha=0.25, linewidth=0.6)
    axb.set_axisbelow(True)
    for s in ("top", "right"):
        axb.spines[s].set_visible(False)
    add_panel_letter(axb, "a")
    
    # Panel (b): Overlap vs disagreement
    div_sorted = div.sort_values("phi")
    phi_vals = pd.to_numeric(div_sorted["phi"], errors='coerce').to_numpy()
    overlap = pd.to_numeric(div_sorted["overlap"], errors='coerce').to_numpy() * 100
    disagreement = pd.to_numeric(div_sorted["disagreement"], errors='coerce').to_numpy() * 100
    
    axc.plot(phi_vals, overlap, marker="o", ms=4, lw=1.6, color=COLORS["orange"], label="subset overlap")
    axc.plot(phi_vals, disagreement, marker="s", ms=4, lw=1.6, color=COLORS["mauve"], label="learner disagreement")
    axc.fill_between(phi_vals, disagreement, overlap, where=overlap >= disagreement,
                     color=COLORS["grey"], alpha=0.07, linewidth=0)
    axc.set_xlim(phi_vals.min() - 0.04, phi_vals.max() + 0.04)
    axc.set_ylim(0, 100)
    axc.set_xlabel(r"sampling ratio $\phi$")
    axc.set_ylabel("percent (%)")
    axc.set_title("Diversity", fontsize=8.5, fontweight="bold")
    axc.legend(loc="upper center", bbox_to_anchor=(0.5, -0.185), ncol=1,
               frameon=False, handlelength=1.2, labelspacing=0.25, fontsize=7)
    axc.grid(alpha=0.25, linewidth=0.6)
    axc.set_axisbelow(True)
    for s in ("top", "right"):
        axc.spines[s].set_visible(False)
    add_panel_letter(axc, "b")
    
    # Panel (c): Oracle and headroom
    oracle = pd.to_numeric(div_sorted["oracle"], errors='coerce').to_numpy() * 100
    achieved = pd.to_numeric(div_sorted["macro_f1"], errors='coerce').to_numpy() * 100
    headroom = oracle - achieved
    
    axd.fill_between(phi_vals, achieved, oracle, color=COLORS["sky"], alpha=0.30, linewidth=0,
                     label="headroom")
    axd.plot(phi_vals, oracle, marker="D", ms=4, lw=1.6, color=COLORS["blue"], label="oracle ceiling")
    axd.plot(phi_vals, achieved, marker="o", ms=4, lw=1.6, color=COLORS["orange"], label="DDEL-GMM")
    
    pad = 0.35
    axd.set_ylim(min(achieved.min(), oracle.min()) - pad, oracle.max() + pad)
    axd.set_xlim(phi_vals.min() - 0.04, phi_vals.max() + 0.04)
    axd.set_xlabel(r"sampling ratio $\phi$")
    axd.set_ylabel("Macro F-score (%)")
    axd.set_title("Oracle headroom", fontsize=8.5, fontweight="bold")
    axd.legend(loc="upper center", bbox_to_anchor=(0.5, -0.185), ncol=1,
               frameon=False, handlelength=1.2, labelspacing=0.22, fontsize=7)
    axd.grid(alpha=0.25, linewidth=0.6)
    axd.set_axisbelow(True)
    for s in ("top", "right"):
        axd.spines[s].set_visible(False)
    add_panel_letter(axd, "c")
    
    save_figure(fig, "fig2_diagnostics")
    plt.close(fig)
    return fig

# ============================================================================
# Figure 5: SOTA Comparison
# ============================================================================

def figure_sota_comparison():
    """
    Figure 5: State-of-the-art comparison with error bars and p-values.
    
    Uses per-fold data to compute p-values via Wilcoxon signed-rank test.
    Data: figure_sota_perfold.csv (per-fold F-scores, one row per fold, one column per method)
    """
    perfold_path = os.path.join(RESULTS_DIR, "figure_sota_perfold.csv")
    
    if not os.path.exists(perfold_path):
        fig = placeholder_figure("sota_comparison - awaiting per-fold data", width_mm=160, height_mm=110)
        save_figure(fig, "sota_comparison")
        plt.close(fig)
        return fig
    
    # Load per-fold data
    per = pd.read_csv(perfold_path)
    ours = "DDEL-GMM (ours)"
    
    if ours not in per.columns:
        # Try alternate name
        ours_cols = [c for c in per.columns if 'ddel' in c.lower() or 'ours' in c.lower()]
        if ours_cols:
            ours = ours_cols[0]
        else:
            ours = per.columns[0]  # Use first column
    
    baselines = [c for c in per.columns if c != ours]
    
    # Compute stats and p-values
    rows = []
    for m in [ours] + baselines:
        v = pd.to_numeric(per[m], errors='coerce').to_numpy()
        v = v[~np.isnan(v)]  # Remove NaNs
        if len(v) > 0:
            if m == ours:
                p = np.nan
            else:
                try:
                    p = wilcoxon(pd.to_numeric(per[ours], errors='coerce'), v, alternative="greater").pvalue
                except:
                    p = np.nan
            rows.append((m, v.mean(), v.std(ddof=1), p))
    
    res = pd.DataFrame(rows, columns=["method", "mean", "sd", "p"])
    
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    x = np.arange(len(res))
    colors = [COLORS["orange"]] + [COLORS["sky"]] * (len(baselines))
    
    ax.bar(x, res["mean"], yerr=res["sd"], capsize=4, color=colors,
           edgecolor="black", linewidth=0.7, width=0.62,
           error_kw=dict(elinewidth=0.9, ecolor="#333333"))
    
    lo = float((res["mean"] - res["sd"]).min())
    hi = float((res["mean"] + res["sd"]).max())
    pad = 0.25 * (hi - lo)
    ax.set_ylim(max(0.0, lo - pad), hi + pad * 1.6)
    
    # Add value labels and p-values
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
    ax.set_ylabel("Macro F-score")
    ax.set_title("State-of-the-art comparison")
    ax.grid(axis="y", alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    save_figure(fig, "sota_comparison")
    plt.close(fig)
    return fig

# ============================================================================
# Figure 6: GMM vs KMeans Synthetic (6 panels)
# ============================================================================

def figure_gmm_vs_kmeans_synthetic():
    """
    Figure 6: 6-panel synthetic clustering comparison.
    
    This is currently a complex multi-panel figure. For now, create a placeholder.
    The actual implementation will require the synthetic sweep data.
    """
    fig = placeholder_figure("gmm_vs_kmeans_synthetic - 6-panel synthetic ablation\n(awaiting sweep data)", 
                            width_mm=177, height_mm=140)
    save_figure(fig, "gmm_vs_kmeans_synthetic")
    plt.close(fig)
    return fig

# ============================================================================
# Figure 7: No-Clustering Comparison
# ============================================================================

def figure_noclustering_comparison():
    """
    Figure 7: Comparison of DDEL-GMM against methods without clustering.
    
    Uses per-fold data to show Nemenyi critical difference and boxplots.
    Data: figure_noclustering_perfold.csv (per-fold F-scores, 10 folds × N methods)
    """
    from scipy.stats import rankdata, studentized_range
    
    perfold_path = os.path.join(RESULTS_DIR, "figure_noclustering_perfold.csv")
    
    if not os.path.exists(perfold_path):
        fig = placeholder_figure("noclustering_comparison - awaiting per-fold data", width_mm=177, height_mm=130)
        save_figure(fig, "noclustering_comparison")
        plt.close(fig)
        return fig
    
    # Load per-fold data
    pf = pd.read_csv(perfold_path)
    
    # Method names and order
    ours = "DDEL-GMM (ours)"
    order = pf.mean().sort_values(ascending=False).index.tolist()
    n, k = len(pf), pf.shape[1]
    
    # Compute mean ranks for Nemenyi CD
    R = np.vstack([rankdata(-pf.iloc[i].to_numpy()) for i in range(n)])
    mr = pd.Series(R.mean(0), index=pf.columns)
    
    # Nemenyi critical difference at alpha=0.05
    CD = studentized_range.ppf(0.95, k, np.inf) / np.sqrt(2) * np.sqrt(k * (k + 1) / (6.0 * n))
    
    # Create figure with two subplots
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.2, 4.3),
                                   gridspec_kw={"width_ratios": [1.35, 1]})
    
    # Left panel: boxplots of per-fold distributions
    cols = [COLORS["orange"] if c == ours else COLORS["sky"] for c in order]
    bp = axL.boxplot([pf[c] for c in order], patch_artist=True, widths=0.62,
                     medianprops=dict(color="black", lw=1.4),
                     flierprops=dict(marker="o", ms=3, mfc="0.4", mec="none"))
    for patch, c in zip(bp["boxes"], cols):
        patch.set_facecolor(c)
        patch.set_alpha(0.85)
        patch.set_edgecolor("black")
        patch.set_linewidth(0.8)
    
    # Add mean markers
    for i, c in enumerate(order, 1):
        axL.plot(i, pf[c].mean(), marker="D", ms=5, color="white",
                 mec="black", mew=0.9, zorder=5)
    
    axL.set_xticks(range(1, len(order) + 1))
    axL.set_xticklabels([c.replace(" (ours)", "\n(ours)").replace(" (LR)", "\n(LR)")
                         .replace("Gradient Boosting", "Gradient\nBoosting")
                         .replace("Random Forest", "Random\nForest")
                         for c in order], fontsize=8.5)
    axL.set_ylabel("Macro F-score", fontsize=9)
    axL.set_title(f"Per-fold F-score ({n}-fold CV)", fontsize=8.5, fontweight="bold")
    axL.grid(axis="y", alpha=0.3, lw=0.6)
    axL.set_axisbelow(True)
    axL.text(0.99, 0.965, "white diamond = mean", transform=axL.transAxes,
             ha="right", va="top", fontsize=7, style="italic", color="0.35")
    add_panel_letter(axL, "a", x=-0.05, y=1.08)
    
    # Right panel: mean ranks with Nemenyi CD
    mro = mr[order]
    ypos = np.arange(len(order))[::-1]
    axR.barh(ypos, mro.values, color=cols, alpha=0.85, edgecolor="black", lw=0.8, height=0.6)
    
    # Add CD error bar
    axR.errorbar(mro[ours], ypos[order.index(ours)], xerr=CD / 2, color="black",
                 capsize=4, lw=1.3, zorder=6)
    axR.axvline(mro[ours] + CD, ls="--", lw=1.1, color=COLORS["orange"])
    axR.text(mro[ours] + CD, len(order) - 0.35, f"  CD={CD:.2f}", color=COLORS["orange"],
             fontsize=8, va="top")
    
    # Add value labels
    for yv, c in zip(ypos, order):
        axR.text(mro[c] + 0.09, yv, f"{mro[c]:.2f}", va="center", fontsize=7.5)
    
    axR.set_yticks(ypos)
    axR.set_yticklabels(order, fontsize=8)
    axR.set_xlabel("Mean Friedman rank  (1 = best)", fontsize=9)
    axR.set_title("Mean rank & Nemenyi CD", fontsize=8.5, fontweight="bold")
    axR.grid(axis="x", alpha=0.3, lw=0.6)
    axR.set_axisbelow(True)
    axR.set_xlim(0, k + 0.6)
    add_panel_letter(axR, "b", x=-0.08, y=1.08)
    
    fig.suptitle("DDEL-GMM vs non-clustering baselines", fontsize=10, y=0.98)
    fig.tight_layout()
    save_figure(fig, "noclustering_comparison")
    plt.close(fig)
    return fig

# ============================================================================
# Reviewer-Requested Figure Stubs
# ============================================================================

def figure_concept_drift():
    """Stub: Concept drift over time windows."""
    csv_path = os.path.join(RESULTS_DIR, "figure_concept_drift.csv")
    try:
        df = pd.read_csv(csv_path)
    except:
        df = pd.DataFrame()
    
    if is_empty(df):
        fig = placeholder_figure("concept_drift - awaiting drift simulation data", width_mm=160, height_mm=110)
    else:
        fig = placeholder_figure("concept_drift - data present but not yet visualized", width_mm=160, height_mm=110)
    
    save_figure(fig, "concept_drift")
    plt.close(fig)
    return fig

def figure_delak_fhdes():
    """Stub: DELAK and FH-DES comparison."""
    csv_path = os.path.join(RESULTS_DIR, "table_delak_fhdes.csv")
    try:
        df = pd.read_csv(csv_path)
    except:
        df = pd.DataFrame()
    
    if is_empty(df):
        fig = placeholder_figure("delak_fhdes - awaiting new method implementations", width_mm=160, height_mm=110)
    else:
        fig = placeholder_figure("delak_fhdes - data present but not yet visualized", width_mm=160, height_mm=110)
    
    save_figure(fig, "delak_fhdes")
    plt.close(fig)
    return fig

def figure_nonspherical():
    """Stub: Non-spherical cluster comparison."""
    csv_path = os.path.join(RESULTS_DIR, "table_nonspherical.csv")
    try:
        df = pd.read_csv(csv_path)
    except:
        df = pd.DataFrame()
    
    if is_empty(df):
        fig = placeholder_figure("nonspherical - awaiting synthetic non-spherical data", width_mm=160, height_mm=110)
    else:
        fig = placeholder_figure("nonspherical - data present but not yet visualized", width_mm=160, height_mm=110)
    
    save_figure(fig, "nonspherical")
    plt.close(fig)
    return fig

def figure_case_study():
    """Stub: Medical case study."""
    csv_path = os.path.join(RESULTS_DIR, "table_case_study.csv")
    try:
        df = pd.read_csv(csv_path)
    except:
        df = pd.DataFrame()
    
    if is_empty(df):
        fig = placeholder_figure("case_study - awaiting medical dataset results", width_mm=160, height_mm=110)
    else:
        fig = placeholder_figure("case_study - data present but not yet visualized", width_mm=160, height_mm=110)
    
    save_figure(fig, "case_study")
    plt.close(fig)
    return fig

# ============================================================================
# Main entry point
# ============================================================================

def regenerate_all_figures():
    """Regenerate all figures and return a summary."""
    ensure_output_dir()
    
    print("=" * 70)
    print("DDEL-GMM Figure Renderer")
    print("=" * 70)
    
    figures = [
        ("fscore_vs_phi", figure_fscore_vs_phi),
        ("fscore_vs_clusters", figure_fscore_vs_clusters),
        ("boxplot_comparison_v2", figure_boxplot_comparison),
        ("fig2_diagnostics", figure_diagnostics),
        ("sota_comparison", figure_sota_comparison),
        ("gmm_vs_kmeans_synthetic", figure_gmm_vs_kmeans_synthetic),
        ("noclustering_comparison", figure_noclustering_comparison),
    ]
    
    stubs = [
        ("concept_drift", figure_concept_drift),
        ("delak_fhdes", figure_delak_fhdes),
        ("nonspherical", figure_nonspherical),
        ("case_study", figure_case_study),
    ]
    
    results = []
    
    print("\nGenerating main figures:")
    for name, func in figures:
        try:
            func()
            pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
            if os.path.exists(pdf_path):
                size_kb = os.path.getsize(pdf_path) / 1024
                print(f"  ✓ {name:30s} ({size_kb:6.1f} KB)")
                results.append({"name": name, "status": "generated"})
            else:
                print(f"  ✗ {name:30s} (output not found)")
                results.append({"name": name, "status": "failed"})
        except Exception as e:
            print(f"  ✗ {name:30s} (error: {str(e)[:50]})")
            results.append({"name": name, "status": "error"})
    
    print("\nGenerating placeholder stubs for reviewer-requested figures:")
    for name, func in stubs:
        try:
            func()
            pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
            if os.path.exists(pdf_path):
                size_kb = os.path.getsize(pdf_path) / 1024
                print(f"  ✓ {name:30s} (placeholder, {size_kb:6.1f} KB)")
                results.append({"name": name, "status": "stub"})
            else:
                print(f"  ✗ {name:30s} (output not found)")
                results.append({"name": name, "status": "failed"})
        except Exception as e:
            print(f"  ✗ {name:30s} (error: {str(e)[:50]})")
            results.append({"name": name, "status": "error"})
    
    print("\n" + "=" * 70)
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    regenerate_all_figures()
