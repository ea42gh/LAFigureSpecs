import sympy as sym
import pytest

from LAFigureSpecs.qr import gram_schmidt_qr_matrices


def test_gram_schmidt_qr_rank_deficient_raises_by_default():
    A = sym.Matrix([[1, 2], [2, 4]])
    with pytest.raises(ValueError):
        gram_schmidt_qr_matrices(A)


def test_gram_schmidt_qr_rank_deficient_allow():
    A = sym.Matrix([[1, 2], [2, 4]])
    mats = gram_schmidt_qr_matrices(A, allow_rank_deficient=True)
    assert mats[0][2].shape == A.shape
    assert mats[0][3].shape == A.shape


def test_gram_schmidt_qr_rank_deficient_drop():
    A = sym.Matrix([[1, 2], [2, 4]])
    mats = gram_schmidt_qr_matrices(A, rank_deficient="drop")
    assert mats[0][2].shape == (2, 1)
    assert mats[0][3].shape == (2, 1)


def test_qr_matrix_extraction_supports_tuple_and_dict_views():
    from LAFigureSpecs.qr import qr_matrices_dict_from_grid, qr_matrices_from_grid

    A = sym.Matrix([[1, 1], [0, 1]])
    mats = gram_schmidt_qr_matrices(A)

    extracted = qr_matrices_from_grid(mats)
    as_tuple = extracted.as_tuple()
    as_dict = extracted.as_dict()
    dict_from_grid = qr_matrices_dict_from_grid(mats)

    assert extracted["A"] == A
    assert as_tuple[0] == A
    assert as_dict["Q"] == extracted["Q"]
    assert dict_from_grid["R"] == extracted["R"]


def test_naive_gram_schmidt_handles_empty_and_fractional_columns():
    import pytest

    from LAFigureSpecs.qr import naive_gram_schmidt_w

    with pytest.raises(ValueError, match="non-empty A"):
        naive_gram_schmidt_w(None)

    A = sym.Matrix([[sym.Rational(1, 2), 1], [sym.Rational(1, 3), 0]])
    W_scaled = naive_gram_schmidt_w(A, scale_lcd=True)
    W_raw = naive_gram_schmidt_w(A, scale_lcd=False)

    assert W_scaled[0, 0] == 3
    assert W_scaled[1, 0] == 2
    assert W_raw[0, 0] == sym.Rational(1, 2)


def test_qr_float_inputs_do_not_lcd_scale_binary_float_denominators():
    A = sym.Matrix(
        [
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [1.0, 1.0, 0.0],
            [1.0, -1.0, 1.0],
        ]
    )

    mats = gram_schmidt_qr_matrices(A)
    W = mats[0][3]

    assert W[:, 0] == A[:, 0]
    assert W[0, 0] == sym.Float(1.0)
    assert max(abs(float(value)) for value in W) < 10


def test_qr_formatter_applies_to_s_block_for_float_inputs():
    from LAFigureSpecs.qr import qr_spec_from_matrices
    from matrixlayout.qr import render_qr_tex

    A = sym.Matrix(
        [
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [1.0, 1.0, 0.0],
            [1.0, -1.0, 1.0],
        ]
    )
    mats = gram_schmidt_qr_matrices(A)
    tex = render_qr_tex(
        spec=qr_spec_from_matrices(mats),
        formatter=lambda value: f"[{float(value):.2f}]",
        array_names=False,
    )

    assert "[0.58]" in tex
    assert "sqrt" not in tex


def test_naive_qr_rejects_bad_inputs_and_runs_square_case():
    import pytest

    from LAFigureSpecs.qr import naive_qr

    with pytest.raises(ValueError, match="non-empty square"):
        naive_qr(None)
    with pytest.raises(ValueError, match="square"):
        naive_qr([[1, 2, 3], [4, 5, 6]])

    Q, T, conv = naive_qr([[2, 1], [0, 3]], max_iter=5)
    assert Q.shape == (2, 2)
    assert T.shape == (2, 2)
    assert conv >= 0.0


def test_qr_specs_from_matrices_and_layout_spec():
    import pytest

    pytest.importorskip("matrixlayout")
    from LAFigureSpecs.qr import qr_layout_spec, qr_spec_from_matrices

    mats = gram_schmidt_qr_matrices([[1, 0], [1, 1]])
    spec = qr_spec_from_matrices(mats, array_names=False, fig_scale=1.2)

    assert spec["matrices"] == mats
    assert spec["array_names"] is False
    assert spec["fig_scale"] == 1.2

    callouts = [{"grid": (0, 2), "label": "A", "side": "right"}]
    layout = qr_layout_spec([[1, 0], [1, 1]], callouts=callouts, array_names=False)
    assert layout.matrices
    assert layout.callouts == callouts
