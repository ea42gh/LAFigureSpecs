# Specs

`*_spec` functions return plain dictionaries suitable for matrixlayout.
`*_layout_spec` functions return typed layout objects (use `.to_dict()` for dict access).

Specs emitted for matrixlayout use `body_preamble` for document-body setup and
`document_preamble` for true LaTeX preamble insertion. GE, QR, eigen, and SVD
computed wrappers use those same canonical keyword names where TeX hooks apply.

Selectors and decorators use 0-based entry indices within each matrix block.
Grid positions are addressed by (row, column) in the outer list.

## GE

`ge_tbl_spec` parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `ref_A` | matrix | required | Reference matrix. |
| `ref_rhs` | matrix | None | Reference RHS (augmented). |
| `rhs` | matrix | None | RHS to eliminate. |
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

- `ge_tbl_spec`: `pivoting="none"`, `gj=False`, `show_pivots=True`
- `qr_tbl_spec`: `array_names=True`
- `eig_tbl_spec`: `normal=False`

GE convenience wrappers render TeX to SVG via matrixlayout. Shared renderer
parameters: `toolchain_name`, `crop`, `padding`, `output_dir`, `output_stem`,
`frame`.

For most users, prefer `ge_tbl_svg(...)` over direct `render_ge_svg(...)`.

`ge_svg(...)` parameters (subset shown):

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `matrices` | grid | required | Matrix grid. |
| `n_rhs` | int/list | 0 | RHS partitioning for matrixlayout specs. |
| `pivot_list` | list | None | Legacy pivot specs. |
| `bg_for_entries` | list | None | Background highlights. |
| `ref_path_list` | list | None | Row‑echelon paths. |
| `comment_list` | list | None | Right‑side comments. |
| `array_names` | list/bool | None | Matrix labels. |
| `array_name_indices` | bool | True | Add step indices to shorthand `array_names` labels. |
| `decorators` | list | None | Entry decorators. |

`ge_tbl_tex`, `ge_tbl_svg`, `ge_bundle` accept the same algorithmic
parameters as `ge_tbl_spec` plus renderer options (for SVG).

Bundle return contract (`ge_bundle`):

- `spec`, `tex`, `svg`, `data`, `render_error`
- GE-specific intermediates are in `data`:
  - `data["trace"]`, `data["decor"]`, `data["layers"]`, `data["typed_layout"]`
  - optional `data["submatrix_spans"]`

Note on RHS separators:

`ge_tbl_spec` now emits RHS separator lines via `decorations` (per-block vlines)
and disables format-level separators to keep label rows clean. The resulting
vertical lines only appear in the matrix rows.

## QR

`qr_tbl_spec` parameters:

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

`qr_svg(...)` / `qr_tbl_svg(...)` parameters (subset shown):

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `A` | matrix | required | Input matrix. |
| `W` | matrix | required | Computed internally via naive Gram–Schmidt (LCD-scaled, no normalization). |
| `array_names` | bool/list | True | Labels. |
| `decorators` | list | None | Entry decorators. |

`qr_tbl_tex`, `qr_tbl_svg`, `qr_bundle` follow `qr_tbl_spec` plus renderer
options (for SVG).

Bundle return contract (`qr_bundle`): `spec`, `tex`, `svg`, `data`, `render_error`.

For most users, prefer `qr_svg(...)` over direct `render_qr_svg(...)`.

QR callout labels are nudged vertically to align with their arrows. For 2x2
inputs, the Q^T label uses a longer arrow to avoid overlapping the R label.

## Eigen/SVD

`eig_tbl_spec` parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `A` | matrix | required | Input matrix. |
| `normal` | bool | False | Normal matrix handling. |
| `Ascale` | scalar | None | Scaling factor. |
| `eig_digits` | int | None | Rounding for eigenvalues. |
| `vec_digits` | int | None | Rounding for eigenvectors. |

`svd_tbl_spec` parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `A` | matrix | required | Input matrix. |
| `Ascale` | scalar | None | Scaling factor. |

`eig_tbl_tex`, `eig_tbl_svg`, `svd_tbl_tex`, `svd_tbl_svg` accept `A` plus the
corresponding spec parameters, along with renderer options (for SVG).

Bundle return contract (`eig_bundle`, `svd_bundle`):
`spec`, `tex`, `svg`, `data`, `render_error`.

For most users, prefer `eig_svg(...)` / `svd_svg(...)` over direct
`render_eig_svg(...)`.
