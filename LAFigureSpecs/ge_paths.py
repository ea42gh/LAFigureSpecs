"""Compatibility wrapper for GE row-echelon path helpers.

The path geometry is owned by :mod:`matrixlayout.ge_paths`.
"""

from __future__ import annotations

from matrixlayout.ge_paths import (
    ref_path_list_to_rowechelon_paths,
    rowechelon_paths_from_legacy_tuples,
    rowechelon_paths_from_specs,
)

__all__ = [
    "ref_path_list_to_rowechelon_paths",
    "rowechelon_paths_from_legacy_tuples",
    "rowechelon_paths_from_specs",
]
