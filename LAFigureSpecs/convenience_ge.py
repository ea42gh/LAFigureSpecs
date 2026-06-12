"""Import forwarding for Gaussian elimination convenience wrappers.

Some callers import GE wrappers from :mod:`LAFigureSpecs.convenience_ge`. The
current implementation lives in :mod:`LAFigureSpecs.ge_convenience`.

This module re-exports the public wrappers so both import paths work.
"""

from .ge_convenience import (
    ge,
    ge_bundle,
    ge_layout_spec,
    ge_spec,
    ge_stack_svg,
    ge_svg,
    ge_tex,
)

__all__ = [
    "ge_bundle",
    "ge_layout_spec",
    "ge_spec",
    "ge_stack_svg",
    "ge_svg",
    "ge_tex",
    "ge",
]
