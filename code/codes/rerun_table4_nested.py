"""Table IV rerun: DDEL-GMM with NESTED hyperparameter selection.

Why nested: K=8/phi=0.4/T=80 was chosen by inspecting TEST-fold scores. Reporting
that directly is selection on the test set. Here, for each outer fold, the config is
chosen on a validation split carved from the TRAINING data only, then refit on the
full training fold and scored once on the untouched test fold. This is the number
that belongs in the paper.

Baselines are NOT re-run: fold identity was verified (Single LR matches the earlier
run to 0.0 on all 10 folds), so the measured baseline columns are spliced in.

Grid: K in {5,8} x phi in {0.4,0.9} x T in {1,80}. GMM depends only on K and the
base learners only on (K,phi), so T is swept post-hoc from cached probabilities.
"""
import numpy as np, pandas as pd, time, json
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
from scipy.special import softmax

ROOT="/home/ali/Documents/ensemble/"; NPC,SEED=157,42
K_GRID,PHI_GRID,T_GRID=(5,8),(0.4,0.9),(1.0,80.0)

d=pd.read_csv(ROOT+"code/Data/UCI_HAR_Dataset/data_uci_handled.csv")
drop=[c for c in ["Activity","ActivityName","subject"] if c in d.columns]
X=d.drop(columns=drop).select_dtypes(include=[np.number]).to_numpy(np.float64)
y=d["Activity"].to_numpy(); classes=np.unique(y)
print(f"X={X.shape}",flush=True)

def build(Xa,ya,Xb,K,PHI):
    """Fit GMM on Xa, K subset learners, return (K,n_b,C) probs and test log-probs."""
    gm=GaussianMixture(K,covariance_type="full",random_state=SEED,
                       reg_covar=1e-4,max_iter=200).fit(Xa)
    lp_a=gm._estimate_weighted_log_prob(Xa); lp_b=gm._estimate_weighted_log_prob(Xb)
    Pk=[]
    for k in range(K):
        idx=np.argsort(-lp_a[:,k])[:max(int(PHI*len(Xa)),60)]
        if len(np.unique(ya[idx]))<2: idx=np.arange(len(Xa))
        m=LogisticRegression(max_iter=2000).fit(Xa[idx],ya[idx])
        p=np.zeros((len(Xb),len(classes)))
        p[:,np.searchsorted(classes,m.classes_)]=m.predict_proba(Xb); Pk.append(p)
    return np.array(Pk), lp_b

def agg(Pk,lp,T):
    W=softmax(lp/T,axis=1)
    return np.einsum("nk,knc->nc",W,Pk)

F,ACC,AUC,CHOSEN,fit_s,sel_s=[],[],[],[],[],[]
for f,(tr,te) in enumerate(StratifiedKFold(10,shuffle=True,random_state=SEED).split(X,y)):
    sc=StandardScaler().fit(X[tr]); pca=PCA(NPC,random_state=SEED).fit(sc.transform(X[tr]))
    Xtr=pca.transform(sc.transform(X[tr])); Xte=pca.transform(sc.transform(X[te]))
    ytr,yte=y[tr],y[te]

    # ---- inner selection: validation split from TRAIN only ----
    t0=time.time()
    Xi,Xv,yi,yv=train_test_split(Xtr,ytr,test_size=0.25,stratify=ytr,random_state=SEED)
    best=(-1,None)
    for K in K_GRID:
        for PHI in PHI_GRID:
            Pk,lp=build(Xi,yi,Xv,K,PHI)
            for T in T_GRID:
                s=f1_score(yv,classes[agg(Pk,lp,T).argmax(1)],average="macro")
                if s>best[0]: best=(s,(K,PHI,T))
    sel_s.append(time.time()-t0)
    K,PHI,T=best[1]; CHOSEN.append(f"K{K}/phi{PHI}/T{T:g}")

    # ---- refit selected config on FULL train, score untouched test ----
    t0=time.time(); Pk,lp=build(Xtr,ytr,Xte,K,PHI); P=agg(Pk,lp,T); fit_s.append(time.time()-t0)
    pred=classes[P.argmax(1)]
    F.append(f1_score(yte,pred,average="macro")); ACC.append(accuracy_score(yte,pred))
    AUC.append(roc_auc_score(yte,P/P.sum(1,keepdims=True),multi_class="ovr",average="macro"))
    print(f"fold {f+1}/10 chose {CHOSEN[-1]:16s} val={best[0]:.4f} test_F={F[-1]:.4f} "
          f"fit={fit_s[-1]:.0f}s sel={sel_s[-1]:.0f}s",flush=True)
    pd.DataFrame(dict(fold=range(1,len(F)+1),F=F,Acc=ACC,AUC=AUC,chosen=CHOSEN,
                      fit_s=fit_s,sel_s=sel_s)).to_csv(ROOT+"data/_partial_nested.csv",index=False)

out=pd.DataFrame(dict(fold=range(1,11),F=F,Acc=ACC,AUC=AUC,chosen=CHOSEN,fit_s=fit_s,sel_s=sel_s))
out.to_csv(ROOT+"data/ddel_nested_perfold.csv",index=False)
print(f"\nDDEL-GMM (nested) F={np.mean(F):.5f} SD={np.std(F,ddof=1):.5f} "
      f"Acc={np.mean(ACC):.5f} AUC={np.mean(AUC):.5f} fit={np.mean(fit_s):.1f}s sel={np.mean(sel_s):.1f}s")
print("configs chosen:", pd.Series(CHOSEN).value_counts().to_dict())
