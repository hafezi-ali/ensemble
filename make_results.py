#!/usr/bin/env python3
"""One command to rebuild every table and figure in the manuscript from results/*.csv.

    python3 make_results.py            # rebuild everything
    python3 make_results.py --verify   # check the tables still match the paper
    python3 make_results.py --tables   # tables only
    python3 make_results.py --figures  # figures only

WORKFLOW
--------
1. Paste new numbers from Colab into the relevant file in results/ (one CSV per
   table or figure; see RESULTS_WORKFLOW.md for which file drives what).
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


def main():
    argv = sys.argv[1:]
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
