from typing import Any, Dict


def test_eig_tbl_svg_uses_tmp_dir_as_output_dir(monkeypatch):
    import LAFigureSpecs

    captured: Dict[str, Any] = {}

    def fake_render_eig_svg(*args, **kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.render_eig_svg", fake_render_eig_svg)
    svg = LAFigureSpecs.eig_tbl_svg([[1, 0], [0, 1]], tmp_dir="tmp-out")
    assert svg == "<svg/>"
    assert captured["output_dir"] == "tmp-out"


def test_eig_tbl_svg_prefers_output_dir_over_tmp_dir(monkeypatch):
    import LAFigureSpecs

    captured: Dict[str, Any] = {}

    def fake_render_eig_svg(*args, **kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.render_eig_svg", fake_render_eig_svg)
    svg = LAFigureSpecs.eig_tbl_svg([[1, 0], [0, 1]], tmp_dir="tmp-out", output_dir="out")
    assert svg == "<svg/>"
    assert captured["output_dir"] == "out"


def test_qr_tbl_svg_uses_tmp_dir_as_output_dir(monkeypatch):
    import LAFigureSpecs

    captured: Dict[str, Any] = {}

    def fake_render_qr_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.qr.render_qr_svg", fake_render_qr_svg)
    svg = LAFigureSpecs.qr_tbl_svg([[1, 0], [0, 1]], tmp_dir="tmp-out")
    assert svg == "<svg/>"
    assert captured["output_dir"] == "tmp-out"


def test_qr_tbl_svg_prefers_output_dir_over_tmp_dir(monkeypatch):
    import LAFigureSpecs

    captured: Dict[str, Any] = {}

    def fake_render_qr_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.qr.render_qr_svg", fake_render_qr_svg)
    svg = LAFigureSpecs.qr_tbl_svg([[1, 0], [0, 1]], tmp_dir="tmp-out", output_dir="out")
    assert svg == "<svg/>"
    assert captured["output_dir"] == "out"


def test_ge_tbl_svg_uses_tmp_dir_as_output_dir(monkeypatch):
    import LAFigureSpecs

    captured: Dict[str, Any] = {}

    def fake_render_ge_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.ge.render_ge_svg", fake_render_ge_svg)
    svg = LAFigureSpecs.ge_tbl_svg([[1, 0], [0, 1]], tmp_dir="tmp-out")
    assert svg == "<svg/>"
    assert captured["output_dir"] == "tmp-out"


def test_ge_tbl_svg_prefers_output_dir_over_tmp_dir(monkeypatch):
    import LAFigureSpecs

    captured: Dict[str, Any] = {}

    def fake_render_ge_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.ge.render_ge_svg", fake_render_ge_svg)
    svg = LAFigureSpecs.ge_tbl_svg([[1, 0], [0, 1]], tmp_dir="tmp-out", output_dir="out")
    assert svg == "<svg/>"
    assert captured["output_dir"] == "out"
