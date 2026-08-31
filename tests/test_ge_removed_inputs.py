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
    from LAFigureSpecs.ge_convenience import ge_svg
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
    from LAFigureSpecs.ge_convenience import ge_svg
    import sympy as sym

    matrices = [[None, sym.Matrix([[1, 2], [3, 4]])]]

    with pytest.raises(TypeError, match="rowechelon_paths entries.*grid=.*pivots="):
        ge_svg(
            matrices,
            rowechelon_paths=[(0, 1, [(0, 0), (1, 1)], "hh")],
            output_dir="tmp",
        )


def test_grid_helpers_handle_empty_ragged_and_sequence_inputs():
    from LAFigureSpecs.ge_stack_helpers import _grid_metrics, _grid_offsets, _matrix_shape

    assert _matrix_shape(None) == (0, 0)
    assert _matrix_shape([]) == (0, 0)
    assert _matrix_shape([[1, 2], [3]]) == (2, 2)
    assert _matrix_shape([1, 2, 3]) == (3, 1)
    assert _grid_metrics([]) == ([], [], [], [], [])
    grid, heights, widths, cell_heights, cell_widths = _grid_metrics(
        [[[1, 2]], [None, [[1], [2], [3]]]]
    )
    assert len(grid[1]) == 2
    assert heights == [2, 3]
    assert widths == [1, 1]
    assert cell_heights == [[2, 0], [0, 3]]
    assert cell_widths == [[1, 0], [0, 1]]
    assert _grid_offsets([]) == ([], [], [], [])


def test_grid_padding_supports_alignment_and_coordinate_clamping():
    from LAFigureSpecs.ge_stack_helpers import (
        _grid_block_padding,
        _grid_cell_coord,
    )

    matrices = [[[[1, 2, 3]]], [[[1], [2], [3]]]]
    padded = _grid_block_padding(matrices, block_align="center", block_valign="top")
    assert padded[4] == [[0], [1]]
    assert padded[5] == [[0], [0]]
    assert _grid_cell_coord(matrices, gM=0, gN=0, i=0, j=99) == "(1-3)"
    assert _grid_cell_coord(matrices, gM=1, gN=0, i=99, j=0) == "(4-3)"
    with pytest.raises(ValueError, match="out of range"):
        _grid_cell_coord(matrices, gM=3, gN=0, i=0, j=0)


def test_grid_padding_rejects_unknown_alignment_modes():
    from LAFigureSpecs.ge_stack_helpers import _block_pad_left, _block_pad_top

    with pytest.raises(ValueError, match="Invalid block_align"):
        _block_pad_left(3, 1, "diagonal")
    with pytest.raises(ValueError, match="Invalid block_valign"):
        _block_pad_top(3, 1, "diagonal")


def test_array_callout_helpers_normalize_rhs_labels_and_indices():
    from LAFigureSpecs.ge_stack_helpers import (
        _array_callout_specs,
        _array_name_callouts,
        _coerce_rhs_labels,
        _n_rhs_count,
    )

    assert _n_rhs_count(None) == 0
    assert _n_rhs_count([1, 2]) == 3
    assert _n_rhs_count("invalid") == 0
    assert _coerce_rhs_labels(["A", "B"], 1) == ["A", "b"]
    assert _coerce_rhs_labels(["A", "b"], 2) == ["A", "B"]
    assert _array_callout_specs(2, "E", ["A", "b"], start_index=None)[:2] == [
        ((0, 1), "ar", r"$\mathbf{ \left(  A \mid  b \right) }$") ,
        ((1, 0), "al", r"$\mathbf{ E }$") ,
    ]
    assert _array_callout_specs(1, "E", ["A"], start_index=1, array_name_indices=False)[0][2].endswith("A }$")
    assert _array_name_callouts([[None, [[1]]]], array_names=None, n_rhs=1, start_index=1) == []
    with pytest.raises(TypeError, match="array_names"):
        _array_name_callouts([[1]], array_names={"A": "B"}, n_rhs=1, start_index=1)


def test_callout_conversion_strips_math_and_ignores_missing_grid_blocks():
    from LAFigureSpecs.ge_stack_helpers import _callout_specs_to_callouts
    import sympy as sym

    matrices = [[sym.Matrix([[1]])]]
    out = _callout_specs_to_callouts(
        matrices,
        [((0, 0), "al", r"$A$"), ((4, 4), "unknown", "B")],
        color="red",
    )
    assert len(out) == 1
    assert out[0]["label"] == "A"
    assert out[0]["math_mode"] is True
    assert out[0]["side"] == "left"