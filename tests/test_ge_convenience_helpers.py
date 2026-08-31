import pytest
import sympy as sym

from LAFigureSpecs.ge_convenience import (
    _is_stack_matrix_cell,
    _looks_like_ge_stack,
    _normalize_stack_text_annotations,
    _resolve_n_rhs,
    _variable_summary_label_rows,
)


def test_stack_detection_distinguishes_matrix_cells_from_plain_matrices():
    assert _is_stack_matrix_cell(None)
    assert _is_stack_matrix_cell(sym.Matrix([[1]]))
    assert _is_stack_matrix_cell([[1]])
    assert not _is_stack_matrix_cell("matrix")
    assert _looks_like_ge_stack([[None, sym.Matrix([[1]])]])
    assert not _looks_like_ge_stack([[1, 2], [3, 4]])
    assert not _looks_like_ge_stack([])


def test_resolve_n_rhs_uses_zero_only_when_omitted():
    assert _resolve_n_rhs() == 0
    assert _resolve_n_rhs(n_rhs=None) is None
    assert _resolve_n_rhs(n_rhs=[1, 2]) == [1, 2]


def test_variable_summary_adds_rhs_status_marks():
    matrices = [[sym.Matrix([[1, 2, 3]])]]
    rows = _variable_summary_label_rows(
        matrices,
        [True, False],
        ["red", "black"],
        rhs_status=["inconsistent"],
    )
    assert len(rows) == 1
    assert rows[0]["side"] == "below"
    assert r"\times" in rows[0]["labels"][0][-1]


def test_text_annotation_normalization_supports_negative_grid_indices_and_styles():
    matrices = [[sym.Matrix([[1, 2]])], [sym.Matrix([[3, 4]])]]
    out = _normalize_stack_text_annotations(
        matrices,
        [
            {"grid_row": -1, "grid_col": -1, "text": "right", "side": "right"},
            {"grid_row": 0, "text": "custom", "style": "draw=red"},
            "raw",
        ],
        comment_shift_x_mm=2,
        comment_shift_y_mm=3,
    )
    assert out[0][0] == "(2-2.east)"
    assert "xshift=2.0mm" in out[0][2]
    assert out[1][2] == "draw=red"
    assert out[2] == "raw"


def test_text_annotation_normalization_rejects_invalid_targets():
    matrices = [[sym.Matrix([[1]])]]
    with pytest.raises(ValueError, match="grid_row out of range"):
        _normalize_stack_text_annotations(
            matrices, [{"grid_row": 2, "text": "bad"}], comment_shift_x_mm=1, comment_shift_y_mm=1
        )
    with pytest.raises(ValueError, match="side must"):
        _normalize_stack_text_annotations(
            matrices, [{"grid_row": 0, "text": "bad", "side": "above"}], comment_shift_x_mm=1, comment_shift_y_mm=1
        )
