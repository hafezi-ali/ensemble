# tools/ — project-local LaTeX toolchain

Self-contained Tectonic build. No system TeX installation, no conda
environment, and no network access required.

## Build the manuscript

```bash
tools/build_pdf.sh                 # manuscript/document.tex -> build_pdf/document.pdf
tools/build_pdf.sh document_tier4_highlighted.tex
```

Verified to run under `env -i` (empty environment, conda not on `PATH`) with
zero network downloads.

## Contents

| Path | Size | What |
|---|---|---|
| `tectonic/bin/tectonic` | 19 MB | Tectonic 0.16.9, XeTeX-based engine |
| `tectonic/lib/` | 70 MB | 16 shared libraries (harfbuzz, freetype, fontconfig, icu, openssl, glib) |
| `tectonic/texcache/` | 44 MB | Pre-populated TeX resource bundle — 347 files: `IEEEtran.cls`, `IEEEtran.bst`, Type-1 fonts, format files |
| `build_pdf.sh` | — | Wrapper: sets `XDG_CACHE_HOME`, runs `tectonic -X compile` |

Total ~135 MB.

## Why vendored rather than installed into `venv/`

`venv/` is a Python virtual environment; Tectonic is a compiled Rust binary
with C library dependencies, not a Python package — `pip install tectonic`
fails (`No matching distribution found`). There is no PyPI wheel for it.

Independently, **`venv/` is not writable from this sandbox.** It is owned by
`nobody:nogroup` and the host mount enforces DAC, so even as uid 0 a `chmod`
returns `Operation not permitted`. The same applies to `results/`, `tables/`
and `figures_out/`. Writable: project root, `manuscript/`, `build_pdf/`,
`notes/`, and this `tools/` directory.

The vendored binary relocates cleanly because it is linked with
`RPATH=$ORIGIN/../lib`, so `bin/tectonic` finds `lib/` beside it wherever the
tree is copied. `ldd` reports no unresolved libraries after relocation.

## Python side

`venv/` already satisfies every import in `make_results.py`, `make_tables.py`,
`make_figures.py` and `verify_tables.py` — numpy 2.5.1, pandas 3.0.5,
scipy 1.18.0, matplotlib 3.11.1, scikit-learn 1.9.0. Nothing to add:

```bash
venv/bin/python make_results.py --status
venv/bin/python make_results.py
```

## Caveats

- The TeX bundle is only as complete as the packages `document.tex` currently
  uses. Adding a `\usepackage` not already cached will make Tectonic fetch it
  from `archive.org` on the next build; run once with network access to
  re-populate `texcache/`.
- `tectonic/` is ~135 MB of binaries. Consider a `.gitignore` entry rather
  than committing it, and rebuild on other machines with
  `conda install -c conda-forge tectonic`.
- Build is clean: 20 pages, 0 undefined references, 0 undefined citations.
  The ~160 log warnings are `TU/ptm` font-shape substitutions (harmless);
  3 overfull hboxes remain, the largest 53 pt.
