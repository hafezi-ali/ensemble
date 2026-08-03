# results/ — the numbers that drive the paper

Every CSV here feeds a table, a figure, or both. Edit a file, then run:

```bash
cd ..
python3 make_results.py --status     # what still needs numbers
python3 make_results.py              # rebuild
```

**Full documentation is in [`../docs/`](../docs/README.md):**

- [How to paste your results in](../docs/1-EDITING-RESULTS.md) — start here
- [Which CSV drives which output](../docs/2-CSV-TO-OUTPUT-MAP.md)
- [Column-level schema](../docs/3-CSV-SCHEMA.md) — units, precision, merit direction

Do not rename columns or row labels; the generators match on those exact strings.
Use `---` (not a blank) where a value genuinely does not apply.
