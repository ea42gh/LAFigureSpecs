import re

from LAFigureSpecs._ge_legacy_compat import _legacy_ref_path_list_to_rowechelon_paths


def _path_anchor_keys(path):
    out = []
    for row, col in re.findall(r"\((\d+)-\|([A-Za-z0-9_-]+)\)", path):
        col_key = int(col) if col.isdigit() else col
        out.append(((int(row), "rule"), (col_key, "rule")))
    for row, col, anchor in re.findall(r"\((\d+)-(\d+)\.([a-z ]+)\)", path):
        parts = set(anchor.split())
        vertical = "north" if "north" in parts else "south" if "south" in parts else "center"
        horizontal = "west" if "west" in parts else "east" if "east" in parts else "center"
        out.append(((int(row), vertical), (int(col), horizontal)))
    return out


def _assert_manhattan_path(path):
    keys = _path_anchor_keys(path)
    assert len(keys) >= 2
    for prev, cur in zip(keys, keys[1:], strict=False):
        row_changes = prev[0] != cur[0]
        col_changes = prev[1] != cur[1]
        assert not (row_changes and col_changes), path


def _assert_no_cell_anchor_path(path):
    assert ".north" not in path
    assert ".south" not in path
    assert ".east" not in path
    assert ".west" not in path


def test_legacy_ref_paths_use_nicematrix_rule_coordinates():
    matrices = [[None, [[1, 2], [3, 4]]]]
    ref_path_list = [(0, 1, [(0, 0), (1, 1)], "hh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    assert all("-|" in p for p in paths)
    assert all(not p.startswith(r"\tikz") for p in paths)
    for path in paths:
        _assert_no_cell_anchor_path(path)
        _assert_manhattan_path(path)


def test_ref_paths_interior_pivot_anchors_for_all_cases():
    matrices = [[None, [[1, 2, 3], [4, 5, 6], [7, 8, 9]]]]
    pivots = [(0, 0), (1, 1), (2, 2)]
    for case in ("vv", "vh", "hv", "hh"):
        ref_path_list = [(0, 1, pivots, case)]
        paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
        assert paths
        path = paths[0]
        assert "|-" not in path
        assert r"\p" not in path
        assert r"\x" not in path
        assert r"\y" not in path
        assert not path.startswith(r"\tikz")
        _assert_no_cell_anchor_path(path)
        _assert_manhattan_path(path)


def test_ref_path_vh_uses_right_boundary_for_nonzero_columns():
    matrices = [[None, [[1, 2, 3, 4, 5, 6],
                        [7, 8, 9, 10, 11, 12],
                        [13, 14, 15, 16, 17, 18]]]]
    pivots = [(0, 0), (1, 4), (2, 5)]
    ref_path_list = [(0, 1, pivots, "vh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    assert "|-" not in path
    _assert_no_cell_anchor_path(path)
    _assert_manhattan_path(path)


def test_ref_path_uses_row_col_projection_operator_order():
    matrices = [[None, [[1, 2, 3], [4, 5, 6]]]]
    pivots = [(0, 1), (1, 2)]
    ref_path_list = [(0, 1, pivots, "hh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    assert "|-" not in path
    _assert_no_cell_anchor_path(path)
    _assert_manhattan_path(path)


def test_ref_path_hh_traces_lower_pivot_boundary():
    matrices = [[None, [[1, 2, 4, 1], [0, "k^2-1", 8, "k"], [0, 0, 0, 0]]]]
    pivots = [(0, 0), (1, 1)]
    ref_path_list = [(0, 1, pivots, "hh", "red")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths == [
        r"\draw[red] (2-|4) -- (2-|5) -- (3-|5) -- (3-|8);"
    ]
    _assert_manhattan_path(paths[0])


def test_ref_path_vh_traces_right_pivot_boundary():
    matrices = [[None, [[1, 2, 4, 1], [0, "k^2-1", 8, "k"], [0, 0, 0, 0]]]]
    pivots = [(0, 0), (1, 1)]
    ref_path_list = [(0, 1, pivots, "vh", "red")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths == [
        r"\draw[red] (1-|4) -- (2-|4) -- (2-|5) -- (3-|5) -- (3-|8);"
    ]
    _assert_manhattan_path(paths[0])


def test_ref_path_vv_traces_right_pivot_boundary_to_bottom():
    matrices = [[None, [[1, 2, 4, 1], [0, "k^2-1", 8, "k"], [0, 0, 0, 0]]]]
    pivots = [(0, 0), (1, 1)]
    ref_path_list = [(0, 1, pivots, "vv", "red")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths == [
        r"\draw[red] (1-|4) -- (2-|4) -- (2-|5) -- (4-|5);"
    ]
    _assert_manhattan_path(paths[0])


def test_ref_path_node_offsets_shift_old_staircase_nodes():
    matrices = [[None, [[1, 2, 4, 1], [0, "k^2-1", 8, "k"], [0, 0, 0, 0]]]]
    pivots = [(0, 0), (1, 1)]
    ref_path_list = [(0, 1, pivots, "vh", "red", 0.1, 0.0, (0.2, -0.05))]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths == [
        r"\draw[red] ($ (1-|4) + (0.2,-0.05) $) -- ($ (2-|4) + (0.2,-0.05) $) -- ($ (2-|5) + (0.2,-0.05) $) -- ($ (3-|5) + (0.2,-0.05) $) -- ($ (3-|8) + (0.2,-0.05) $);"
    ]
    _assert_manhattan_path(paths[0])


def test_ref_path_vh_sequence_matches_expected_turns():
    # 3x6 matrix with pivots at (0,0), (1,4), (2,5) in 0-based coords.
    # Expect: start at the top-right boundary of (0,0), go down, then
    # horizontal at pivot columns, and end at the right boundary of the final
    # pivot row. Validate key boundary points appear.
    matrices = [[None, [[1, 2, 3, 4, 5, 6],
                        [7, 8, 9, 10, 11, 12],
                        [13, 14, 15, 16, 17, 18]]]]
    pivots = [(0, 0), (1, 4), (2, 5)]
    ref_path_list = [(0, 1, pivots, "vh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    # Key projected points along the path (row,col in 1-based NiceArray terms).
    assert "(1-|4)" in path
    assert "(2-|8)" in path
    assert "(3-|9)" in path
    assert "|-" not in path
    _assert_no_cell_anchor_path(path)
    _assert_manhattan_path(path)


def test_ref_path_vv_single_pivot_top_left_corner():
    matrices = [[None, [[1, 2], [3, 4]]], [[[1, 0], [0, 1]], [[1, 2], [3, 4]]]]
    pivots = [(0, 0)]
    ref_path_list = [(0, 1, pivots, "vv")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    # A single-pivot vertical cutoff is drawn on the left edge of the pivot
    # entry. The logical pivot column must not be shifted to the next rule.
    assert paths == [r"\draw[blue,line width=0.4mm] (1-|A0x1-left) -- (3-|A0x1-left);"]
    _assert_manhattan_path(path)


def test_ref_path_right_edge_helper_anchors_stay_on_existing_nodes():
    identity = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]
    augmented = [
        [1, 1, 1, 2, 2, 3],
        [0, 1, -1, 1, 0, 4],
        [0, 0, 0, 0, 0, 5],
        [0, 0, 0, 1, -2, 6],
    ]
    matrices = [
        [None, augmented],
        [identity, augmented],
        [identity, augmented],
        [identity, augmented],
    ]
    paths = _legacy_ref_path_list_to_rowechelon_paths(
        matrices,
        [(3, 1, [(0, 0), (1, 1), (2, 5)], "hh")],
        legacy_submatrix_names=True,
    )

    assert paths
    path = paths[0]
    assert "|-" not in path
    _assert_no_cell_anchor_path(path)
    assert r"\p" not in path
    assert r"\x" not in path
    assert r"\y" not in path
    assert "(15-|10)" in path
    _assert_manhattan_path(path)
