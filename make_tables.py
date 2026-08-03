#!/usr/bin/env python3
"""Regenerate the manuscript's table floats from the hand-editable CSVs in results/.

DESIGN: TEMPLATE SUBSTITUTION, NOT RECONSTRUCTION.
--------------------------------------------------
Earlier attempts rebuilt each float's LaTeX from scratch and kept silently losing
things the paper depends on: \\cite keys, caption whitespace, \\hline structure,
bold placement, math-vs-text mode. So this renderer does the opposite.

For every table it takes the ORIGINAL float out of the manuscript verbatim, finds
only the cells that are pure numbers, and replaces those - and nothing else. Every
other byte (caption, \\label, column spec, \\hline pattern, \\cite keys, row labels
such as "DDEL-GMM (ours)" and "Single SVM (converged)", \\setlength, whitespace)
is carried through untouched, because it is never regenerated.

Consequences that matter:
  * A \\cite key cannot be dropped - it lives in a label cell we never rewrite.
  * "(ours)" cannot vanish - same reason. The CSV keeps a clean identifier column.
  * \\mathbf can never leak into a text-mode cell: each cell records whether the
    original wrapped its number in $...$, and bold uses \\mathbf only there,
    \\textbf otherwise.
  * Precision is preserved per cell: the original "$0.9800$" records 4 decimals, so
    a CSV value of 0.98 still renders as 0.9800, and "530" stays "0.530".
  * "+0.0018" records a forced sign; "62\\,015" records a thousands separator.

VERIFICATION (verify_tables.py, or --verify here) renders each table from the CSV
and compares it BYTE-FOR-BYTE against the original float. Because the CSVs were
transcribed from the paper, a faithful renderer must reproduce the paper exactly.
Any byte of difference is a real defect or a real data discrepancy - not a
formatting opinion.

Usage:
    python3 make_tables.py            # write tables/*.tex
    python3 make_tables.py --verify   # byte-for-byte round trip against document.tex
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "tables")

# The manuscript is the source of the templates. Prefer the pristine backup so that
# rewiring document.tex to \input these files can never feed the renderer its own
# output (which would let drift compound silently).
def _template_candidates():
    """Pristine backup first, live manuscript only as a fallback.

    Once document.tex \\inputs tables/*.tex its floats are gone, so the templates
    MUST come from the untouched backup. The backup carries a date suffix
    (document_ORIGINAL_YYYYMMDD.tex); take the newest one.
    """
    import glob
    backups = sorted(glob.glob(os.path.join(
        ROOT, "manuscript", "original_backup", "document_ORIGINAL*.tex")))
    return list(reversed(backups)) + [os.path.join(ROOT, "manuscript", "document.tex")]


TEMPLATE_SOURCES = _template_candidates()

# ---------------------------------------------------------------------------
# Per-table contract.
#   csv      : hand-editable file in results/
#   col_map  : one entry per tabular COLUMN, in order. A column name means "this
#              column's numeric cells come from that CSV field". None means "never
#              touch this column" - label columns, \cite cells, text cells.
#   bold     : csv field -> policy. 'max'/'min' bold the best value in the column
#              (merit direction stated explicitly - never inferred). ('row', key)
#              bolds the row whose first identifier equals key, i.e. the paper's
#              "selected operating point". Absent field = never bold.
#   row_key  : CSV field identifying a row, used to keep CSV rows and template rows
#              aligned and to report misalignment instead of scrambling cells.
# ---------------------------------------------------------------------------
SPECS = {
    "selection_rule": {
        "csv": "table_selection_rule.csv",
        "col_map": ["phi", "f1_distance", "f1_responsibility",
                    "disagreement_distance", "disagreement_responsibility", "overlap"],
        "bold": {"f1_distance": ("row", "0.5")},
        "row_key": "phi",
    },
    "ensemble_comparison": {
        "csv": "table_ensemble_comparison.csv",
        "col_map": [None, None, "mean_score", "std_score", "max_score"],
        "bold": {},
        "row_key": None,
    },
    "diversity_cost": {
        "csv": "table_diversity_cost.csv",
        "col_map": ["phi", "overlap", "disagreement", "oracle",
                    "macro_f1", "delta_single", "fit_seconds"],
        "bold": {"macro_f1": ("row", "0.5")},
        "row_key": "phi",
    },
    "sota_comparison": {
        "csv": "table_sota_comparison.csv",
        "col_map": [None, "accuracy", "mean_f_score", "auc", "rank",
                    "p_value", "time_seconds"],
        # The paper bolds the winner in the four merit columns only. p and time are
        # deliberately unbolded there - do not "improve" this.
        "bold": {"accuracy": "max", "mean_f_score": "max", "auc": "max", "rank": "min"},
        "row_key": "method",
    },
    "clustering_ablation": {
        "csv": "table_clustering_ablation.csv",
        "col_map": [None, None, "accuracy", "mean_f_score", "auc", "rank",
                    "covariance_params", "ari"],
        "bold": {"accuracy": "max", "mean_f_score": "max", "auc": "max",
                 "rank": "min", "covariance_params": "min", "ari": "max"},
        "row_key": "variant",
    },
    "noclustering": {
        "csv": "table_noclustering.csv",
        "col_map": [None, "accuracy", "mean_f_score", "std_dev", "auc", "rank",
                    "p_value", "time_seconds"],
        "bold": {"accuracy": "max", "mean_f_score": "max", "std_dev": "min",
                 "auc": "max", "rank": "min", "time_seconds": "min"},
        "row_key": "method",
    },
}

RULE_RE = re.compile(r"^(?:\s*(?:\\hline|\\cline\{[^}]*\}|\\midrule|\\toprule|\\bottomrule)\s*)+")
NUM_RE = re.compile(r"^([+-]?)(\d+)(?:\.(\d+))?$")


# ---------------------------------------------------------------------------
# Cell parsing: recognise a cell that is PURELY a number (optionally wrapped in
# math mode and/or a bold command). Anything else - "---", "lr", "META-DES
# \cite{...}", "\multicolumn{2}{c}{Macro $F_1$}" - returns None and is preserved.
# ---------------------------------------------------------------------------
def parse_numeric_cell(cell):
    s = cell.strip()
    if not s:
        return None
    math = s.startswith("$") and s.endswith("$") and len(s) > 2
    if math:
        s = s[1:-1].strip()
    bold = None
    m = re.fullmatch(r"\\(mathbf|textbf)\{(.*)\}", s, re.S)
    if m:
        bold, s = m.group(1), m.group(2).strip()
        if not math and s.startswith("$") and s.endswith("$"):
            math, s = True, s[1:-1].strip()
    raw = s
    flat = raw.replace("\\,", "").replace("\\ ", "").replace(",", "").replace("~", "")
    m2 = NUM_RE.fullmatch(flat)
    if not m2:
        return None
    return {
        "math": math,
        "bold": bold,
        "force_sign": m2.group(1) == "+",
        "decimals": len(m2.group(3) or ""),
        "thousands": "\\," in raw,
        "value": float(flat),
    }


def format_value(value, fmt, bold):
    """Render a number using the formatting recorded from the original cell."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    txt = f"{v:.{fmt['decimals']}f}"
    if fmt["force_sign"] and not txt.startswith("-"):
        txt = "+" + txt
    if fmt["thousands"]:
        neg = txt.startswith("-") or txt.startswith("+")
        sign, body = (txt[0], txt[1:]) if neg else ("", txt)
        int_part, _, frac = body.partition(".")
        groups = []
        while len(int_part) > 3:
            groups.insert(0, int_part[-3:])
            int_part = int_part[:-3]
        groups.insert(0, int_part)
        body = "\\,".join(groups) + (("." + frac) if frac else "")
        txt = sign + body
    if bold:
        # $...$ cell -> \mathbf (math-mode command). Text cell -> \textbf.
        txt = (f"\\mathbf{{{txt}}}" if fmt["math"] else f"\\textbf{{{txt}}}")
    if fmt["math"]:
        txt = f"${txt}$"
    return txt


# ---------------------------------------------------------------------------
# Template extraction
# ---------------------------------------------------------------------------
def read_template_source():
    for path in TEMPLATE_SOURCES:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                return fh.read(), path
    raise SystemExit("no manuscript source found for templates")


def extract_float(src, label):
    """Return the verbatim text of the float carrying \\label{tab:<label>}."""
    m = re.search(r"\\label\{tab:%s\}" % re.escape(label), src)
    if not m:
        return None
    starts = [mm.start() for mm in re.finditer(r"\\begin\{table\*?\}", src) if mm.start() < m.start()]
    if not starts:
        return None
    start = starts[-1]
    end_m = re.search(r"\\end\{table\*?\}", src[m.end():])
    if not end_m:
        return None
    return src[start:m.end() + end_m.end()]


def split_rows(body):
    """Split a tabular body on '\\\\' row terminators, keeping the terminators."""
    return re.split(r"(\\\\)", body)


def build_template(float_text, spec):
    """Locate the data rows and record a formatting spec for each numeric cell.

    Returns (template_text, cellmap) where template_text has «r,c» placeholders and
    cellmap[(r, col_name)] is the formatting recorded from the paper's own cell.
    """
    tab_m = re.search(r"(\\begin\{tabular\}\{[^}]*\})(.*?)(\\end\{tabular\})", float_text, re.S)
    if not tab_m:
        raise ValueError("no tabular found")
    body = tab_m.group(2)
    col_map = spec["col_map"]
    ncols = len(col_map)

    parts = split_rows(body)
    cellmap = {}
    out_parts = []
    data_row = 0
    for part in parts:
        if part == "\\\\":
            out_parts.append(part)
            continue
        cells = part.split("&")
        if len(cells) != ncols:
            out_parts.append(part)          # header, rule-only or structural row
            continue
        # A data row must have at least one purely-numeric cell in a mapped column.
        parsed = {}
        for ci, cell in enumerate(cells):
            if col_map[ci] is None:
                continue
            probe = cell
            if ci == 0:
                probe = RULE_RE.sub("", cell)
            info = parse_numeric_cell(probe)
            if info:
                parsed[ci] = info
        if not parsed:
            out_parts.append(part)
            continue
        new_cells = list(cells)
        for ci, info in parsed.items():
            name = col_map[ci]
            cellmap[(data_row, name)] = info
            token = "\u00ab%d,%s\u00bb" % (data_row, name)
            if ci == 0:
                prefix = RULE_RE.match(cells[ci])
                pre = prefix.group(0) if prefix else ""
                rest = cells[ci][len(pre):]
                new_cells[ci] = pre + rest.replace(rest.strip(), token, 1)
            else:
                original = cells[ci]
                new_cells[ci] = original.replace(original.strip(), token, 1)
        out_parts.append("&".join(new_cells))
        data_row += 1

    new_body = "".join(out_parts)
    template = float_text[:tab_m.start(2)] + new_body + float_text[tab_m.end(2):]
    return template, cellmap, data_row


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(
            (ln for ln in fh if not ln.lstrip().startswith("#")))]
    return rows


def numeric(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def bold_targets(rows, spec):
    """Decide which (row, field) cells get bold, from declared policy only."""
    targets = set()
    for field, policy in spec["bold"].items():
        vals = [(i, float(r[field])) for i, r in enumerate(rows)
                if field in r and numeric(r.get(field))]
        if not vals:
            continue
        if policy == "max":
            best = max(v for _, v in vals)
        elif policy == "min":
            best = min(v for _, v in vals)
        elif isinstance(policy, tuple) and policy[0] == "row":
            key_field = spec["row_key"]
            for i, r in enumerate(rows):
                if key_field and str(float(r[key_field])) == str(float(policy[1])) \
                        if numeric(r.get(key_field)) else False:
                    targets.add((i, field))
            continue
        else:
            continue
        for i, v in vals:
            if v == best:
                targets.add((i, field))
    return targets


def render(label, spec, src, strict=True):
    float_text = extract_float(src, label)
    if float_text is None:
        return None, ["no float with \\label{tab:%s} in the manuscript" % label]
    template, cellmap, n_template_rows = build_template(float_text, spec)
    rows = load_csv(os.path.join(RESULTS, spec["csv"]))
    notes = []
    if len(rows) != n_template_rows:
        notes.append("row count differs: CSV has %d, paper float has %d - only the "
                     "first %d rows are rendered (add/remove rows in the float "
                     "template if the table's shape really changed)"
                     % (len(rows), n_template_rows, min(len(rows), n_template_rows)))
    targets = bold_targets(rows, spec)
    out = template
    for (r, name), fmt in cellmap.items():
        token = "\u00ab%d,%s\u00bb" % (r, name)
        if r >= len(rows):
            out = out.replace(token, format_value(fmt["value"], fmt, fmt["bold"] is not None))
            continue
        raw = rows[r].get(name, "")
        txt = format_value(raw, fmt, (r, name) in targets)
        if txt is None:
            # CSV holds a non-number (e.g. "---") where the paper had a number.
            notes.append("row %d field %s: CSV value %r is not numeric" % (r, name, raw))
            txt = raw.strip()
        out = out.replace(token, txt)
    return out, notes


# ---------------------------------------------------------------------------
# Reviewer-requested tables that do not exist in the manuscript yet.
#
# These have no original float to use as a template, so they are built from a
# declared column layout instead. While the CSV is empty each data cell prints
# "---", which is what the paper's own tables use for "not applicable"; as soon
# as you paste numbers in, the same code prints them and bolds the winner.
# ---------------------------------------------------------------------------
SLOTS = {
    "delak_fhdes": {
        "csv": "table_delak_fhdes.csv",
        "caption": ("Direct comparison of DDEL-GMM against DELAK and FH-DES on the HAR "
                    "dataset under an identical $10$-fold stratified protocol. Best value "
                    "in each column in bold; $p$ is the two-sided Wilcoxon signed-rank "
                    "test of DDEL-GMM against each baseline on paired per-fold scores."),
        "label": "tab:delak_fhdes",
        "align": "|l|c|c|c|c|c|c|",
        "headers": ["Method", "Acc.", "Mean F", "AUC", "Rank", "$p$", "Time (s)"],
        "label_cols": ["method"],
        "col_map": ["accuracy", "mean_f_score", "auc", "rank", "p_value", "time_seconds"],
        "fmt": {"accuracy": "%.4f", "mean_f_score": "%.4f", "auc": "%.3f",
                "rank": "%.2f", "p_value": "%.3f", "time_seconds": "%.1f"},
        "bold": {"accuracy": "max", "mean_f_score": "max", "auc": "max", "rank": "min"},
        "own": "DDEL-GMM",
    },
    "nonspherical": {
        "csv": "table_nonspherical.csv",
        "caption": ("GMM against K-means partitioning across synthetic cluster geometries, "
                    "isolating the effect of the clustering model while holding the "
                    "density-based weighting fixed. Best value per geometry in bold."),
        "label": "tab:nonspherical",
        "align": "|l|l|c|c|c|",
        "headers": ["Clustering", "Geometry", "Acc.", "ARI", "Silhouette"],
        "label_cols": ["clustering_type", "data_geometry"],
        "col_map": ["accuracy", "ari", "silhouette"],
        "fmt": {"accuracy": "%.3f", "ari": "%.3f", "silhouette": "%.2f"},
        "bold": {},
        "own": None,
    },
    "bagging_boosting": {
        "csv": "table_bagging_boosting.csv",
        "caption": ("DDEL-GMM against classic bagging and boosting ensembles that build "
                    "committees on the full feature space with no partitioning. Best value "
                    "in each column in bold."),
        "label": "tab:bagging_boosting",
        "align": "|l|l|c|c|c|c|",
        "headers": ["Method", "Learner", "Acc.", "Mean F", "Std Dev", "AUC"],
        "label_cols": ["method", "base_learner"],
        "col_map": ["accuracy", "mean_f_score", "std_dev", "auc"],
        "fmt": {"accuracy": "%.4f", "mean_f_score": "%.4f", "std_dev": "%.4f",
                "auc": "%.3f"},
        "bold": {"accuracy": "max", "mean_f_score": "max", "std_dev": "min", "auc": "max"},
        "own": "DDEL-GMM",
    },
    "case_study": {
        "csv": "table_case_study.csv",
        "caption": ("Real-world medical case study. Best value in each column in bold; "
                    "$p$ is the two-sided Wilcoxon signed-rank test of DDEL-GMM against "
                    "each baseline on paired per-fold scores."),
        "label": "tab:case_study",
        "align": "|l|l|c|c|c|c|c|c|",
        "headers": ["Method", "Dataset", "Acc.", "Mean F", "Sens.", "Spec.", "AUC", "$p$"],
        "label_cols": ["method", "dataset"],
        "col_map": ["accuracy", "mean_f_score", "sensitivity", "specificity",
                    "auc", "p_value"],
        "fmt": {"accuracy": "%.4f", "mean_f_score": "%.4f", "sensitivity": "%.3f",
                "specificity": "%.3f", "auc": "%.3f", "p_value": "%.3f"},
        "bold": {"accuracy": "max", "mean_f_score": "max", "sensitivity": "max",
                 "specificity": "max", "auc": "max"},
        "own": "DDEL-GMM",
    },
}


def slot_value(v):
    """Parse a CSV cell to float, or None when it is blank / not a number.

    NOTE: the module-level numeric() returns a BOOLEAN, not a value. Using it
    here silently turned every empty cell into 0.0000, which would have printed
    fabricated zeros into the reviewer tables. Keep these two separate.
    """
    if v is None:
        return None
    v = str(v).strip()
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def render_slot(name, spec):
    """Build a reviewer-slot table from its CSV; '---' in every empty cell."""
    rows = load_csv(os.path.join(RESULTS, spec["csv"]))
    winners = {}
    for col, direction in spec["bold"].items():
        vals = [(i, slot_value(r.get(col))) for i, r in enumerate(rows)]
        vals = [(i, v) for i, v in vals if v is not None]
        if vals:
            pick = max(vals, key=lambda t: t[1]) if direction == "max" \
                else min(vals, key=lambda t: t[1])
            winners[col] = pick[0]

    out = ["\\begin{table}[htbp]", "\t\\begin{center}",
           "\t\t\\caption{%s}" % spec["caption"],
           "\t\t\\label{%s}" % spec["label"],
           "\t\t\\begin{tabular}{%s}" % spec["align"], "\t\t\t\\hline",
           "\t\t\t%s \\\\" % " & ".join("\\textbf{%s}" % h for h in spec["headers"]),
           "\t\t\t\\hline"]
    n_filled = 0
    for i, r in enumerate(rows):
        cells = []
        for c in spec["label_cols"]:
            lab = (r.get(c) or "").strip()
            if spec["own"] and lab == spec["own"]:
                lab = "\\textbf{%s (ours)}" % lab
            cells.append(lab)
        for c in spec["col_map"]:
            v = slot_value(r.get(c))
            raw = (r.get(c) or "").strip()
            if v is None:
                cells.append(raw if raw else "---")
                continue
            n_filled += 1
            txt = spec["fmt"].get(c, "%.4f") % v
            cells.append("\\textbf{%s}" % txt if winners.get(c) == i else txt)
        out.append("\t\t\t%s \\\\" % " & ".join(cells))
    out += ["\t\t\t\\hline", "\t\t\\end{tabular}", "\t\\end{center}", "\\end{table}"]
    return "\n".join(out) + "\n", n_filled


def main():
    verify = "--verify" in sys.argv
    src, src_path = read_template_source()
    os.makedirs(OUT, exist_ok=True)
    print("templates from: %s" % os.path.relpath(src_path, ROOT))
    failures = 0
    for label, spec in SPECS.items():
        text, notes = render(label, spec, src)
        if text is None:
            print("  %-22s SKIP  %s" % (label, "; ".join(notes)))
            continue
        if verify:
            original = extract_float(src, label)
            ok = (text == original)
            print("  %-22s %s" % (label, "PASS byte-identical" if ok else "FAIL"))
            if not ok:
                failures += 1
                o = original.split("\n")
                n = text.split("\n")
                for i in range(max(len(o), len(n))):
                    a = o[i] if i < len(o) else "<missing>"
                    b = n[i] if i < len(n) else "<missing>"
                    if a != b:
                        print("      paper : %s" % a.strip())
                        print("      render: %s" % b.strip())
        else:
            dest = os.path.join(OUT, "%s.tex" % label)
            with open(dest, "w", encoding="utf-8") as fh:
                fh.write(text if text.endswith("\n") else text + "\n")
            print("  %-22s -> tables/%s.tex" % (label, label))
        for nt in notes:
            print("      note: %s" % nt)
    if not verify:
        print("\nreviewer-requested tables (no manuscript original):")
        for name, spec in SLOTS.items():
            text, n_filled = render_slot(name, spec)
            with open(os.path.join(OUT, "%s.tex" % name), "w", encoding="utf-8") as fh:
                fh.write(text)
            state = "%d values" % n_filled if n_filled else "EMPTY - fill results/%s" % spec["csv"]
            print("  %-22s -> tables/%s.tex  (%s)" % (name, name, state))

    if verify:
        print("\n%d of %d tables differ from the manuscript"
              % (failures, len(SPECS)))
    return 1 if (verify and failures) else 0


if __name__ == "__main__":
    sys.exit(main())
