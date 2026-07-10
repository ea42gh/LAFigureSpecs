import numpy as np
import sympy as sym


def test_to_sympy_matrix_tuple_rationals_2d_list():
    from LAFigureSpecs._sympy_utils import to_sympy_matrix

    A = [[(1, 2), (0, 1)], [(3, 4), (5, 6)]]
    M = to_sympy_matrix(A)
    assert M.shape == (2, 2)
    assert M[0, 0] == sym.Rational(1, 2)
    assert M[1, 0] == sym.Rational(3, 4)


def test_to_sympy_matrix_tuple_rationals_numpy_array():
    from LAFigureSpecs._sympy_utils import to_sympy_matrix

    A = np.array([[(1, 2), (0, 1)], [(3, 4), (5, 6)]], dtype=object)
    M = to_sympy_matrix(A)
    assert M.shape == (2, 2)
    assert M[0, 0] == sym.Rational(1, 2)
    assert M[1, 1] == sym.Rational(5, 6)


def test_eig_spec_accepts_tuple_rationals():
    import LAFigureSpecs

    A = [[(1, 1), (0, 1)], [(0, 1), (2, 1)]]
    spec = LAFigureSpecs.eig_spec(A, normal=True)
    assert "lambda" in spec and spec["lambda"]
    assert "qvecs" in spec  # normal=True should populate qvecs


def test_svd_spec_accepts_tuple_rationals():
    import LAFigureSpecs

    A = [[(1, 1), (0, 1)], [(0, 1), (0, 1)]]
    spec = LAFigureSpecs.svd_spec(A)
    assert spec["sz"] == (2, 2)
    # For this A, the only nonzero singular value is 1.
    assert sym.simplify(spec["sigma"][0] - 1) == 0


def test_to_sympy_matrix_accepts_juliacall_arrayvalue_wrapper():
    """Simulate PythonCall/JuliaCall ArrayValue (1-based indexing)"""

    from LAFigureSpecs._sympy_utils import to_sympy_matrix

    class FakeArrayValue:
        __module__ = "juliacall"

        def __init__(self, data):
            self._data = data
            self.shape = (len(data), len(data[0]))

        def __getitem__(self, idx):
            # Expect idx either (i,j) 1-based, or i 1-based for 1D
            if isinstance(idx, tuple):
                i, j = idx
                if i < 1 or j < 1:
                    raise IndexError("1-based")
                return self._data[i - 1][j - 1]
            if idx < 1:
                raise IndexError("1-based")
            return self._data[idx - 1]

    A = FakeArrayValue([[1, 2], [3, 4]])
    M = to_sympy_matrix(A)
    assert M.shape == (2, 2)
    assert int(M[0, 0]) == 1
    assert int(M[1, 1]) == 4


def test_to_sympy_matrix_prefers_juliacall_indexing_over_numpy_hook():
    import numpy as np

    from LAFigureSpecs._sympy_utils import to_sympy_matrix

    class FakeArrayValue:
        __module__ = "juliacall"

        shape = (2, 2)

        def __getitem__(self, idx):
            i, j = idx
            return [[1, 2], [3, 4]][i - 1][j - 1]

        def to_numpy(self):
            return np.array([[99, 98], [97, 96]])

    M = to_sympy_matrix(FakeArrayValue())
    assert M == sym.Matrix([[1, 2], [3, 4]])


def test_to_sympy_matrix_accepts_juliacall_to_numpy_hook():
    import numpy as np

    from LAFigureSpecs._sympy_utils import to_sympy_matrix

    class FakeArrayValue:
        __module__ = "juliacall"

        def to_numpy(self):
            arr = np.empty((1, 2), dtype=object)
            arr[0, 0] = (1, 2)
            arr[0, 1] = (3, 4)
            return arr

    M = to_sympy_matrix(FakeArrayValue())
    assert M.shape == (1, 2)
    assert M[0, 0] == sym.Rational(1, 2)
    assert M[0, 1] == sym.Rational(3, 4)


def test_to_sympy_matrix_juliacall_vector_and_failure_fallbacks():
    import pytest

    from LAFigureSpecs._sympy_utils import to_sympy_col, to_sympy_matrix

    class FakeVectorValue:
        __module__ = "juliacall"

        shape = (2,)

        def __getitem__(self, idx):
            if idx < 1:
                raise IndexError("1-based")
            return (idx, idx + 1)

    class BadShapeValue:
        __module__ = "juliacall"
        shape = ("not", "ints")

    v = to_sympy_matrix(FakeVectorValue())
    assert list(v) == [sym.Rational(1, 2), sym.Rational(2, 3)]
    with pytest.raises(TypeError, match="Cannot convert object"):
        to_sympy_matrix(BadShapeValue())
    assert to_sympy_col(FakeVectorValue()).shape == (2, 1)


def test_to_sympy_matrix_numpy_tuple_vector_and_invalid_rhs():
    import pytest

    from LAFigureSpecs._sympy_utils import to_sympy_col, to_sympy_matrix

    v = np.empty((2,), dtype=object)
    v[0] = (1, 3)
    v[1] = (2, 5)
    M = to_sympy_matrix(v)
    assert M.shape == (2, 1)
    assert M[1, 0] == sym.Rational(2, 5)

    with pytest.raises(ValueError, match="rhs must be a vector"):
        to_sympy_col([[1, 2], [3, 4]])

    with pytest.raises(TypeError, match="Cannot convert object"):
        to_sympy_matrix(object())


def test_julia_symbol_normalization_in_convenience_wrappers():
    from LAFigureSpecs.convenience import _julia_str

    class FakeSymbol:
        __module__ = "juliacall"

        def __str__(self):
            return ":tight"

    class FakePyCallSymbol:
        __module__ = "pycall"

        def __str__(self):
            return "Symbol(:tight)"

    assert _julia_str(FakeSymbol()) == "tight"
    assert _julia_str(FakePyCallSymbol()) == "tight"


def test_convenience_tex_wrappers_smoke():
    import pytest

    pytest.importorskip("matrixlayout")
    import LAFigureSpecs

    A = [[1, 0], [0, 2]]
    tex_eig = LAFigureSpecs.eig_tex(A)
    assert "\\begin{tabular}" in tex_eig

    tex_svd = LAFigureSpecs.svd_tex([[1, 0], [0, 0]])
    assert "\\begin{tabular}" in tex_svd
