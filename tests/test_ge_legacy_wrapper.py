import sympy as sym


def test_legacy_pivot_list_to_pivot_locs():
    from LAFigureSpecs.ge_convenience import _legacy_pivot_list_to_pivot_locs

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]

    pivot_list = [
        ((1, 1), [(0, 0), (1, 1)]),
    ]

    pivot_locs = _legacy_pivot_list_to_pivot_locs(matrices, pivot_list, index_base=1, pivot_style="draw=red")
    assert pivot_locs == [
        ("(3-3)(3-3)", "draw=red"),
        ("(4-4)(4-4)", "draw=red"),
    ]


def test_ge_legacy_wrapper_rejects_unsupported_options(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge
    from matrixlayout import ge as ml_ge

    A = sym.Matrix([[1, 2], [3, 4]])
    monkeypatch.setattr(ml_ge, "render_ge_svg", lambda **kwargs: "<svg/>")

    assert ge([[None, A]], func=lambda m: m) == "<svg/>"


def test_ge_legacy_wrapper_supports_backgrounds_and_comments():
    from LAFigureSpecs.convenience_ge import ge
    from matrixlayout import ge as ml_ge

    A = sym.Matrix([[1, 2], [3, 4]])
    matrices = [[None, A]]

    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        out = ge(
            matrices,
            bg_for_entries=[(0, 1, [(0, 0)], "red!15", 0)],
            comment_list=["note"],
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["codebefore"]
    assert captured["txt_with_locs"]


def test_ge_legacy_wrapper_forwards_structured_decorations(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge
    from matrixlayout import ge as ml_ge

    A = sym.Matrix([[1, 2], [3, 4]])
    matrices = [[None, A]]
    decorations = [
        {
            "grid": (0, 1),
            "rows": (0, 0),
            "cols": (0, 3),
            "background": "yellow!35",
            "padding_pt": 1,
        }
    ]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_svg)

    out = ge(matrices, decorations=decorations)

    assert out == "<svg/>"
    assert captured["decorations"] == decorations
    assert captured["format_nrhs"] is True


def test_ge_legacy_wrapper_supports_ref_path_list():
    from LAFigureSpecs.convenience_ge import ge
    from matrixlayout import ge as ml_ge

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]

    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        out = ge(
            matrices,
            ref_path_list=[(1, 1, [(0, 0), (1, 1)], "hh")],
            output_dir="tmp",
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["rowechelon_paths"]


def test_ge_legacy_wrapper_supports_variable_summary():
    from LAFigureSpecs.convenience_ge import ge
    from matrixlayout import ge as ml_ge

    A = sym.Matrix([[1, 2], [3, 4]])
    matrices = [[None, A]]

    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        out = ge(
            matrices,
            variable_summary=[True, False],
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["variable_labels"]


def test_ge_legacy_wrapper_supports_array_names():
    from LAFigureSpecs.convenience_ge import ge
    from matrixlayout import ge as ml_ge

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]

    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        out = ge(
            matrices,
            array_names=["E", ["A", "b"]],
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["callouts"]


def test_ge_legacy_wrapper_rhs_callout_labels_follow_rhs_size():
    from LAFigureSpecs.convenience_ge import ge
    from matrixlayout import ge as ml_ge

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]

    def _extract_labels(callouts):
        return [c.get("label", "") for c in callouts or []]

    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        ge(matrices, array_names=True, Nrhs=1)
        labels = _extract_labels(captured.get("callouts"))
        assert any(r"\mid  b" in label for label in labels)

        captured.clear()
        ge(matrices, array_names=True, Nrhs=2)
        labels = _extract_labels(captured.get("callouts"))
        assert any(r"\mid  B" in label for label in labels)

        captured.clear()
        ge(matrices, array_names=["E", ["A", "b"]], Nrhs=2)
        labels = _extract_labels(captured.get("callouts"))
        assert any(r"\mid  b" in label for label in labels)
    finally:
        ml_ge.render_ge_svg = ge_svg_orig


def test_ge_legacy_wrapper_supports_canonical_n_rhs_keyword():
    from LAFigureSpecs.convenience_ge import ge
    from matrixlayout import ge as ml_ge

    matrices = [[None, sym.Matrix([[1, 2, 3], [4, 5, 6]])]]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        assert ge(matrices, n_rhs=1) == "<svg/>"
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert captured["n_rhs"] == 1
