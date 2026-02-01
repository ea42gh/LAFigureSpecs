"""la_figures: linear algebra algorithms + description objects for matrixlayout.

This package owns *algorithmic decisions* (row reduction, pivot/free-variable
choices, orthonormalization, eigen/SVD computations, etc.) and returns explicit
description objects intended to be consumed by :mod:`matrixlayout`.

The core rule is strict layering:

- la_figures does **not** render and does **not** call TeX toolchains.
- matrixlayout does **not** do linear algebra; it only formats and lays out.
"""

from .eig import (
    EigenDecomposition,
    eig_spec_from_eigenvects,
    eig_tbl_spec,
    eigendecomposition,
    eig_matrices_from_spec,
)
from .svd import svd_tbl_spec, svd_tbl_spec_from_right_singular_vectors, svd_matrices_from_spec
from .convenience import (
    eig_tbl_bundle,
    eig_tbl_svg,
    eig_tbl_tex,
    svd_tbl_bundle,
    svd_tbl_svg,
    svd_tbl_tex,
)
from .qr import (
    compute_qr_matrices,
    gram_schmidt_qr_matrices,
    qr_tbl_layout_spec,
    qr_tbl_spec,
    qr_tbl_spec_from_matrices,
    qr_matrices_from_grid,
)
from .convenience_qr import qr, qr_tbl_bundle as qr_tbl_bundle, qr_tbl_tex, qr_tbl_svg, gram_schmidt_qr
from .backsub import (
    backsubstitution_tex,
    linear_system_tex,
    standard_solution_tex,
)
from .ge import ge_trace, trace_to_layer_matrices
from .ge_convenience import show_ge
from .convenience_ge import ge as ge, ge_tbl_bundle, ge_tbl_layout_spec, ge_tbl_spec, ge_tbl_tex, ge_tbl_svg
from matrixlayout.ge import render_ge_svg, render_ge_tex
from matrixlayout.qr import render_qr_svg, render_qr_tex
from matrixlayout import render_eig_svg, render_eig_tex
from .formatting import (
    decorate_tex_entries,
    latexify,
    make_decorator,
    decorator_box,
    decorator_color,
    decorator_bg,
    decorator_bf,
    sel_entry,
    sel_box,
    sel_row,
    sel_col,
    sel_rows,
    sel_cols,
    sel_all,
    sel_vec,
    sel_vec_range,
)


def show_svg(svg: str):
    """Display an SVG string in a notebook when possible."""
    try:
        from IPython.display import SVG, display  # type: ignore
    except Exception:
        return svg
    return display(SVG(svg))

__all__ = [
    "EigenDecomposition",
    "eigendecomposition",
    "eig_spec_from_eigenvects",
    "eig_tbl_spec",
    "eig_matrices_from_spec",
    "svd_tbl_spec",
    "svd_tbl_spec_from_right_singular_vectors",
    "svd_matrices_from_spec",
    "eig_tbl_tex",
    "eig_tbl_svg",
    "eig_tbl_bundle",
    "svd_tbl_tex",
    "svd_tbl_svg",
    "svd_tbl_bundle",
    "compute_qr_matrices",
    "gram_schmidt_qr_matrices",
    "qr_tbl_spec",
    "qr_tbl_spec_from_matrices",
    "qr_matrices_from_grid",
    "qr_tbl_layout_spec",
    "qr_tbl_tex",
    "qr_tbl_svg",
    "qr_tbl_bundle",
    "gram_schmidt_qr",
    "backsubstitution_tex",
    "linear_system_tex",
    "standard_solution_tex",
    "ge_trace",
    "trace_to_layer_matrices",
    "ge_tbl_spec",
    "ge_tbl_layout_spec",
    "ge_tbl_tex",
    "ge_tbl_svg",
    "show_ge",
    "ge_tbl_bundle",
    "ge",
    "render_ge_svg",
    "render_ge_tex",
    "render_qr_svg",
    "render_qr_tex",
    "render_eig_svg",
    "render_eig_tex",
    "qr",
    "latexify",
    "make_decorator",
    "decorate_tex_entries",
    "decorator_box",
    "decorator_color",
    "decorator_bg",
    "decorator_bf",
    "sel_entry",
    "sel_box",
    "sel_row",
    "sel_col",
    "sel_rows",
    "sel_cols",
    "sel_all",
    "sel_vec",
    "sel_vec_range",
    "show_svg",
]
