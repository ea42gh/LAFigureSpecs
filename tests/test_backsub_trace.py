def test_backsubstitution_tex_has_base_and_steps():
    from la_figures import backsubstitution_tex

    # System with one free variable (x_3)
    A = [[1, 0, 1], [0, 1, 1]]
    b = [1, 2]
    lines = backsubstitution_tex(A, b)

    text = "\n".join(lines)
    assert "x_3" in text
    assert r"\alpha_3" in text
    assert "x_2 =" in text
    assert "x_1 =" in text


def test_backsubstitution_full_rank_uses_last_pivot_base():
    from la_figures import backsubstitution_tex, standard_solution_tex

    A = [[2, 1], [0, -3]]
    b = [5, 6]

    lines = backsubstitution_tex(A, b, var_name="u", param_name=r"\tau")
    text = "\n".join(lines)

    assert "u_2" in text
    assert r"\tau" not in text
    assert r"- \frac{1}{3}" in text

    solution = standard_solution_tex(A, b, var_name="u")
    assert r"\begin{pNiceArray}{r} u_1 \\  u_2\end{pNiceArray}" in solution
    assert r"\alpha" not in solution


def test_backsubstitution_without_rhs_uses_homogeneous_base():
    from la_figures.backsub import backsubstitution_tex

    lines = backsubstitution_tex([[1, 2, 0], [0, 0, 1]], var_name="z", param_name=r"\beta")
    text = "\n".join(lines)

    assert "z_2 = \\beta_2" in text
    assert "z_3 =" in text
    assert "z_1 =" in text


def test_linear_system_tex_handles_zero_and_symbolic_rows():
    import sympy as sym

    from la_figures import linear_system_tex

    a = sym.Symbol("a")
    tex = linear_system_tex([[0, 0], [a, -1]], [3, 4], var_name="y")

    assert "0  = 3" in tex
    assert r"ay_1" in tex
    assert r"- y_2" in tex


def test_backsub_helpers_reject_missing_inputs():
    import pytest

    from la_figures import linear_system_tex, standard_solution_tex
    from la_figures.backsub import backsubstitution_tex

    with pytest.raises(ValueError, match="ref_A"):
        backsubstitution_tex(None)
    with pytest.raises(ValueError, match="A and b"):
        linear_system_tex([[1]], None)
    with pytest.raises(ValueError, match="ref_A and ref_rhs"):
        standard_solution_tex(None, [1])
