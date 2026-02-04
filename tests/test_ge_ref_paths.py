from la_figures.ge_convenience import _legacy_ref_path_list_to_rowechelon_paths


def test_legacy_ref_paths_do_not_use_projection_operator():
    matrices = [[None, [[1, 2], [3, 4]]]]
    ref_path_list = [(0, 1, [(0, 0), (1, 1)], "hh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    assert all("-|" not in p for p in paths)


def test_ref_paths_interior_pivot_anchors_for_all_cases():
    matrices = [[None, [[1, 2, 3], [4, 5, 6], [7, 8, 9]]]]
    pivots = [(0, 0), (1, 1), (2, 2)]
    for case in ("vv", "vh", "hv", "hh"):
        ref_path_list = [(0, 1, pivots, case)]
        paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
        assert paths
        # Interior pivot should attach to left and bottom borders.
        path = paths[0]
        assert ".west" in path
        assert ".south" in path
        assert "-|" not in path


def test_ref_paths_do_not_reference_out_of_bounds_cells():
    matrices = [[None, [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]]]
    # Pivot list ends at last row/col; hh case used to generate (row+1) nodes.
    ref_path_list = [(0, 1, [(0, 0), (1, 1), (2, 1), (3, 1), (4, 1)], "hh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    # For a 5x2 matrix, the last valid row index is 5 in 1-based NiceArray terms.
    # Ensure we do not reference row 6.
    assert "6-" not in path


def test_ref_path_hh_last_pivot_does_not_step_past_last_row():
    # Mirror the PLU example shape: 5x5 block with pivots ending on the diagonal.
    matrices = [[None, [[1, 0, 0, 0, 0],
                        [0, 1, 0, 0, 0],
                        [0, 0, 1, 0, 0],
                        [0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 1]]]]
    pivots = [(0, 0), (1, 1), (2, 3), (3, 3), (4, 4)]
    ref_path_list = [(0, 1, pivots, "hh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    # Last valid row index in 1-based NiceArray terms is 5; ensure no row 6.
    assert "6-" not in path


def test_ref_path_vh_uses_left_border_for_nonzero_columns():
    matrices = [[None, [[1, 2, 3, 4, 5, 6],
                        [7, 8, 9, 10, 11, 12],
                        [13, 14, 15, 16, 17, 18]]]]
    pivots = [(0, 0), (1, 4), (2, 5)]
    ref_path_list = [(0, 1, pivots, "vh")]
    paths = _legacy_ref_path_list_to_rowechelon_paths(matrices, ref_path_list, legacy_submatrix_names=True)
    assert paths
    path = paths[0]
    assert ".west" in path
    assert ".south" in path
