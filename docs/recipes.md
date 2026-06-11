# Spec Recipes

Compact examples for common tasks. Specs are passed directly to matrixlayout
renderers (e.g., `render_ge_svg`, `render_qr_svg`). You can also pass extra
row/column labels via `annotations` and matrix arrow labels via `callouts` to
the matrixlayout QR/GE renderers.
Use specs when you want consistent layout across TeX and SVG; use renderers when
you only need the final output.

Decision table:

```
Goal                          | Use                                    | Notes
------------------------------|----------------------------------------|------------------------------
Reuse a spec for TeX + SVG     | LAFigureSpecs.*_spec + matrixlayout.*_svg | Stable layout across outputs
Quick render, no extra edits   | LAFigureSpecs.*_svg wrappers              | Shortest path
Custom row/column labels       | matrixlayout.*_svg with annotations       | Avoid manual label rows/cols
Custom matrix arrow labels     | matrixlayout.*_svg with callouts          | Attach labels to matrix blocks
```

Note: all SVG renderers accept `render_opts`, which is forwarded to
`jupyter_tikz.render_svg` (e.g., `crop`, `padding`, `toolchain_name`, `frame`).
Explicit kwargs override keys in `render_opts`. The wrappers resolve
`output_dir`/`tmp_dir` once before rendering, with `output_dir` preferred for
new code and `tmp_dir` kept for compatibility.

## GE with pivots

```python
import sympy as sym
import LAFigureSpecs

A = sym.Matrix([[1, 2], [3, 4]])
spec = LAFigureSpecs.ge_tbl_spec(A, show_pivots=True)
```

## GE trace to SVG

```python
import sympy as sym
from LAFigureSpecs import ge_trace, ge_tbl_spec
from matrixlayout.ge import render_ge_svg

A = sym.Matrix([[2, 1], [4, 3]])
trace = ge_trace(A, show_pivots=True)
spec = ge_tbl_spec(A, trace=trace)
svg = render_ge_svg(spec=spec)
```

## QR with labels

```python
import sympy as sym
import LAFigureSpecs

A = sym.Matrix([[1, 2], [3, 4]])
W = sym.eye(2)
spec = LAFigureSpecs.qr_tbl_spec(A, array_names=True)
```

## QR with custom annotations

```python
import sympy as sym
from LAFigureSpecs import qr_tbl_spec
from matrixlayout.qr import render_qr_svg

A = sym.Matrix([[1, 2], [3, 4]])
W = sym.eye(2)
spec = qr_tbl_spec(A)
annotations = [{"grid": (0, 2), "side": "above", "labels": ["x_1", "x_2"]}]
svg = render_qr_svg(spec=spec, annotations=annotations)
```

## QR with custom callouts

```python
import sympy as sym
from LAFigureSpecs import qr_tbl_spec
from matrixlayout.qr import render_qr_svg

A = sym.Matrix([[1, 2], [3, 4]])
spec = qr_tbl_spec(A, array_names=False)
callouts = [{"grid": (0, 2), "label": r"$A$", "side": "right"}]
svg = render_qr_svg(spec=spec, callouts=callouts)
```

## Eigen/SVD

```python
import sympy as sym
import LAFigureSpecs

A = sym.Matrix([[2, 0], [0, 3]])
eig_spec = LAFigureSpecs.eig_tbl_spec(A)
Λ, V = LAFigureSpecs.eig_matrices_from_spec(eig_spec)
svd_spec = LAFigureSpecs.svd_tbl_spec(A)
U, Σ, V, rank = LAFigureSpecs.svd_matrices_from_spec(svd_spec)
```

## Backsubstitution blocks

```python
import sympy as sym
from LAFigureSpecs import linear_system_tex, backsubstitution_tex, standard_solution_tex
from matrixlayout.backsubst import backsubst_tex, backsubst_svg

A = sym.Matrix([[1, 0, sym.pi], [0, 1, 1]])
b = sym.Matrix([1, 2])

system_txt = linear_system_tex(A, b)
cascade_txt = backsubstitution_tex(A, b)
solution_txt = standard_solution_tex(A, b)

tex = backsubst_tex(
    system_txt=system_txt,
    cascade_txt=cascade_txt,
    solution_txt=solution_txt,
)
svg = backsubst_svg(
    system_txt=system_txt,
    cascade_txt=cascade_txt,
    solution_txt=solution_txt,
)
```

Minimal (no SymPy) example:

```python
from LAFigureSpecs import linear_system_tex, backsubstitution_tex, standard_solution_tex
from matrixlayout.backsubst import backsubst_tex

A = [[1, 0, 1], [0, 1, 1]]
b = [1, 2]

tex = backsubst_tex(
    system_txt=linear_system_tex(A, b),
    cascade_txt=backsubstitution_tex(A, b),
    solution_txt=standard_solution_tex(A, b),
)
```

Debug tip:
use `matrixlayout.ge.render_ge_tex` (or `render_qr_tex`) to inspect TeX when layout is off.
