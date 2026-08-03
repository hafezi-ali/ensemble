"""Why does DDEL-GMM tie Single LR? Measure ensemble diversity vs phi and K.

Diagnostics per config:
  overlap    - mean pairwise Jaccard of the K training subsets (1.0 = identical data)
  disagree   - mean pairwise fraction of test points where two base learners differ
  H(W)       - mean entropy of GMM posterior weights, normalised (0 = hard 1-of-K, 1 = uniform)
  oracle     - accuracy if an omniscient combiner picked the best base learner per test point.
               This is the CEILING for ANY weighting scheme. If oracle ~= single LR,
               no aggregation rule can beat a single model, and the mechanism is dead.
  ddel       - actual DDEL-GMM macro F
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))
from ddel_paths import ROOT, DATA, FIGS, DATASET, NPC, SEED, K_PUB, PHI_PUB, require_dataset
require_dataset()

import numpy as np, pandas as pd, itertools, time
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score

NPC, SEED = 157, 42
d = pd.read_csv(DATASET)
drop=[c for c in ["Activity","ActivityName","subject"] if c in d.columns]
X = d.drop(columns=drop).select_dtypes(include=[np.number]).to_numpy(np.float64)
y = d["Activity"].to_numpy(); classes = np.unique(y)

skf = StratifiedKFold(10, shuffle=True, random_state=SEED)
tr, te = next(iter(skf.split(X, y)))          # fold 1 only: this is a diagnostic
sc = StandardScaler().fit(X[tr])
pca = PCA(NPC, random_state=SEED).fit(sc.transform(X[tr]))
Xtr, Xte = pca.transform(sc.transform(X[tr])), pca.transform(sc.transform(X[te]))
ytr, yte = y[tr], y[te]
print(f"fold1 train={Xtr.shape} test={Xte.shape}", flush=True)

single = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
sF = f1_score(yte, single.predict(Xte), average="macro")
print(f"Single LR macro-F = {sF:.4f}\n", flush=True)

rows=[]
for K in (5, 8):
    gm = GaussianMixture(K, covariance_type="full", random_state=SEED,
                         reg_covar=1e-4, max_iter=200).fit(Xtr)
    lp_all = gm._estimate_weighted_log_prob(Xtr)
    W = gm.predict_proba(Xte)
    Hn = float(np.mean(-(W*np.log(W+1e-12)).sum(1))/np.log(K))
    for PHI in (0.2, 0.4, 0.6, 0.9):
        t0=time.time(); idxs=[]; preds=[]; P=np.zeros((len(Xte), len(classes)))
        for k in range(K):
            idx = np.argsort(-lp_all[:,k])[:max(int(PHI*len(Xtr)),60)]
            if len(np.unique(ytr[idx]))<2: idx=np.arange(len(Xtr))
            idxs.append(set(idx.tolist()))
            m = LogisticRegression(max_iter=2000).fit(Xtr[idx], ytr[idx])
            pk=np.zeros((len(Xte),len(classes)))
            pk[:,np.searchsorted(classes,m.classes_)]=m.predict_proba(Xte)
            P += W[:,k,None]*pk
            preds.append(m.predict(Xte))
        preds=np.array(preds)
        ov=np.mean([len(a&b)/len(a|b) for a,b in itertools.combinations(idxs,2)])
        dis=np.mean([np.mean(preds[i]!=preds[j]) for i,j in itertools.combinations(range(K),2)])
        oracle=np.mean((preds==yte).any(0))
        F=f1_score(yte, classes[P.argmax(1)], average="macro")
        rows.append(dict(K=K, phi=PHI, overlap=ov, disagree=dis, H_W=Hn,
                         oracle=oracle, ddel_F=F, delta_vs_single=F-sF, sec=time.time()-t0))
        print(f"K={K} phi={PHI}: overlap={ov:.3f} disagree={dis:.4f} H(W)={Hn:.3f} "
              f"oracle={oracle:.4f} F={F:.4f} ({F-sF:+.4f})", flush=True)

df=pd.DataFrame(rows); df.to_csv(DATA+"diversity_diagnostic.csv", index=False)
print("\nsingle LR macro-F", round(sF,4))
