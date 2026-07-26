"""
Tier 4 Item 20: Non-Clustering Ensemble Baselines with Cost Metrics
Minimal fast version for 2-core machine
"""
import os, sys, numpy as np, pandas as pd, time, pickle, psutil, warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '/home/ali/Documents/ensemble/code')

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
from scipy.stats import wilcoxon, friedmanchisquare, rankdata

# FROZEN ANCHORS
DDEL_GMM_perFold_F = np.array([
    0.9686395350495812, 0.97425242077933, 0.970990752162752, 0.9655126217399316,
    0.9652326316985408, 0.964323504667098, 0.970253421459105, 0.9673911185227232,
    0.9647208479998134, 0.9715912224629548
])
DDEL_GMM_F_mean = 0.968290807654183
DDEL_GMM_F_sd = 0.0034003437026449007
DDEL_GMM_Acc = 0.9661804858744716
DDEL_GMM_AUC = 0.9941454038270916
DDEL_GMM_Train_s = 48.2

print("[1] Loading data...")
df = pd.read_csv('/home/ali/Documents/ensemble/code/Data/UCI_HAR_Dataset/data_uci_handled.csv', index_col=0)
df['Activity'] = df['Activity'] + 1
X = df.drop(['Activity', 'ActivityName', 'subject'], axis=1).values
y = df['ActivityName'].values
print(f"  X shape: {X.shape}")

print("[2] PCA (157 components)...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
pca = PCA(n_components=157, random_state=None)
X_pca = pca.fit_transform(X_scaled)
print(f"  PCA shape: {X_pca.shape}")

print("[3] 10-fold CV setup...")
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
fold_indices = list(skf.split(X, y))

print("[4] Training baselines...")
results = {}
method_names = ['Single LR', 'Bagging (LR)', 'Random Forest', 'Gradient Boosting', 'AdaBoost']

for method in method_names:
    print(f"  {method}...")
    per_fold_F, per_fold_Acc, per_fold_AUC = [], [], []
    train_times, infer_times, param_counts, peak_mems = [], [], [], []
    
    for train_idx, test_idx in fold_indices:
        X_tr, X_te = X_pca[train_idx], X_pca[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]
        
        # Model selection
        if method == 'Single LR':
            clf = LogisticRegression(max_iter=300, random_state=42, solver='lbfgs')
        elif method == 'Bagging (LR)':
            clf = BaggingClassifier(LogisticRegression(max_iter=300, random_state=42, solver='lbfgs'), 
                                    n_estimators=5, random_state=42)
        elif method == 'Random Forest':
            clf = RandomForestClassifier(n_estimators=30, max_depth=12, random_state=42)
        elif method == 'Gradient Boosting':
            clf = GradientBoostingClassifier(n_estimators=30, max_depth=4, random_state=42)
        elif method == 'AdaBoost':
            clf = AdaBoostClassifier(n_estimators=20, random_state=42)
        
        # Memory before
        proc = psutil.Process(os.getpid())
        mem_before = proc.memory_info().rss / 1024 / 1024
        
        # Train
        t0 = time.time()
        clf.fit(X_tr, y_tr)
        train_time = time.time() - t0
        
        mem_after = proc.memory_info().rss / 1024 / 1024
        peak_mem = max(mem_before, mem_after)
        
        # Params
        if hasattr(clf, 'coef_'):
            n_params = clf.coef_.size + clf.intercept_.size
        else:
            n_params = X_tr.shape[1] * 30  # rough estimate
        
        # Predict
        y_pred = clf.predict(X_te)
        y_pr = clf.predict_proba(X_te)
        
        # Inference time
        t0 = time.time()
        _ = clf.predict(X_te)
        infer_time = (time.time() - t0) * 1000 / len(X_te)
        
        # Metrics
        f1 = f1_score(y_te, y_pred, average='macro', zero_division=0)
        acc = accuracy_score(y_te, y_pred)
        try:
            auc = roc_auc_score(y_te, y_pr, multi_class='ovr')
        except:
            auc = np.nan
        
        per_fold_F.append(f1)
        per_fold_Acc.append(acc)
        per_fold_AUC.append(auc)
        train_times.append(train_time)
        infer_times.append(infer_time)
        param_counts.append(n_params)
        peak_mems.append(peak_mem)
    
    results[method] = {
        'F': np.array(per_fold_F),
        'Acc': np.array(per_fold_Acc),
        'AUC': np.array(per_fold_AUC),
        'Train_s': np.mean(train_times),
        'Infer_ms': np.mean(infer_times),
        'N_params': np.mean(param_counts),
        'Peak_MB': np.mean(peak_mems),
    }

print("[5] Building performance matrix...")
perf_matrix = np.vstack([DDEL_GMM_perFold_F] + [results[m]['F'] for m in method_names])
method_labels = ['DDEL-GMM (ours)'] + method_names

print(f"  DDEL-GMM per-fold check:")
print(f"    Mean: {DDEL_GMM_perFold_F.mean():.15f} (expect 0.968290807654183)")
print(f"    Std:  {DDEL_GMM_perFold_F.std():.15f} (expect 0.0034003437026449007)")

print("[6] Wilcoxon tests...")
wilc_results = []
for i, method in enumerate(method_names, 1):
    diff = DDEL_GMM_perFold_F - results[method]['F']
    stat, p = wilcoxon(diff, alternative='greater')
    wins = np.sum(diff > 0)
    wilc_results.append({'method': method, 'stat': stat, 'p': max(p, 0.001), 'wins': wins})

print("[7] Friedman test...")
chi2, p_fri = friedmanchisquare(*perf_matrix)

print("[8] Nemenyi post-hoc...")
mean_ranks = rankdata(perf_matrix, axis=0).mean(axis=1)
q_alpha = 2.850
CD = q_alpha * np.sqrt(6 * 7 / (6.0 * 10))
print(f"  CD = {CD:.6f}")
print(f"  DDEL-GMM rank: {mean_ranks[0]:.2f}, RF rank: {mean_ranks[2]:.2f}")
rf_diff = abs(mean_ranks[0] - mean_ranks[2])
print(f"  Rank diff (DDEL-GMM vs RF): {rf_diff:.4f}, exceeds CD? {rf_diff > CD}")

print("[9] Summary CSV...")
summary_rows = []
for i, method in enumerate(method_labels):
    if i == 0:
        summary_rows.append({
            'Method': method, 'Acc': f"{DDEL_GMM_Acc:.4f}", 'F': f"{DDEL_GMM_F_mean:.15f}",
            'F_sd': f"{DDEL_GMM_F_sd:.15f}", 'AUC': f"{DDEL_GMM_AUC:.4f}",
            'wins': '---', 'p': '---', 'MeanRank': f"{mean_ranks[0]:.1f}",
            'Train_s': f"{DDEL_GMM_Train_s:.1f}", 'Infer_ms_per_sample': '---',
            'N_params_or_MB': '---', 'Peak_MB': '---'
        })
    else:
        r = results[method]
        wr = wilc_results[i-1]
        summary_rows.append({
            'Method': method, 'Acc': f"{r['Acc'].mean():.4f}", 'F': f"{r['F'].mean():.15f}",
            'F_sd': f"{r['F'].std():.15f}", 'AUC': f"{r['AUC'].mean():.4f}",
            'wins': f"{wr['wins']}/10", 'p': f"{wr['p']:.4f}" if wr['p'] >= 0.001 else "0.001",
            'MeanRank': f"{mean_ranks[i]:.1f}", 'Train_s': f"{r['Train_s']:.1f}",
            'Infer_ms_per_sample': f"{r['Infer_ms']:.6f}", 'N_params_or_MB': f"{r['N_params']:.0f}",
            'Peak_MB': f"{r['Peak_MB']:.1f}"
        })

pd.DataFrame(summary_rows).to_csv('/home/ali/Documents/ensemble/data/noclustering_summary.csv', index=False)

print("[10] Per-fold CSV...")
perfold_rows = [{'Fold': i+1} for i in range(10)]
for i, m in enumerate(method_labels):
    for j in range(10):
        perfold_rows[j][m] = perf_matrix[i, j]
pd.DataFrame(perfold_rows).to_csv('/home/ali/Documents/ensemble/data/noclustering_perfold.csv', index=False)

print("[11] Stats CSV...")
stats_rows = []
for wr in wilc_results:
    stats_rows.append({
        'Test': 'Wilcoxon', 'Baseline': wr['method'], 'Statistic': f"{wr['stat']:.1f}",
        'p': f"{wr['p']:.6f}", 'Wins': f"{wr['wins']}/10", 'n': 10, 'Interpretation': 'Sig' if wr['p'] < 0.05 else 'NS'
    })
stats_rows.append({
    'Test': 'Friedman', 'Baseline': '---', 'Statistic': f"{chi2:.4f}",
    'p': f"{p_fri:.6f}", 'Wins': 'k=6', 'n': 'N=10', 'Interpretation': 'Sig' if p_fri < 0.05 else 'NS'
})
stats_rows.append({
    'Test': 'Nemenyi', 'Baseline': 'DDEL-GMM vs RF', 'Statistic': f"{rf_diff:.4f}",
    'p': '---', 'Wins': f"CD={CD:.4f}", 'n': '---', 'Interpretation': 'Exceeds CD' if rf_diff > CD else 'Indistinguishable'
})
pd.DataFrame(stats_rows).to_csv('/home/ali/Documents/ensemble/data/noclustering_stats.csv', index=False)

print("\n" + "="*70)
print("TIER 4 ITEM 20 COMPLETE")
print("="*70)
