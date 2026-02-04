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
