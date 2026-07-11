def test_backsubstitution_tex_has_base_and_steps():
    from LAFigureSpecs import backsubstitution_tex

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
    from LAFigureSpecs import backsubstitution_tex, standard_solution_tex

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
    from LAFigureSpecs.backsub import backsubstitution_tex

    lines = backsubstitution_tex([[1, 2, 0], [0, 0, 1]], var_name="z", param_name=r"\beta")
    text = "\n".join(lines)

    assert "z_2 = \\beta_2" in text
    assert "z_3 =" in text
    assert "z_1 =" in text


def test_linear_system_tex_handles_zero_and_symbolic_rows():
    import sympy as sym

    from LAFigureSpecs import linear_system_tex

    a = sym.Symbol("a")
    tex = linear_system_tex([[0, 0], [a, -1]], [3, 4], var_name="y")

    assert "0  = 3" in tex
    assert r"ay_1" in tex
    assert r"- y_2" in tex


def test_linear_system_tex_handles_juliacall_encoded_rationals_without_vector_terms():
    from LAFigureSpecs import linear_system_tex

    class FakeTupleValue:
        __module__ = "juliacall"

        def __init__(self, *items):
            self._items = items

        def __len__(self):
            return len(self._items)

        def __getitem__(self, idx):
            if idx < 1:
                raise IndexError("1-based")
            return self._items[idx - 1]

    class FakeArrayValue:
        __module__ = "juliacall"

        def __init__(self, data):
            self._data = data
            self.shape = (len(data), len(data[0]))

        def __getitem__(self, idx):
            i, j = idx
            return self._data[i - 1][j - 1]

    A = FakeArrayValue(
        [
            [FakeTupleValue(1, 1), FakeTupleValue(-2, 1)],
            [FakeTupleValue(3, 2), FakeTupleValue(0, 1)],
        ]
    )
    b = FakeArrayValue([[FakeTupleValue(4, 1)], [FakeTupleValue(-5, 2)]])

    tex = linear_system_tex(A, b)

    assert r"\systeme" in tex
    assert r"\cr" not in tex
    assert r"\left" not in tex
    assert r"\right" not in tex
    assert r"\frac{3}{2}" in tex
    assert r"\frac{5}{2}" in tex


def test_backsub_helpers_reject_missing_inputs():
    import pytest

    from LAFigureSpecs import linear_system_tex, standard_solution_tex
    from LAFigureSpecs.backsub import backsubstitution_tex

    with pytest.raises(ValueError, match="ref_A"):
        backsubstitution_tex(None)
    with pytest.raises(ValueError, match="A and b"):
        linear_system_tex([[1]], None)
    with pytest.raises(ValueError, match="ref_A and rhs"):
        standard_solution_tex(None, [1])
