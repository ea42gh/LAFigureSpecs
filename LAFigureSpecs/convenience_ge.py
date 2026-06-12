"""Import forwarding for Gaussian elimination convenience wrappers.

Some callers import GE wrappers from :mod:`LAFigureSpecs.convenience_ge`. The
current implementation lives in :mod:`LAFigureSpecs.ge_convenience`.

This module re-exports the public wrappers so both import paths work.
"""

from .ge_convenience import (
    ge,
    ge_tbl_bundle,
    ge_tbl_layout_spec,
    ge_tbl_spec,
    ge_tbl_tex,
    ge_tbl_svg,
)

ge_table_tex = ge_tbl_tex
ge_table_svg = ge_tbl_svg
ge_table_bundle = ge_tbl_bundle

__all__ = [
    "ge_tbl_bundle",
    "ge_tbl_layout_spec",
    "ge_tbl_spec",
    "ge_tbl_tex",
    "ge_tbl_svg",
    "ge_table_tex",
    "ge_table_svg",
    "ge_table_bundle",
    "ge",
]
