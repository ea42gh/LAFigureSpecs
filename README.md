# LAFigureSpecs

[![CI](https://github.com/ea42gh/LAFigureSpecs/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/ea42gh/LAFigureSpecs/actions/workflows/ci.yml)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ea42gh/LAFigureSpecs/master?labpath=LAFigureSpecs_demo.ipynb)
[![Docs](https://img.shields.io/badge/docs-live-blue.svg)](https://ea42gh.github.io/LAFigureSpecs/)

`LAFigureSpecs` is the algorithm layer for linear-algebra teaching figures. It
computes Gaussian-elimination traces, back-substitution fragments, QR layouts,
eigenproblem tables, and SVD tables, then hands explicit layout specs to
[`matrixlayout`](https://github.com/ea42gh/matrixlayout) for rendering.

The package is intended for notebooks and course material where the displayed
figure should follow the actual linear algebra computation.

## Top-Level Use Functions

Canonical cross-language names:

- render helpers: `ge_svg`, `qr_svg`, `qr_figure`
- bundle helpers: `ge_bundle`, `qr_bundle`, `eig_bundle`, `svd_bundle`
- workflow/display helpers on `ShowGE` objects:
  `ref`, `show_layout`, `show_system`, `show_backsubstitution`,
  `show_solution`, `rhs_block`, `solutions`

The older `_tbl` bundle names and historical QR/GE convenience names remain
available for compatibility, but the names above are the preferred top-level
surface for parity with `LATeachingSuite`.

| Area | Function | Output |
|---|---|---|
| GE | `ge(...)` / `ge_svg(...)` | Rendered SVG for a row-reduction layout. |
| GE | `show_ge(...)` / `ShowGE` | Notebook-friendly row-reduction workflow/display helpers. |
| GE | `show_layout(show)` / `show_system(show)` / `show_solution(show)` | Top-level workflow/display wrappers over `ShowGE` methods. |
| GE | `ge_tbl_spec(...)` | Reusable spec dictionary for a GE layout. |
| GE | `ge_tbl_tex(...)` | TeX source for a GE layout. |
| GE | `ge_tbl_svg(...)` | Rendered SVG for a GE layout. |
| GE | `ge_bundle(...)` / `ge_tbl_bundle(...)` | `spec`, `tex`, optional `svg`, and render status in one object. |
| QR | `gram_schmidt_qr(...)` / `qr_figure(...)` | Computes and renders a Gram-Schmidt/QR layout as SVG. |
| QR | `qr(...)` / `qr_svg(...)` | Renders a precomputed QR matrix stack as SVG. |
| QR | `qr_tbl_spec(...)` | Reusable spec dictionary for a QR layout. |
| QR | `qr_tbl_tex(...)` | TeX source for a QR layout. |
| QR | `qr_tbl_svg(...)` | Rendered SVG for a QR layout. |
| QR | `qr_bundle(...)` / `qr_tbl_bundle(...)` | `spec`, `tex`, optional `svg`, and render status in one object. |
| Eigen | `eigendecomposition(...)` | Structured eigenvalue/eigenvector data. |
| Eigen | `eig_tbl_spec(...)` | Reusable spec dictionary for an eigen layout. |
| Eigen | `eig_tbl_tex(...)` | TeX source for an eigen layout. |
| Eigen | `eig_tbl_svg(...)` | Rendered SVG for an eigen layout. |
| Eigen | `eig_bundle(...)` / `eig_tbl_bundle(...)` | `spec`, `tex`, optional `svg`, and render status in one object. |
| SVD | `svd_bundle(...)` / `svd_tbl_bundle(...)` | `spec`, `tex`, optional `svg`, and render status in one object. |

## Try It

Open the Binder demo:

https://mybinder.org/v2/gh/ea42gh/LAFigureSpecs/master?labpath=LAFigureSpecs_demo.ipynb

The demo renders examples for row reduction, systems with right-hand sides,
back-substitution helpers, Gram-Schmidt/QR, eigenproblem tables, and SVD tables.

## Install

For local development:

```bash
python -m pip install -e .[dev]
```

Rendering SVG figures also requires the `render` dependencies and a TeX/SVG
toolchain:

```bash
python -m pip install -e .[render]
```

Binder uses the pinned `jupyter-tikz` version in `binder/requirements.txt` so
notebook rendering stays aligned with the tested toolchain.

## Quick Example

```python
import sympy as sym
import LAFigureSpecs as lf

A = sym.Matrix([[1, 2], [1, 2], [3, 4]])
spec = lf.ge_tbl_spec(A, gj=False)
svg = lf.render_ge_svg(**spec)
```

For one-call rendering:

```python
A = sym.Matrix([[2, 1], [0, 3]])
svg = lf.eig_tbl_svg(A)
```

## Decorators

The convenience wrappers pass decorator specs through to `matrixlayout`. Use
selector helpers from `matrixlayout.formatting` (or re-exported via
`LAFigureSpecs`) to target entries or vector rows.

## Rendering Helpers

`LAFigureSpecs` also exposes generic helpers for rendering standalone LaTeX
fragments or full LaTeX documents to SVG:

```python
svg = lf.latex_svg(r"$A x = b$")
```

Pass `tex_packages="..."` when the fragment uses another installed LaTeX
package:

```python
svg = lf.latex_svg(
    r'\begin{tikzcd} V \arrow[r, "T"] & W \end{tikzcd}',
    tex_packages="amsmath,amssymb,tikz-cd",
)
```

## Julia interop

See `../JULIA_INTEROP.md` for PyCall/PythonCall usage patterns and a small
Julia façade module that re-exports the Python convenience wrappers under the
same top-level function names.

## Documentation

MkDocs configuration lives in `LAFigureSpecs/mkdocs.yml` with content under
`LAFigureSpecs/docs/`.

Build the docs:

```bash
cd LAFigureSpecs
mkdocs build
```
