import pytest


def test_pivot_selectors_to_pivot_locs():
    from LAFigureSpecs.ge_stack_helpers import _pivot_selectors_to_pivot_locs
    import sympy as sym

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]

    pivot_selectors = [
        ((1, 1), [(0, 0), (1, 1)]),
    ]

    pivot_locs = _pivot_selectors_to_pivot_locs(matrices, pivot_selectors, index_base=1, pivot_style="draw=red")
    assert pivot_locs == [
        ("(3-3)(3-3)", "draw=red"),
        ("(4-4)(4-4)", "draw=red"),
    ]


def test_ge_svg_rejects_removed_ref_path_list_keyword():
    from LAFigureSpecs.convenience_ge import ge_svg
    import sympy as sym

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


def test_ge_svg_rejects_tuple_rowechelon_path_entries():
    from LAFigureSpecs.convenience_ge import ge_svg
    import sympy as sym

    matrices = [[None, sym.Matrix([[1, 2], [3, 4]])]]

    with pytest.raises(TypeError, match="rowechelon_paths.*ref_path_list"):
        ge_svg(
            matrices,
            rowechelon_paths=[(0, 1, [(0, 0), (1, 1)], "hh")],
            output_dir="tmp",
        )
