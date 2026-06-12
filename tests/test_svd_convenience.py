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


def test_svd_tex_smoke():
    import LAFigureSpecs

    tex = LAFigureSpecs.svd_tex([[1, 0], [0, 0]])
    assert "\\begin{tabular}" in tex
    assert "\\Sigma" in tex


def test_svd_tex_factors_orthonormal_vectors_when_requested():
    import sympy as sym
    import LAFigureSpecs

    tex = LAFigureSpecs.svd_tex(sym.Matrix([[4, 2], [0, 9]]), factor_out={"qvecs": True})

    vector_row = next(
        line
        for line in tex.splitlines()
        if r"\frac{\sqrt{2}}{2 \sqrt{5017 - 69 \sqrt{5017}}}\,\begin{pNiceArray}{r}-69 + \sqrt{5017}" in line
    )
    assert r"\frac{\sqrt{2}}{2 \sqrt{5017 - 69 \sqrt{5017}}}\,\begin{pNiceArray}{r}-69 + \sqrt{5017}" in vector_row
    assert r"\frac{8 \sqrt{2}}{\sqrt{5017 - 69 \sqrt{5017}}}" not in vector_row


def test_svd_svg_defaults_exact_bbox(monkeypatch):
    import LAFigureSpecs.convenience as conv

    calls = {}

    def fake_render(spec, **kwargs):
        calls["spec"] = spec
        calls["kwargs"] = kwargs
        return "<svg/>"

    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", fake_render)

    svg = conv.svd_svg([[1, 0], [0, 0]])

    assert svg == "<svg/>"
    assert calls["kwargs"]["exact_bbox"] is True


def test_svd_tex_passes_factor_out(monkeypatch):
    import LAFigureSpecs.convenience as conv

    calls = {}

    def fake_render(spec, **kwargs):
        calls["spec"] = spec
        calls["kwargs"] = kwargs
        return "tex"

    monkeypatch.setattr(conv, "_render_eig_tex_from_spec", fake_render)

    tex = conv.svd_tex([[1, 0], [0, 0]], factor_out={"u": True})

    assert tex == "tex"
    assert calls["kwargs"]["factor_out"] == {"u": True}


def test_svd_svg_passes_factor_out(monkeypatch):
    import LAFigureSpecs.convenience as conv

    calls = {}

    def fake_render(spec, **kwargs):
        calls["spec"] = spec
        calls["kwargs"] = kwargs
        return "<svg/>"

    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", fake_render)

    svg = conv.svd_svg(
        [[1, 0], [0, 0]],
        factor_out={"sigma": True, "u": True},
    )

    assert svg == "<svg/>"
    assert calls["kwargs"]["factor_out"] == {"sigma": True, "u": True}


def test_top_level_svd_svg_passes_factor_out(monkeypatch):
    import LAFigureSpecs
    import LAFigureSpecs.convenience as conv

    calls = {}

    def fake_render(spec, **kwargs):
        calls["spec"] = spec
        calls["kwargs"] = kwargs
        return "<svg/>"

    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", fake_render)

    svg = LAFigureSpecs.svd_svg(
        [[1, 0], [0, 0]],
        factor_out={"sigma": True, "u": True},
    )

    assert svg == "<svg/>"
    assert calls["kwargs"]["factor_out"] == {"sigma": True, "u": True}


def test_svd_tex_selective_matrix_factoring_example():
    import sympy as sym
    import LAFigureSpecs

    tex = LAFigureSpecs.svd_tex(
        sym.Matrix([[4, 9], [0, 2]]),
        factor_out={"u": True, "v": True, "sigma": False},
    )

    assert r"\frac{\sqrt{2}}{2}\,\begin{pNiceArray}{r@{\hspace{4mm}}r}" in tex
    assert r"$4\,\begin{pNiceArray}{r@{\hspace{4mm}}r}" in tex
    assert (
        r"\color{blue}{ \Sigma =}$ & \multicolumn{2}{c}{"
        "\n"
        r"$\begin{pNiceArray}{c@{\hspace{8mm}}c}\frac{\sqrt{2} \sqrt{3 \sqrt{1105} + 101}}{2}"
    ) in tex
    assert r"\begin{pNiceArray}{r@{\hspace{4mm}}r}\frac{\sqrt{2}}{2}\," not in tex
    assert r"\begin{pNiceArray}{r@{\hspace{4mm}}r}4\," not in tex


@pytest.mark.render
def test_svd_svg_smoke():
    pytest.importorskip("jupyter_tikz")

    import LAFigureSpecs

    svg = LAFigureSpecs.svd_svg(
        [[1, 0], [0, 0]],
        toolchain_name=_pick_toolchain_name_or_skip(),
        crop="tight",
        padding=(2, 2, 2, 2),
    )
    assert isinstance(svg, str)
    assert "<svg" in svg
