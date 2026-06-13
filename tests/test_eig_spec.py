import sympy as sym


def _flatten_groups(groups):
    return [sym.Matrix(v) for g in groups for v in g]


def test_eig_spec_from_eigenvects_matches_eig_spec():
    import LAFigureSpecs

    A = sym.Matrix([[2, 0], [0, 1]])
    expected = LAFigureSpecs.eig_spec(A)
    got = LAFigureSpecs.eig_spec_from_eigenvects(A.eigenvects())

    assert got["lambda"] == expected["lambda"]
    assert got["ma"] == expected["ma"]

    # Compare eigenvector entries (diagonal matrix gives canonical basis vectors).
    got_vecs = [v.tolist() for v in _flatten_groups(got["evecs"])]
    exp_vecs = [v.tolist() for v in _flatten_groups(expected["evecs"])]
    assert got_vecs == exp_vecs


def test_eig_spec_normal_adds_orthonormal_basis():
    import LAFigureSpecs

    A = sym.Matrix([[2, 0], [0, 1]])
    spec = LAFigureSpecs.eig_spec(A, normal=True)
    assert "qvecs" in spec
    assert len(spec["qvecs"]) == len(spec["evecs"])

    # Each q vector should have unit norm.
    for v in _flatten_groups(spec["qvecs"]):
        assert sym.simplify(v.dot(v) - 1) == 0


def test_eigendecomposition_to_spec_roundtrips():
    import LAFigureSpecs

    A = sym.Matrix([[2, 0], [0, 1]])
    dec = LAFigureSpecs.eigendecomposition(A, normal=True)
    assert dec.to_spec() == LAFigureSpecs.eig_spec(A, normal=True)


def test_eig_spec_order_sympy_is_reverse_of_default_descending_for_numeric_values():
    import LAFigureSpecs

    A = sym.Matrix([[2, 0], [0, 1]])
    default_order = LAFigureSpecs.eig_spec(A)
    descending = LAFigureSpecs.eig_spec_from_eigenvects(A.eigenvects(), order="descending")
    sympy_order = LAFigureSpecs.eig_spec_from_eigenvects(A.eigenvects(), order="sympy")
    assert descending == default_order
    assert list(reversed(default_order["lambda"])) == sympy_order["lambda"]


def test_eig_spec_descending_order_uses_scaled_display_values():
    import LAFigureSpecs

    A = sym.Matrix([[2, 0], [0, 1]])
    spec = LAFigureSpecs.eig_spec_from_eigenvects(A.eigenvects(), Ascale=-1, order="descending")

    assert spec["lambda"] == [-1, -2]


def test_eig_spec_order_rejects_removed_old_names():
    import pytest

    import LAFigureSpecs

    A = sym.Matrix([[2, 0], [0, 1]])
    with pytest.raises(ValueError, match="descending"):
        LAFigureSpecs.eig_spec_from_eigenvects(A.eigenvects(), order="legacy")
    with pytest.raises(ValueError, match="descending"):
        LAFigureSpecs.eig_spec_from_eigenvects(A.eigenvects(), order="reverse_sympy")
