"""Wilcoxon / Friedman / Nemenyi on the MEASURED per-fold F-score vectors.

Reads data/noclustering_perfold.csv (10 folds x methods) and writes
data/noclustering_stats.csv. No value is hardcoded: every p and every
critical difference is computed from the measured vectors.

Attainable p floor: a two-sided exact Wilcoxon on n=10 paired folds cannot
go below 2^-10 = 0.00098, so no p < 0.001 is ever reported.
"""
import numpy as np, pandas as pd
from scipy.stats import wilcoxon, friedmanchisquare, rankdata, studentized_range

ROOT = "/home/ali/Documents/ensemble/"
pf = pd.read_csv(ROOT + "data/noclustering_perfold.csv")
ours = "DDEL-GMM (ours)"
others = [c for c in pf.columns if c != ours]
n, k = len(pf), pf.shape[1]

# ---- Friedman across all methods -------------------------------------------
chi2, p_fried = friedmanchisquare(*[pf[c].to_numpy() for c in pf.columns])

# ---- mean ranks (1 = best) --------------------------------------------------
R = np.vstack([rankdata(-pf.iloc[i].to_numpy()) for i in range(n)])
mean_rank = dict(zip(pf.columns, R.mean(0)))

# ---- Nemenyi critical difference at alpha=0.05 ------------------------------
q_alpha = studentized_range.ppf(0.95, k, np.inf) / np.sqrt(2)
CD = q_alpha * np.sqrt(k * (k + 1) / (6.0 * n))

# ---- pairwise Wilcoxon, ours vs each baseline -------------------------------
rec = []
for c in others:
    d = pf[ours].to_numpy() - pf[c].to_numpy()
    if np.allclose(d, 0):
        W, p = np.nan, 1.0
    else:
        W, p = wilcoxon(pf[ours], pf[c], zero_method="wilcox", alternative="two-sided")
    rank_gap = mean_rank[c] - mean_rank[ours]
    rec.append({
        "Baseline": c,
        "F_ours": pf[ours].mean(), "F_base": pf[c].mean(),
        "Delta_F": pf[ours].mean() - pf[c].mean(),
        "Wilcoxon_W": W, "Wilcoxon_p": p,
        "Signif_0.05": "yes" if p < 0.05 else "no",
        "MeanRank_ours": mean_rank[ours], "MeanRank_base": mean_rank[c],
        "RankGap": rank_gap,
        "Nemenyi_CD": CD,
        "Nemenyi_separates": "yes" if abs(rank_gap) > CD else "no",
        "folds_ours_win": int((pf[ours].to_numpy() > pf[c].to_numpy()).sum()),
        "n_folds": n,
    })
st = pd.DataFrame(rec).sort_values("Delta_F", ascending=False)
st.insert(0, "Friedman_chi2", chi2)
st.insert(1, "Friedman_p", p_fried)
st.to_csv(ROOT + "data/noclustering_stats.csv", index=False)

print(f"n={n} folds, k={k} methods")
print(f"Friedman chi2={chi2:.3f} p={p_fried:.2e}")
print(f"Nemenyi CD (alpha=0.05, k={k}, n={n}) = {CD:.3f}")
print(f"exact Wilcoxon p floor at n={n}: {2.0**-n:.5f}\n")
print(st[["Baseline","F_base","Delta_F","Wilcoxon_p","Signif_0.05",
          "MeanRank_base","RankGap","Nemenyi_separates","folds_ours_win"]]
      .to_string(index=False))
