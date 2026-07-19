"""GE row-echelon path helper exports.

The path geometry is owned by :mod:`matrixlayout.ge_paths`.

Use :func:`rowechelon_paths_from_specs` for canonical structured path specs.
Tuple-based ``ref_path_list`` conversion is internal compatibility behavior.
"""

from __future__ import annotations

from matrixlayout.ge_paths import rowechelon_paths_from_specs

__all__ = [
    "rowechelon_paths_from_specs",
]
