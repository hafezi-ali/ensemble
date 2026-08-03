"""Two mechanisms to close the oracle gap, measured on fold 1, K=8 phi=0.4.

A) TEMPERATURE on the posterior. H(W)~0 means DENSITYE is hard 1-of-K selection.
   W = softmax(log_prob / T). T>1 SOFTENS, letting several learners contribute.
   Usual DES advice is to sharpen; here the measurement says sharpen is already
   maxed out, so the untried direction is soften.
B) HETEROGENEOUS base learners. Diversity from model bias instead of from data
   subsetting, so it does not pay the sample-starvation cost that low phi does.
   Uses the same 4 families as the user's get_models().
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))
from ddel_paths import ROOT, DATA, FIGS, DATASET, NPC, SEED, K_PUB, PHI_PUB, require_dataset
require_dataset()

import numpy as np, pandas as pd, time
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import f1_score
from scipy.special import softmax

NPC,SEED,K,PHI = 157,42,8,0.4
d=pd.read_csv(DATASET)
drop=[c for c in ["Activity","ActivityName","subject"] if c in d.columns]
X=d.drop(columns=drop).select_dtypes(include=[np.number]).to_numpy(np.float64)
y=d["Activity"].to_numpy(); classes=np.unique(y)
tr,te=next(iter(StratifiedKFold(10,shuffle=True,random_state=SEED).split(X,y)))
sc=StandardScaler().fit(X[tr]); pca=PCA(NPC,random_state=SEED).fit(sc.transform(X[tr]))
Xtr=pca.transform(sc.transform(X[tr])); Xte=pca.transform(sc.transform(X[te]))
ytr,yte=y[tr],y[te]
sF=f1_score(yte,LogisticRegression(max_iter=2000).fit(Xtr,ytr).predict(Xte),average="macro")

gm=GaussianMixture(K,covariance_type="full",random_state=SEED,reg_covar=1e-4,max_iter=200).fit(Xtr)
lp_all=gm._estimate_weighted_log_prob(Xtr)
LP_te=gm._estimate_weighted_log_prob(Xte)          # raw log-densities, un-normalised

def subsets():
    out=[]
    for k in range(K):
        idx=np.argsort(-lp_all[:,k])[:max(int(PHI*len(Xtr)),60)]
        if len(np.unique(ytr[idx]))<2: idx=np.arange(len(Xtr))
        out.append(idx)
    return out
IDX=subsets()

def fit_probs(factory):
    Pk=[]
    for k in range(K):
        m=factory(k).fit(Xtr[IDX[k]],ytr[IDX[k]])
        p=np.zeros((len(Xte),len(classes)))
        p[:,np.searchsorted(classes,m.classes_)]=m.predict_proba(Xte)
        Pk.append(p)
    return np.array(Pk)                             # (K, n, C)

HOMO = fit_probs(lambda k: LogisticRegression(max_iter=2000))
HET_F=[lambda k: LogisticRegression(max_iter=2000),
       lambda k: SVC(C=1,kernel="linear",probability=True,random_state=SEED),
       lambda k: DecisionTreeClassifier(max_depth=12,random_state=SEED),
       lambda k: KNeighborsClassifier(15)]
HET = fit_probs(lambda k: HET_F[k%4](k))

rows=[]
for name,Pk in (("homogeneous LR",HOMO),("heterogeneous",HET)):
    for T in (1.0,5.0,20.0,80.0,300.0,1e9):        # 1e9 -> uniform == AvgE
        W=softmax(LP_te/T,axis=1)
        Hn=float(np.mean(-(W*np.log(W+1e-12)).sum(1))/np.log(K))
        F=f1_score(yte,classes[np.einsum("nk,knc->nc",W,Pk).argmax(1)],average="macro")
        rows.append(dict(base=name,T=T,H_W=Hn,F=F,delta=F-sF))
        print(f"{name:16s} T={T:<8g} H(W)={Hn:.3f}  F={F:.4f} ({F-sF:+.4f})",flush=True)

df=pd.DataFrame(rows); df.to_csv(DATA+"weighting_improvement.csv",index=False)
print(f"\nSingle LR {sF:.4f}   best {df.F.max():.4f} = {df.loc[df.F.idxmax(),'base']} T={df.loc[df.F.idxmax(),'T']:g}")
