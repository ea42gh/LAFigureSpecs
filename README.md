# la-figures

Linear algebra algorithms, layout specs, and rendering convenience helpers.

This package contains algorithmic traces/specs (e.g., eigen tables, GE traces)
and convenience wrappers that render through `matrixlayout` and `jupyter_tikz`.

It also exposes generic helpers for rendering standalone LaTeX fragments or
full LaTeX documents to SVG.

## Decorators

The convenience wrappers pass decorator specs through to `matrixlayout`. Use
selector helpers from `matrixlayout.formatting` (or re-exported via
`la_figures`) to target entries or vector rows.

## Julia interop

See `../JULIA_INTEROP.md` for PyCall/PythonCall usage patterns and a small
Julia façade module that re-exports the Python convenience wrappers under the
same top-level function names.

## Documentation

MkDocs configuration lives in `la_figures/mkdocs.yml` with content under
`la_figures/docs/`.

Build the docs:

```bash
cd la_figures
mkdocs build
```
