from typing import Any, Dict

import pytest


def test_eig_svg_uses_output_dir(monkeypatch):
    import LAFigureSpecs

    captured: Dict[str, Any] = {}

    def fake_render_eig_svg(*args, **kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.render_eig_svg", fake_render_eig_svg)
    svg = LAFigureSpecs.eig_svg([[1, 0], [0, 1]], output_dir="out")
    assert svg == "<svg/>"
    assert captured["output_dir"] == "out"


def test_eig_svg_rejects_tmp_dir():
    import LAFigureSpecs

    with pytest.raises(TypeError):
        LAFigureSpecs.eig_svg([[1, 0], [0, 1]], tmp_dir="tmp-out")


def test_qr_svg_uses_output_dir(monkeypatch):
    import LAFigureSpecs

    captured: Dict[str, Any] = {}

    def fake_render_qr_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.qr.render_qr_svg", fake_render_qr_svg)
    svg = LAFigureSpecs.qr_svg([[1, 0], [0, 1]], output_dir="out")
    assert svg == "<svg/>"
    assert captured["output_dir"] == "out"


def test_qr_svg_rejects_tmp_dir():
    import LAFigureSpecs

    with pytest.raises(TypeError):
        LAFigureSpecs.qr_svg([[1, 0], [0, 1]], tmp_dir="tmp-out")


def test_ge_svg_uses_output_dir(monkeypatch):
    import LAFigureSpecs

    captured: Dict[str, Any] = {}

    def fake_render_ge_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr("matrixlayout.ge.render_ge_svg", fake_render_ge_svg)
    svg = LAFigureSpecs.ge_svg([[1, 0], [0, 1]], output_dir="out")
    assert svg == "<svg/>"
    assert captured["output_dir"] == "out"


def test_ge_svg_rejects_tmp_dir():
    import LAFigureSpecs

    with pytest.raises(TypeError):
        LAFigureSpecs.ge_svg([[1, 0], [0, 1]], tmp_dir="tmp-out")
