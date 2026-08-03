#!/usr/bin/env python3
"""
Table Verification Module - FIXED v4
=====================================

Properly extracts tables with flexible line-range matching.

Usage:
    python verify_tables.py
    python verify_tables.py table_name
"""

import re
import sys
from pathlib import Path
from typing import Dict, Tuple, List


def normalize_cell(cell_text: str) -> str:
    """Normalize cell text for comparison."""
    cell_text = re.sub(r'\$(.+?)\$', r'\1', cell_text)
    cell_text = re.sub(r'\\mathbf\{(.+?)\}', r'\1', cell_text)
    cell_text = re.sub(r'\\textbf\{(.+?)\}', r'\1', cell_text)
    cell_text = re.sub(r'\\cite\{[^}]+\}', '', cell_text)
    cell_text = re.sub(r'\\emph\{(.+?)\}', r'\1', cell_text)
    cell_text = cell_text.replace('\\,', '')
    cell_text = ' '.join(cell_text.split())
    return cell_text.strip()


def extract_data_rows_from_tex(tex_content: str) -> Dict[Tuple[int, int], str]:
    """Extract DATA rows from generated .tex file."""
    cells = {}
    lines = tex_content.split('\n')
    row_idx = 0
    in_tabular = False
    past_first_hline = False
    
    for line in lines:
        if '\\begin{tabular}' in line:
            in_tabular = True
            continue
        if '\\end{tabular}' in line:
            break
        
        if not in_tabular:
            continue
        
        if '\\hline' in line:
            if not past_first_hline:
                past_first_hline = True
            continue
        
        if not ('&' in line and '\\\\' in line):
            continue
        
        if any(x in line for x in ['\\cline', '\\multicolumn']):
            continue
        
        line_clean = line.replace('\\\\', '').strip()
        if not line_clean or line_clean.startswith('%'):
            continue
        
        parts = line_clean.split('&')
        for col_idx, part in enumerate(parts):
            part = normalize_cell(part)
            if part:
                cells[(row_idx, col_idx)] = part
        
        row_idx += 1
    
    return cells


def extract_data_rows_from_doc(doc_tex: str, start_line: int, end_line: int) -> Dict[Tuple[int, int], str]:
    """
    Extract DATA rows from manuscript.
    Flexible: looks for \end{tabular} even if beyond end_line.
    """
    lines = doc_tex.split('\n')
    
    # Start from start_line, search forward until we find \end{tabular}
    search_start = start_line - 1
    search_end = min(start_line + 200, len(lines))  # Look up to 200 lines ahead
    section = lines[search_start:search_end]
    section_text = '\n'.join(section)
    
    # Find the tabular environment using simple string search (more robust)
    begin_idx = section_text.find('\\begin{tabular}')
    end_idx = section_text.find('\\end{tabular}')
    
    if begin_idx < 0 or end_idx < 0:
        return {}
    
    # Extract the tabular content between begin and end
    tabular_start = section_text.find('{', begin_idx) + 1
    tabular_end = section_text.find('}', tabular_start - 1)
    # The colspec is between first { and }
    
    tabular_content = section_text[end_idx:end_idx]
    if end_idx > begin_idx:
        tabular_content = section_text[begin_idx:end_idx + len('\\end{tabular}')]
    else:
        return {}
    
    # Now extract rows from the tabular
    cells = {}
    row_idx = 0
    header_hline_count = 0
    in_header = True
    
    for line in tabular_content.split('\n'):
        line_stripped = line.strip()
        
        if not line_stripped:
            continue
        
        if '\\hline' in line:
            header_hline_count += 1
            if header_hline_count >= 1:
                in_header = False
            continue
        
        if in_header:
            continue
        
        if any(x in line for x in ['\\cline', '\\multicolumn']):
            continue
        
        if not ('&' in line and '\\\\' in line):
            continue
        
        line_clean = line.replace('\\\\', '').strip()
        if not line_clean or line_clean.startswith('%'):
            continue
        
        parts = line_clean.split('&')
        for col_idx, part in enumerate(parts):
            part = normalize_cell(part)
            if part:
                cells[(row_idx, col_idx)] = part
        
        row_idx += 1
    
    return cells


def compare_tables(label: str, start_line: int, end_line: int, doc_tex: str, 
                   generated_tex: str) -> Tuple[bool, List[str]]:
    """Compare generated table against manuscript."""
    doc_cells = extract_data_rows_from_doc(doc_tex, start_line, end_line)
    gen_cells = extract_data_rows_from_tex(generated_tex)
    
    if not doc_cells:
        return False, ["ERROR: Could not extract cells from manuscript"]
    
    if not gen_cells:
        return False, ["ERROR: Could not extract cells from generated table"]
    
    # Compare
    mismatches = []
    all_keys = set(doc_cells.keys()) | set(gen_cells.keys())
    
    for row_idx, col_idx in sorted(all_keys):
        doc_val = doc_cells.get((row_idx, col_idx), '')
        gen_val = gen_cells.get((row_idx, col_idx), '')
        
        if doc_val != gen_val:
            mismatches.append(
                f"Row {row_idx}, Col {col_idx}: manuscript='{doc_val}' / generated='{gen_val}'"
            )
    
    return len(mismatches) == 0, mismatches


TABLE_METADATA = {
    'selection_rule': {'label': 'tab:selection_rule', 'start_line': 280, 'end_line': 303},
    'ensemble_comparison': {'label': 'tab:ensemble_comparison', 'start_line': 397, 'end_line': 447},
    'diversity_cost': {'label': 'tab:diversity_cost', 'start_line': 613, 'end_line': 635},
    'sota_comparison': {'label': 'tab:sota_comparison', 'start_line': 643, 'end_line': 664},
    'clustering_ablation': {'label': 'tab:clustering_ablation', 'start_line': 689, 'end_line': 704},
    'noclustering': {'label': 'tab:noclustering', 'start_line': 731, 'end_line': 756},
}


def main():
    """Main entry point."""
    repo_root = Path('/home/ali/Documents/ensemble')
    tables_dir = repo_root / 'tables'
    doc_tex_path = repo_root / 'manuscript' / 'document.tex'
    
    with open(doc_tex_path) as f:
        doc_tex = f.read()
    
    table_names = [arg for arg in sys.argv[1:]] or list(TABLE_METADATA.keys())
    
    results = []
    
    for table_name in table_names:
        if table_name not in TABLE_METADATA:
            print(f"Warning: Unknown table '{table_name}'")
            continue
        
        meta = TABLE_METADATA[table_name]
        tex_path = tables_dir / f"{meta['label'].replace('tab:', '')}.tex"
        
        if not tex_path.exists():
            print(f"ERROR: Generated table not found: {tex_path}")
            continue
        
        with open(tex_path) as f:
            generated_tex = f.read()
        
        matches, mismatches = compare_tables(
            meta['label'], meta['start_line'], meta['end_line'], doc_tex, generated_tex
        )
        
        status = 'PASS' if matches else 'FAIL'
        print(f"\n{table_name:25s} [{status}]")
        
        if mismatches:
            for mismatch in mismatches[:10]:
                print(f"  {mismatch}")
            if len(mismatches) > 10:
                print(f"  ... and {len(mismatches) - 10} more mismatches")
        
        results.append({'table_name': table_name, 'label': meta['label'], 'status': status, 'mismatches': mismatches})
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    print(f"\n{'='*70}")
    print(f"SUMMARY: {passed}/{total} tables PASS")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
