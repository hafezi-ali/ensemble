#!/usr/bin/env python3
"""One command to rebuild every table and figure in the manuscript from results/*.csv.

    python3 make_results.py            # rebuild everything
    python3 make_results.py --verify   # check the tables still match the paper
    python3 make_results.py --tables   # tables only
    python3 make_results.py --figures  # figures only

WORKFLOW
--------
1. Paste new numbers from Colab into the relevant file in results/ (one CSV per
   table or figure; see docs/2-CSV-TO-OUTPUT-MAP.md for which file drives what).
2. Run this script.
3. Recompile the manuscript. document.tex \\inputs tables/*.tex and reads the
   figures, so the PDF picks up the new numbers with no LaTeX edits.

WHAT --verify MEANS
-------------------
The CSVs were transcribed from the manuscript as it stands today, so rendering
them must reproduce the original floats BYTE FOR BYTE. --verify checks exactly
that. Run it BEFORE you edit any numbers: a PASS says the pipeline is faithful.
Once you deliberately change a value it will FAIL for that table, and the diff it
prints shows old-vs-new - that is the intended signal, not an error.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def run(script, args=()):
    cmd = [sys.executable, os.path.join(ROOT, script), *args]
    print("\n" + "=" * 70)
    print("$ python3 %s %s" % (script, " ".join(args)))
    print("=" * 70)
    return subprocess.call(cmd, cwd=ROOT)


# Index columns carry row labels, not measurements: a filled 'phi' column
# does not mean anyone has pasted results in yet.
INDEX_COLS = {"phi", "k", "drift_point", "fold", "method", "learner",
              "base_learner", "variant", "clustering", "clustering_type",
              "data_geometry", "dataset", "ensemble_method", "model",
              "covariance_type", "cite_key", "algorithm"}


def status():
    """Print which results/*.csv still need numbers pasted in."""
    import csv as _csv
    import glob

    def is_number(v):
        v = str(v or "").strip()
        if v == "---":
            return True   # deliberate "not applicable", not a gap
        try:
            float(v)
            return True
        except ValueError:
            return False

    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "*.csv"))):
        with open(path, newline="", encoding="utf-8-sig") as fh:
            data = list(_csv.DictReader(fh))
        if not data:
            continue
        cols = [c for c in data[0] if c and c.lower() not in INDEX_COLS]
        cells = [r.get(c) for r in data for c in cols]
        filled = sum(1 for v in cells if is_number(v))
        total = len(cells)
        rows.append((os.path.basename(path), filled, total))

    width = max(len(n) for n, _, _ in rows)
    print("\n" + "=" * 70)
    print("RESULTS STATUS - which files still need your numbers")
    print("=" * 70)
    for group, keep in (("NEEDS DATA", lambda f, t: f == 0),
                        ("PARTIAL", lambda f, t: 0 < f < t),
                        ("COMPLETE", lambda f, t: f == t and t > 0)):
        sel = [r for r in rows if keep(r[1], r[2])]
        if not sel:
            continue
        print("\n%s:" % group)
        for name, filled, total in sel:
            bar = "empty" if filled == 0 else "%d/%d values" % (filled, total)
            print("  %-*s  %s" % (width, name, bar))
    print("\nPaste numbers into the files above, then run: python3 make_results.py")
    print("=" * 70)
    return 0


def main():
    argv = sys.argv[1:]
    if "--status" in argv:
        return status()
    verify = "--verify" in argv
    only_tables = "--tables" in argv
    only_figures = "--figures" in argv
    do_tables = not only_figures
    do_figures = not only_tables and not verify

    rc = 0
    if do_tables:
        rc |= run("make_tables.py", ["--verify"] if verify else [])
    if do_figures:
        rc |= run("make_figures.py")

    print("\n" + "=" * 70)
    if verify:
        print("VERIFY COMPLETE - see per-table result above.")
        print("Any FAIL after you have edited a CSV is expected: it is the")
        print("difference between the paper's original number and your new one.")
    else:
        print("BUILD COMPLETE")
        print("  tables/*.tex      -> \\input by manuscript/document.tex")
        print("  figures_out/*.pdf -> picked up via \\graphicspath")
        print("Recompile the manuscript to see the new numbers.")
    print("=" * 70)
    return rc


if __name__ == "__main__":
    sys.exit(main())
