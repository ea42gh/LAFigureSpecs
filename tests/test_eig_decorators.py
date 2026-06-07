import sympy as sym


def test_eig_tbl_tex_decorates_eigenbasis_entry():
    from LAFigureSpecs import eig_tbl_tex

    A = sym.Matrix([[2]])

    def dec(tex: str) -> str:
        return rf"\boxed{{{tex}}}"

    tex = eig_tbl_tex(
        A,
        formatter=sym.latex,
        decorators=[{"target": "eigenbasis", "entries": [(0, 0, 0)], "decorator": dec}],
        body_preamble="",
    )

    assert r"\boxed{1}" in tex or r"\boxed{1.0}" in tex


def test_svd_tbl_tex_decorates_sigma_matrix_entry():
    from LAFigureSpecs import svd_tbl_tex

    A = sym.Matrix([[3, 0], [0, 0]])

    def dec(tex: str) -> str:
        return rf"\boxed{{{tex}}}"

    tex = svd_tbl_tex(
        A,
        formatter=sym.latex,
        decorators=[{"matrix": "sigma", "entries": [(0, 0)], "decorator": dec}],
        body_preamble="",
    )

    assert r"\boxed" in tex


def test_eig_tbl_spec_as_scale_inference_matches_explicit():
    from LAFigureSpecs.eig import eig_tbl_spec, _factor_out_denominator

    A = sym.Matrix([[sym.Rational(1, 2), 0], [0, sym.Rational(3, 4)]])
    d, _ = _factor_out_denominator(A)

    spec_inferred = eig_tbl_spec(A, Ascale=None)
    spec_explicit = eig_tbl_spec(A, Ascale=d)

    assert spec_inferred["lambda"] == spec_explicit["lambda"]
    assert spec_inferred["evecs"] == spec_explicit["evecs"]


def test_eig_tbl_tex_default_case_includes_S_matrix():
    from LAFigureSpecs import eig_tbl_tex

    A = sym.Matrix([[1, 0], [0, 2]])
    tex = eig_tbl_tex(A, body_preamble="")
    assert "S" in tex


def test_eig_tbl_tex_includes_lambda_and_S_labels():
    from LAFigureSpecs import eig_tbl_tex

    A = sym.Matrix([[1, 0], [0, 2]])
    tex = eig_tbl_tex(A, body_preamble="")
    assert r"\Lambda" in tex
    assert r"S" in tex


def test_svd_tbl_tex_includes_sigma_v_u_labels():
    from LAFigureSpecs import svd_tbl_tex

    A = sym.Matrix([[1, 0], [0, 2]])
    tex = svd_tbl_tex(A, body_preamble="")
    assert r"\Sigma" in tex
    assert r"V" in tex
    assert r"U" in tex
