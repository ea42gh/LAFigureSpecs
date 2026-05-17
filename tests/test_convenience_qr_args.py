from typing import Any, Dict

import sympy as sym

import LAFigureSpecs


def test_qr_tbl_svg_normalizes_svg_args(monkeypatch):
    import LAFigureSpecs.convenience_qr as convenience_qr

    captured: Dict[str, Any] = {}

    def fake_render_qr_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.qr.render_qr_svg", fake_render_qr_svg)

    A = [[1, 0], [0, 1]]
    svg = convenience_qr.qr_tbl_svg(
        A,
        toolchain_name=":pdftex_dvisvgm",
        crop="  tight ",
        padding=[1, 2, 3, 4],
    )
    assert svg == "<svg/>"
    assert captured["toolchain_name"] == "pdftex_dvisvgm"
    assert captured["crop"] == "tight"
    assert captured["padding"] == (1, 2, 3, 4)


def test_qr_tbl_spec_sets_create_extra_nodes_for_array_names():
    A = sym.Matrix([[1, 2], [3, 4]])

    spec = LAFigureSpecs.qr_tbl_spec(A, array_names=True)
    assert spec.get("create_extra_nodes") is True


def test_qr_tbl_tex_passes_strict_override(monkeypatch):
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

    tex = convenience_qr.qr_tbl_tex([[1, 0], [0, 1]], strict=True)

    assert tex == "tex"
    assert captured["strict"] is True
    assert captured["spec"]["array_names"] is True


def test_qr_tbl_bundle_success_uses_default_svg_options(monkeypatch):
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

    bundle = convenience_qr.qr_tbl_bundle([[1, 0], [0, 1]])

    assert bundle["tex"] == "tex"
    assert bundle["svg"] == "<svg/>"
    assert bundle["render_error"] is None
    assert captured["crop"] == "tight"
    assert captured["padding"] == (2, 2, 2, 2)


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
