# Table IV rerun: nested hyperparameter selection

## Why this rerun happened
The retuned configuration K=8/phi=0.4/T=80 was chosen by inspecting TEST-fold scores.
Reporting that number would be selection on the test set. This rerun selects K, phi and T
inside each outer training fold on a held-out 25% validation split, refits on the full
training fold, and scores once on the untouched test fold.

## The three numbers, same 10 folds

    Variant                              mean F     SD
    K=5/phi=0.9 (previous Table IV)      0.97341    0.00554
    NESTED selection (now in Table IV)   0.97418    0.00670
    K=8/phi=0.4/T=80 (test-set chosen)   0.97555    0.00527

Optimism of test-set selection over nested: +0.00137 F. That is the amount a referee
would be entitled to subtract from a tuned-on-test number, and it is now disclosed in
the Protocol paragraph rather than hidden.

## What changed in Table IV

    Field                     was        now
    DDEL-GMM Acc              0.9725     0.9735
    DDEL-GMM mean F           0.9734     0.9742
    DDEL-GMM SD               0.0055     0.0067
    DDEL-GMM mean rank        2.65       2.05   <- now best in table
    DDEL-GMM train time       103.2 s    81.1 s (+268.5 s selection, disclosed)
    Bagging rank / p          2.20/0.770 2.40/0.625
    Single LR rank / p        2.35/1.000 2.55/0.496
    Single SVM rank / p       2.80/0.275 3.00/0.105
    Friedman chi2 / p         49.86/5.0e-9  50.37/4.0e-9
    Nemenyi CD                2.85       2.85 (unchanged)

Bold marks moved: ours now takes Acc, mean F AND mean rank; Bagging keeps SD and takes
AUC; Single LR takes time. Baseline columns were NOT re-run - fold identity was verified
first (Single LR matches the earlier run to 0.0 on all 10 folds), so the nested DDEL row
was spliced into the existing measured matrix.

## What improved, and what did not

CHANGED for the better: DDEL-GMM now holds the best mean rank (2.05) in the table and
wins the majority of folds against every baseline (7/10 vs Bagging, 5/10 vs Single LR,
7/10 vs SVM). Gradient boosting is now separated by Nemenyi as well (gap 2.95 > CD 2.85),
so three baselines are formally separated instead of two.

UNCHANGED: none of the three strong baselines is statistically separated. p = 0.625,
0.496, 0.105. The claim is still 'best mean rank, consistent direction, not significant
at n=10' - NOT 'outperforms'. Do not upgrade this wording.

WORSE: SD rose from 0.0055 to 0.0067, because per-fold configuration switching adds
variance. Bagging still has the lowest SD. Reported honestly in the table.

## The selection behaviour is itself a finding
phi=0.4 was chosen on 8 of 10 folds; phi=0.9 on 2. The inner validation independently
rediscovers the diversity diagnosis: at phi=0.9 subset overlap is 0.84 and base learners
disagree on <1% of instances, so the ensemble degenerates to a single model. This is now
in the Insight paragraph as the mechanism governing when the framework helps.
T=80 was chosen on 4 folds, T=1 on 6 - the temperature is a real but marginal effect,
which is why it is presented as a selected hyperparameter and not as a headline claim.

## Separate issue found, NOT yet fixed
code/codes/base_train.py line 25 uses a single 80/20 train_test_split, and the 45-config
grid (9 phi x 5 K) in evaluation.py is scored on that one test set with the best reported.
Your published 0.973 in Table I is therefore a maximum over 45 test-set evaluations.
Measured optimism from selecting among just 3 configs was +0.0014; over 45 it is larger.
Table IV is now immune to this objection; Table I is not. Options: rerun Table I under
nested selection, or state the protocol explicitly and let the reader weigh it.

## Files
- data/ddel_nested_perfold.csv - per-fold nested result incl. chosen config and both timings
- data/noclustering_perfold.csv, _summary.csv, _stats.csv - regenerated with the nested row
- manuscript/noclustering_comparison.pdf - refreshed figure (ours now rank 1)
- code/codes/rerun_table4_nested.py - the nested protocol