from typing import Any, Dict

import sympy as sym

import la_figures


def test_qr_tbl_svg_normalizes_svg_args(monkeypatch):
    import la_figures.convenience_qr as convenience_qr

    captured: Dict[str, Any] = {}

    def fake_render_qr_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.qr.render_qr_svg", fake_render_qr_svg)

    A = [[1, 0], [0, 1]]
    W = [[1, 0], [0, 1]]
    svg = convenience_qr.qr_tbl_svg(
        A,
        W,
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
    W = sym.Matrix([[1, 0], [0, 1]])

    spec = la_figures.qr_tbl_spec(A, W, array_names=True)
    assert spec.get("create_extra_nodes") is True
