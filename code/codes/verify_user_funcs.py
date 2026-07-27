"""Verify: does using the user's own Funcs/ code change the measured item-20 numbers?

Compares three subset-selection rules under IDENTICAL folds, identical
single_preprocessing() from Funcs/Functions.py, and identical GMM posterior
aggregation (DENSITYE):
  A) user_sampling  - Funcs.sampling(): phi*n nearest points to each GMM MEAN by
                      Euclidean distance (their up_memberc)
  B) my_loglik      - top phi*n by GMM weighted log-likelihood per component
Both then aggregate with cluster_model.predict_proba(X) weights, exactly as
Model_functions.py DENSITYE does.
"""
import sys, types, numpy as np, pandas as pd
sys.path.insert(0, "/home/ali/Documents/ensemble/code")
# torch is imported by Funcs only to wrap outputs in tensors; stub it so the
# user's numerical code runs unmodified without a 2GB install.

# tensorflow/keras is imported by Lib/lib.py only for model/metric CLASSES that the
# sampling + preprocessing path never calls. A meta-path finder returns permissive
# stubs for any tensorflow.* submodule, so no 600MB install is needed on a 4GB box.
import importlib.abc, importlib.machinery
class _Any:
    def __init__(self,*a,**k): pass
    def __call__(self,*a,**k): return None
    def __getattr__(self,n): return _Any()
class _StubMod(types.ModuleType):
    __path__ = []
    def __getattr__(self,n):
        if n.startswith("__"): raise AttributeError(n)
        return _Any
class _TFFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, name, path=None, target=None):
        if name in ("tensorflow","torch") or name.startswith(("tensorflow.","torch.")):
            return importlib.machinery.ModuleSpec(name, self, is_package=True)
        return None
    def create_module(self, spec): return _StubMod(spec.name)
    def exec_module(self, module): pass
sys.meta_path.insert(0, _TFFinder())
import torch
torch.tensor = lambda x, **k: np.asarray(x)
torch.from_numpy = lambda x: np.asarray(x)
torch.Tensor = np.ndarray
import torch._VF
torch._VF.nan_to_num = np.nan_to_num

from Funcs.Functions import single_preprocessing, sampling
from sklearn.model_selection import StratifiedKFold
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

ROOT="/home/ali/Documents/ensemble/"; K,PHI,NPC,SEED=5,0.9,157,42
d=pd.read_csv(ROOT+"code/Data/UCI_HAR_Dataset/data_uci_handled.csv")
X=d.drop(columns=[c for c in ["Activity","ActivityName","subject"] if c in d.columns]
        ).select_dtypes(include=[np.number]).to_numpy(np.float64)
y=d["Activity"].to_numpy(); classes=np.unique(y)

def fit_predict(subsets, gm, Xte):
    W=gm.predict_proba(Xte); P=np.zeros((len(Xte),len(classes)))
    for k,(Xs,ys) in enumerate(subsets):
        if len(np.unique(ys))<2: continue
        m=LogisticRegression(max_iter=1000).fit(Xs,ys)
        pk=np.zeros((len(Xte),len(classes)))
        pk[:,np.searchsorted(classes,m.classes_)]=m.predict_proba(Xte)
        P+=W[:,k,None]*pk
    return classes[P.argmax(1)]

fa,fb=[],[]
for f,(tr,te) in enumerate(StratifiedKFold(10,shuffle=True,random_state=SEED).split(X,y)):
    # user's own preprocessing function
    R=single_preprocessing(X[tr],X[te],y[tr],n_components=NPC,random_state_pca=SEED)
    Xtr,Xte=R["X_train"],R["X_test"]; ytr,yte=y[tr],y[te]

    # A) the user's own sampling(): nearest phi*n to each GMM mean
    gmA=GaussianMixture(K,covariance_type="full",random_state=SEED,reg_covar=1e-4,max_iter=200)
    S=sampling(cluster_model=gmA,distance_metrics="Euclidean",phi=PHI,xtr=Xtr,ytr=ytr)
    subA=[(np.asarray(S["cluster_samples"][k]),np.asarray(S["cluster_samples_lables"][k]).ravel())
          for k in range(K)]
    fa.append(f1_score(yte,fit_predict(subA,S["cluster_model"],Xte),average="macro"))

    # B) my log-likelihood ranking
    gmB=GaussianMixture(K,covariance_type="full",random_state=SEED,reg_covar=1e-4,max_iter=200).fit(Xtr)
    lp=gmB._estimate_weighted_log_prob(Xtr); kk=int(PHI*len(Xtr))
    subB=[(Xtr[np.argsort(-lp[:,k])[:kk]],ytr[np.argsort(-lp[:,k])[:kk]]) for k in range(K)]
    fb.append(f1_score(yte,fit_predict(subB,gmB,Xte),average="macro"))
    print(f"fold {f+1}/10  user_sampling={fa[-1]:.4f}  my_loglik={fb[-1]:.4f}",flush=True)

fa,fb=np.array(fa),np.array(fb)
print(f"\nuser sampling() : {fa.mean():.6f} +- {fa.std(ddof=1):.6f}")
print(f"my log-lik rank : {fb.mean():.6f} +- {fb.std(ddof=1):.6f}")
print(f"difference      : {fa.mean()-fb.mean():+.6f}")
pd.DataFrame({"fold":range(1,11),"user_sampling":fa,"my_loglik":fb}).to_csv(
    ROOT+"data/subset_rule_verification.csv",index=False)
