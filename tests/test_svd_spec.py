import sympy as sym


def _flatten_groups(groups):
    return [sym.Matrix(v) for g in groups for v in g]


def test_svd_spec_from_right_singular_vectors_matches_svd_tbl_spec():
    import LAFigureSpecs

    A = sym.Matrix([[1, 0], [0, 0]])  # rank-deficient
    expected = LAFigureSpecs.svd_tbl_spec(A)

    G = A.T * A  # Gramian; its eigenvectors are right singular vectors
    got = LAFigureSpecs.svd_tbl_spec_from_right_singular_vectors(A, G.eigenvects())

    assert got["sz"] == expected["sz"]
    assert got["lambda"] == expected["lambda"]
    assert got["sigma"] == expected["sigma"]
    assert got["ma"] == expected["ma"]

    # V should be n columns (flattened across groups)
    V_cols = _flatten_groups(got["qvecs"])
    assert len(V_cols) == A.cols
    assert all(v.shape == (A.cols, 1) for v in V_cols)

    # U should be m columns (flattened across groups + null(A^T) completion)
    U_cols = _flatten_groups(got["uvecs"])
    assert len(U_cols) == A.rows
    assert all(u.shape == (A.rows, 1) for u in U_cols)

    # Right singular vectors are orthonormal by construction.
    for i, v in enumerate(V_cols):
        assert sym.simplify(v.dot(v) - 1) == 0
        for w in V_cols[i + 1 :]:
            assert sym.simplify(v.dot(w)) == 0


def test_svd_spec_from_right_singular_vectors_orthonormal_full_rank_rectangular():
    import LAFigureSpecs

    A = sym.Matrix([[1, 2], [3, 4], [5, 6]])
    G = A.T * A
    got = LAFigureSpecs.svd_tbl_spec_from_right_singular_vectors(A, G.eigenvects())

    V_cols = _flatten_groups(got["qvecs"])
    assert len(V_cols) == A.cols
    for i, v in enumerate(V_cols):
        assert sym.simplify(v.dot(v) - 1) == 0
        for w in V_cols[i + 1 :]:
            assert sym.simplify(v.dot(w)) == 0


def test_svd_tbl_spec_sigma_sorted_and_scaled():
    import LAFigureSpecs

    A = sym.Matrix([[2, 0], [0, 1]])
    spec = LAFigureSpecs.svd_tbl_spec(A)
    sigmas = spec["sigma"]
    assert len(sigmas) == len(spec["lambda"])
    assert sigmas == sorted(sigmas, reverse=True)

    spec_scaled = LAFigureSpecs.svd_tbl_spec(A, Ascale=2)
    sigmas_scaled = spec_scaled["sigma"]
    assert len(sigmas_scaled) == len(sigmas)
    for s, s_scaled in zip(sigmas, sigmas_scaled, strict=False):
        assert sym.simplify(s_scaled * 2 - s) == 0


def test_svd_spec_from_right_singular_vectors_respects_Ascale():
    import LAFigureSpecs

    A = sym.Matrix([[2, 0], [0, 1]])
    G = A.T * A
    got = LAFigureSpecs.svd_tbl_spec_from_right_singular_vectors(A, G.eigenvects(), Ascale=2)
    expected = LAFigureSpecs.svd_tbl_spec(A, Ascale=2)
    assert got["sigma"] == expected["sigma"]


def test_svd_spec_simplifies_rectangular_full_rank_vectors():
    import LAFigureSpecs

    A = sym.Matrix([[1, 2], [3, 4], [5, 6]])
    spec = LAFigureSpecs.svd_tbl_spec(A)

    sigma0 = spec["sigma"][0]
    assert sym.simplify(sigma0**2 - spec["lambda"][0]) == 0

    V_cols = _flatten_groups(spec["qvecs"])
    U_cols = _flatten_groups(spec["uvecs"])
    assert all(sym.simplify(v.dot(v) - 1) == 0 for v in V_cols)
    assert all(sym.simplify(u.dot(u) - 1) == 0 for u in U_cols)

    # The displayed vectors should keep a readable quotient-style exact form,
    # not the fully exploded product-of-radicals entries from plain radsimp().
    assert V_cols[0][1] == 44 * sym.sqrt(2) / sym.sqrt(8185 - 21 * sym.sqrt(8185))
    assert U_cols[0][0] == (sym.sqrt(8185) + 155) / (
        sym.sqrt(8185 - 21 * sym.sqrt(8185)) * sym.sqrt(sym.sqrt(8185) + 91)
    )
