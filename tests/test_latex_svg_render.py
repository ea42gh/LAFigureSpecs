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


@pytest.mark.render
def test_latex_svg_smoke():
    pytest.importorskip("matrixlayout")
    pytest.importorskip("jupyter_tikz")
    import LAFigureSpecs

    svg = LAFigureSpecs.latex_svg(
        r"$A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}$",
        crop="tight",
        padding=(2, 2, 2, 2),
        toolchain_name=_pick_toolchain_name_or_skip(),
    )

    assert "<svg" in svg
