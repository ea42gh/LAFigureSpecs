# Overview

LAFigureSpecs implements algorithmic logic and produces layout specs consumed by
*matrixlayout*. It does not render TeX directly unless using the convenience
wrappers that delegate to *matrixlayout* and *jupyter_tikz*.

## Layering

- *LAFigureSpecs*: algorithms and spec construction.
- *matrixlayout*: formatting, layout, TeX emission, SVG rendering.
- *jupyter_tikz*: toolchain execution and SVG conversion.

## Compatibility matrix

| Component | Minimum | Notes |
| --- | --- | --- |
| Python | 3.9 | Tested with 3.9–3.12. |
| SymPy | 1.10 | Required for exact arithmetic. |
| matrixlayout | 0.4 | Spec/render backend. |
| jupyter_tikz | itikz_port | TeX toolchains + SVG. |
| TeX toolchain | TeX Live 2022+ | Needed for SVG rendering. |

## Package boundary

- Use `LAFigureSpecs` when you want algorithmic outputs (traces, specs).
- Use `matrixlayout` when you want layout/rendering of a known spec or matrix grid.
- Use `LAFigureSpecs.latex_svg(...)` when you already have a LaTeX fragment and want
  the same SVG rendering controls (`crop`, `padding`, `frame`, `exact_bbox`)
  used by the table renderers.

## Data flow

Input matrices → algorithm trace → spec dictionary → matrixlayout renderer.

```
matrices -> LAFigureSpecs (trace/spec) -> matrixlayout (tex/svg)
```

Example:

```
A -> ge_spec(A) -> render_ge_svg(spec=spec)
```

For standalone LaTeX fragments:

```
tex body -> LAFigureSpecs.latex_svg(...) -> matrixlayout.render.render_svg(...)
```

## Module map

- GE: `ge_trace`, `ge_spec`, `ge_layout_spec`, `ge_table_svg`.
- QR: `compute_qr_matrices`, `qr_spec`, `qr_table_svg`.
- Eigen/SVD: `eig_spec`, `eig_matrices_from_spec`, `svd_spec`, `svd_matrices_from_spec`.
- Backsubstitution: `linear_system_tex`, `backsubstitution_tex`, `standard_solution_tex`.

## Pitfalls

- QR with rank‑deficient `W` requires `rank_deficient` or `allow_rank_deficient`.
- SVD tables may include zero singular values; set digits to control formatting.

## Common outputs

- `spec` dicts for GE/QR/EIG/SVD.
- `systeme`/`cascade`/solution TeX blocks for backsubstitution.
- SVG strings from algorithmic renderers and generic LaTeX helpers.
