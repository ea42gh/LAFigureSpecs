# Specs

`*_spec` functions return plain dictionaries suitable for matrixlayout.
`*_layout_spec` functions return typed layout objects (use `.to_dict()` for dict access).

Specs emitted for matrixlayout use `body_preamble` for document-body setup and
`document_preamble` for true LaTeX preamble insertion. GE, QR, eigen, and SVD
computed wrappers use those same canonical keyword names where TeX hooks apply.

Selectors and decorators use 0-based entry indices within each matrix block.
Grid positions are addressed by (row, column) in the outer list.

## GE

`ge_spec` parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `A` | matrix | required | Coefficient matrix. |
| `rhs` | matrix | None | Right-hand side columns for the system. |
| `pivoting` | str | "none" | "none", "partial", or "full". |
| `gj` | bool | False | Use Gauss-Jordan. |
| `show_pivots` | bool | True | Emit pivot boxes (entry decorators). |
| `index_base` | int | 1 | Index base for labels. |
| `pivot_style` | str | "" | Use CodeAfter fit boxes when set. |
| `pivot_text_color` | str | "red" | Pivot entry text color. |
| `body_preamble` | str | nicematrix opts | Document-body setup emitted to matrixlayout. |
| `document_preamble` | str | "" | True LaTeX preamble insertion emitted to matrixlayout. |
| `row_stretch` | float | None | Row spacing multiplier. |
| `nice_options` | str | "" | NiceArray options. |
| `callouts` | list/bool | None | Explicit matrix arrow labels. |
| `array_names` | list/bool | None | Matrix name labels. |
| `array_name_indices` | bool | True | Add step indices to shorthand `array_names` labels. |
| `decorators` | list | None | Entry decorators. |
| `format_nrhs` | bool | True | Use format-level RHS separators (disabled when line decorations are emitted). |
| `fig_scale` | float | None | Figure scale. |
| `outer_hspace_mm` | int | 6 | Horizontal block spacing (mm). |
| `cell_align` | str | "r" | Cell alignment in TeX. |
| `variable_summary` | list | None | Override pivot/free indicator row. |
| `variable_colors` | tuple | ("red","black") | Colors for pivot/free indicators. |
| `strict` | bool | None | Error on invalid decorators. |

Use `callouts` for explicit matrix arrow labels. `array_names` is a
convenience shorthand that expands to callouts; `array_name_indices=false`
suppresses the generated step indices.

When `strict=True`, invalid decorator selectors raise errors instead of being ignored.

Pivot rendering:

- Default (`pivot_style=""`): boxed entry decorators in the matrix body.
- Explicit `pivot_style`: CodeAfter `fit` boxes using the provided TikZ style.

Defaults (selected):

- `ge_spec`: `pivoting="none"`, `gj=False`, `show_pivots=True`
- `qr_spec`: `array_names=True`
- `eig_spec`: `normal=False`

GE convenience wrappers render TeX to SVG via matrixlayout. Shared renderer
parameters: `toolchain_name`, `crop`, `padding`, `output_dir`, `output_stem`,
`frame`.

For most users, prefer `ge_svg(...)` over direct `render_ge_svg(...)`.

`ge_tex`, `ge_svg`, and `ge_bundle` accept the same algorithmic parameters as
`ge_spec` plus renderer options (for SVG).

`ge_stack_svg(...)` is the compatibility renderer for precomputed GE matrix
grids. It remains available for notebooks and wrappers that already computed the
row-reduction stack, but new algorithm-facing code should prefer `ge_svg(...)`
or `ge_bundle(...)`.

`ge_stack_svg(...)` parameters (subset shown):

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `matrices` | grid | required | Matrix grid. |
| `n_rhs` | int/list | 0 | RHS partitioning for matrixlayout specs. |
| `pivot_locs` | list | None | Canonical pivot selector/decorator specs. |
| `codebefore` | list | None | Canonical raw CodeBefore snippets. |
| `text_annotations` | list | None | Canonical text annotation specs. |
| `label_rows` | list | None | Canonical label-row specs. |
| `rowechelon_paths` | list | None | Canonical row-echelon path snippets. |
| `pivot_list` | list | None | Compatibility pivot specs converted to renderer decorators. |
| `bg_for_entries` | list | None | Compatibility background highlights converted to renderer code. |
| `ref_path_list` | list | None | Compatibility row‑echelon paths converted to renderer paths. |
| `comment_list` | list | None | Compatibility right-side comments converted to text annotations. |
| `callouts` | list | None | Explicit matrix arrow labels. |
| `array_names` | list/bool | None | Shorthand matrix labels converted to callouts. |
| `array_name_indices` | bool | True | Add step indices to shorthand `array_names` labels. |
| `decorators` | list | None | Entry decorators. |
| `specs` | list | None | Compatibility alias for callouts; old `angle`/`length` keys are normalized. |

For stack renderers, `pivot_locs` may use structured selectors:
`{"grid": (block_row, block_col), "entries": [(row, col)], "style": "draw=blue"}`.
`rowechelon_paths` may also use structured selectors:
`{"grid": (block_row, block_col), "pivots": [(row, col)], "case": "hh", "color": "blue"}`.
Raw renderer snippets remain accepted for advanced uses.

The old `pivot_list`, `bg_for_entries`, `ref_path_list`, `comment_list`, and
`specs` inputs are intentionally isolated as compatibility inputs.
Matrixlayout-facing specs should use canonical renderer fields such as
`decorators`, `decorations`, `text_annotations`, `rowechelon_paths`, and
`callouts`.

Bundle return contract (`ge_bundle`):

- `spec`, `tex`, `svg`, `data`, `render_error`
- GE-specific intermediates are in `data`:
  - `data["trace"]`, `data["decor"]`, `data["layers"]`, `data["typed_layout"]`
  - optional `data["submatrix_spans"]`

Note on RHS separators:

`ge_spec` now emits RHS separator lines via `decorations` (per-block vlines)
and disables format-level separators to keep label rows clean. The resulting
vertical lines only appear in the matrix rows.

## QR

`qr_spec` parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `A` | matrix | required | Input matrix. |
| `W` | matrix | required | Computed internally via naive Gram–Schmidt (LCD-scaled, no normalization). |
| `callouts` | list | None | Explicit matrix arrow labels. |
| `array_names` | bool/list | True | Enable labels or custom list. |
| `fig_scale` | float | None | Figure scale. |
| `body_preamble` | str | nicematrix opts | Document-body setup emitted to matrixlayout. |
| `document_preamble` | str | "" | True LaTeX preamble insertion emitted to matrixlayout. |
| `nice_options` | str | "vlines-in-sub-matrix = I" | NiceArray options. |
| `label_color` | str | "blue" | Label color. |
| `label_text_color` | str | "red" | Label text color. |
| `known_zero_color` | str | "brown" | Known-zero highlight. |
| `decorators` | list | None | Entry decorators. |
| `strict` | bool | None | Error on invalid decorators. |

`qr_svg(...)` parameters (subset shown):

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `A` | matrix | required | Input matrix. |
| `W` | matrix | required | Computed internally via naive Gram–Schmidt (LCD-scaled, no normalization). |
| `array_names` | bool/list | True | Labels. |
| `decorators` | list | None | Entry decorators. |

`qr_tex`, `qr_svg`, `qr_bundle` follow `qr_spec` plus renderer
options (for SVG).

Bundle return contract (`qr_bundle`): `spec`, `tex`, `svg`, `data`, `render_error`.

For most users, prefer `qr_svg(...)` over direct `render_qr_svg(...)`.

QR callout labels are nudged vertically to align with their arrows. For 2x2
inputs, the Q^T label uses a longer arrow to avoid overlapping the R label.

## Eigen/SVD

`eig_spec` parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `A` | matrix | required | Input matrix. |
| `normal` | bool | False | Normal matrix handling. |
| `Ascale` | scalar | None | Scaling factor. |
| `eig_digits` | int | None | Rounding for eigenvalues. |
| `vec_digits` | int | None | Rounding for eigenvectors. |

`svd_spec` parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `A` | matrix | required | Input matrix. |
| `Ascale` | scalar | None | Scaling factor. |

`eig_tex`, `eig_svg`, `svd_tex`, `svd_svg` accept `A` plus the
corresponding spec parameters, along with renderer options (for SVG).

Bundle return contract (`eig_bundle`, `svd_bundle`):
`spec`, `tex`, `svg`, `data`, `render_error`.

For most users, prefer `eig_svg(...)` / `svd_svg(...)` over direct
`render_eig_svg(...)`.
