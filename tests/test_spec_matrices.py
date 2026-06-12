import sympy as sym

import LAFigureSpecs


def test_eig_matrices_from_spec_basic():
    A = sym.Matrix([[2, 0], [0, 3]])
    spec = LAFigureSpecs.eig_spec(A)
    lam, vecs = LAFigureSpecs.eig_matrices_from_spec(spec)
    assert lam.shape == (2, 2)
    assert vecs.shape == (2, 2)
    assert list(lam.diagonal()) == [3, 2] or list(lam.diagonal()) == [2, 3]


def test_svd_matrices_from_spec_reduced_rank():
    A = sym.Matrix([[3, 0], [0, 0]])
    spec = LAFigureSpecs.svd_spec(A)
    U, S, V, rank = LAFigureSpecs.svd_matrices_from_spec(spec)
    assert rank == 1
    assert S.shape == (1, 1)
    assert list(S.diagonal()) == [3]
    assert U.shape[1] == 1
    assert V.shape[1] == 1


def test_qr_matrices_from_grid():
    A = sym.Matrix([[1, 0], [0, 1]])
    mats = LAFigureSpecs.gram_schmidt_qr_matrices(A)
    out = LAFigureSpecs.qr_matrices_from_grid(mats)
    assert out["A"] == A
    assert out["R"] == sym.Matrix([[1, 0], [0, 1]])
    out_dict = LAFigureSpecs.qr_matrices_dict_from_grid(mats)
    assert out_dict["A"] == A


def test_qr_factorization_rational_3x3():
    A = sym.Matrix(
        [
            [sym.Rational(1, 2), sym.Rational(2, 3), sym.Rational(3, 4)],
            [sym.Rational(4, 5), sym.Rational(5, 6), sym.Rational(6, 7)],
            [sym.Rational(7, 8), sym.Rational(8, 9), sym.Rational(9, 10)],
        ]
    )
    mats = LAFigureSpecs.gram_schmidt_qr_matrices(A, allow_rank_deficient=True)
    out = LAFigureSpecs.qr_matrices_from_grid(mats)
    Q = out["Q"]
    R = out["R"]
    assert A.equals(Q * R)
