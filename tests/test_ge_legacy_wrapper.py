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
