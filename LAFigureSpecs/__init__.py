"""LAFigureSpecs: linear algebra algorithms + teaching-display facades for matrixlayout.

This package owns *algorithmic decisions* (row reduction, pivot/free-variable
choices, orthonormalization, eigen/SVD computations, etc.) and returns explicit
description objects intended to be consumed by :mod:`matrixlayout`.

The core design keeps responsibilities separate:

- LAFigureSpecs owns linear-algebra/spec-building decisions.
- matrixlayout owns formatting, layout, and rendering mechanics.
- LAFigureSpecs re-exports selected matrixlayout render helpers so Python users
  can access the full teaching surface from one top-level package.
"""

from .__about__ import __version__, __build__

from .eig import (
    EigenDecomposition,
    eig_spec_from_eigenvects,
    eig_spec,
    eigendecomposition,
    eig_matrices_from_spec,
)
from .svd import (
    svd_spec,
    svd_spec_from_right_singular_vectors,
    svd_matrices_from_spec,
)
from .convenience import (
    eig_bundle,
    eig_svg,
    eig_tex,
    svd_bundle,
    svd_svg,
    svd_tex,
)
from .qr import (
    compute_qr_matrices,
    gram_schmidt_qr_matrices,
    naive_gram_schmidt_w,
    naive_qr,
    qr_layout_spec,
    qr_spec,
    qr_spec_from_matrices,
    qr_matrices_from_grid,
    qr_matrices_dict_from_grid,
)
from .convenience_qr import (
    qr_bundle,
    qr_figure,
    qr_svg,
    qr_tex,
)
from .backsub import (
    backsubstitution_tex,
    linear_system_tex,
    standard_solution_tex,
)
from .ge import ge_trace, trace_to_layer_matrices
from .ge_convenience import show_ge
from .show_ge import (
    ShowGE,
    ref,
    lhs_matrix,
    rhs_matrix,
    rhs_column,
    show_backsubstitution,
    show_layout,
    show_solution,
    show_system,
    solutions,
)
from .convenience_utils import bundle_summary
from .ge_convenience import (
    ge_bundle,
    ge_layout_spec,
    ge_spec,
    ge_svg,
    ge_tex,
)
from .rendering import latex_svg, latex_document_svg, lshow_svg
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
        from IPython.display import SVG, display
    except Exception:
        return svg
    return display(SVG(svg))


def mm_to_px(mm: float) -> float:
    """Convert millimeters to px-equivalent SVG units (96 px per inch)."""
    return float(mm) * 96.0 / 25.4


def px_to_mm(px: float) -> float:
    """Convert px-equivalent SVG units to millimeters (96 px per inch)."""
    return float(px) * 25.4 / 96.0


__all__ = [
    "__version__",
    "__build__",
    "EigenDecomposition",
    "eigendecomposition",
    "eig_spec_from_eigenvects",
    "eig_spec",
    "eig_matrices_from_spec",
    "svd_spec",
    "svd_spec_from_right_singular_vectors",
    "svd_matrices_from_spec",
    "eig_tex",
    "eig_bundle",
    "svd_tex",
    "svd_bundle",
    "compute_qr_matrices",
    "gram_schmidt_qr_matrices",
    "naive_gram_schmidt_w",
    "naive_qr",
    "qr_spec_from_matrices",
    "qr_matrices_from_grid",
    "qr_matrices_dict_from_grid",
    "qr_spec",
    "qr_layout_spec",
    "qr_tex",
    "qr_svg",
    "qr_figure",
    "qr_bundle",
    "backsubstitution_tex",
    "linear_system_tex",
    "standard_solution_tex",
    "ge_trace",
    "trace_to_layer_matrices",
    "ge_spec",
    "ge_layout_spec",
    "ge_tex",
    "show_ge",
    "ShowGE",
    "ref",
    "lhs_matrix",
    "rhs_matrix",
    "rhs_column",
    "show_layout",
    "show_system",
    "show_backsubstitution",
    "show_solution",
    "solutions",
    "ge_svg",
    "ge_bundle",
    "eig_svg",
    "svd_svg",
    "render_ge_svg",
    "render_ge_tex",
    "render_qr_svg",
    "render_qr_tex",
    "render_eig_svg",
    "render_eig_tex",
    "latex_svg",
    "latex_document_svg",
    "lshow_svg",
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
    "mm_to_px",
    "px_to_mm",
    "bundle_summary",
]
