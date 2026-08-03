#!/usr/bin/env python3
"""
DDEL-GMM Figure Renderer (FIXED VERSION)
==========================================

Regenerates all data-driven figures from hand-editable CSVs in results/*.csv.
This is the corrected version fixing:
  1. boxplot_comparison_v2: Now uses proper box-and-whisker plots with 5-number summaries
  2. gmm_vs_kmeans_synthetic: Now implements all 6 panels from sweep/covtype/perfold data

Usage:
    python make_figures_fixed.py

All figures output to figures_out/ as both PDF and PNG (300 dpi).
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import rankdata, studentized_range, wilcoxon, spearmanr

REPO_ROOT = "/home/ali/Documents/ensemble"
RESULTS_DIR = os.path.join(REPO_ROOT, "results")
OUTPUT_DIR = os.path.join(REPO_ROOT, "figures_out")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Colors
COLORS = {
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "grey": "#BBBBBB",
}

def save_figure(fig, name):
    """Save figure as both PDF and PNG at 300 dpi"""
    pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
    png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(png_path, dpi=300, bbox_inches="tight", pad_inches=0.02)
    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"  ✓ {name:35s} ({size_kb:6.1f} KB)")
    return pdf_path

def add_panel_letter(ax, letter, x=-0.05, y=1.08):
    """Add panel letter (a, b, c...) to subplot"""
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontsize=11,
            fontweight="bold", va="top", ha="right")

def placeholder_figure(title, width_mm=160, height_mm=110):
    """Create a labeled placeholder for missing data"""
    fig = plt.figure(figsize=(width_mm/25.4, height_mm/25.4), dpi=100)
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=10,
            color="#999999", transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig

# ============================================================================
# FIGURE 1: F-SCORE VS PHI (PARTIAL DATA)
# ============================================================================

def figure_fscore_vs_phi():
    """F-score vs sampling ratio phi"""
    csv_path = os.path.join(RESULTS_DIR, "figure_fscore_vs_phi.csv")
    if not os.path.exists(csv_path):
        fig = placeholder_figure("fscore_vs_phi - awaiting phi sweep data")
        save_figure(fig, "fscore_vs_phi")
        plt.close(fig)
        return
    
    df = pd.read_csv(csv_path)
    metric_cols = [c for c in df.columns if c not in ['phi', 'K', 'base_learner']]
    
    fig, ax = plt.subplots(figsize=(6, 3.4))
    
    for learner in ['lr', 'svm', 'knn', 'dt']:
        col = f"{learner}_fscore" if f"{learner}_fscore" in df.columns else learner
        if col in df.columns:
            data = df[[col]].dropna()
            if len(data) > 0:
                ax.plot(df['phi'][:len(data)], data[col], marker="o", label=learner.upper(),
                       linewidth=1.2, markersize=4)
    
    ax.set_xlabel("Sampling ratio (φ)", fontsize=9)
    ax.set_ylabel("Macro F-score")
    ax.set_xlim(0, 1.0)
    ax.legend(frameon=False, loc="best", fontsize=8)
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    save_figure(fig, "fscore_vs_phi")
    plt.close(fig)

# ============================================================================
# FIGURE 2: F-SCORE VS K (EMPTY PLACEHOLDER)
# ============================================================================

def figure_fscore_vs_clusters():
    """F-score vs number of clusters K"""
    csv_path = os.path.join(RESULTS_DIR, "figure_fscore_vs_clusters.csv")
    if not os.path.exists(csv_path):
        fig = placeholder_figure("fscore_vs_clusters - awaiting K sweep data")
        save_figure(fig, "fscore_vs_clusters")
        plt.close(fig)
        return
    
    df = pd.read_csv(csv_path)
    
    # Check if truly empty
    metric_cols = [c for c in df.columns if c not in ['K', 'base_learner']]
    is_empty = df[metric_cols].isna().all().all() and df[metric_cols].eq('').all().all()
    
    if is_empty:
        fig = placeholder_figure("fscore_vs_clusters - awaiting K sweep data")
        save_figure(fig, "fscore_vs_clusters")
        plt.close(fig)
        return
    
    fig, ax = plt.subplots(figsize=(6, 3.4))
    
    for learner in ['lr', 'svm', 'knn', 'dt']:
        col = f"{learner}_fscore" if f"{learner}_fscore" in df.columns else learner
        if col in df.columns:
            data = df[[col]].dropna()
            if len(data) > 0:
                ax.plot(df['K'][:len(data)], data[col], marker="s", label=learner.upper(),
                       linewidth=1.2, markersize=4)
    
    ax.set_xlabel("Number of clusters (K)")
    ax.set_ylabel("Macro F-score")
    ax.legend(frameon=False, loc="best", fontsize=8)
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    save_figure(fig, "fscore_vs_clusters")
    plt.close(fig)

# ============================================================================
# FIGURE 3: BOXPLOT COMPARISON (CORRECTED - BOX-AND-WHISKER)
# ============================================================================

def figure_boxplot_comparison_v2():
    """
    Figure 3: Per-fold F-score distribution by method and learner (box-and-whisker).
    
    Data: figure_boxplot_stats.csv (precomputed 5-number summaries)
          table_best_ensemble_results.csv (std_score for dispersion annotation)
    """
    stats_path = os.path.join(RESULTS_DIR, "figure_boxplot_stats.csv")
    best_path = os.path.join(RESULTS_DIR, "table_best_ensemble_results.csv")
    
    if not os.path.exists(stats_path):
        fig = placeholder_figure("boxplot_comparison_v2 - awaiting stats data")
        save_figure(fig, "boxplot_comparison_v2")
        plt.close(fig)
        return
    
    stats = pd.read_csv(stats_path)
    best = pd.read_csv(best_path)
    
    # Exact order: (DensityE, lr), (DistE, lr), (DensityE, svm), ...
    order = [
        ("DensityE", "lr"),
        ("DistE", "lr"),
        ("DensityE", "svm"),
        ("DistE", "svm"),
        ("DensityE", "knn"),
        ("DistE", "knn"),
        ("Single Model", "single_svm"),
    ]
    
    COLORS_BXP = {
        "DensityE": "#E69F00",     # amber
        "DistE": "#56B4E9",        # blue
        "Single Model": "#BBBBBB"  # grey
    }
    
    # Build bxp data
    bxp_data = []
    colors = []
    for method, learner in order:
        row = stats[(stats["method"] == method) & (stats["learner"] == learner)]
        if len(row) > 0:
            r = row.iloc[0]
            bxp_data.append({
                "med": r["median"],
                "q1": r["q1"],
                "q3": r["q3"],
                "whislo": r["whislo"],
                "whishi": r["whishi"],
                "mean": r["mean"],
                "fliers": [],
                "label": ""
            })
            colors.append(COLORS_BXP[method])
    
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    
    bp = ax.bxp(bxp_data, showmeans=True, patch_artist=True, widths=0.62,
                meanprops=dict(marker="x", markeredgecolor="crimson",
                               markersize=6, markeredgewidth=1.4),
                medianprops=dict(color="black", linewidth=1.2),
                boxprops=dict(linewidth=0.8),
                whiskerprops=dict(linewidth=0.8),
                capprops=dict(linewidth=0.8))
    
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.85)
    
    # Group labels: positions for LogReg, SVM, KNN, Single SVM
    positions = [1.5, 3.5, 5.5, 7]
    ax.set_xticks(positions)
    ax.set_xticklabels(["LogReg", "SVM", "KNN", "Single SVM"], fontsize=9)
    
    ax.set_ylabel("weighted $F_1$-score", fontsize=9)
    ax.set_ylim(0.88, 0.99)
    ax.grid(axis="y", alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Legend
    handles = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS_BXP["DensityE"], alpha=0.85, ec="black", lw=0.8),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS_BXP["DistE"], alpha=0.85, ec="black", lw=0.8),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS_BXP["Single Model"], alpha=0.85, ec="black", lw=0.8)
    ]
    ax.legend(handles, ["DensityE", "DistE", "single-SVM reference"],
              loc="lower left", frameon=False, fontsize=8, ncol=3,
              bbox_to_anchor=(0.0, -0.30))
    
    # Dispersion annotation (LogReg fold SDs)
    def get_sd(method, learner):
        method_norm = method.lower().replace("e", "").replace("density", "densitye")
        row = best[(best["ensemble_method"] == method_norm) & (best["base_learner"] == learner)]
        if len(row) > 0:
            return float(row.iloc[0]["std_score"])
        return np.nan
    
    sd_d = get_sd("DensityE", "lr")
    sd_x = get_sd("DistE", "lr")
    
    if not np.isnan(sd_d) and not np.isnan(sd_x) and sd_d > 0:
        ratio = sd_x / sd_d
        ax.annotate(
            f"LogReg fold SD:  DensityE ${sd_d:.3f}$   vs   DistE ${sd_x:.3f}$   ({ratio:.0f}$\\times$ tighter)",
            xy=(0.5, 0.975), xycoords="axes fraction", ha="center",
            fontsize=8.5, color="#333333"
        )
    
    fig.tight_layout()
    save_figure(fig, "boxplot_comparison_v2")
    plt.close(fig)

# ============================================================================
# FIGURE 4: DIAGNOSTICS (existing, no changes)
# ============================================================================

def figure_diagnostics():
    """3-panel diagnostics figure"""
    ens_path = os.path.join(RESULTS_DIR, "table_ensemble_comparison.csv")
    div_path = os.path.join(RESULTS_DIR, "table_diversity_cost.csv")
    
    if not os.path.exists(ens_path) or not os.path.exists(div_path):
        fig = placeholder_figure("fig2_diagnostics - awaiting data")
        save_figure(fig, "fig2_diagnostics")
        plt.close(fig)
        return
    
    ens = pd.read_csv(ens_path)
    div = pd.read_csv(div_path)
    
    fig, (axa, axb, axc) = plt.subplots(1, 3, figsize=(12, 3.4),
                                        gridspec_kw={"width_ratios": [1.2, 1.2, 1]})
    
    # Panel (a): aggregation comparison
    agg_methods = ["DensityE", "DistE", "MaxE", "AvgE"]
    agg_means = []
    for m in agg_methods:
        rows = ens[ens["method"] == m]
        if len(rows) > 0:
            agg_means.append(rows["mean_f_score"].astype(float).mean())
        else:
            agg_means.append(np.nan)
    
    x = np.arange(len(agg_methods))
    axa.bar(x, agg_means, color=[COLORS["orange"]] + [COLORS["sky"]]*3,
           edgecolor="black", linewidth=0.7, alpha=0.85)
    axa.set_xticks(x)
    axa.set_xticklabels(agg_methods, fontsize=8)
    axa.set_ylabel("Mean F-score", fontsize=9)
    axa.set_ylim(0.94, 0.975)
    axa.grid(axis="y", alpha=0.3, linewidth=0.5)
    axa.set_axisbelow(True)
    add_panel_letter(axa, "a")
    
    # Panel (b): overlap vs disagreement
    if "phi" in div.columns and "disagreement" in div.columns:
        axb.scatter(div["phi"], div["disagreement"], s=40, color=COLORS["orange"],
                   alpha=0.7, edgecolor="black", linewidth=0.5)
        axb.set_xlabel("Cluster overlap", fontsize=9)
        axb.set_ylabel("Disagreement metric", fontsize=9)
        axb.grid(alpha=0.3, linewidth=0.5)
        axb.set_axisbelow(True)
    add_panel_letter(axb, "b")
    
    # Panel (c): oracle ceiling
    if "oracle_ceiling" in div.columns:
        axc.plot(div["phi"], div["oracle_ceiling"], marker="o", color=COLORS["orange"],
                linewidth=2, markersize=4)
        axc.set_xlabel("Cluster overlap", fontsize=9)
        axc.set_ylabel("Oracle headroom", fontsize=9)
        axc.grid(alpha=0.3, linewidth=0.5)
        axc.set_axisbelow(True)
    add_panel_letter(axc, "c")
    
    fig.tight_layout()
    save_figure(fig, "fig2_diagnostics")
    plt.close(fig)

# ============================================================================
# FIGURE 5: SOTA COMPARISON (existing, no changes)
# ============================================================================

def figure_sota_comparison():
    """State-of-the-art comparison with per-fold p-values"""
    perfold_path = os.path.join(RESULTS_DIR, "figure_sota_perfold.csv")
    
    if not os.path.exists(perfold_path):
        fig = placeholder_figure("sota_comparison - awaiting per-fold data")
        save_figure(fig, "sota_comparison")
        plt.close(fig)
        return
    
    per = pd.read_csv(perfold_path)
    ours = "DDEL-GMM (ours)" if "DDEL-GMM (ours)" in per.columns else per.columns[0]
    
    baselines = [c for c in per.columns if c != ours]
    rows = []
    
    for m in [ours] + baselines:
        v = pd.to_numeric(per[m], errors='coerce').to_numpy()
        v = v[~np.isnan(v)]
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

# ============================================================================
# FIGURE 6: GMM VS KMEANS SYNTHETIC (CORRECTED - 6 PANELS)
# ============================================================================

def figure_gmm_vs_kmeans_synthetic():
    """
    Figure 6: 6-panel synthetic clustering ablation.
    
    Panels:
      (a) ARI vs overlap at d<=10 (spherical vs eccentric)
      (b) ARI gap vs eccentricity at d=2, 10, 50
      (c) ARI gap across d and eccentricity (the reversal)
      (d) ARI by covariance parameterization (d=2,10,50,157)
      (e) Free parameters vs dimensionality
      (f) Paired per-fold macro-F1 on UCI HAR
    """
    sweep_path = os.path.join(RESULTS_DIR, "figure_gmm_vs_kmeans_sweep.csv")
    covtype_path = os.path.join(RESULTS_DIR, "figure_gmm_vs_kmeans_covtype.csv")
    perfold_path = os.path.join(RESULTS_DIR, "figure_gmm_vs_kmeans_perfold.csv")
    
    if not os.path.exists(sweep_path):
        fig = placeholder_figure("gmm_vs_kmeans_synthetic - awaiting sweep data")
        save_figure(fig, "gmm_vs_kmeans_synthetic")
        plt.close(fig)
        return
    
    sweep = pd.read_csv(sweep_path)
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 6.5))
    
    # -------- Panel (a): ARI vs overlap at d<=10 --------
    ax = axes[0, 0]
    for d in [2, 10]:
        for eccval, ls in [(1, ':'), (30, '-')]:
            data = sweep[(sweep['d'] == d) & (sweep['eccentricity'] == eccval)]
            for alg in ['GMM', 'KMeans']:
                subset = data[data['algorithm'] == alg]
                if len(subset) > 0:
                    ov = subset.groupby('overlap')['ARI'].mean()
                    label = f"{alg} d={d} ecc={eccval}"
                    ax.plot(ov.index, ov.values, marker="o", linestyle=ls, label=label, 
                           markersize=3, linewidth=1.2)
    ax.set_xlabel("Cluster overlap")
    ax.set_ylabel("ARI")
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.legend(fontsize=7, loc="best", frameon=False)
    add_panel_letter(ax, "a")
    
    # -------- Panel (b): ARI gap vs eccentricity at d=2,10,50 --------
    ax = axes[0, 1]
    for d in [2, 10, 50]:
        gaps = []
        eccs = sorted(sweep[sweep['d'] == d]['eccentricity'].unique())
        for ecc in eccs:
            subset = sweep[(sweep['d'] == d) & (sweep['eccentricity'] == ecc)]
            gmm_ari = subset[subset['algorithm'] == 'GMM']['ARI'].mean()
            km_ari = subset[subset['algorithm'] == 'KMeans']['ARI'].mean()
            gaps.append(gmm_ari - km_ari)
        ax.plot(eccs, gaps, marker="o", label=f"d={d}", markersize=4, linewidth=1.2)
    ax.set_xlabel("Eccentricity")
    ax.set_ylabel("ARI gap (GMM - KMeans)")
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.legend(fontsize=7, frameon=False)
    add_panel_letter(ax, "b")
    
    # -------- Panel (c): ARI gap across d and eccentricity --------
    ax = axes[0, 2]
    gap_data = []
    for d in sweep['d'].unique():
        for ecc in sweep['eccentricity'].unique():
            subset = sweep[(sweep['d'] == d) & (sweep['eccentricity'] == ecc)]
            gmm_ari = subset[subset['algorithm'] == 'GMM']['ARI'].mean()
            km_ari = subset[subset['algorithm'] == 'KMeans']['ARI'].mean()
            gap = gmm_ari - km_ari
            gap_data.append((d, ecc, gap))
    
    gap_df = pd.DataFrame(gap_data, columns=['d', 'ecc', 'gap'])
    for d in sorted(gap_df['d'].unique()):
        data = gap_df[gap_df['d'] == d].sort_values('ecc')
        ax.plot(data['ecc'], data['gap'], marker="s", label=f"d={d}", 
               markersize=4, linewidth=1.2)
    ax.set_xlabel("Eccentricity")
    ax.set_ylabel("ARI gap (GMM - KMeans)")
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.legend(fontsize=7, frameon=False)
    add_panel_letter(ax, "c")
    
    # -------- Panel (d): ARI by covariance parameterization --------
    ax = axes[1, 0]
    if os.path.exists(covtype_path):
        covtype = pd.read_csv(covtype_path)
        for model in ['GMM-spherical', 'GMM-diag', 'GMM-tied', 'GMM-full', 'KMeans']:
            data = covtype[covtype['model'] == model].sort_values('d')
            if len(data) > 0:
                ax.plot(data['d'], data['ARI'].astype(float), marker="o", label=model.replace("GMM-", ""),
                       markersize=4, linewidth=1.2)
    ax.set_xlabel("Dimensionality (d)")
    ax.set_ylabel("ARI")
    ax.set_ylim(0.7, 1.0)
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.legend(fontsize=7, frameon=False)
    add_panel_letter(ax, "d")
    
    # -------- Panel (e): Free parameters vs dimensionality --------
    ax = axes[1, 1]
    if os.path.exists(covtype_path):
        covtype = pd.read_csv(covtype_path)
        for model in ['GMM-spherical', 'GMM-diag', 'GMM-tied', 'GMM-full', 'KMeans']:
            data = covtype[covtype['model'] == model].drop_duplicates('d').sort_values('d')
            if len(data) > 0:
                ax.plot(data['d'], data['n_params'].astype(float), marker="o",
                       label=model.replace("GMM-", ""), markersize=4, linewidth=1.2)
    # Add sample count line
    n_samples = 1000
    ax.axhline(y=n_samples, color='red', linestyle='--', linewidth=1.2, label=f"n_samples={n_samples}")
    ax.set_xlabel("Dimensionality (d)")
    ax.set_ylabel("Free parameters")
    ax.set_yscale('log')
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.legend(fontsize=7, frameon=False)
    add_panel_letter(ax, "e")
    
    # -------- Panel (f): Per-fold macro-F1 on UCI HAR --------
    ax = axes[1, 2]
    if os.path.exists(perfold_path):
        perfold = pd.read_csv(perfold_path)
        x = np.arange(len(perfold))
        width = 0.35
        ax.bar(x - width/2, perfold["DDEL-GMM (ours)"], width, label="GMM",
              color=COLORS["orange"], edgecolor="black", linewidth=0.7, alpha=0.85)
        ax.bar(x + width/2, perfold["DDEL-KMeans"], width, label="KMeans",
              color=COLORS["sky"], edgecolor="black", linewidth=0.7, alpha=0.85)
        ax.set_xlabel("Fold")
        ax.set_ylabel("Macro F-score")
        ax.set_xticks(x)
        ax.set_xticklabels(range(len(perfold)), fontsize=8)
        ax.set_ylim(0.95, 0.98)
        ax.grid(axis="y", alpha=0.3, linewidth=0.5)
        ax.set_axisbelow(True)
        ax.legend(fontsize=7, frameon=False)
    add_panel_letter(ax, "f")
    
    fig.suptitle("GMM vs K-means clustering comparison (synthetic & HAR)", fontsize=11, y=1.00)
    fig.tight_layout()
    save_figure(fig, "gmm_vs_kmeans_synthetic")
    plt.close(fig)

# ============================================================================
# FIGURE 7: NOCLUSTERING COMPARISON (existing, no changes)
# ============================================================================

def figure_noclustering_comparison():
    """Noclustering baseline comparison with Nemenyi CD"""
    perfold_path = os.path.join(RESULTS_DIR, "figure_noclustering_perfold.csv")
    
    if not os.path.exists(perfold_path):
        fig = placeholder_figure("noclustering_comparison - awaiting per-fold data")
        save_figure(fig, "noclustering_comparison")
        plt.close(fig)
        return
    
    pf = pd.read_csv(perfold_path)
    ours = "DDEL-GMM (ours)"
    order = pf.mean().sort_values(ascending=False).index.tolist()
    n, k = len(pf), pf.shape[1]
    
    R = np.vstack([rankdata(-pf.iloc[i].to_numpy()) for i in range(n)])
    mr = pd.Series(R.mean(0), index=pf.columns)
    CD = studentized_range.ppf(0.95, k, np.inf) / np.sqrt(2) * np.sqrt(k * (k + 1) / (6.0 * n))
    
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.2, 4.3),
                                   gridspec_kw={"width_ratios": [1.35, 1]})
    
    cols = [COLORS["orange"] if c == ours else COLORS["sky"] for c in order]
    bp = axL.boxplot([pf[c] for c in order], patch_artist=True, widths=0.62,
                     medianprops=dict(color="black", lw=1.4),
                     flierprops=dict(marker="o", ms=3, mfc="0.4", mec="none"))
    for patch, c in zip(bp["boxes"], cols):
        patch.set_facecolor(c)
        patch.set_alpha(0.85)
        patch.set_edgecolor("black")
        patch.set_linewidth(0.8)
    
    for i, c in enumerate(order, 1):
        axL.plot(i, pf[c].mean(), marker="D", ms=5, color="white",
                 mec="black", mew=0.9, zorder=5)
    
    axL.set_xticks(range(1, len(order) + 1))
    axL.set_xticklabels(order, rotation=15, ha="right", fontsize=8)
    axL.set_ylabel("Macro F-score", fontsize=9)
    axL.grid(axis="y", alpha=0.3, lw=0.6)
    axL.set_axisbelow(True)
    add_panel_letter(axL, "a")
    
    mro = mr[order]
    ypos = np.arange(len(order))[::-1]
    axR.barh(ypos, mro.values, color=cols, alpha=0.85, edgecolor="black", lw=0.8, height=0.6)
    
    axR.errorbar(mro[ours], ypos[order.index(ours)], xerr=CD / 2, color="black",
                 capsize=4, lw=1.3, zorder=6)
    axR.axvline(mro[ours] + CD, ls="--", lw=1.1, color=COLORS["orange"])
    axR.text(mro[ours] + CD, len(order) - 0.35, f"  CD={CD:.2f}", color=COLORS["orange"],
             fontsize=8, va="top")
    
    for yv, c in zip(ypos, order):
        axR.text(mro[c] + 0.09, yv, f"{mro[c]:.2f}", va="center", fontsize=7.5)
    
    axR.set_yticks(ypos)
    axR.set_yticklabels(order, fontsize=8)
    axR.set_xlabel("Mean Friedman rank  (1 = best)", fontsize=9)
    axR.set_xlim(0, k + 0.6)
    axR.grid(axis="x", alpha=0.3, lw=0.6)
    axR.set_axisbelow(True)
    add_panel_letter(axR, "b")
    
    fig.suptitle("DDEL-GMM vs non-clustering baselines", fontsize=10, y=0.98)
    fig.tight_layout()
    save_figure(fig, "noclustering_comparison")
    plt.close(fig)

# ============================================================================
# PLACEHOLDER STUBS FOR REVIEWER-REQUESTED FIGURES
# ============================================================================

def figure_concept_drift():
    """Placeholder for concept drift figure (awaiting data)"""
    fig = placeholder_figure("concept_drift - awaiting drift simulation data", 160, 120)
    save_figure(fig, "concept_drift")
    plt.close(fig)

def figure_delak_fhdes():
    """Placeholder for DELAK vs FH-DES comparison"""
    fig = placeholder_figure("delak_fhdes - awaiting method comparison", 160, 120)
    save_figure(fig, "delak_fhdes")
    plt.close(fig)

def figure_nonspherical():
    """Placeholder for non-spherical cluster comparison"""
    fig = placeholder_figure("nonspherical - awaiting cluster geometry data", 160, 120)
    save_figure(fig, "nonspherical")
    plt.close(fig)

def figure_case_study():
    """Placeholder for medical case study"""
    fig = placeholder_figure("case_study - awaiting case study data", 160, 120)
    save_figure(fig, "case_study")
    plt.close(fig)

# ============================================================================
# MAIN
# ============================================================================

def regenerate_all_figures():
    """Regenerate all figures"""
    print("\n" + "=" * 70)
    print("DDEL-GMM FIGURE RENDERER (FIXED VERSION)")
    print("=" * 70)
    print("\nGenerating main figures:")
    
    figure_fscore_vs_phi()
    figure_fscore_vs_clusters()
    figure_boxplot_comparison_v2()
    figure_diagnostics()
    figure_sota_comparison()
    figure_gmm_vs_kmeans_synthetic()
    figure_noclustering_comparison()
    
    print("\nGenerating placeholder stubs for reviewer-requested figures:")
    figure_concept_drift()
    figure_delak_fhdes()
    figure_nonspherical()
    figure_case_study()
    
    print("\n" + "=" * 70)
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    regenerate_all_figures()
