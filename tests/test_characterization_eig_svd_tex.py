import sympy as sym


def _render_eig_tex_for_spec(spec, *, case: str) -> str:
    from matrixlayout import render_eig_tex

    return render_eig_tex(spec, case=case, formatter=sym.latex)


def _assert_common_table_tex(tex: str) -> None:
    assert r"\begin{tabular}" in tex
    assert r"\toprule" in tex
    assert r"\bottomrule" in tex
    assert r"\end{tabular}" in tex


def test_eigenproblem_tex_contains_current_table_structure():
    from LAFigureSpecs import eig_spec

    tex = _render_eig_tex_for_spec(eig_spec(sym.Matrix([[2, 0], [0, 3]])), case="S")

    _assert_common_table_tex(tex)
    assert r"$\color{blue}{\lambda}$ & $3$ &  & $2$" in tex
    assert r"$\color{blue}{m_a}$ & $1$ &  & $1$" in tex
    assert r"\color{blue}{ \Lambda =}" in tex
    assert r"\color{blue}{ S = }" in tex


def test_svd_tex_contains_rank_deficient_zero_singular_column():
    from LAFigureSpecs import svd_spec

    tex = _render_eig_tex_for_spec(svd_spec(sym.Matrix([[3, 0], [0, 0]])), case="SVD")

    _assert_common_table_tex(tex)
    assert r"$\color{blue}{\sigma}$ & $3$ &  & $$" in tex
    assert r"$\color{blue}{\lambda}$ & $9$ &  & $0$" in tex
    assert r"\color{blue}{ \Sigma =}" in tex
    assert r"\color{blue}{ U = }" in tex
    assert r"\color{blue}{ V = }" in tex


def test_svd_tex_contains_rectangular_full_rank_table():
    from LAFigureSpecs import svd_spec

    tex = _render_eig_tex_for_spec(svd_spec(sym.Matrix([[1, 2], [3, 4], [5, 6]])), case="SVD")

    _assert_common_table_tex(tex)
    assert r"$\color{blue}{\sigma}$" in tex
    assert r"\sqrt{8185}" in tex
    assert r"\color{blue}{ \Sigma =}" in tex
    assert r"\color{blue}{ U = }" in tex
    assert r"\color{blue}{ V = }" in tex


def test_svd_tex_contains_wide_matrix_padding_column():
    from LAFigureSpecs import svd_spec

    tex = _render_eig_tex_for_spec(svd_spec(sym.Matrix([[1, 2, 3], [4, 5, 6]])), case="SVD")

    _assert_common_table_tex(tex)
    assert r"\begin{tabular}{@{}lccccc@{}}" in tex
    assert r"\sqrt{8065}" in tex
    assert r"&  & $$" in tex


def test_svd_tex_with_Ascale_keeps_scaled_a_column():
    from LAFigureSpecs import svd_spec

    tex = _render_eig_tex_for_spec(svd_spec(sym.Matrix([[2, 0], [0, 1]]), Ascale=sym.Integer(2)), case="SVD")

    _assert_common_table_tex(tex)
    assert r"$\color{blue}{\sigma}$ & $1$ &  & $\frac{1}{2}$" in tex
    assert r"$\color{blue}{\lambda}$ & $1$ &  & $\frac{1}{4}$" in tex
    assert r"\color{blue}{ \Sigma =}" in tex
