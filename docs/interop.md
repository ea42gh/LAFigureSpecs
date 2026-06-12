# Interop

LAFigureSpecs accepts Julia-style inputs via PythonCall/PyCall.

- Julia Symbols are normalized (e.g., `:tight`).
- Julia arrays are converted to nested Python lists when possible.
- Non-numeric entries may need explicit conversion before passing to Python.

## PythonCall sketch

```julia
using PythonCall
la = pyimport("LAFigureSpecs")
A = [1 2; 3 4]
spec = la.ge_spec(A)
```

If `LAlatex` is available in Julia, you can also ask Python to render the
result of Julia `LAlatex.L_show(...)` directly:

```julia
using PythonCall
la = pyimport("LAFigureSpecs")
svg = la.lshow_svg("A = ", [1 2; 3 4])
```

When called from Python, `lshow_svg(...)` normalizes simple numeric vectors and
matrices before passing them to Julia. In practice that means NumPy arrays and
rectangular nested lists of numbers can be used directly.

See `JULIA_INTEROP.md` in the repo root for concrete usage.
