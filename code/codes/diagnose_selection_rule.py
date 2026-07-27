"""Does the selection rule matter? Algorithm 1 (responsibility-ranked, per component)
vs up_memberc (distance-ranked to the mean, over the whole training set).

Also adds the published operating point phi=0.5 and the published K=6, which the
earlier diagnostic grid skipped.
"""
import numpy as np, pandas as pd, itertools, time
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

ROOT="/home/ali/Documents/ensemble/"; NPC, SEED = 157, 42
d = pd.read_csv(ROOT+"code/Data/UCI_HAR_Dataset/data_uci_handled.csv")
drop=[c for c in ["Activity","ActivityName","subject"] if c in d.columns]
X = d.drop(columns=drop).select_dtypes(include=[np.number]).to_numpy(np.float64)
y = d["Activity"].to_numpy(); classes = np.unique(y)

skf = StratifiedKFold(10, shuffle=True, random_state=SEED)
tr, te = next(iter(skf.split(X, y)))
sc = StandardScaler().fit(X[tr])
pca = PCA(NPC, random_state=SEED).fit(sc.transform(X[tr]))
Xtr, Xte = pca.transform(sc.transform(X[tr])), pca.transform(sc.transform(X[te]))
ytr, yte = y[tr], y[te]

single = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
sF = f1_score(yte, single.predict(Xte), average="macro")
print(f"Single LR macro-F = {sF:.4f}", flush=True)

rows=[]
for K in (5, 6):
    gm = GaussianMixture(K, covariance_type="full", random_state=SEED,
                         reg_covar=1e-4, max_iter=200).fit(Xtr)
    lp_all = gm._estimate_weighted_log_prob(Xtr)          # Algorithm 1 ranking key
    dist   = np.linalg.norm(Xtr[:,None,:] - gm.means_[None,:,:], axis=2)  # up_memberc key
    W = gm.predict_proba(Xte)
    for rule in ("responsibility", "distance"):
        for PHI in (0.2, 0.4, 0.5, 0.6, 0.9):
            t0=time.time(); idxs=[]; preds=[]; P=np.zeros((len(Xte), len(classes)))
            k_n = max(int(PHI*len(Xtr)), 60)
            for k in range(K):
                idx = (np.argsort(-lp_all[:,k])[:k_n] if rule=="responsibility"
                       else np.argsort(dist[:,k])[:k_n])
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
            rows.append(dict(K=K, rule=rule, phi=PHI, overlap=ov, disagree=dis,
                             oracle=oracle, ddel_F=F, delta_vs_single=F-sF, sec=time.time()-t0))
            print(f"K={K} {rule:14s} phi={PHI}: overlap={ov:.3f} disagree={dis:.4f} "
                  f"oracle={oracle:.4f} F={F:.4f} ({F-sF:+.4f})", flush=True)

df=pd.DataFrame(rows); df.to_csv(ROOT+"data/selection_rule_diagnostic.csv", index=False)
print("\nsingle LR macro-F", round(sF,4))
