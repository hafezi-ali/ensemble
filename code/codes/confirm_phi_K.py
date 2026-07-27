"""10-fold confirmation: does K=8/phi=0.4 (+T=80) beat K=5/phi=0.9 and Single LR?
Paired Wilcoxon on identical folds. No baselines re-run; DDEL variants + Single LR only.
"""
import numpy as np, pandas as pd, time
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from scipy.special import softmax
from scipy.stats import wilcoxon

ROOT="/home/ali/Documents/ensemble/"; NPC,SEED=157,42
d=pd.read_csv(ROOT+"code/Data/UCI_HAR_Dataset/data_uci_handled.csv")
drop=[c for c in ["Activity","ActivityName","subject"] if c in d.columns]
X=d.drop(columns=drop).select_dtypes(include=[np.number]).to_numpy(np.float64)
y=d["Activity"].to_numpy(); classes=np.unique(y)

CFG={"DDEL K5 phi0.9 T1 (current)":(5,0.9,1.0),
     "DDEL K8 phi0.4 T1":(8,0.4,1.0),
     "DDEL K8 phi0.4 T80":(8,0.4,80.0)}
res={k:[] for k in CFG}; res["Single LR"]=[]

for f,(tr,te) in enumerate(StratifiedKFold(10,shuffle=True,random_state=SEED).split(X,y)):
    sc=StandardScaler().fit(X[tr]); pca=PCA(NPC,random_state=SEED).fit(sc.transform(X[tr]))
    Xtr=pca.transform(sc.transform(X[tr])); Xte=pca.transform(sc.transform(X[te]))
    ytr,yte=y[tr],y[te]
    res["Single LR"].append(f1_score(yte,LogisticRegression(max_iter=2000).fit(Xtr,ytr).predict(Xte),average="macro"))
    cache={}
    for name,(K,PHI,T) in CFG.items():
        if K not in cache:
            gm=GaussianMixture(K,covariance_type="full",random_state=SEED,reg_covar=1e-4,max_iter=200).fit(Xtr)
            cache[K]=(gm,gm._estimate_weighted_log_prob(Xtr),gm._estimate_weighted_log_prob(Xte))
        gm,lp_tr,lp_te=cache[K]
        Pk=[]
        for k in range(K):
            idx=np.argsort(-lp_tr[:,k])[:max(int(PHI*len(Xtr)),60)]
            if len(np.unique(ytr[idx]))<2: idx=np.arange(len(Xtr))
            m=LogisticRegression(max_iter=2000).fit(Xtr[idx],ytr[idx])
            p=np.zeros((len(Xte),len(classes)))
            p[:,np.searchsorted(classes,m.classes_)]=m.predict_proba(Xte); Pk.append(p)
        W=softmax(lp_te/T,axis=1)
        res[name].append(f1_score(yte,classes[np.einsum("nk,knc->nc",W,np.array(Pk)).argmax(1)],average="macro"))
    print(f"fold {f+1}/10 "+" ".join(f"{n.split()[1] if n.startswith('DDEL') else 'LR'}={res[n][-1]:.4f}" for n in res),flush=True)

df=pd.DataFrame(res); df.insert(0,"fold",range(1,11))
df.to_csv(ROOT+"data/phi_K_confirmation.csv",index=False)
print("\n"+df.drop(columns="fold").agg(['mean','std']).round(5).to_string())
base=np.array(res["DDEL K5 phi0.9 T1 (current)"]); lr=np.array(res["Single LR"])
for n in ["DDEL K8 phi0.4 T1","DDEL K8 phi0.4 T80"]:
    v=np.array(res[n])
    print(f"\n{n}: vs current p={wilcoxon(v,base).pvalue:.4f} wins={int((v>base).sum())}/10 "
          f"| vs SingleLR p={wilcoxon(v,lr).pvalue:.4f} wins={int((v>lr).sum())}/10 mean_delta={v.mean()-lr.mean():+.5f}")
