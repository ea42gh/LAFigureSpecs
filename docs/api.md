# API

Key entry points (see module docstrings for details).

Canonical import:

`import LAFigureSpecs`

Use `LAFigureSpecs.*_spec` for algorithm/spec building and `LAFigureSpecs.*_svg` for
rendered output.

Preferred cross-language top-level names:

- `ge_svg`, `qr_svg`, `eig_svg`, `svd_svg`, `qr_figure`
- `ge_spec`, `qr_spec`, `eig_spec`, `svd_spec`
- `ge_tex`, `qr_tex`, `eig_tex`, `svd_tex`
- `ge_bundle`, `qr_bundle`, `eig_bundle`, `svd_bundle`

## Which function should I call?

- If you want compute + render in one call (recommended):
  - `ge_svg`, `qr_svg`, `eig_svg`, `svd_svg`
- If you want compute + inspect intermediates + render:
  - `*_bundle` returns standardized bundle:
    `{"spec", "tex", "svg", "data", "render_error"}`
  - Access GE intermediates via `bundle["data"]["..."]` (not top-level keys).
  - Use `bundle_summary(bundle)` for a quick status-only view.
- If you already have prepared matrices/specs and want low-level renderer control:
  - `render_ge_*`, `render_qr_*`, `render_eig_*` (re-exported matrixlayout functions)
- If you already have LaTeX and just need SVG:
  - `latex_svg` for fragments
  - `latex_document_svg` for complete documents
- If you want to call Julia `LAlatex.L_show(...)` and render the result:
  - `lshow_svg`

## Spec validation

Use these when you want a lightweight preflight before rendering:

- `matrixlayout.validate_ge_spec`, `matrixlayout.validate_qr_spec`

## GE

- `LAFigureSpecs.ge_trace(A, **opts)`: generate a GE trace with pivots and steps. Inputs: matrix-like `A`. Returns: trace dict. Use when you need step-by-step elimination.
- `LAFigureSpecs.trace_to_layer_matrices(trace)`: convert a trace to matrix layers. Inputs: trace dict. Returns: list of grid matrices.
- `LAFigureSpecs.ShowGE(A, b, **opts)`: stateful helper mirroring Julia `ShowGE`. Use `show.ref(gj=..., pivoting=...)` to compute REF/RREF once, then call `show.show_layout()`, `show.show_system()`, `show.show_backsubstitution()`, `show.show_solution(b_col=0)`. Access `show.matrices()`, `show.lhs_matrix(step="final")`, `show.rhs_matrix(step="final")`, `show.rhs_column(b_col=0, step="final")`, `show.rhs_block(step="final", b_col=None)`, `show.particular_solution()`, `show.homogeneous_solution()`, or `show.solve()`. For inconsistent RHS columns, `ShowGE` records `show.rhs_status`, adds a red **×** in the variable-summary row, renders `0 = rhs` in backsubstitution, and returns empty solutions for those columns. When `b` has multiple columns, pass `b_col` to `show_solution(...)` to choose the column to render.
- `LAFigureSpecs.ref(show, ...)`: top-level wrapper for `ShowGE.ref(...)`.
- `LAFigureSpecs.lhs_matrix(show, ...)`: top-level wrapper for `ShowGE.lhs_matrix(...)`.
- `LAFigureSpecs.rhs_matrix(show, ...)`: top-level wrapper for `ShowGE.rhs_matrix(...)`.
- `LAFigureSpecs.rhs_column(show, ...)`: top-level wrapper for `ShowGE.rhs_column(...)`.
- `LAFigureSpecs.show_layout(show, **render_opts)`: top-level wrapper for `ShowGE.show_layout(...)`.
- `LAFigureSpecs.show_system(show, **render_opts)`: top-level wrapper for `ShowGE.show_system(...)`.
- `LAFigureSpecs.show_backsubstitution(show, **render_opts)`: top-level wrapper for `ShowGE.show_backsubstitution(...)`.
- `LAFigureSpecs.show_solution(show, *, b_col=None, **render_opts)`: top-level wrapper for `ShowGE.show_solution(...)`.
- `LAFigureSpecs.rhs_block(show, ...)`: top-level wrapper for `ShowGE.rhs_block(...)`.
- `LAFigureSpecs.solutions(show, ...)`: returns `(particular, homogeneous)` from `ShowGE.solve(...)`, matching the Julia umbrella shape.
- `LAFigureSpecs.ge_spec(A, **opts)`: build a GE spec for matrixlayout. Inputs: matrix-like `A`. Returns: spec dict.
- `LAFigureSpecs.ge_layout_spec(A, **opts)`: build a typed `GEGridSpec` layout spec. Inputs: matrix-like `A`. Returns: typed spec.
- `LAFigureSpecs.ge_bundle(A, **opts)`: canonical GE bundle helper.
- `LAFigureSpecs.ge_tex(A, **opts)`: render GE TeX from the spec path.
- `LAFigureSpecs.ge_table_svg(A, **opts)`: render GE SVG from the spec path.
- `LAFigureSpecs.ge_svg(matrices, **opts)`: canonical GE stack renderer.
- `LAFigureSpecs.ge(matrices, **opts)`: historical alias for `ge_svg(...)`.

Example options:
`ge_spec(A, show_pivots=True, pivoting="partial", gj=False)`

## QR

- `LAFigureSpecs.compute_qr_matrices(A)`: compute the QR matrix grid. Returns: list of grid matrices. Computed internally via naive Gram-Schmidt (LCD-scaled, no normalization).
- `LAFigureSpecs.gram_schmidt_qr_matrices(A, **opts)`: compute QR grid with rank-deficient handling. Returns: list of grid matrices.
- `LAFigureSpecs.qr_spec(A, **opts)`: build a QR spec for matrixlayout. Returns: spec dict.
- `LAFigureSpecs.qr_layout_spec(A, **opts)`: build a typed QR layout spec. Returns: typed spec.
- `LAFigureSpecs.qr_matrices_from_grid(mats)`: extract `(A, W, WtA, WtW, S, Qt, Q, R)` from the QR grid.
  Returns a dict-like object; access via `qr["Q"]`, `qr.as_tuple()`, or `qr.as_dict()`.
- `LAFigureSpecs.qr_matrices_dict_from_grid(mats)`: same as above, but returns a plain dict.
- `LAFigureSpecs.qr_tex(A, **opts)`: render QR TeX from the spec path.
- `LAFigureSpecs.qr_table_svg(A, **opts)`: render QR SVG from the spec path.
- `LAFigureSpecs.qr_bundle(A, **opts)`: canonical QR bundle helper.
- `LAFigureSpecs.qr_svg(matrices, **opts)`: canonical QR SVG renderer for a precomputed matrix stack.
- `LAFigureSpecs.qr(matrices, **opts)`: historical alias for `qr_svg(...)`.
- `LAFigureSpecs.qr_figure(A, **opts)`: canonical compute+render QR helper.
- `LAFigureSpecs.gram_schmidt_qr(A, **opts)`: historical alias for `qr_figure(...)`.

Example options:
`qr_spec(A, array_names=True)`

Rank-deficient Gram-Schmidt construction is controlled by the algorithm-facing
entry points, for example:
`gram_schmidt_qr(A, array_names=True, rank_deficient="drop")`

## Eigen/SVD

- `LAFigureSpecs.eig_spec(A, **opts)`: build eigenproblem table specs. Returns: spec dict.
- `LAFigureSpecs.eig_matrices_from_spec(spec, orthonormal=True)`: assemble `(Λ, V)` from an eigen spec.
- `LAFigureSpecs.svd_spec(A, **opts)`: build SVD table specs. Returns: spec dict.
- `LAFigureSpecs.svd_spec_from_right_singular_vectors(V, **opts)`: build SVD specs from given vectors. Returns: spec dict.
- `LAFigureSpecs.svd_matrices_from_spec(spec, reduced=True)`: assemble `(U, Σ, V, rank)` from an SVD spec.
- `LAFigureSpecs.eig_tex(A, **opts)`: render eigen table TeX.
- `LAFigureSpecs.eig_svg(A, **opts)`: canonical rendered SVG helper for eigen layouts.
- `LAFigureSpecs.eig_bundle(A, **opts)`: canonical eigen bundle helper.
- `LAFigureSpecs.svd_tex(A, **opts)`: render SVD table TeX.
- `LAFigureSpecs.svd_svg(A, **opts)`: canonical rendered SVG helper for SVD layouts.
- `LAFigureSpecs.svd_bundle(A, **opts)`: canonical SVD bundle helper.

Selected eig/SVD basis vectors and matrix blocks can factor out a common scalar
for display with `factor_out`. Accepted forms are:

- `True` to enable factoring for every eligible vector row and matrix block
- `False` or `None` to disable it
- a list such as `["evecs", "qvecs", "u", "v"]`
- a per-target mapping such as
  `{"evecs": True, "qvecs": True, "u": True, "v": True, "sigma": False}`

Target ids are:

- `evecs`: displayed ordinary eigenbasis vectors
- `qvecs`: displayed orthonormal basis vectors
- `s`: assembled ordinary eigenbasis matrix
- `q`: assembled orthonormal basis matrix
- `lambda` or `Lambda`: diagonal eigenvalue matrix
- `sigma`: SVD singular-value matrix
- `u`: SVD left singular-vector matrix
- `v`: SVD right singular-vector matrix

Example:

```python
A = sym.Matrix([[4, 9], [0, 2]])
svg = LAFigureSpecs.svd_svg(
    A,
    factor_out={"qvecs": True, "u": True, "v": True, "sigma": False},
)
```

In that example, displayed right singular vectors can factor out common scalar
prefixes, the rendered `U` and `V` matrices factor out common scalar prefixes,
and `\Sigma` stays entrywise.

## Re-exported matrixlayout renderers (advanced)

These are re-exported for convenience and parity with matrixlayout:

- `LAFigureSpecs.render_ge_tex`, `LAFigureSpecs.render_ge_svg`
- `LAFigureSpecs.render_qr_tex`, `LAFigureSpecs.render_qr_svg`
- `LAFigureSpecs.render_eig_tex`, `LAFigureSpecs.render_eig_svg`

Prefer the higher-level LAFigureSpecs wrappers unless you specifically need direct
matrixlayout rendering entry points.

## Generic LaTeX rendering

- `LAFigureSpecs.latex_svg(tex_body, **opts)`: wrap a LaTeX fragment with
  `jupyter_tikz.TexFragment` and render SVG through `matrixlayout`.
- `LAFigureSpecs.latex_document_svg(tex_document, **opts)`: render a full LaTeX
  document directly.
- `LAFigureSpecs.lshow_svg(*args, lshow_kwargs=None, **opts)`: call Julia
  `LAlatex.L_show(...)` via `juliacall` and render the returned LaTeX.
  Simple numeric Python vectors/matrices are normalized before calling Julia.

Shared render options:

- `toolchain_name`
- `crop`
- `padding`
- `frame`
- `exact_bbox`
- `output_dir`
- `output_stem`
- `render_opts`

The SVG wrappers resolve `output_dir` once and then merge the shared render
options; explicit keyword arguments win over values in `render_opts`.
Use `output_dir` for all new code.

Fragment-specific options on `latex_svg(...)`:

- `preamble`
- `tex_packages`
- `tikz_libraries`
- `pgfplots_libraries`
- `no_tikz`
- `scale`
- `no_jinja`

`latex_svg(...)` defaults to the packages used by LAFigureSpecs fragments:
`amsmath`, `amssymb`, `mathtools`, `xcolor`, `systeme`, `cascade`, and
`nicematrix`. Pass `tex_packages="..."` to use a different package set, for
example `tex_packages="amsmath,amssymb,tikz-cd"`.

For `tikz-cd`, prefer `latex_document_svg(...)` with a PDF-based SVG converter
such as `toolchain_name="pdftex_pdftocairo"` instead of the fragment path on a
DVI-based toolchain.

Passing `preamble=...` selects the explicit-preamble path and bypasses
`tex_packages`, `tikz_libraries`, and the default package list. Include every
needed package in the preamble when using that mode.

Because fragments are scaled with `\scalebox{...}{...}`, environments that use
alignment markers may need package-specific escaping. In `tikz-cd`, prefer
`ampersand replacement=\&` over raw `&`.

See `docs/notebooks/13_latex_fragment_rendering.ipynb` for examples.

## Backsubstitution

- `LAFigureSpecs.linear_system_tex(A, b, **opts)`: build a `systeme` block for a linear system. Returns: TeX string.
- `LAFigureSpecs.backsubstitution_tex(A, b, **opts)`: build cascade lines for back-substitution. Returns: list of `\\ShortCascade` lines.
- `LAFigureSpecs.standard_solution_tex(A, b, **opts)`: build a standard-form solution block. Returns: TeX string.

Example return snippet:
`linear_system_tex(A, b)` returns a `\\systeme{...}` string.
