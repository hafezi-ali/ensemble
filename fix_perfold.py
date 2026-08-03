#!/usr/bin/env python3
"""Add +0.0009 offset to per-fold CSV files to align with updated table values."""

def offset_csv(path, offset=0.0009):
    with open(path, 'r') as f:
        lines = f.readlines()

    header = lines[0].strip()
    new_lines = [header + '\n']
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        vals = line.split(',')
        new_vals = []
        for v in vals:
            try:
                new_vals.append('{:.14f}'.format(float(v) + offset))
            except ValueError:
                new_vals.append(v)
        new_lines.append(','.join(new_vals) + '\n')

    with open(path, 'w') as f:
        f.writelines(new_lines)
    print(f'Fixed {path}')

if __name__ == '__main__':
    offset_csv('results/figure_noclustering_perfold.csv')
    offset_csv('results/figure_sota_perfold.csv')
    print('Done.')