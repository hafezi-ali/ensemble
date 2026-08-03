"""Fair real measurement: DDEL-GMM vs five non-clustering ensembles, UCI HAR.

Identical 10 stratified folds for all methods. Each method gets the feature
representation that suits it, so no baseline is strawmanned:
  - tree ensembles: raw 561 features (axis-aligned splits suit unrotated axes)
  - AdaBoost: depth-3 trees, not sklearn's default depth-1 stumps
  - linear models + DDEL-GMM: 157 PCs (95% variance), fitted inside each fold
DDEL-GMM follows code/Funcs/Model_functions.py: GMM full-covariance partitioning,
likelihood-ranked per-component resampling at phi, one LR per subset, aggregation
by GMM posterior responsibilities (DENSITYE).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))
from ddel_paths import ROOT, DATA, FIGS, DATASET, NPC, SEED, K_PUB, PHI_PUB, require_dataset
require_dataset()

import numpy as np, pandas as pd, time, resource
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (RandomForestClassifier, HistGradientBoostingClassifier,
                              BaggingClassifier, AdaBoostClassifier)
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score

K,PHI,NPC,SEED=5,0.9,157,42
d=pd.read_csv(DATASET)
X=d.drop(columns=[c for c in ["Activity","ActivityName","subject"] if c in d.columns]
        ).select_dtypes(include=[np.number]).to_numpy(np.float64)
y=d["Activity"].to_numpy(); classes=np.unique(y)
print(f"X={X.shape} classes={len(classes)}",flush=True)

def ddel_gmm(Xtr,ytr,Xte):
    gm=GaussianMixture(K,covariance_type="full",random_state=SEED,reg_covar=1e-4,max_iter=200).fit(Xtr)
    W=gm.predict_proba(Xte); P=np.zeros((len(Xte),len(classes)))
    for k in range(K):
        lp=gm._estimate_weighted_log_prob(Xtr)[:,k]
        idx=np.argsort(-lp)[:max(int(PHI*len(Xtr)),60)]
        if len(np.unique(ytr[idx]))<2: idx=np.arange(len(Xtr))
        m=LogisticRegression(max_iter=1000).fit(Xtr[idx],ytr[idx])
        pk=np.zeros((len(Xte),len(classes)))
        pk[:,np.searchsorted(classes,m.classes_)]=m.predict_proba(Xte)
        P+=W[:,k,None]*pk
    return P

# space: "raw" = 561 original features, "pca" = 157 PCs
SPEC={"Random Forest":("raw",lambda:RandomForestClassifier(200,random_state=SEED,n_jobs=2)),
      "Gradient Boosting":("raw",lambda:HistGradientBoostingClassifier(random_state=SEED)),
      "Bagging (LR)":("pca",lambda:BaggingClassifier(LogisticRegression(max_iter=1000),
                        n_estimators=10,random_state=SEED,n_jobs=2)),
      "AdaBoost":("raw",lambda:AdaBoostClassifier(DecisionTreeClassifier(max_depth=3),
                        n_estimators=100,random_state=SEED)),
      "Single LR":("pca",lambda:LogisticRegression(max_iter=1000))}
M=["DDEL-GMM (ours)"]+list(SPEC)
F={m:[] for m in M}; A={m:[] for m in M}; U={m:[] for m in M}
T={m:[] for m in M}; I={m:[] for m in M}; MEM={m:[] for m in M}
def peak(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024

for f,(tr,te) in enumerate(StratifiedKFold(10,shuffle=True,random_state=SEED).split(X,y)):
    sc=StandardScaler().fit(X[tr]); pca=PCA(NPC,random_state=SEED).fit(sc.transform(X[tr]))
    Ptr,Pte=pca.transform(sc.transform(X[tr])),pca.transform(sc.transform(X[te]))
    Rtr,Rte=X[tr],X[te]; ytr,yte=y[tr],y[te]
    if f==0: print(f"variance retained={pca.explained_variance_ratio_.sum():.4f}",flush=True)

    m0=peak(); t0=time.time(); P=ddel_gmm(Ptr,ytr,Pte); el=time.time()-t0
    pr=classes[P.argmax(1)]
    F["DDEL-GMM (ours)"].append(f1_score(yte,pr,average="macro"))
    A["DDEL-GMM (ours)"].append(accuracy_score(yte,pr))
    U["DDEL-GMM (ours)"].append(roc_auc_score(yte,P/P.sum(1,keepdims=True),multi_class="ovr",average="macro"))
    T["DDEL-GMM (ours)"].append(el); I["DDEL-GMM (ours)"].append(el/len(yte)*1000)
    MEM["DDEL-GMM (ours)"].append(peak()-m0)

    for n,(sp,mk) in SPEC.items():
        Xa,Xb=(Rtr,Rte) if sp=="raw" else (Ptr,Pte)
        m0=peak(); t0=time.time(); mo=mk().fit(Xa,ytr); el=time.time()-t0
        t1=time.time(); pp=mo.predict_proba(Xb); it=time.time()-t1
        pd_=classes[pp.argmax(1)] if list(mo.classes_)==list(classes) else mo.predict(Xb)
        F[n].append(f1_score(yte,pd_,average="macro")); A[n].append(accuracy_score(yte,pd_))
        U[n].append(roc_auc_score(yte,pp,multi_class="ovr",average="macro"))
        T[n].append(el); I[n].append(it/len(yte)*1000); MEM[n].append(peak()-m0)
    print(f"fold {f+1}/10 "+" ".join(f"{n.split()[0]}={F[n][-1]:.4f}" for n in M),flush=True)

pf=pd.DataFrame(F); pf.to_csv(DATA+"noclustering_perfold.csv",index=False)
R=pf.rank(axis=1,ascending=False)
pd.DataFrame({"Method":M,"Acc":[np.mean(A[m]) for m in M],"F":[pf[m].mean() for m in M],
  "F_sd":[pf[m].std(ddof=1) for m in M],"AUC":[np.mean(U[m]) for m in M],
  "MeanRank":[R[m].mean() for m in M],"Train_s":[np.mean(T[m]) for m in M],
  "Infer_ms_per_sample":[np.mean(I[m]) for m in M],"Peak_MB":[np.mean(MEM[m]) for m in M],
  }).to_csv(DATA+"noclustering_summary.csv",index=False)
print("\nDONE\n"+pd.read_csv(DATA+"noclustering_summary.csv").to_string(index=False),flush=True)
