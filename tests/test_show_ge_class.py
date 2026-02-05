def test_show_ge_methods_use_backsubst(monkeypatch):
    import la_figures

    captured = {}

    def fake_backsubst_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.backsubst.backsubst_svg", fake_backsubst_svg)

    A = [[1, 0], [0, 1]]
    b = [[1], [2]]
    show = la_figures.ShowGE(A, b)
    show.show_system()
    assert captured["show_system"] is True
    assert captured["show_cascade"] is False
    assert captured["show_solution"] is False


def test_show_ge_solve_returns_particular_and_homogeneous():
    import la_figures
    import sympy as sym

    A = sym.Matrix([[1, 1], [0, 0]])
    b = sym.Matrix([[1], [0]])
    show = la_figures.ShowGE(A, b, gj=True)
    sol = show.solve()

    assert sol["pivot_cols"] == [0]
    assert sol["free_cols"] == [1]
    assert sol["particular"].shape == (2, 1)
    assert len(sol["homogeneous"]) == 1


def test_show_ge_ref_updates_trace_and_layers():
    import la_figures
    import sympy as sym

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = la_figures.ShowGE(A, b)
    show.ref(gj=True, pivoting="none")
    assert show.trace() is not None
    mats = show.matrices()
    assert mats and mats[-1][1] is not None


def test_show_ge_show_ref_alias():
    import la_figures
    import sympy as sym

    A = sym.Matrix([[1, 0], [0, 1]])
    b = sym.Matrix([[1], [0]])
    show = la_figures.ShowGE(A, b)
    show.show_ref(gj=True, pivoting=None)
    assert show.trace() is not None


def test_show_ge_normal_eq_layers_include_at_and_ata():
    import la_figures
    import sympy as sym

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = la_figures.ShowGE(A, b, normal_eq=True)
    show.ref()
    mats = show.matrices()
    assert mats
    A_aug = A.row_join(b)
    At = A.T
    AtA_aug = (At * A).row_join(At * b)
    assert mats[0][1] == A_aug
    assert mats[1][0] == At
    assert mats[1][1] == AtA_aug


def test_show_ge_inconsistent_rhs_status_and_solution(monkeypatch):
    import la_figures
    import sympy as sym

    captured = {}

    def fake_backsubst_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.backsubst.backsubst_svg", fake_backsubst_svg)

    A = sym.Matrix([[1, 0], [0, 0]])
    b = sym.Matrix([[1, 0], [1, 0]])
    show = la_figures.ShowGE(A, b, gj=True)
    show.ref()

    assert show.rhs_status == ["inconsistent", "consistent"]
    assert show.status == "mixed"

    show.show_backsubstitution()
    assert captured["show_cascade"] is True
    assert captured["show_solution"] is False
    cascade_txt = captured.get("cascade_txt") or []
    assert cascade_txt
    assert "0 =" in cascade_txt[0]
    assert "No Solution" in cascade_txt[1]

    assert show.show_solution() == []
