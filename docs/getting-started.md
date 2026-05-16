# Getting Started

Minimal examples for common entry points. Expected output: spec dictionaries
ready for matrixlayout rendering.

Use high-level wrappers by default:

- `ge_tbl_svg`, `qr_tbl_svg`, `eig_tbl_svg`, `svd_tbl_svg`
- `latex_svg` for standalone LaTeX fragments
- `latex_document_svg` for full LaTeX documents
- `lshow_svg` for Julia `LAlatex.L_show(...)` output

The `render_*` functions are low-level matrixlayout renderer re-exports.

## Bundle contract

All `*_tbl_bundle(...)` helpers return the same keys:

- `spec`: render spec dictionary
- `tex`: rendered TeX source
- `svg`: rendered SVG string or `None` when rendering fails
- `data`: compute-time metadata/results (GE includes trace/decor/layers)
- `render_error`: error text when SVG rendering fails, else `None`

Common defaults:

- `ge_tbl_spec`: `pivoting="none"`, `gj=False`, `show_pivots=True`.
- `qr_tbl_spec`: `array_names=True`.
- `eig_tbl_spec`: `normal=False`.

## What is a spec?

A spec is a plain dictionary that describes which matrices to render and which
labels/lines/callouts to attach. You can pass it to `matrixlayout` to emit TeX
or SVG.

```python
import sympy as sym
import la_figures

A = sym.Matrix([[1, 2], [3, 4]])
spec = la_figures.ge_tbl_spec(A)
# spec["decorations"] includes RHS separators (if present) as vline specs.
# spec["matrices"] holds the matrix grid
# pass extra label/callout targets with annotations=...
```

## GE spec

```python
import sympy as sym
import la_figures

A = sym.Matrix([[1, 2], [3, 4]])
spec = la_figures.ge_tbl_spec(A)
```

Minimal render from a spec:

```python
from matrixlayout.ge import render_ge_svg

svg = render_ge_svg(spec=spec)
```

## Stateful GE helper (ShowGE)

```python
import sympy as sym
import la_figures as lf

A = sym.Matrix([[1, 2], [3, 4]])
b = sym.Matrix([[5], [6]])

show = lf.ShowGE(A, b, gj=True)
show.ref(pivoting="partial")
show.show_layout()
show.show_backsubstitution()
show.show_solution()
rhs = show.rhs_block()
```

By default, la_figures renders to a subdirectory under `/tmp/la` unless you
pass `output_dir` or `tmp_dir`.

If the system is inconsistent, `ShowGE` marks the offending RHS columns with a
red **×** in the variable-summary row, `show_backsubstitution()` reduces the
cascade to `0 = rhs` with **No Solution**, and `show_solution()` returns an
empty list.

## QR spec

```python
import sympy as sym
import la_figures

A = sym.Matrix([[1, 2], [3, 4]])
spec = la_figures.qr_tbl_spec(A)
```

## QR end-to-end render

```python
import sympy as sym
from la_figures import qr_tbl_spec
from matrixlayout.qr import render_qr_svg

A = sym.Matrix([[1, 2], [3, 4]])
spec = qr_tbl_spec(A)
svg = render_qr_svg(spec=spec)
```

## Eigen/SVD specs

```python
import sympy as sym
import la_figures

A = sym.Matrix([[4, 2], [0, 9]])
eig_spec = la_figures.eig_tbl_spec(A)
Λ, V = la_figures.eig_matrices_from_spec(eig_spec)
svd_spec = la_figures.svd_tbl_spec(A)
U, Σ, V, rank = la_figures.svd_matrices_from_spec(svd_spec)
```

## Backsubstitution blocks

```python
from la_figures import linear_system_tex, backsubstitution_tex, standard_solution_tex
from matrixlayout.backsubst import backsubst_svg

A = [[1, 0, 1], [0, 1, 1]]
b = [1, 2]

svg = backsubst_svg(
    system_txt=linear_system_tex(A, b),
    cascade_txt=backsubstitution_tex(A, b),
    solution_txt=standard_solution_tex(A, b),
)
```

## Generic LaTeX to SVG

For a standalone fragment that is not tied to GE/QR/EIG/SVD specs:

```python
import la_figures

svg = la_figures.latex_svg(
    r"$A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}$",
    crop="tight",
    padding=(2, 2, 2, 2),
    frame=True,
)
```

For an already complete LaTeX document:

```python
import la_figures

doc = r"""
\documentclass{standalone}
\usepackage{amsmath}
\begin{document}
$x^2 + y^2 = 1$
\end{document}
"""

svg = la_figures.latex_document_svg(doc, crop="tight")
```

## End-to-end render

```python
import sympy as sym
import la_figures

A = sym.Matrix([[1, 2], [3, 4]])
svg = la_figures.ge_tbl_svg(A, output_dir="./_out", output_stem="ge_min")
```

### render_opts pass-through

All high-level SVG helpers accept `render_opts`, which is forwarded to
`jupyter_tikz.render_svg`. Explicit kwargs override keys in `render_opts`.
Padding tuples use the order `(left, right, top, bottom)` in SVG units; use
`la_figures.mm_to_px` to convert millimeters.
`output_dir` is the canonical way to persist artifacts; `tmp_dir` is accepted as
a legacy alias.

```python
import sympy as sym
import la_figures

A = sym.Matrix([[1, 2], [3, 4]])
svg = la_figures.ge_tbl_svg(
    A,
    render_opts={
        "toolchain_name": "pdftex_dvisvgm",
        "crop": "tight",
        "padding": (2, 2, 2, 2),
        "frame": True,
    },
)
```

The same render options contract applies to `latex_svg(...)` and
`latex_document_svg(...)`.

## Julia LAlatex bridge

If `juliacall` is installed and the Julia package `LAlatex` is available:

```python
import la_figures

svg = la_figures.lshow_svg(
    "A = ",
    [[1, 2], [3, 4]],
    output_stem="lshow_matrix",
    crop="tight",
    padding=(2, 2, 2, 2),
)
```

Use `lshow_kwargs={...}` to pass Julia keyword arguments to `LAlatex.L_show(...)`.

For numeric Python inputs, `lshow_svg(...)` also normalizes simple vectors and
matrices before calling Julia, so NumPy arrays and rectangular numeric nested
lists work naturally:

```python
import numpy as np
import la_figures

svg = la_figures.lshow_svg(
    "A = ",
    np.array([[1, 2], [3, 4]]),
    crop="tight",
)
```

### Bundle summaries

For a quick status-only view (without dumping SVG/TeX), use `bundle_summary`:

```python
bundle = la_figures.ge_tbl_bundle(A)
print(la_figures.bundle_summary(bundle))
```

### Smoke render helper

If you need a quick toolchain sanity check, run:

```
python render_smoke.py
```

Set `LA_FIGURES_SMOKE_OUT` to control the output directory.

## Troubleshooting

- If SVG rendering fails, call the corresponding `*_tex` wrapper and inspect TeX.
- Use `output_dir` to retain TeX/SVG artifacts for debugging.
- See `matrixlayout/docs/specs.md` for spec keys and examples.
