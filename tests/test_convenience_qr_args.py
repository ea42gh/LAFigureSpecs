from typing import Any, Dict


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
