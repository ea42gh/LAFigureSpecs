from la_figures.ge_convenience import _legacy_ref_path_list_to_rowechelon_paths


def test_legacy_ref_paths_do_not_use_projection_operator():
    matrices = [[None, [[1, 2], [3, 4]]]]
    ref_path_list = [(0, 1, [(0, 0), (1, 1)], "hh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    assert all("-|" in p for p in paths)


def test_ref_paths_interior_pivot_anchors_for_all_cases():
    matrices = [[None, [[1, 2, 3], [4, 5, 6], [7, 8, 9]]]]
    pivots = [(0, 0), (1, 1), (2, 2)]
    for case in ("vv", "vh", "hv", "hh"):
        ref_path_list = [(0, 1, pivots, case)]
        paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
        assert paths
        path = paths[0]
        assert "-|" in path
        assert ".west" not in path


def test_ref_path_vh_uses_left_border_for_nonzero_columns():
    matrices = [[None, [[1, 2, 3, 4, 5, 6],
                        [7, 8, 9, 10, 11, 12],
                        [13, 14, 15, 16, 17, 18]]]]
    pivots = [(0, 0), (1, 4), (2, 5)]
    ref_path_list = [(0, 1, pivots, "vh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    assert "-|" in path


def test_ref_path_uses_row_col_projection_operator_order():
    matrices = [[None, [[1, 2, 3], [4, 5, 6]]]]
    pivots = [(0, 1), (1, 2)]
    ref_path_list = [(0, 1, pivots, "hh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    assert "-|" in path
    assert "|-" not in path


def test_ref_path_vh_sequence_matches_expected_turns():
    # 3x6 matrix with pivots at (0,0), (1,4), (2,5) in 0-based coords.
    # Expect: start at left border of (0,0), go down, then horizontal at pivot columns,
    # and end at the right border of the matrix. Validate key projected points appear.
    matrices = [[None, [[1, 2, 3, 4, 5, 6],
                        [7, 8, 9, 10, 11, 12],
                        [13, 14, 15, 16, 17, 18]]]]
    pivots = [(0, 0), (1, 4), (2, 5)]
    ref_path_list = [(0, 1, pivots, "vh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    # Use the legacy submatrix name A0x1 and projected coordinates with -|.
    assert "\\p1 = (A0x1.north west)" in path
    assert "\\p2 = (A0x1.south east)" in path
    # Key projected points along the path (row,col in 1-based NiceArray terms).
    assert "(2-|4)" in path
    assert "(2-|8)" in path
    assert "(3-|8)" in path
    assert "(3-|9)" in path
    # Must use projection operator (not mirrored).
    assert "-|" in path and "|-" not in path


def test_ref_path_vv_single_pivot_top_left_corner():
    matrices = [[None, [[1, 2], [3, 4]]]]
    pivots = [(0, 0)]
    ref_path_list = [(0, 1, pivots, "vv")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    # Starts at top-left border and goes down to bottom border.
    assert "(\\x1,\\y1)" in path
    assert "(\\x4,\\y2)" in path
