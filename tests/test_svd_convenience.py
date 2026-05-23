import shutil

import pytest


def _pick_toolchain_name_or_skip() -> str:
    if shutil.which("latexmk") is None:
        pytest.skip("latexmk not found")

    if shutil.which("dvisvgm") is not None:
        return "pdftex_dvisvgm"
    if shutil.which("pdftocairo") is not None:
        return "pdftex_pdftocairo"
    if shutil.which("pdf2svg") is not None:
        return "pdftex_pdf2svg"

    pytest.skip("no SVG converter found (need dvisvgm, pdftocairo, or pdf2svg)")
    raise AssertionError("unreachable")


def test_svd_tbl_tex_smoke():
    import LAFigureSpecs

    tex = LAFigureSpecs.svd_tbl_tex([[1, 0], [0, 0]])
    assert "\\begin{tabular}" in tex
    assert "\\Sigma" in tex


def test_svd_tbl_tex_factors_orthonormal_vectors_for_default_formatter():
    import sympy as sym
    import LAFigureSpecs

    tex = LAFigureSpecs.svd_tbl_tex(sym.Matrix([[4, 2], [0, 9]]))

    vector_row = next(
        line
        for line in tex.splitlines()
        if r"\frac{\sqrt{2}}{2 \sqrt{5017 - 69 \sqrt{5017}}}\,\begin{pNiceArray}{r}-69 + \sqrt{5017}" in line
    )
    assert r"\frac{\sqrt{2}}{2 \sqrt{5017 - 69 \sqrt{5017}}}\,\begin{pNiceArray}{r}-69 + \sqrt{5017}" in vector_row
    assert r"\frac{8 \sqrt{2}}{\sqrt{5017 - 69 \sqrt{5017}}}" not in vector_row


def test_svd_tbl_svg_defaults_exact_bbox(monkeypatch):
    import LAFigureSpecs.convenience as conv

    calls = {}

    def fake_render(spec, **kwargs):
        calls["spec"] = spec
        calls["kwargs"] = kwargs
        return "<svg/>"

    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", fake_render)

    svg = conv.svd_tbl_svg([[1, 0], [0, 0]])

    assert svg == "<svg/>"
    assert calls["kwargs"]["exact_bbox"] is True


def test_svd_tbl_tex_passes_matrix_factor_out(monkeypatch):
    import LAFigureSpecs.convenience as conv

    calls = {}

    def fake_render(spec, **kwargs):
        calls["spec"] = spec
        calls["kwargs"] = kwargs
        return "tex"

    monkeypatch.setattr(conv, "_render_eig_tex_from_spec", fake_render)

    tex = conv.svd_tbl_tex([[1, 0], [0, 0]], matrix_factor_out={"u": True})

    assert tex == "tex"
    assert calls["kwargs"]["matrix_factor_out"] == {"u": True}


@pytest.mark.render
def test_svd_tbl_svg_smoke():
    pytest.importorskip("jupyter_tikz")

    import LAFigureSpecs

    svg = LAFigureSpecs.svd_tbl_svg(
        [[1, 0], [0, 0]],
        toolchain_name=_pick_toolchain_name_or_skip(),
        crop="tight",
        padding=(2, 2, 2, 2),
    )
    assert isinstance(svg, str)
    assert "<svg" in svg
