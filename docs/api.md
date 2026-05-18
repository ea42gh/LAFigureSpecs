# API

Key entry points (see module docstrings for details).

Canonical import:

`import LAFigureSpecs`

Use `LAFigureSpecs.*_spec` for algorithm/spec building and `LAFigureSpecs.*_svg` for
rendered output.

Preferred cross-language top-level names:

- `ge_svg`, `qr_svg`, `qr_figure`
- `ge_bundle`, `qr_bundle`, `eig_bundle`, `svd_bundle`

The older `_tbl` bundle names remain available for compatibility.

## Which function should I call?

- If you want compute + render in one call (recommended):
  - `ge_svg`, `qr_svg`, `eig_tbl_svg`, `svd_tbl_svg`
- If you want compute + inspect intermediates + render:
  - `*_bundle` / `*_tbl_bundle` (returns standardized bundle:
    `{"spec", "tex", "svg", "data", "render_error"}`)
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
- `LAFigureSpecs.ShowGE(A, b, **opts)`: stateful helper mirroring Julia `ShowGE`. Use `show.ref(gj=..., pivoting=...)` to compute REF/RREF once, then call `show.show_layout()`, `show.show_system()`, `show.show_backsubstitution()`, `show.show_solution()`. Access `show.matrices()`, `show.rhs_block(step="final", b_col=None)`, `show.particular_solution()`, `show.homogeneous_solution()`, or `show.solve()`. For inconsistent RHS columns, `ShowGE` records `show.rhs_status`, adds a red **×** in the variable-summary row, renders `0 = rhs` in backsubstitution, and returns empty solutions for those columns.
- `LAFigureSpecs.ge_tbl_spec(A, **opts)`: build a GE spec for matrixlayout. Inputs: matrix-like `A`. Returns: spec dict.
- `LAFigureSpecs.ge_tbl_layout_spec(A, **opts)`: build a typed `GEGridSpec` layout spec. Inputs: matrix-like `A`. Returns: typed spec.
- `LAFigureSpecs.ge_bundle(A, **opts)`: canonical GE bundle helper.
- `LAFigureSpecs.ge_tbl_bundle(A, **opts)`: compatibility alias returning the same standardized bundle; `data` includes GE intermediates (`trace`, `layers`, `decor`, `typed_layout`).
- `LAFigureSpecs.ge_tbl_tex(A, **opts)`: render GE TeX from the spec path.
- `LAFigureSpecs.ge_tbl_svg(A, **opts)`: render GE SVG from the spec path.
- `LAFigureSpecs.ge_svg(matrices, **opts)`: canonical GE stack renderer.
- `LAFigureSpecs.ge(matrices, **opts)`: compatibility alias for `ge_svg(...)`.

Example options:
`ge_tbl_spec(A, show_pivots=True, pivoting="partial", gj=False)`

## QR

- `LAFigureSpecs.compute_qr_matrices(A)`: compute the QR matrix grid. Returns: list of grid matrices. Computed internally via naive Gram-Schmidt (LCD-scaled, no normalization).
- `LAFigureSpecs.gram_schmidt_qr_matrices(A, **opts)`: compute QR grid with rank-deficient handling. Returns: list of grid matrices.
- `LAFigureSpecs.qr_tbl_spec(A, **opts)`: build a QR spec for matrixlayout. Returns: spec dict.
- `LAFigureSpecs.qr_tbl_layout_spec(A, **opts)`: build a typed QR layout spec. Returns: typed spec.
- `LAFigureSpecs.qr_matrices_from_grid(mats)`: extract `(A, W, WtA, WtW, S, Qt, Q, R)` from the QR grid.
  Returns a dict-like object; access via `qr["Q"]`, `qr.as_tuple()`, or `qr.as_dict()`.
- `LAFigureSpecs.qr_matrices_dict_from_grid(mats)`: same as above, but returns a plain dict.
- `LAFigureSpecs.qr_tbl_tex(A, **opts)`: render QR TeX from the spec path.
- `LAFigureSpecs.qr_tbl_svg(A, **opts)`: render QR SVG from the spec path.
- `LAFigureSpecs.qr_bundle(A, **opts)`: canonical QR bundle helper.
- `LAFigureSpecs.qr_tbl_bundle(A, **opts)`: compatibility alias returning the same standardized bundle.
- `LAFigureSpecs.qr_svg(matrices, **opts)`: canonical QR SVG renderer for a precomputed matrix stack.
- `LAFigureSpecs.qr(matrices, **opts)`: compatibility alias for `qr_svg(...)`.
- `LAFigureSpecs.qr_figure(A, **opts)`: canonical compute+render QR helper.
- `LAFigureSpecs.gram_schmidt_qr(A, **opts)`: compatibility alias for `qr_figure(...)`.

Example options:
`qr_tbl_spec(A, array_names=True, rank_deficient=True)`

## Eigen/SVD

- `LAFigureSpecs.eig_tbl_spec(A, **opts)`: build eigenproblem table specs. Returns: spec dict.
- `LAFigureSpecs.eig_matrices_from_spec(spec, orthonormal=True)`: assemble `(Λ, V)` from an eigen spec.
- `LAFigureSpecs.svd_tbl_spec(A, **opts)`: build SVD table specs. Returns: spec dict.
- `LAFigureSpecs.svd_tbl_spec_from_right_singular_vectors(V, **opts)`: build SVD specs from given vectors. Returns: spec dict.
- `LAFigureSpecs.svd_matrices_from_spec(spec, reduced=True)`: assemble `(U, Σ, V, rank)` from an SVD spec.
- `LAFigureSpecs.eig_tbl_tex(A, **opts)`: render eigen table TeX.
- `LAFigureSpecs.eig_tbl_svg(A, **opts)`: render eigen table SVG.
- `LAFigureSpecs.eig_bundle(A, **opts)`: canonical eigen bundle helper.
- `LAFigureSpecs.eig_tbl_bundle(A, **opts)`: compatibility alias returning the same standardized bundle.
- `LAFigureSpecs.svd_tbl_tex(A, **opts)`: render SVD table TeX.
- `LAFigureSpecs.svd_tbl_svg(A, **opts)`: render SVD table SVG.
- `LAFigureSpecs.svd_bundle(A, **opts)`: canonical SVD bundle helper.
- `LAFigureSpecs.svd_tbl_bundle(A, **opts)`: compatibility alias returning the same standardized bundle.

## Re-exported matrixlayout renderers (advanced)

These are re-exported for convenience and parity with matrixlayout:

- `LAFigureSpecs.render_ge_tex`, `LAFigureSpecs.render_ge_svg`
- `LAFigureSpecs.render_qr_tex`, `LAFigureSpecs.render_qr_svg`
- `LAFigureSpecs.render_eig_tex`, `LAFigureSpecs.render_eig_svg`

Prefer the higher-level `*_tbl_*` wrappers unless you specifically need direct
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

The SVG wrappers resolve `output_dir`/`tmp_dir` once and then merge the shared
render options; explicit keyword arguments win over values in `render_opts`.
Use `output_dir` for new code. `tmp_dir` remains available as a compatibility
alias.

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
