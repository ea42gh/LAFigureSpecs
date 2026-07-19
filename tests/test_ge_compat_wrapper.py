import pytest
import sympy as sym


def test_legacy_pivot_list_to_pivot_locs():
    from LAFigureSpecs._ge_legacy_compat import _legacy_pivot_list_to_pivot_locs

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]

    pivot_list = [
        ((1, 1), [(0, 0), (1, 1)]),
    ]

    pivot_locs = _legacy_pivot_list_to_pivot_locs(matrices, pivot_list, index_base=1, pivot_style="draw=red")
    assert pivot_locs == [
        ("(3-3)(3-3)", "draw=red"),
        ("(4-4)(4-4)", "draw=red"),
    ]


def test_structured_rowechelon_paths_match_internal_legacy_ref_path_conversion():
    from LAFigureSpecs.ge_paths import rowechelon_paths_from_specs
    from LAFigureSpecs.ge_paths import _rowechelon_paths_from_legacy_tuples

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]

    structured_paths = rowechelon_paths_from_specs(
        matrices,
        [{"grid": (1, 1), "pivots": [(0, 0), (1, 1)], "case": "hh", "color": "red"}],
        legacy_submatrix_names=True,
    )
    legacy_paths = _rowechelon_paths_from_legacy_tuples(
        matrices,
        [(1, 1, [(0, 0), (1, 1)], "hh", "red")],
        legacy_submatrix_names=True,
    )

    assert structured_paths == legacy_paths


def test_ge_svg_rejects_removed_ref_path_list_keyword():
    from LAFigureSpecs.convenience_ge import ge_svg

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]

    with pytest.raises(TypeError, match="ref_path_list"):
        ge_svg(
            matrices,
            ref_path_list=[(1, 1, [(0, 0), (1, 1)], "hh")],
            output_dir="tmp",
        )
