from typing import Any, Dict

import sympy as sym

import LAFigureSpecs


def test_qr_table_svg_normalizes_svg_args(monkeypatch):
    import LAFigureSpecs.convenience_qr as convenience_qr

    captured: Dict[str, Any] = {}

    def fake_render_qr_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.qr.render_qr_svg", fake_render_qr_svg)

    A = [[1, 0], [0, 1]]
    svg = convenience_qr.qr_table_svg(
        A,
        toolchain_name=":pdftex_dvisvgm",
        crop="  tight ",
        padding=[1, 2, 3, 4],
    )
    assert svg == "<svg/>"
    assert captured["toolchain_name"] == "pdftex_dvisvgm"
    assert captured["crop"] == "tight"
    assert captured["padding"] == (1, 2, 3, 4)


def test_qr_spec_sets_create_extra_nodes_for_array_names():
    A = sym.Matrix([[1, 2], [3, 4]])

    spec = LAFigureSpecs.qr_spec(A, array_names=True)
    assert spec.get("create_extra_nodes") is True


def test_qr_spec_sets_create_extra_nodes_for_callouts():
    A = sym.Matrix([[1, 2], [3, 4]])
    callouts = [{"grid": (0, 2), "label": "A", "side": "right"}]

    spec = LAFigureSpecs.qr_spec(A, array_names=False, callouts=callouts)

    assert spec.get("callouts") == callouts
    assert spec.get("create_extra_nodes") is True


def test_qr_tex_passes_strict_override(monkeypatch):
    import LAFigureSpecs.convenience_qr as convenience_qr

    captured: Dict[str, Any] = {}

    def fake_render_qr_tex_from_spec(spec, *, formatter, strict):
        captured["spec"] = spec
        captured["formatter"] = formatter
        captured["strict"] = strict
        return "tex"

    monkeypatch.setattr(
        convenience_qr,
        "_render_qr_tex_from_spec",
        fake_render_qr_tex_from_spec,
    )

    tex = convenience_qr.qr_tex([[1, 0], [0, 1]], strict=True)

    assert tex == "tex"
    assert captured["strict"] is True
    assert captured["spec"]["array_names"] is True


def test_qr_tex_forwards_callouts(monkeypatch):
    import LAFigureSpecs.convenience_qr as convenience_qr

    captured: Dict[str, Any] = {}
    callouts = [{"grid": (0, 2), "label": "A", "side": "right"}]

    def fake_render_qr_tex_from_spec(spec, *, formatter, strict):
        captured["spec"] = spec
        return "tex"

    monkeypatch.setattr(
        convenience_qr,
        "_render_qr_tex_from_spec",
        fake_render_qr_tex_from_spec,
    )

    tex = convenience_qr.qr_tex([[1, 0], [0, 1]], array_names=False, callouts=callouts)

    assert tex == "tex"
    assert captured["spec"]["callouts"] == callouts


def test_qr_bundle_success_uses_default_svg_options(monkeypatch):
    import LAFigureSpecs.convenience_qr as convenience_qr

    captured: Dict[str, Any] = {}

    monkeypatch.setattr(
        convenience_qr,
        "_render_qr_tex_from_spec",
        lambda *args, **kwargs: "tex",
    )

    def fake_render_qr_svg_from_spec(*args, **kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(
        convenience_qr,
        "_render_qr_svg_from_spec",
        fake_render_qr_svg_from_spec,
    )

    bundle = convenience_qr.qr_bundle([[1, 0], [0, 1]])

    assert bundle["tex"] == "tex"
    assert bundle["svg"] == "<svg/>"
    assert bundle["render_error"] is None
    assert captured["crop"] == "tight"
    assert captured["padding"] == (2, 2, 2, 2)


def test_qr_bundle_keeps_formatter_out_of_spec_builder(monkeypatch):
    import LAFigureSpecs.convenience_qr as convenience_qr

    captured: Dict[str, Any] = {}

    def fake_spec(A, **kwargs):
        captured["spec_kwargs"] = dict(kwargs)
        return {
            "matrices": [[None, [[1]]]],
            "array_names": True,
            "fig_scale": None,
            "body_preamble": "",
            "document_preamble": "",
            "nice_options": "",
            "label_color": "blue",
            "label_text_color": "red",
            "known_zero_color": "brown",
            "decorators": None,
            "strict": False,
        }

    def fake_render_qr_tex_from_spec(spec, *, formatter, strict):
        captured["tex_formatter"] = formatter
        return "tex"

    def fake_render_qr_svg_from_spec(spec, **kwargs):
        captured["svg_formatter"] = kwargs["formatter"]
        return "<svg/>"

    monkeypatch.setattr(convenience_qr, "qr_spec", fake_spec)
    monkeypatch.setattr(
        convenience_qr,
        "_render_qr_tex_from_spec",
        fake_render_qr_tex_from_spec,
    )
    monkeypatch.setattr(
        convenience_qr,
        "_render_qr_svg_from_spec",
        fake_render_qr_svg_from_spec,
    )

    def fmt(x):
        return str(x)

    bundle = convenience_qr.qr_bundle([[1, 0], [0, 1]], formatter=fmt)

    assert bundle["tex"] == "tex"
    assert bundle["svg"] == "<svg/>"
    assert "formatter" not in captured["spec_kwargs"]
    assert captured["tex_formatter"] is fmt
    assert captured["svg_formatter"] is fmt


def test_qr_render_wrapper_defers_crop_padding_to_render_opts(monkeypatch):
    import LAFigureSpecs.convenience_qr as convenience_qr

    captured: Dict[str, Any] = {}

    def fake_render_qr_svg_from_spec(spec, **kwargs):
        captured["spec"] = spec
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(
        convenience_qr,
        "_render_qr_svg_from_spec",
        fake_render_qr_svg_from_spec,
    )

    svg = convenience_qr.qr(
        [[[1]], [[1]], [[1]]],
        render_opts={"crop": "loose", "padding": (9, 9, 9, 9)},
    )

    assert svg == "<svg/>"
    assert captured["crop"] is None
    assert captured["padding"] is None
    assert captured["render_opts"] == {"crop": "loose", "padding": (9, 9, 9, 9)}


def test_gram_schmidt_qr_wrapper_uses_rank_deficient_mode_and_svg_defaults(
    monkeypatch,
):
    import LAFigureSpecs.convenience_qr as convenience_qr

    captured: Dict[str, Any] = {}

    def fake_render_qr_svg_from_spec(spec, **kwargs):
        captured["spec"] = spec
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(
        convenience_qr,
        "_render_qr_svg_from_spec",
        fake_render_qr_svg_from_spec,
    )

    svg = convenience_qr.gram_schmidt_qr(
        [[1, 2], [2, 4]],
        rank_deficient="drop",
        fig_scale=1.2,
    )

    assert svg == "<svg/>"
    assert captured["crop"] == "tight"
    assert captured["padding"] == (2, 2, 2, 2)
    assert captured["spec"]["fig_scale"] == 1.2
