def test_show_ge_methods_use_backsubst(monkeypatch):
    import LAFigureSpecs

    captured = {}

    def fake_backsubst_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.backsubst.backsubst_svg", fake_backsubst_svg)

    A = [[1, 0], [0, 1]]
    b = [[1], [2]]
    show = LAFigureSpecs.ShowGE(A, b)
    show.show_system()
    assert captured["show_system"] is True
    assert captured["show_cascade"] is False
    assert captured["show_solution"] is False


def test_top_level_show_ge_wrappers_delegate_to_instance_methods(monkeypatch):
    import LAFigureSpecs

    calls = []

    class DummyShow:
        def ref(self, *, gj=None, pivoting=None):
            calls.append(("ref", gj, pivoting))
            return "ref-ok"

        def show_layout(self, **render_opts):
            calls.append(("show_layout", render_opts))
            return "layout-ok"

        def show_system(self, *, var_name="x", **render_opts):
            calls.append(("show_system", var_name, render_opts))
            return "system-ok"

        def show_backsubstitution(self, *, var_name="x", param_name=r"\alpha", **render_opts):
            calls.append(("show_backsubstitution", var_name, param_name, render_opts))
            return "backsub-ok"

        def show_solution(self, *, b_col=None, var_name="x", param_name=r"\alpha", **render_opts):
            calls.append(("show_solution", b_col, var_name, param_name, render_opts))
            return "solution-ok"

        def lhs_matrix(self, *, step="final"):
            calls.append(("lhs_matrix", step))
            return "lhs-ok"

        def rhs_matrix(self, *, step="final"):
            calls.append(("rhs_matrix", step))
            return "rhs-mat-ok"

        def rhs_column(self, b_col=0, *, step="final"):
            calls.append(("rhs_column", b_col, step))
            return "rhs-col-ok"

        def rhs_block(self, *, step="final", b_col=None):
            calls.append(("rhs_block", step, b_col))
            return "rhs-ok"

        def solve(self, *, gj=None):
            calls.append(("solve", gj))
            return {"particular": "xp", "homogeneous": "xh"}

    show = DummyShow()

    assert LAFigureSpecs.ref(show, gj=True, pivoting="partial") == "ref-ok"
    assert LAFigureSpecs.show_layout(show, crop="tight") == "layout-ok"
    assert LAFigureSpecs.show_system(show, var_name="y", crop="tight") == "system-ok"
    assert LAFigureSpecs.show_backsubstitution(show, var_name="y", param_name="β") == "backsub-ok"
    assert LAFigureSpecs.show_solution(show, b_col=1, var_name="y", param_name="β") == "solution-ok"
    assert LAFigureSpecs.lhs_matrix(show, step=1) == "lhs-ok"
    assert LAFigureSpecs.rhs_matrix(show, step=2) == "rhs-mat-ok"
    assert LAFigureSpecs.rhs_column(show, 0, step=2) == "rhs-col-ok"
    assert LAFigureSpecs.rhs_block(show, step=2, b_col=0) == "rhs-ok"
    assert LAFigureSpecs.solutions(show, gj=False) == ("xp", "xh")

    assert calls == [
        ("ref", True, "partial"),
        ("show_layout", {"crop": "tight"}),
        ("show_system", "y", {"crop": "tight"}),
        ("show_backsubstitution", "y", "β", {}),
        ("show_solution", 1, "y", "β", {}),
        ("lhs_matrix", 1),
        ("rhs_matrix", 2),
        ("rhs_column", 0, 2),
        ("rhs_block", 2, 0),
        ("solve", False),
    ]


def test_show_ge_show_solution_selects_rhs_column(monkeypatch):
    import LAFigureSpecs
    import sympy as sym

    captured = {}

    def fake_standard_solution_tex(ref_A, ref_rhs, *, var_name="x", param_name=r"\alpha"):
        captured["ref_A"] = ref_A
        captured["ref_rhs"] = ref_rhs
        captured["var_name"] = var_name
        captured["param_name"] = param_name
        return "solution-ok"

    def fake_backsubst_svg(**kwargs):
        captured["render_opts"] = kwargs
        return "<svg/>"

    def fake_show_svg(svg):
        captured["svg"] = svg
        return "<display/>"

    monkeypatch.setattr("LAFigureSpecs.show_ge.standard_solution_tex", fake_standard_solution_tex)
    monkeypatch.setattr("matrixlayout.backsubst.backsubst_svg", fake_backsubst_svg)
    monkeypatch.setattr("LAFigureSpecs.show_ge._show_svg", fake_show_svg)

    A = sym.Matrix([[1, 0], [0, 1]])
    b = sym.Matrix([[1, 2], [3, 4]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True)
    show.ref()

    result = show.show_solution(b_col=1, var_name="y", param_name="β", crop="tight")
    assert result == "<display/>"
    assert captured["ref_rhs"] == sym.Matrix([[2], [4]])
    assert captured["var_name"] == "y"
    assert captured["param_name"] == "β"
    assert captured["render_opts"]["solution_txt"] == "solution-ok"
    assert captured["svg"] == "<svg/>"


def test_show_ge_show_solution_requires_b_col_for_multi_rhs():
    import LAFigureSpecs
    import pytest
    import sympy as sym

    A = sym.Matrix([[1, 0], [0, 1]])
    b = sym.Matrix([[1, 2], [3, 4]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True)
    show.ref()

    with pytest.raises(ValueError, match="requires b_col"):
        show.show_solution()


def test_show_ge_solve_returns_particular_and_homogeneous():
    import LAFigureSpecs
    import sympy as sym

    A = sym.Matrix([[1, 1], [0, 0]])
    b = sym.Matrix([[1], [0]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True)
    sol = show.solve()

    assert sol["pivot_cols"] == [0]
    assert sol["free_cols"] == [1]
    assert sol["particular"].shape == (2, 1)
    assert len(sol["homogeneous"]) == 1


def test_show_ge_ref_updates_trace_and_layers():
    import LAFigureSpecs
    import sympy as sym

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = LAFigureSpecs.ShowGE(A, b)
    show.ref(gj=True, pivoting="none")
    assert show.trace() is not None
    mats = show.matrices()
    assert mats and mats[-1][1] is not None


def test_show_ge_show_ref_alias():
    import LAFigureSpecs
    import sympy as sym

    A = sym.Matrix([[1, 0], [0, 1]])
    b = sym.Matrix([[1], [0]])
    show = LAFigureSpecs.ShowGE(A, b)
    show.show_ref(gj=True, pivoting=None)
    assert show.trace() is not None


def test_show_ge_normal_eq_layers_include_at_and_ata():
    import LAFigureSpecs
    import sympy as sym

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = LAFigureSpecs.ShowGE(A, b, normal_eq=True)
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
    import LAFigureSpecs
    import sympy as sym

    captured = {}

    def fake_backsubst_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.backsubst.backsubst_svg", fake_backsubst_svg)

    A = sym.Matrix([[1, 0], [0, 0]])
    b = sym.Matrix([[1, 0], [1, 0]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True)
    show.ref()

    assert show.rhs_status == ["inconsistent", "consistent"]
    assert show.rhs_consistent == [False, True]
    assert show.status == "mixed"

    show.show_backsubstitution()
    assert captured["show_cascade"] is True


def test_show_ge_normal_eq_name_specs(monkeypatch):
    import LAFigureSpecs
    import sympy as sym

    captured = {}

    def fake_ge(mats, **kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("LAFigureSpecs.ge_convenience.ge", fake_ge)

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True, normal_eq=True)
    show.ref()
    show.show_layout()

    array_names = captured.get("array_names")
    assert isinstance(array_names, dict)
    specs = array_names.get("name_specs") or []
    labels = [entry[2] for entry in specs]
    assert any("A^T" in lbl for lbl in labels)


def test_show_ge_layout_uses_full_stack(monkeypatch):
    import LAFigureSpecs
    import sympy as sym

    captured = {"legacy": 0}

    def fake_ge(mats, **kwargs):
        captured["legacy"] += 1
        captured["mats_len"] = len(mats)
        return "<svg/>"

    def fail_ge_tbl_svg(*args, **kwargs):
        raise RuntimeError("ge_tbl_svg should not be called when full stack is available")

    monkeypatch.setattr("LAFigureSpecs.ge_convenience.ge", fake_ge)
    monkeypatch.setattr("LAFigureSpecs.show_ge.ge_tbl_svg", fail_ge_tbl_svg)

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True)
    show.ref()
    show.show_layout()

    assert captured["legacy"] == 1
    assert captured["mats_len"] > 1


def test_show_ge_layout_forwards_python_decorate_ge_backgrounds(monkeypatch):
    import LAFigureSpecs
    import sympy as sym

    captured = {}

    def fake_ge(mats, **kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("LAFigureSpecs.ge_convenience.ge", fake_ge)

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True)
    show.ref()
    show.show_layout()

    assert captured.get("bg_for_entries")


def test_show_ge_rhs_block_accessor():
    import LAFigureSpecs
    import sympy as sym

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True)
    show.ref()

    rhs = show.rhs_block()
    assert rhs.shape == (2, 1)

    col = show.rhs_block(b_col=0)
    assert col.shape == (2, 1)


def test_show_ge_lhs_rhs_accessors():
    import LAFigureSpecs
    import sympy as sym

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True)
    show.ref()

    lhs = show.lhs_matrix()
    rhs = show.rhs_matrix()
    col = show.rhs_column()

    assert lhs.shape == (2, 2)
    assert rhs.shape == (2, 1)
    assert col.shape == (2, 1)
    assert lhs == show.matrices()[-1][1][:, :-1]
    assert rhs == show.matrices()[-1][1][:, -1:]
    assert col == rhs


def test_show_ge_homogeneous_returns_zero_vector_when_full_rank():
    import LAFigureSpecs
    import sympy as sym

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    show = LAFigureSpecs.ShowGE(A, b, gj=True)
    sol = show.solve()

    homog = sol["homogeneous"]
    assert len(homog) == 1
    assert homog[0] == sym.zeros(A.shape[1], 1)


def test_show_ge_default_array_names(monkeypatch):
    import LAFigureSpecs

    captured = {}

    def fake_ge_tbl_svg(*args, **kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("LAFigureSpecs.show_ge.ge_tbl_svg", fake_ge_tbl_svg)

    show = LAFigureSpecs.ShowGE([[1, 0], [0, 1]])
    show.ref()
    show.show_layout()
    assert captured["array_names"] == ["E", "A"]

    captured.clear()
    show2 = LAFigureSpecs.ShowGE([[1, 0], [0, 1]], [[1], [2]])
    show2.ref()
    show2.show_layout()
    assert captured["array_names"] == ["E", ["A", "b"]]

    captured.clear()
    show3 = LAFigureSpecs.ShowGE([[1, 0], [0, 1]], [[1, 0], [2, 0]])
    show3.ref()
    show3.show_layout()
    assert captured["array_names"] == ["E", ["A", "B"]]
