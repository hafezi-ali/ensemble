#!/usr/bin/env bash
# Reproduce every measured result and figure in the DDEL-GMM manuscript.
#
#   ./run_all.sh            run everything (several hours: exp2 dominates)
#   ./run_all.sh figures    redraw figures from the shipped CSVs (~30 s)
#   ./run_all.sh diag       diagnostics only (selection rule, diversity, phi/K)
#
# Every script writes into data/ and figures/ next to this file. Nothing is
# written outside the reproduce/ folder.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs data figures
PY=${PYTHON:-python3}

run () {  # run <script> <label>
  echo "=== $2"
  local log="logs/$(basename "$1" .py).log"
  if $PY "$1" > "$log" 2>&1; then
      tail -3 "$log" | sed 's/^/    /'
  else
      echo "    FAILED - see $log"; tail -5 "$log" | sed 's/^/    /'; exit 1
  fi
}

MODE=${1:-all}

if [ "$MODE" = all ] || [ "$MODE" = experiments ]; then
  run scripts/exp1_gmm_vs_kmeans.py       "Exp 1  GMM vs K-means (synthetic sweep + covtype + HAR)"
  run scripts/exp2_noclustering_measure.py "Exp 2  vs bagging/boosting/RF, 10 folds  [SLOW, ~2 h]"
  run scripts/exp2_noclustering_stats.py   "Exp 2  Wilcoxon / Friedman / Nemenyi"
  run scripts/exp3_table4_nested.py        "Table IV  nested hyperparameter selection  [SLOW]"
fi

if [ "$MODE" = all ] || [ "$MODE" = diag ]; then
  run scripts/diag_selection_rule.py   "Diag  selection rule + phi sweep (feeds Fig. 7)"
  run scripts/diag_diversity.py        "Diag  diversity vs phi and K"
  run scripts/diag_confirm_phi_K.py    "Diag  confirm the chosen (K, phi)"
  run scripts/diag_weighting.py        "Diag  candidate fixes for the oracle gap"
  run scripts/check_svm_cap.py         "Check single-SVM 0.925: SVM or max_iter?"
  run scripts/check_user_funcs.py      "Check author's Funcs/ reproduce the numbers"
fi

if [ "$MODE" = all ] || [ "$MODE" = figures ]; then
  run scripts/figures/fig1_and_fig7.py     "Fig. 1 pipeline + Fig. 7 diagnostics"
  run scripts/figures/fig5_boxplot.py      "Fig. 5 per-fold boxplot"
  run scripts/figures/fig8_sota.py         "Fig. 8 vs published DES methods"
  run scripts/figures/fig10_noclustering.py "Fig. 10 vs non-clustering ensembles"
fi

echo
echo "done.  data/ and figures/ updated; per-script logs in logs/"
