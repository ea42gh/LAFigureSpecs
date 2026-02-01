import sympy as sym

import la_figures


def test_eig_matrices_from_spec_basic():
    A = sym.Matrix([[2, 0], [0, 3]])
    spec = la_figures.eig_tbl_spec(A)
    lam, vecs = la_figures.eig_matrices_from_spec(spec)
    assert lam.shape == (2, 2)
    assert vecs.shape == (2, 2)
    assert list(lam.diagonal()) == [3, 2] or list(lam.diagonal()) == [2, 3]


def test_svd_matrices_from_spec_reduced_rank():
    A = sym.Matrix([[3, 0], [0, 0]])
    spec = la_figures.svd_tbl_spec(A)
    U, S, V, rank = la_figures.svd_matrices_from_spec(spec)
    assert rank == 1
    assert S.shape == (1, 1)
    assert list(S.diagonal()) == [3]
    assert U.shape[1] == 1
    assert V.shape[1] == 1


def test_qr_matrices_from_grid():
    A = sym.Matrix([[1, 0], [0, 1]])
    W = sym.Matrix([[1, 0], [0, 1]])
    mats = la_figures.gram_schmidt_qr_matrices(A, W)
    out = la_figures.qr_matrices_from_grid(mats)
    assert out["A"] == A
    assert out["W"] == W
    assert out["R"] == sym.Matrix([[1, 0], [0, 1]])
