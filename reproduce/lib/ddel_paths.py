"""Path resolution for the DDEL-GMM reproduction package.

Every script imports ROOT from here instead of hardcoding an absolute path,
so the folder can be moved or cloned anywhere.

Layout assumed:
    <repo>/reproduce/lib/ddel_paths.py   <- this file
    <repo>/reproduce/data/               <- CSVs written by the scripts
    <repo>/reproduce/figures/            <- PDFs/PNGs written by the scripts
    <repo>/code/Data/UCI_HAR_Dataset/data_uci_handled.csv   <- input dataset
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG  = os.path.dirname(HERE)                 # <repo>/reproduce
ROOT = os.path.dirname(PKG) + os.sep         # <repo>/

DATA = os.path.join(PKG, "data") + os.sep
FIGS = os.path.join(PKG, "figures") + os.sep

# UCI HAR feature matrix, 10299 x 561 plus label columns
DATASET = os.environ.get(
    "DDEL_DATASET",
    os.path.join(ROOT, "code", "Data", "UCI_HAR_Dataset", "data_uci_handled.csv"))

# the author's original module tree (Funcs/, Lib/), importable by the scripts
sys.path.insert(0, os.path.join(ROOT, "code"))

NPC  = 157      # principal components retained (95% of variance)
SEED = 42
K_PUB, PHI_PUB = 6, 0.5      # operating point reported in the manuscript


def require_dataset():
    if not os.path.exists(DATASET):
        raise SystemExit(
            "UCI HAR dataset not found at:\n  %s\n"
            "Set DDEL_DATASET to its location, e.g.\n"
            "  export DDEL_DATASET=/path/to/data_uci_handled.csv" % DATASET)
    return DATASET
