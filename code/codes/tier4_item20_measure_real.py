"""Real measurement: DDEL-GMM vs five non-clustering ensembles on UCI HAR.

Identical 10-fold stratified folds for every method. 157 PCs (95% variance),
fitted inside each fold to avoid leakage. DDEL-GMM reproduces the pipeline of
code/Funcs/Model_functions.py: GMM full-covariance partitioning, likelihood-ranked
per-component resampling at ratio phi, one logistic-regression base learner per
subset, aggregation by GMM posterior responsibilities (DENSITYE).
"""
import numpy as np, pandas as pd, time, json, sys
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (RandomForestClassifier, HistGradientBoostingClassifier,
                              BaggingClassifier, AdaBoostClassifier)
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score

ROOT = "/home/ali/Documents/ensemble/"
K, PHI, NPC, SEED = 5, 0.9, 157, 42

d = pd.read_csv(ROOT+"code/Data/UCI_HAR_Dataset/data_uci_handled.csv")
drop = [c for c in ["Activity","ActivityName","subject"] if c in d.columns]
X = d.drop(columns=drop).select_dtypes(include=[np.number]).to_numpy(np.float64)
y = d["Activity"].to_numpy()
print(f"X={X.shape} classes={len(np.unique(y))}", flush=True)

def ddel_gmm(Xtr, ytr, Xte, classes):
    gm = GaussianMixture(K, covariance_type="full", random_state=SEED,
                         reg_covar=1e-4, max_iter=200).fit(Xtr)
    P = np.zeros((len(Xte), len(classes)))
    W = gm.predict_proba(Xte)
    for k in range(K):
        # likelihood-ranked resampling: top PHI fraction under component k
        lp = gm._estimate_weighted_log_prob(Xtr)[:, k]
        idx = np.argsort(-lp)[:max(int(PHI*len(Xtr)), 60)]
        if len(np.unique(ytr[idx])) < 2:
            idx = np.arange(len(Xtr))
        m = LogisticRegression(max_iter=2000).fit(Xtr[idx], ytr[idx])
        pk = np.zeros((len(Xte), len(classes)))
        pk[:, np.searchsorted(classes, m.classes_)] = m.predict_proba(Xte)
        P += W[:, k, None] * pk
    return P

BASE = {
    "Random Forest":     lambda: RandomForestClassifier(300, random_state=SEED, n_jobs=2),
    "Gradient Boosting": lambda: HistGradientBoostingClassifier(random_state=SEED),
    "Bagging (LR)":      lambda: BaggingClassifier(LogisticRegression(max_iter=2000),
                                    n_estimators=10, random_state=SEED, n_jobs=2),
    # depth-3 trees, not stumps: a stump cannot separate 6 activity classes, and
    # AdaBoost-with-stumps collapses to ~0.4 F. Depth-3 is the fair configuration.
    "AdaBoost":          lambda: AdaBoostClassifier(
                                    DecisionTreeClassifier(max_depth=3, random_state=SEED),
                                    n_estimators=100, random_state=SEED),
    "Single LR":         lambda: LogisticRegression(max_iter=2000),
    # max_iter=-1 (converged). The manuscript's original SVC(max_iter=1000) stops
    # libsvm before convergence on 9,269x157 and scores 0.886 instead of 0.967.
    "Single SVM":        lambda: SVC(C=1, kernel="linear", max_iter=-1,
                                     probability=True, random_state=SEED),
}
classes = np.unique(y)
rows, times = {m: [] for m in ["DDEL-GMM (ours)"]+list(BASE)}, {m: 0.0 for m in ["DDEL-GMM (ours)"]+list(BASE)}
acc, auc = {m: [] for m in rows}, {m: [] for m in rows}

for f, (tr, te) in enumerate(StratifiedKFold(10, shuffle=True, random_state=SEED).split(X, y)):
    sc = StandardScaler().fit(X[tr]); pca = PCA(NPC, random_state=SEED).fit(sc.transform(X[tr]))
    Xtr, Xte = pca.transform(sc.transform(X[tr])), pca.transform(sc.transform(X[te]))
    ytr, yte = y[tr], y[te]
    if f == 0: print(f"variance retained={pca.explained_variance_ratio_.sum():.4f}", flush=True)

    t0 = time.time(); P = ddel_gmm(Xtr, ytr, Xte, classes); times["DDEL-GMM (ours)"] += time.time()-t0
    pred = classes[P.argmax(1)]
    rows["DDEL-GMM (ours)"].append(f1_score(yte, pred, average="macro"))
    acc["DDEL-GMM (ours)"].append(accuracy_score(yte, pred))
    auc["DDEL-GMM (ours)"].append(roc_auc_score(yte, P/P.sum(1, keepdims=True), multi_class="ovr", average="macro"))

    for name, mk in BASE.items():
        t0 = time.time(); m = mk().fit(Xtr, ytr); times[name] += time.time()-t0
        pr = m.predict_proba(Xte); pd_ = m.predict(Xte)
        rows[name].append(f1_score(yte, pd_, average="macro"))
        acc[name].append(accuracy_score(yte, pd_))
        auc[name].append(roc_auc_score(yte, pr, multi_class="ovr", average="macro"))
    print(f"fold {f+1}/10 " + " ".join(f"{n.split()[0]}={rows[n][-1]:.4f}" for n in rows), flush=True)
    # checkpoint every fold: a killed run keeps its completed folds
    pd.DataFrame({m: rows[m] for m in rows}).to_csv(
        ROOT+"data/_partial_perfold.csv", index=False)
    json.dump({"acc": acc, "auc": auc, "times": times, "folds_done": f+1},
              open(ROOT+"data/_partial_meta.json", "w"))

pf = pd.DataFrame(rows); pf.to_csv(ROOT+"data/noclustering_perfold_MEASURED.csv", index=False)
R = pf.rank(axis=1, ascending=False)
summ = pd.DataFrame({"Method": list(rows),
    "Acc":[np.mean(acc[m]) for m in rows], "F":[pf[m].mean() for m in rows],
    "F_sd":[pf[m].std(ddof=1) for m in rows], "AUC":[np.mean(auc[m]) for m in rows],
    "MeanRank":[R[m].mean() for m in rows], "Train_s":[times[m]/10 for m in rows]})
summ.to_csv(ROOT+"data/noclustering_summary_MEASURED.csv", index=False)
print("\n"+summ.to_string(index=False), flush=True)
