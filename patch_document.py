#!/usr/bin/env python3
"""Rewire manuscript/document.tex to \\input the generated tables and find generated figures.

Run ONCE:
    python3 patch_document.py            # apply
    python3 patch_document.py --dry-run  # show what would change
    python3 patch_document.py --revert   # restore the pre-patch backup

WHAT IT CHANGES (three things, nothing else)
  1. Each of the six data tables' float bodies is replaced by a single
     \\input{../tables/<name>.tex} line. The generated file currently contains a
     byte-identical copy of the float it replaces, so the compiled PDF is
     unchanged until you edit a CSV.
  2. \\graphicspath{{../figures_out/}{./}} is added after \\usepackage{graphicx},
     so regenerated figures are picked up first and the hand-drawn schematics
     (fig1_pipeline, the two phase diagrams) still resolve from manuscript/.
  3. Nothing else. Prose, captions, references and the bibliography are untouched.

SAFETY
  * A timestamped backup is written next to the file before any edit, on top of
    the pristine copy already in manuscript/original_backup/.
  * Re-running is a no-op: patched floats are detected and skipped.
  * The renderer reads its templates from original_backup/, never from the
    patched document, so the originals can never be lost to compounding edits.
"""
import datetime
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(ROOT, "manuscript", "document.tex")
BACKUP_DIR = os.path.join(ROOT, "manuscript", "original_backup")

TABLES = ["selection_rule", "ensemble_comparison", "diversity_cost",
          "sota_comparison", "clustering_ablation", "noclustering"]

GRAPHICSPATH = "\\graphicspath{{../figures_out/}{./}}"


def extract_float(src, label):
    m = re.search(r"\\label\{tab:%s\}" % re.escape(label), src)
    if not m:
        return None
    starts = [mm.start() for mm in re.finditer(r"\\begin\{table\*?\}", src)
              if mm.start() < m.start()]
    if not starts:
        return None
    end_m = re.search(r"\\end\{table\*?\}", src[m.end():])
    if not end_m:
        return None
    return starts[-1], m.end() + end_m.end()


def main():
    dry = "--dry-run" in sys.argv
    revert = "--revert" in sys.argv

    if revert:
        cands = sorted(f for f in os.listdir(BACKUP_DIR)
                       if f.startswith("document_prepatch_"))
        if not cands:
            print("no pre-patch backup found")
            return 1
        src = os.path.join(BACKUP_DIR, cands[-1])
        shutil.copyfile(src, DOC)
        print("restored document.tex from %s" % cands[-1])
        return 0

    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()
    original = text
    changes = []

    # --- 1. graphicspath -----------------------------------------------------
    if "\\graphicspath" in text:
        changes.append("graphicspath: already present, left alone")
    else:
        m = re.search(r"\\usepackage\{graphicx\}", text)
        if m:
            text = text[:m.end()] + "\n" + GRAPHICSPATH + text[m.end():]
            changes.append("graphicspath: added after \\usepackage{graphicx}")
        else:
            changes.append("graphicspath: NOT ADDED - no \\usepackage{graphicx} found")

    # --- 2. table floats -> \input ------------------------------------------
    for name in TABLES:
        if re.search(r"\\input\{\.\./tables/%s(\.tex)?\}" % re.escape(name), text):
            changes.append("%-22s already \\input - skipped" % name)
            continue
        span = extract_float(text, name)
        if span is None:
            changes.append("%-22s NOT FOUND - skipped" % name)
            continue
        a, b = span
        # Keep the float's own leading indentation so the source stays tidy.
        line_start = text.rfind("\n", 0, a) + 1
        indent = text[line_start:a]
        text = text[:a] + "\\input{../tables/%s.tex}" % name + text[b:]
        changes.append("%-22s float replaced by \\input (%d chars -> %d)"
                       % (name, b - a, len("\\input{../tables/%s.tex}" % name)))
        del indent

    for c in changes:
        print("  " + c)

    if dry:
        print("\n--dry-run: nothing written")
        return 0
    if text == original:
        print("\nno changes needed")
        return 0

    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bpath = os.path.join(BACKUP_DIR, "document_prepatch_%s.tex" % stamp)
    shutil.copyfile(DOC, bpath)
    with open(DOC, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("\nbackup : manuscript/original_backup/%s" % os.path.basename(bpath))
    print("patched: manuscript/document.tex")
    return 0


if __name__ == "__main__":
    sys.exit(main())
