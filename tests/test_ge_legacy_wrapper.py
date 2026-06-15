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


def test_ge_legacy_wrapper_rejects_unsupported_options(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    A = sym.Matrix([[1, 2], [3, 4]])
    monkeypatch.setattr(ml_ge, "render_ge_svg", lambda **kwargs: "<svg/>")

    assert ge_stack_svg([[None, A]], func=lambda m: m) == "<svg/>"


def test_ge_legacy_wrapper_supports_backgrounds_and_comments():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
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
        out = ge_stack_svg(
            matrices,
            bg_for_entries=[(0, 1, [(0, 0)], "red!15", 0)],
            comment_list=["note"],
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["codebefore"]
    assert captured["text_annotations"]


def test_ge_legacy_wrapper_forwards_structured_decorations(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_stack_svg
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

    out = ge_stack_svg(matrices, decorations=decorations)

    assert out == "<svg/>"
    assert captured["decorations"] == decorations
    assert captured["format_nrhs"] is True


def test_ge_stack_svg_accepts_canonical_renderer_fields(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    A = sym.Matrix([[1, 2], [3, 4]])
    matrices = [[None, A]]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_svg)

    out = ge_stack_svg(
        matrices,
        n_rhs=1,
        pivot_locs=[{"grid": (0, 1), "entries": [(0, 0)]}],
        codebefore=[r"\CodeBefore"],
        text_annotations=[{"text": "note"}],
        label_rows=[{"grid": (0, 1), "labels": ["x", "b"]}],
        rowechelon_paths=[r"\draw (1-1) -- (2-2);"],
        decorations=[{"grid": (0, 1), "entries": [(0, 0)], "background": "yellow!35"}],
    )

    assert out == "<svg/>"
    assert captured["pivot_locs"] == [("(1-3)(1-3)", "draw=red, inner sep=2pt, outer sep=0pt")]
    assert captured["codebefore"] == [r"\CodeBefore"]
    assert captured["text_annotations"] == [{"text": "note"}]
    assert captured["label_rows"] == [{"grid": (0, 1), "labels": ["x", "b"]}]
    assert captured["rowechelon_paths"] == [r"\draw (1-1) -- (2-2);"]
    assert captured["decorations"] == [
        {"grid": (0, 1), "entries": [(0, 0)], "background": "yellow!35"},
        {"grid": (0, 1), "vlines": 1},
    ]
    assert captured["create_extra_nodes"] is True
    assert captured["create_medium_nodes"] is True
    assert captured["format_nrhs"] is False


def test_ge_stack_svg_grid_pivot_locs_accept_custom_style(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    A = sym.Matrix([[1, 2], [3, 4]])
    matrices = [[None, A]]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_svg)

    out = ge_stack_svg(
        matrices,
        pivot_locs=[{"grid": (0, 1), "entries": [(1, 1)], "style": "draw=blue"}],
    )

    assert out == "<svg/>"
    assert captured["pivot_locs"] == [("(2-4)(2-4)", "draw=blue")]


def test_ge_stack_svg_accepts_structured_rowechelon_paths(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_stack_svg
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

    out = ge_stack_svg(
        matrices,
        rowechelon_paths=[
            {"grid": (1, 1), "pivots": [(0, 0), (1, 1)], "case": "hh", "color": "red"}
        ],
    )

    assert out == "<svg/>"
    paths = captured["rowechelon_paths"]
    assert len(paths) == 1
    assert paths[0].startswith(r"\draw[red]")
    assert "A1" in paths[0]


def test_ge_stack_svg_accepts_grid_row_text_annotations(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    A0 = sym.Matrix([[1, 2], [3, 4]])
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [sym.eye(2), A1]]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_svg)

    out = ge_stack_svg(
        matrices,
        text_annotations=[
            {
                "grid_row": 1,
                "text": r"\qquad row note",
                "color": "blue",
                "shift_mm": (24, -2),
            }
        ],
    )

    assert out == "<svg/>"
    assert captured["text_annotations"] == [
        ("(3-4.east)", r"\qquad row note", "right,align=left,text=blue, xshift=24.0mm, yshift=-2.0mm")
    ]


def test_ge_stack_svg_preserves_raw_text_annotations(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    A = sym.Matrix([[1, 2], [3, 4]])
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_svg)

    raw = {"coord": "1-1", "text": "raw", "style": "red"}
    out = ge_stack_svg([[A]], text_annotations=[raw])

    assert out == "<svg/>"
    assert captured["text_annotations"] == [raw]


def test_ge_legacy_wrapper_supports_ref_path_list():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
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
        out = ge_stack_svg(
            matrices,
            ref_path_list=[(1, 1, [(0, 0), (1, 1)], "hh")],
            output_dir="tmp",
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["rowechelon_paths"]


def test_ge_legacy_wrapper_preserves_output_dir_artifacts(monkeypatch, tmp_path):
    from pathlib import Path

    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    matrices = [[None, sym.Matrix([[1, 2], [3, 4]])]]
    preserve_dir = tmp_path / "preserve"

    def fake_svg(**kwargs):
        render_dir = Path(kwargs["output_dir"])
        render_dir.mkdir(parents=True, exist_ok=True)
        (render_dir / "demo.svg").write_text("<svg/>", encoding="utf-8")
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_svg)

    assert ge_stack_svg(matrices, output_dir=preserve_dir, output_stem="demo") == "<svg/>"
    assert (preserve_dir / "demo.svg").read_text(encoding="utf-8") == "<svg/>"


def test_ge_legacy_wrapper_supports_variable_summary():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
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
        out = ge_stack_svg(
            matrices,
            variable_summary=[True, False],
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["label_rows"]


def test_ge_legacy_wrapper_supports_array_names():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
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
        out = ge_stack_svg(
            matrices,
            array_names=["E", ["A", "b"]],
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["callouts"]
    labels = [c.get("label", "") for c in captured["callouts"]]
    assert any("E_1" in label for label in labels)


def test_ge_legacy_wrapper_can_suppress_array_name_indices():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
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
        out = ge_stack_svg(
            matrices,
            array_names=["E", ["A", "b"]],
            array_name_indices=False,
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    labels = [c.get("label", "") for c in captured["callouts"]]
    assert labels
    assert not any("E_{" in label for label in labels)
    assert not any("E_1" in label for label in labels)
    assert any(r"\mathbf{ E }" in label for label in labels)
    assert any(r"E A \mid  E b" in label for label in labels)


def test_ge_legacy_wrapper_forwards_explicit_callouts():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]
    callouts = [{"name": "M-0-1", "label": "A", "side": "above"}]

    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        out = ge_stack_svg(matrices, callouts=callouts)
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["callouts"] == callouts


def test_ge_legacy_wrapper_maps_specs_to_callouts():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    A0 = sym.Matrix([[1, 2], [3, 4]])
    E1 = sym.eye(2)
    A1 = sym.Matrix([[1, 2], [0, 1]])
    matrices = [[None, A0], [E1, A1]]
    specs = [
        {
            "grid": (1, 0),
            "label": r"\tilde{E}^{-1}",
            "side": "left",
            "angle": -35,
            "length": 6,
            "label_shift_x_mm": 1,
            "label_shift_y_mm": -2,
            "math_mode": True,
        }
    ]

    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        out = ge_stack_svg(matrices, specs=specs)
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    assert captured["callouts"] == [
        {
            "grid": (1, 0),
            "label": r"\tilde{E}^{-1}",
            "side": "left",
            "angle_deg": -35,
            "length_mm": 6,
            "label_shift_mm": (1, -2),
            "math_mode": True,
        }
    ]
    assert "angle" not in captured["callouts"][0]
    assert "length" not in captured["callouts"][0]


def test_ge_legacy_wrapper_keeps_name_specs_compatibility():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
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
        out = ge_stack_svg(
            matrices,
            array_names={"name_specs": [((0, 1), "ar", "$A$")]},
        )
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert out == "<svg/>"
    labels = [c.get("label", "") for c in captured["callouts"]]
    assert labels == ["A"]


def test_ge_legacy_wrapper_rhs_callout_labels_follow_rhs_size():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
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
        ge_stack_svg(matrices, array_names=True, n_rhs=1)
        labels = _extract_labels(captured.get("callouts"))
        assert any(r"\mid  b" in label for label in labels)

        captured.clear()
        ge_stack_svg(matrices, array_names=True, n_rhs=2)
        labels = _extract_labels(captured.get("callouts"))
        assert any(r"\mid  B" in label for label in labels)

        captured.clear()
        ge_stack_svg(matrices, array_names=["E", ["A", "b"]], n_rhs=2)
        labels = _extract_labels(captured.get("callouts"))
        assert any(r"\mid  b" in label for label in labels)
    finally:
        ml_ge.render_ge_svg = ge_svg_orig


def test_ge_legacy_wrapper_supports_canonical_n_rhs_keyword():
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    matrices = [[None, sym.Matrix([[1, 2, 3], [4, 5, 6]])]]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        assert ge_stack_svg(matrices, n_rhs=1) == "<svg/>"
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert captured["n_rhs"] == 1


def test_ge_svg_with_n_rhs_delegates_to_stack_renderer():
    from LAFigureSpecs.convenience_ge import ge_svg
    from matrixlayout import ge as ml_ge

    matrices = [[None, sym.Matrix([[1, 2, 3], [4, 5, 6]])]]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        assert ge_svg(matrices, n_rhs=1, formatter=str, crop="tight") == "<svg/>"
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert captured["matrices"] == matrices
    assert captured["n_rhs"] == 1
    assert captured["formatter"] is str
    assert captured["crop"] == "tight"


def test_ge_svg_with_stack_only_option_delegates_to_stack_renderer():
    from LAFigureSpecs.convenience_ge import ge_svg
    from matrixlayout import ge as ml_ge

    matrices = [[None, sym.Matrix([[1, 2], [3, 4]])]]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    ge_svg_orig = ml_ge.render_ge_svg
    ml_ge.render_ge_svg = fake_svg
    try:
        assert ge_svg(matrices, formatter=str) == "<svg/>"
    finally:
        ml_ge.render_ge_svg = ge_svg_orig

    assert captured["matrices"] == matrices
    assert captured["n_rhs"] == 0
    assert captured["formatter"] is str


def test_ge_legacy_wrapper_uses_canonical_tex_hook_names(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    matrices = [[None, sym.Matrix([[1, 2], [3, 4]])]]
    captured = {}

    def fake_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_svg)

    assert ge_stack_svg(matrices, body_preamble="%body", document_preamble="%doc") == "<svg/>"

    assert captured["body_preamble"] == "%body"
    assert captured["document_preamble"] == "%doc"


def test_ge_legacy_wrapper_rejects_removed_tex_hook_aliases(monkeypatch):
    from LAFigureSpecs.convenience_ge import ge_stack_svg
    from matrixlayout import ge as ml_ge

    matrices = [[None, sym.Matrix([[1, 2], [3, 4]])]]

    def fake_svg(**kwargs):
        raise AssertionError("render_ge_svg should not be called")
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_svg)

    try:
        ge_stack_svg(matrices, preamble="%old-body", extension="%old-doc")
    except TypeError as exc:
        msg = str(exc)
        assert "preamble" in msg
        assert "extension" in msg
        assert "body_preamble" in msg
        assert "document_preamble" in msg
    else:
        raise AssertionError("expected removed GE TeX hook aliases to be rejected")
