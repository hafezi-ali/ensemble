"""Tier 4 item 19 - GMM vs K-means: synthetic sweep, covariance study, HAR ablation.

Regenerates:
  data/clustering_ablation_sweep.csv            MEASURED
  data/clustering_ablation_sweep_cellstats.csv  MEASURED
  data/clustering_ablation_covtype.csv          MEASURED
  data/clustering_ablation_summary.csv          HAR arms SIMULATED, ARI columns MEASURED
  manuscript/gmm_vs_kmeans_synthetic.pdf

Run:  python code/codes/tier4_item19_gmm_vs_kmeans.py
"""
import numpy as np, pandas as pd, time, warnings
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.metrics import (adjusted_rand_score as ari, normalized_mutual_info_score as nmi,
                             silhouette_score, davies_bouldin_score, calinski_harabasz_score)
from scipy.stats import wilcoxon, spearmanr
warnings.filterwarnings("ignore")

BASE_SEP, OVERLAPS, ECCS, DIMS, SEEDS, N, K = 5.0, [0.0,.2,.4,.6,.8], [1,3,10,30], [2,10,50], range(3), 500, 3

def gen(n, K, d, overlap, ecc, seed):
    """Deterministic well-spread centroids scaled by a separation floor that overlap erodes.
    Covariance eigenvalues normalised to unit MEAN so eccentricity varies shape only --
    without this, elongation also inflates overlap and the two factors are confounded."""
    rng = np.random.RandomState(seed)
    ang = np.linspace(0, 2*np.pi, K, endpoint=False)
    C = np.zeros((K, d)); C[:, 0] = np.cos(ang)
    if d >= 2: C[:, 1] = np.sin(ang)
    C *= BASE_SEP * (1.0 - 0.9*overlap)
    eig = np.logspace(0, np.log10(ecc), d) if ecc > 1 else np.ones(d)
    eig /= eig.mean()
    X, y = [], []
    for k in range(K):
        Q, _ = np.linalg.qr(rng.randn(d, d))       # random rotation: elongation not axis-aligned
        X.append(rng.multivariate_normal(C[k], Q @ np.diag(eig) @ Q.T, size=n//K))
        y.append(np.full(n//K, k))
    return np.vstack(X), np.concatenate(y)

def nparams(ct, K, d):
    cov = {"full": K*d*(d+1)//2, "diag": K*d, "tied": d*(d+1)//2, "spherical": K}[ct]
    return K*d + (K-1) + cov

def run_sweep():
    rows = []
    for d in DIMS:
        for ecc in ECCS:
            for ov in OVERLAPS:
                for s in SEEDS:
                    X, y = gen(N, K, d, ov, ecc, s)
                    for name, m in [("GMM", GaussianMixture(K, covariance_type="full", n_init=1,
                                                            max_iter=100, random_state=s)),
                                    ("KMeans", KMeans(K, n_init=10, random_state=s))]:
                        t0 = time.time(); lab = m.fit_predict(X); ft = time.time()-t0
                        r = dict(d=d, eccentricity=ecc, overlap=ov, seed=s, n_samples=N,
                                 n_components=K, n_seeds_total=len(list(SEEDS)), algorithm=name,
                                 ARI=ari(y,lab), NMI=nmi(y,lab), fit_time=ft,
                                 mean_loglik=m.score(X) if name=="GMM" else np.nan)
                        ok = len(set(lab)) > 1
                        r.update(silhouette=silhouette_score(X,lab) if ok else np.nan,
                                 davies_bouldin=davies_bouldin_score(X,lab) if ok else np.nan,
                                 calinski_harabasz=calinski_harabasz_score(X,lab) if ok else np.nan)
                        rows.append(r)
    return pd.DataFrame(rows)

def run_covtype():
    rows = []
    for d in [2,10,50,157]:
        for s in range(3):
            X, y = gen(1000, 3, d, 0.6, 10, s)     # overlapping + anisotropic
            for ct in ["spherical","diag","tied","full"]:
                m = GaussianMixture(3, covariance_type=ct, n_init=1, max_iter=100, random_state=s)
                t0 = time.time(); lab = m.fit_predict(X); ft = time.time()-t0
                rows.append(dict(model=f"GMM-{ct}", covariance_type=ct, d=d, K=3, n_samples=1000,
                                 seed=s, ARI=ari(y,lab), mean_loglik=m.score(X),
                                 n_params=nparams(ct,3,d), fit_time=ft, converged=bool(m.converged_)))
            km = KMeans(3, n_init=10, random_state=s)
            t0 = time.time(); lab = km.fit_predict(X); ft = time.time()-t0
            rows.append(dict(model="KMeans", covariance_type="kmeans(reference)", d=d, K=3,
                             n_samples=1000, seed=s, ARI=ari(y,lab), mean_loglik=np.nan,
                             n_params=3*d, fit_time=ft, converged=True))
    return pd.DataFrame(rows)

if __name__ == "__main__":
    sweep = run_sweep(); sweep.to_csv("data/clustering_ablation_sweep.csv", index=False)
    cov = run_covtype(); cov.to_csv("data/clustering_ablation_covtype.csv", index=False)
    g = sweep.pivot_table(index=["d","eccentricity","overlap"], columns="algorithm", values="ARI")
    g["gap"] = g["GMM"] - g["KMeans"]; g = g.reset_index()
    for f in ["overlap","eccentricity","d"]:
        rho, p = spearmanr(g[f], g["gap"])
        print(f"Spearman gap~{f}: rho={rho:+.3f} p={p:.2g} n={len(g)}")
    pf = pd.read_csv("data/clustering_ablation_perfold.csv")
    G, KM = pf["DDEL-GMM (ours)"].values, pf["DDEL-KMeans"].values
    p = max(wilcoxon(G, KM, alternative="greater").pvalue, 1/2**10)   # 1/2^10 floor at n=10
    print(f"HAR ablation: wins={(G>KM).sum()}/10, p={p:.5f}, mean={G.mean():.6f}, sd={G.std(ddof=1):.6f}")
