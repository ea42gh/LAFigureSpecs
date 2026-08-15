# Spec Recipes

Compact examples for common LAFigureSpecs tasks. Use the high-level
`*_svg(...)`, `*_tex(...)`, and `*_bundle(...)` helpers for normal workflows;
they compute the linear-algebra data, build the layout spec, and render through
matrixlayout.

Use `*_spec(...)` when you want to inspect or reuse the generated layout data.
For low-level renderer-only options such as arbitrary row/column annotations,
see the matrixlayout documentation.

Decision table:

```
Goal                          | Use                         | Notes
------------------------------|-----------------------------|------------------------------
Quick render                  | LAFigureSpecs.*_svg         | Shortest path
Reuse TeX + SVG layout        | LAFigureSpecs.*_bundle      | Returns spec, TeX, SVG, data
Inspect generated layout      | LAFigureSpecs.*_spec        | Plain dict/spec data
Matrix arrow labels           | callouts=                   | Attach labels to matrix blocks
Entry styling                 | decorators=                 | Callable/structured entry styling
```

Note: SVG helpers accept the shared render options `crop`, `padding`,
`toolchain_name`, `frame`, `output_dir`, and `output_stem`.

## GE with pivots

```python
import sympy as sym
import LAFigureSpecs

A = sym.Matrix([[1, 2], [3, 4]])
svg = LAFigureSpecs.ge_svg(A, show_pivots=True)
```

## GE trace data

```python
import sympy as sym
import LAFigureSpecs

A = sym.Matrix([[2, 1], [4, 3]])
trace = LAFigureSpecs.ge_trace(A, pivoting="none")
layers = LAFigureSpecs.trace_to_layer_matrices(trace)
spec = LAFigureSpecs.ge_spec(A, show_pivots=True)
```

## QR render

```python
import sympy as sym
import LAFigureSpecs

A = sym.Matrix([[1, 2], [3, 4]])
svg = LAFigureSpecs.qr_svg(A)
```

## QR with custom callouts

```python
import sympy as sym
import LAFigureSpecs

A = sym.Matrix([[1, 2], [3, 4]])
callouts = [{"grid": (0, 2), "label": r"$A$", "side": "right"}]
svg = LAFigureSpecs.qr_svg(A, array_names=False, callouts=callouts)
```

## Eigen/SVD

```python
import sympy as sym
import LAFigureSpecs

A = sym.Matrix([[2, 0], [0, 3]])
eig_svg = LAFigureSpecs.eig_svg(A)
svd_svg = LAFigureSpecs.svd_svg(A)

eig_spec = LAFigureSpecs.eig_spec(A)
Λ, V = LAFigureSpecs.eig_matrices_from_spec(eig_spec)

svd_spec = LAFigureSpecs.svd_spec(A)
U, Σ, V, rank = LAFigureSpecs.svd_matrices_from_spec(svd_spec)
```

## Backsubstitution blocks

```python
import sympy as sym
import LAFigureSpecs

A = sym.Matrix([[1, 0, sym.pi], [0, 1, 1]])
b = sym.Matrix([1, 2])

parts = [
    LAFigureSpecs.linear_system_tex(A, b),
    r"\quad\Longleftrightarrow\quad",
    "\n".join(LAFigureSpecs.backsubstitution_tex(A, b)),
    r"\quad",
    LAFigureSpecs.standard_solution_tex(A, b),
]
svg = LAFigureSpecs.latex_svg("$" + "".join(parts) + "$")
```

Debug tip: use `*_tex(...)` or `*_bundle(...)` to inspect generated TeX when a
layout is off.
