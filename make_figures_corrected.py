#!/usr/bin/env python3
"""
DDEL-GMM Figure Renderer - CORRECTED VERSION 2
==============================================

Fixes for four fidelity defects:
  1. Panel (c) x-axis: eccentricity → dimensionality (shows the reversal)
  2. Panel (a) legend: 8 entries → 4 (linestyle + color encoding)
  3. Boxplot layout: learner pairs → aggregation scheme groups
  4. Boxplot fliers: prefer per-fold data (figure_boxplot_perfold.csv) when filled,
     fall back to 5-number summaries when empty. Fliers CANNOT be drawn from summaries alone.

Usage:
    python make_figures_corrected.py

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
# FIGURE 1: F-SCORE VS PHI
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
# FIGURE 2: F-SCORE VS K
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
# FIGURE 3: BOXPLOT COMPARISON (CORRECTED - AGGREGATION SCHEME LAYOUT)
# ============================================================================

def figure_boxplot_comparison_v2():
    """
    Figure 3: Per-fold F-score distribution by aggregation scheme and learner.
    
    CORRECTED LAYOUT:
      - X-axis groups by AGGREGATION SCHEME: DensityE, DistE, Single Model
      - Within each scheme, colour-code by base learner (LR/SVM/KNN or Single SVM)
      - Prefer per-fold data from figure_boxplot_perfold.csv (with true fliers)
      - Fall back to 5-number summaries when per-fold data absent
    
    Data sources:
      - figure_boxplot_perfold.csv (per-fold F-scores; EMPTY_SLOT)
      - figure_boxplot_stats.csv (precomputed 5-number summaries)
      - table_best_ensemble_results.csv (std_score for SD annotation)
    """
    stats_path = os.path.join(RESULTS_DIR, "figure_boxplot_stats.csv")
    perfold_path = os.path.join(RESULTS_DIR, "figure_boxplot_perfold.csv")
    best_path = os.path.join(RESULTS_DIR, "table_best_ensemble_results.csv")
    
    if not os.path.exists(stats_path):
        fig = placeholder_figure("boxplot_comparison_v2 - awaiting stats data")
        save_figure(fig, "boxplot_comparison_v2")
        plt.close(fig)
        return
    
    stats = pd.read_csv(stats_path)
    best = pd.read_csv(best_path)
    
    # Try to load per-fold data; if not available, use 5-number summaries
    has_perfold = os.path.exists(perfold_path) and os.path.getsize(perfold_path) > 100
    perfold = None
    if has_perfold:
        perfold = pd.read_csv(perfold_path)
        # Check if truly filled (has numeric fscore values)
        if 'fscore' not in perfold.columns or perfold['fscore'].isna().all():
            has_perfold = False
            perfold = None
    
    # Arrange boxes: DensityE(lr,svm,knn), DistE(lr,svm,knn), Single Model(svm)
    # Group 1 (x=1-3): DensityE
    # Group 2 (x=4-6): DistE
    # Group 3 (x=7): Single Model
    
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    
    schemes = [("DensityE", ["lr", "svm", "knn"]),
               ("DistE", ["lr", "svm", "knn"]),
               ("Single Model", ["single_svm"])]
    
    COLORS_LEARNER = {
        "lr": "#FF6B6B",           # red
        "svm": "#4ECDC4",          # teal
        "knn": "#FFD93D",          # gold
        "single_svm": "#888888"    # dark grey
    }
    
    SCHEME_COLORS = {
        "DensityE": "#E69F00",     # amber (background/accent)
        "DistE": "#56B4E9",        # blue
        "Single Model": "#BBBBBB"  # grey
    }
    
    bxp_data = []
    colors = []
    positions = []
    pos_counter = 1
    
    for scheme, learners in schemes:
        for learner in learners:
            if has_perfold and perfold is not None:
                # Use per-fold data
                rows = perfold[(perfold['method'] == scheme) & (perfold['learner'] == learner)]
                if len(rows) > 0:
                    scores = rows['fscore'].astype(float).values
                    bxp_data.append(scores)
                    colors.append(COLORS_LEARNER[learner])
                    positions.append(pos_counter)
            else:
                # Use 5-number summaries
                row = stats[(stats["method"] == scheme) & (stats["learner"] == learner)]
                if len(row) > 0:
                    r = row.iloc[0]
                    bxp_data.append([r["whislo"], r["q1"], r["median"], r["q3"], r["whishi"]])
                    colors.append(COLORS_LEARNER[learner])
                    positions.append(pos_counter)
            pos_counter += 1
    
    # Draw boxplot
    if has_perfold and perfold is not None:
        # Use ax.boxplot for per-fold data (with automatic flier circles)
        bp = ax.boxplot(bxp_data, positions=positions, widths=0.62, patch_artist=True,
                       showmeans=True, meanline=False,
                       meanprops=dict(marker="+", markeredgecolor="red", markersize=10, 
                                     markeredgewidth=2),
                       medianprops=dict(color="black", linewidth=1.2),
                       boxprops=dict(linewidth=0.8),
                       whiskerprops=dict(linewidth=0.8),
                       capprops=dict(linewidth=0.8),
                       flierprops=dict(marker="o", markerfacecolor="white", 
                                      markeredgecolor="black", markersize=4, alpha=0.7))
    else:
        # Use ax.bxp for 5-number summaries (no fliers possible)
        bxp_stats = []
        for i, (scheme, learners) in enumerate(schemes):
            for learner in learners:
                row = stats[(stats["method"] == scheme) & (stats["learner"] == learner)]
                if len(row) > 0:
                    r = row.iloc[0]
                    bxp_stats.append({
                        "med": r["median"],
                        "q1": r["q1"],
                        "q3": r["q3"],
                        "whislo": r["whislo"],
                        "whishi": r["whishi"],
                        "mean": r["mean"],
                        "fliers": [],
                        "label": ""
                    })
        
        bp = ax.bxp(bxp_stats, positions=positions, showmeans=True, patch_artist=True, widths=0.62,
                   meanprops=dict(marker="+", markeredgecolor="red", markersize=10,
                                 markeredgewidth=2),
                   medianprops=dict(color="black", linewidth=1.2),
                   boxprops=dict(linewidth=0.8),
                   whiskerprops=dict(linewidth=0.8),
                   capprops=dict(linewidth=0.8))
    
    # Apply colors
    if isinstance(bp.get("boxes", []), list):
        for patch, c in zip(bp["boxes"], colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.75)
            patch.set_edgecolor("black")
            patch.set_linewidth(0.8)
    
    # Group x-axis: DensityE at 2, DistE at 5, Single Model at 7
    ax.set_xticks([2, 5, 7])
    ax.set_xticklabels(["DensityE", "DistE", "Single Model"], fontsize=9)
    
    ax.set_ylabel("Weighted $F_1$-score", fontsize=9)
    ax.set_ylim(0.88, 0.99)
    ax.grid(axis="y", alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Legend: learner colors
    handles = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS_LEARNER["lr"], alpha=0.75, ec="black", lw=0.8),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS_LEARNER["svm"], alpha=0.75, ec="black", lw=0.8),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS_LEARNER["knn"], alpha=0.75, ec="black", lw=0.8),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS_LEARNER["single_svm"], alpha=0.75, ec="black", lw=0.8)
    ]
    ax.legend(handles, ["LogReg", "SVM", "KNN", "Single SVM"],
              loc="lower left", frameon=False, fontsize=8, ncol=4,
              bbox_to_anchor=(0.0, -0.28))
    
    # Configuration annotation (top-right)
    ax.annotate("$n_c = 6$, $\\varphi = 0.5$ (selected configuration)",
                xy=(0.98, 0.97), xycoords="axes fraction", ha="right", va="top",
                fontsize=8, style="italic", color="#333333")
    
    # SD annotation (bottom-left inside axes)
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
        ax.text(0.02, 0.05, f"LogReg fold SD:  DensityE {sd_d:.3f}   vs   DistE {sd_x:.3f}   ({ratio:.0f}× tighter)",
                transform=ax.transAxes, fontsize=7.5, color="#333333",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor="none"))
    
    # Add fliers note if per-fold data missing
    if not has_perfold:
        ax.text(0.5, -0.5, "⚠ No per-fold data: flier circles unavailable (5-number summaries used)",
                transform=ax.transAxes, fontsize=7, color="#CC6666", ha="center",
                style="italic")
    
    fig.tight_layout()
    save_figure(fig, "boxplot_comparison_v2")
    plt.close(fig)

# ============================================================================
# FIGURE 4: DIAGNOSTICS
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
    
    agg_methods = ["DensityE", "DistE", "MaxE", "AvgE"]
    agg_means = []
    for m in agg_methods:
        rows = ens[ens["ensemble_method"] == m]
        if len(rows) > 0:
            agg_means.append(rows["mean_score"].astype(float).mean())
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
    
    if "phi" in div.columns and "disagreement" in div.columns:
        axb.scatter(div["phi"], div["disagreement"], s=40, color=COLORS["orange"],
                   alpha=0.7, edgecolor="black", linewidth=0.5)
        axb.set_xlabel("Cluster overlap", fontsize=9)
        axb.set_ylabel("Disagreement metric", fontsize=9)
        axb.grid(alpha=0.3, linewidth=0.5)
        axb.set_axisbelow(True)
    
    if "oracle_ceiling" in div.columns:
        axc.plot(div["phi"], div["oracle_ceiling"], marker="o", color=COLORS["orange"],
                linewidth=2, markersize=4)
        axc.set_xlabel("Cluster overlap", fontsize=9)
        axc.set_ylabel("Oracle headroom", fontsize=9)
        axc.grid(alpha=0.3, linewidth=0.5)
        axc.set_axisbelow(True)
    
    fig.tight_layout()
    save_figure(fig, "fig2_diagnostics")
    plt.close(fig)

# ============================================================================
# FIGURE 5: SOTA COMPARISON
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
    
    CORRECTED PANELS:
      (a) ARI vs overlap at d≤10 (linestyle: spherical dotted, eccentric solid)
      (b) ARI gap vs ECCENTRICITY at d=2, 10, 50
      (c) ARI gap vs DIMENSIONALITY at ecc=1, 3, 10, 30 [CORRECTED X-AXIS]
      (d) ARI by covariance parameterization
      (e) Free parameters vs dimensionality
      (f) Per-fold macro-F1 on UCI HAR
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
                    c = COLORS["orange"] if alg == 'GMM' else COLORS["sky"]
                    label = f"{alg} d={d}"
                    ax.plot(ov.index, ov.values, marker="o", linestyle=ls, label=label,
                           color=c, markersize=3, linewidth=1.2)
    
    ax.set_xlabel("Cluster overlap")
    ax.set_ylabel("ARI")
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.legend(fontsize=6.5, loc="best", frameon=False, ncol=2)
    add_panel_letter(ax, "a")
    
    # -------- Panel (b): ARI gap vs ECCENTRICITY --------
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
    
    # -------- Panel (c): ARI gap vs DIMENSIONALITY [CORRECTED] --------
    ax = axes[0, 2]
    for ecc in [1, 3, 10, 30]:
        gaps = []
        ds = sorted(sweep[sweep['eccentricity'] == ecc]['d'].unique())
        for d in ds:
            subset = sweep[(sweep['d'] == d) & (sweep['eccentricity'] == ecc)]
            gmm_ari = subset[subset['algorithm'] == 'GMM']['ARI'].mean()
            km_ari = subset[subset['algorithm'] == 'KMeans']['ARI'].mean()
            gap = gmm_ari - km_ari
            gaps.append(gap)
        ax.plot(ds, gaps, marker="s", label=f"ecc={ecc}", markersize=4, linewidth=1.2)
    
    ax.set_xlabel("Dimensionality (d)")
    ax.set_ylabel("ARI gap (GMM - KMeans)")
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.legend(fontsize=7, frameon=False)
    ax.text(0.5, 0.98, "← Reversal at high d", transform=ax.transAxes,
           fontsize=7, ha="center", va="top", color="#B22222", style="italic")
    add_panel_letter(ax, "c")
    
    # -------- Panel (d): ARI by covariance parameterization --------
    ax = axes[1, 0]
    if os.path.exists(covtype_path):
        covtype = pd.read_csv(covtype_path)
        for model in ['GMM-spherical', 'GMM-diag', 'GMM-tied', 'GMM-full', 'KMeans']:
            data = covtype[covtype['model'] == model].sort_values('d')
            if len(data) > 0:
                ax.plot(data['d'], data['ARI'].astype(float), marker="o", 
                       label=model.replace("GMM-", ""),
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
    ax.axhline(y=1000, color='red', linestyle='--', linewidth=1.2, label="$n_{samples}$=1000")
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
# FIGURE 7: NOCLUSTERING COMPARISON
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
    
    fig.suptitle("DDEL-GMM vs non-clustering baselines", fontsize=10, y=0.98)
    fig.tight_layout()
    save_figure(fig, "noclustering_comparison")
    plt.close(fig)

# ============================================================================
# PLACEHOLDER STUBS
# ============================================================================

def figure_concept_drift():
    """Placeholder for concept drift figure"""
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
    print("DDEL-GMM FIGURE RENDERER (CORRECTED VERSION 2)")
    print("=" * 70)
    print("\nGenerating main figures:")
    
    figure_fscore_vs_phi()
    figure_fscore_vs_clusters()
    figure_boxplot_comparison_v2()
    figure_diagnostics()
    figure_sota_comparison()
    figure_gmm_vs_kmeans_synthetic()
    figure_noclustering_comparison()
    
    print("\nGenerating placeholder stubs:")
    figure_concept_drift()
    figure_delak_fhdes()
    figure_nonspherical()
    figure_case_study()
    
    print("\n" + "=" * 70)
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    regenerate_all_figures()
