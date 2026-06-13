import re

import pytest
import sympy as sym

pytest.importorskip("matrixlayout")


def _submatrix_names(tex: str):
    return re.findall(r"name=([A-Za-z0-9_]+)", tex)


def _submatrix_spans(tex: str):
    return re.findall(r"\\SubMatrix\(\{([^}]+)\}\{([^}]+)\}\)", tex)


def test_ge_submatrix_names_and_spans_no_rhs():
    import LAFigureSpecs
    from matrixlayout.ge import render_ge_tex

    A = sym.Matrix([[1, 2], [3, 4]])
    tr = LAFigureSpecs.ge_trace(A, pivoting="none")
    layers = LAFigureSpecs.trace_to_layer_matrices(tr, augmented=True)["matrices"]

    tex = render_ge_tex(matrices=layers, n_rhs=0)

    assert _submatrix_names(tex) == ["A0", "E1", "A1"]
    assert _submatrix_spans(tex) == [("1-3", "2-4"), ("3-1", "4-2"), ("3-3", "4-4")]


def test_ge_submatrix_names_and_spans_with_rhs():
    import LAFigureSpecs
    from matrixlayout.ge import render_ge_tex

    A = sym.Matrix([[1, 2], [3, 4]])
    rhs = sym.Matrix([[5], [6]])
    tr = LAFigureSpecs.ge_trace(A, rhs, pivoting="none")
    layers = LAFigureSpecs.trace_to_layer_matrices(tr, augmented=True)["matrices"]

    tex = render_ge_tex(matrices=layers, n_rhs=1)

    assert _submatrix_names(tex) == ["A0", "E1", "A1"]
    assert _submatrix_spans(tex) == [("1-3", "2-5"), ("3-1", "4-2"), ("3-3", "4-5")]
