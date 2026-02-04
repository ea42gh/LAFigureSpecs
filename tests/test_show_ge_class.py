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
