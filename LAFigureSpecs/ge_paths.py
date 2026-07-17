"""GE row-echelon path helper exports.

The path geometry is owned by :mod:`matrixlayout.ge_paths`.

Use :func:`rowechelon_paths_from_specs` for canonical structured path specs.
Use :func:`rowechelon_paths_from_legacy_tuples` only at compatibility
boundaries that still accept old ``ref_path_list`` tuple inputs.
"""

from __future__ import annotations

from matrixlayout.ge_paths import (
    _rowechelon_paths_from_legacy_tuples,
    rowechelon_paths_from_specs,
)

rowechelon_paths_from_legacy_tuples = _rowechelon_paths_from_legacy_tuples

__all__ = [
    "rowechelon_paths_from_legacy_tuples",
    "rowechelon_paths_from_specs",
]
