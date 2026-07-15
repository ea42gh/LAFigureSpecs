"""GE row-echelon path helper exports.

The path geometry is owned by :mod:`matrixlayout.ge_paths`.

Use :func:`rowechelon_paths_from_specs` for canonical structured path specs.
Use :func:`rowechelon_paths_from_legacy_tuples` only at compatibility
boundaries that still accept old ``ref_path_list`` tuple inputs.
``ref_path_list_to_rowechelon_paths`` is a compatibility alias retained for
older callers and tests that document the supported migration path.
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
