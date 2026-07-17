import sympy as sym


def test_legacy_pivot_list_to_pivot_locs():
    from LAFigureSpecs._ge_legacy_compat import _legacy_pivot_list_to_pivot_locs

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


def test_structured_rowechelon_paths_match_legacy_ref_path_list(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_svg
    from matrixlayout import ge as ml_ge

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_svg)

    ge_svg(
        matrices,
        rowechelon_paths=[{"grid": (1, 1), "pivots": [(0, 0), (1, 1)], "case": "hh", "color": "red"}],
    )
    structured_paths = list(captured["rowechelon_paths"])

    captured.clear()
    ge_svg(
        matrices,
        ref_path_list=[(1, 1, [(0, 0), (1, 1)], "hh", "red")],
    )
    legacy_paths = list(captured["rowechelon_paths"])

    assert structured_paths == legacy_paths


def test_ge_svg_supports_ref_path_list():
    from LAFigureSpecs.convenience_ge import ge_svg
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
        out = ge_svg(
            matrices,
            ref_path_list=[(1, 1, [(0, 0), (1, 1)], "hh")],
            output_dir="tmp",
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["rowechelon_paths"]
