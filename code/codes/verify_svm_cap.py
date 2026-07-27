"""Is single-SVM 0.925 a property of SVM, or of max_iter=1000?
One fold, user's own preprocessing (StandardScaler -> PCA 95%), fitted in-fold.
"""
import warnings, numpy as np, pandas as pd, time
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.exceptions import ConvergenceWarning

d = pd.read_csv("code/Data/UCI_HAR_Dataset/data_uci_handled.csv")
y = d["Activity"]; X = d.drop(columns=[c for c in ["Activity","ActivityName","subject"] if c in d])
tr, te = next(StratifiedKFold(10, shuffle=True, random_state=42).split(X, y))
Xtr, Xte, ytr, yte = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]
sc = StandardScaler().fit(Xtr); A = sc.transform(Xtr); B = sc.transform(Xte)
pca = PCA(n_components=0.95, random_state=42).fit(A)
A, B = pca.transform(A), pca.transform(B)
print(f"fold 1: {A.shape[0]} train x {A.shape[1]} PCs")

for name, m in [("SVC max_iter=1000 (yours)", SVC(max_iter=1000, probability=True, C=1, kernel='linear')),
                ("SVC max_iter=-1 (converged)", SVC(max_iter=-1, probability=True, C=1, kernel='linear')),
                ("LogisticRegression (yours)", LogisticRegression(solver='lbfgs', max_iter=1000))]:
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        t0 = time.time(); m.fit(A, ytr); el = time.time()-t0
        conv = "NOT CONVERGED" if any(issubclass(x.category, ConvergenceWarning) for x in w) else "converged"
    f = f1_score(yte, m.predict(B), average="macro")
    print(f"{name:32s} macroF={f:.4f}  {conv}  {el:.0f}s", flush=True)
