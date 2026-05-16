from __future__ import annotations

import sys
import types

import numpy as np


def test_latex_svg_wraps_fragment_and_forwards_render_options(monkeypatch):
    import la_figures.rendering as rendering

    calls = {}

    class FakeTexFragment:
        def __init__(self, code, **kwargs):
            calls["fragment_code"] = code
            calls["fragment_kwargs"] = kwargs
            self.full_latex = f"FULL::{code}"

    def fake_render_svg(tex_source, **kwargs):
        calls["render_tex_source"] = tex_source
        calls["render_kwargs"] = kwargs
        return "<svg/>"

    monkeypatch.setitem(
        sys.modules,
        "jupyter_tikz",
        types.SimpleNamespace(TexFragment=FakeTexFragment),
    )
    monkeypatch.setitem(
        sys.modules,
        "matrixlayout.render",
        types.SimpleNamespace(render_svg=fake_render_svg),
    )

    svg = rendering.latex_svg(
        r"$x^2$",
        tex_packages="amsmath,amssymb",
        no_tikz=True,
        scale=1.5,
        toolchain_name="pdftex_dvisvgm",
        crop="tight",
        padding=(1, 2, 3, 4),
        frame=True,
        exact_bbox=True,
        output_dir="out",
        output_stem="demo",
        render_opts={"crop": "page", "padding": (9, 9, 9, 9)},
    )

    assert svg == "<svg/>"
    assert calls["fragment_code"] == r"$x^2$"
    assert calls["fragment_kwargs"]["tex_packages"] == "amsmath,amssymb"
    assert calls["fragment_kwargs"]["no_tikz"] is True
    assert calls["fragment_kwargs"]["scale"] == 1.5
    assert calls["render_tex_source"] == "FULL::$x^2$"
    assert calls["render_kwargs"]["toolchain_name"] == "pdftex_dvisvgm"
    assert calls["render_kwargs"]["crop"] == "tight"
    assert calls["render_kwargs"]["padding"] == (1, 2, 3, 4)
    assert calls["render_kwargs"]["frame"] is True
    assert calls["render_kwargs"]["exact_bbox"] is True
    assert calls["render_kwargs"]["output_dir"] == "out"
    assert calls["render_kwargs"]["output_stem"] == "demo"


def test_latex_svg_default_packages_cover_la_figures_fragments(monkeypatch):
    import la_figures.rendering as rendering

    calls = {}

    class FakeTexFragment:
        def __init__(self, code, **kwargs):
            calls["fragment_code"] = code
            calls["fragment_kwargs"] = kwargs
            self.full_latex = f"FULL::{code}"

    monkeypatch.setitem(
        sys.modules,
        "jupyter_tikz",
        types.SimpleNamespace(TexFragment=FakeTexFragment),
    )
    monkeypatch.setitem(
        sys.modules,
        "matrixlayout.render",
        types.SimpleNamespace(render_svg=lambda tex_source, **kwargs: "<svg/>"),
    )

    svg = rendering.latex_svg(r"$\systeme{x=1}$")

    assert svg == "<svg/>"
    assert "systeme" in calls["fragment_kwargs"]["tex_packages"]
    assert "cascade" in calls["fragment_kwargs"]["tex_packages"]
    assert "nicematrix" in calls["fragment_kwargs"]["tex_packages"]


def test_latex_svg_prefers_explicit_preamble_path(monkeypatch):
    import la_figures.rendering as rendering

    calls = {}

    class FakeTexFragment:
        def __init__(self, code, **kwargs):
            calls["fragment_kwargs"] = kwargs
            self.full_latex = code

    monkeypatch.setitem(
        sys.modules,
        "jupyter_tikz",
        types.SimpleNamespace(TexFragment=FakeTexFragment),
    )
    monkeypatch.setitem(
        sys.modules,
        "matrixlayout.render",
        types.SimpleNamespace(render_svg=lambda tex_source, **kwargs: "<svg/>"),
    )

    rendering.latex_svg(
        r"\[\xi\]",
        preamble="\\usepackage{amsmath}",
        tex_packages="SHOULD_NOT_BE_USED",
    )

    assert calls["fragment_kwargs"]["preamble"] == "\\usepackage{amsmath}"
    assert "tex_packages" not in calls["fragment_kwargs"]


def test_latex_document_svg_forwards_render_options(monkeypatch):
    import la_figures.rendering as rendering

    calls = {}

    def fake_render_svg(tex_source, **kwargs):
        calls["render_tex_source"] = tex_source
        calls["render_kwargs"] = kwargs
        return "<svg/>"

    monkeypatch.setitem(
        sys.modules,
        "matrixlayout.render",
        types.SimpleNamespace(render_svg=fake_render_svg),
    )

    svg = rendering.latex_document_svg(
        "\\documentclass{standalone}\\begin{document}x\\end{document}",
        crop="tight",
        padding=(2, 2, 2, 2),
        frame={"stroke": "#666"},
        exact_bbox=True,
        output_dir="out",
        output_stem="doc",
    )

    assert svg == "<svg/>"
    assert calls["render_kwargs"]["crop"] == "tight"
    assert calls["render_kwargs"]["padding"] == (2, 2, 2, 2)
    assert calls["render_kwargs"]["frame"] == {"stroke": "#666"}
    assert calls["render_kwargs"]["exact_bbox"] is True
    assert calls["render_kwargs"]["output_dir"] == "out"
    assert calls["render_kwargs"]["output_stem"] == "doc"


def test_lshow_svg_uses_juliacall_and_delegates_to_latex_svg(monkeypatch):
    import la_figures.rendering as rendering

    calls = {"seval": []}

    class FakeLAlatex:
        @staticmethod
        def L_show(*args, **kwargs):
            calls["lshow_args"] = args
            calls["lshow_kwargs"] = kwargs
            return "LATEX_FROM_JULIA"

    class FakeMain:
        LAlatex = FakeLAlatex()

        @staticmethod
        def seval(expr):
            calls["seval"].append(expr)
            return f"JULIA<{expr}>"

    def fake_latex_svg(tex_body, **kwargs):
        calls["latex_svg_body"] = tex_body
        calls["latex_svg_kwargs"] = kwargs
        return "<svg/>"

    monkeypatch.setitem(
        sys.modules,
        "juliacall",
        types.SimpleNamespace(Main=FakeMain),
    )
    monkeypatch.setattr(rendering, "latex_svg", fake_latex_svg)

    svg = rendering.lshow_svg(
        "A = ",
        [[1, 2], [3, 4]],
        lshow_kwargs={"arraystyle": ":bmatrix"},
        crop="tight",
        output_stem="lshow_demo",
    )

    assert svg == "<svg/>"
    assert calls["seval"] == ["[1 2; 3 4]"]
    assert calls["lshow_args"] == ("A = ", "JULIA<[1 2; 3 4]>")
    assert calls["lshow_kwargs"] == {"arraystyle": ":bmatrix"}
    assert calls["latex_svg_body"] == "LATEX_FROM_JULIA"
    assert calls["latex_svg_kwargs"]["crop"] == "tight"
    assert calls["latex_svg_kwargs"]["output_stem"] == "lshow_demo"


def test_lshow_svg_converts_numeric_python_arrays_for_julia(monkeypatch):
    import la_figures.rendering as rendering

    calls = {"seval": []}

    class FakeLAlatex:
        @staticmethod
        def L_show(*args, **kwargs):
            calls["lshow_args"] = args
            calls["lshow_kwargs"] = kwargs
            return "LATEX_FROM_JULIA"

    class FakeMain:
        LAlatex = FakeLAlatex()

        @staticmethod
        def seval(expr):
            calls["seval"].append(expr)
            return f"JULIA<{expr}>"

    def fake_latex_svg(tex_body, **kwargs):
        calls["latex_svg_body"] = tex_body
        return "<svg/>"

    monkeypatch.setitem(
        sys.modules,
        "juliacall",
        types.SimpleNamespace(Main=FakeMain),
    )
    monkeypatch.setattr(rendering, "latex_svg", fake_latex_svg)

    vec = np.array([1.0, 2.0])
    mat = np.array([[1, 2], [3, 4]])

    svg = rendering.lshow_svg("A = ", vec, mat)

    assert svg == "<svg/>"
    assert calls["seval"] == [
        "[1, 2]",
        "[1 2; 3 4]",
    ]
    assert calls["lshow_args"] == ("A = ", "JULIA<[1, 2]>", "JULIA<[1 2; 3 4]>")
    assert calls["lshow_kwargs"] == {}


def test_lshow_svg_leaves_non_numeric_structures_unchanged(monkeypatch):
    import la_figures.rendering as rendering

    calls = {}

    class FakeLAlatex:
        @staticmethod
        def L_show(*args, **kwargs):
            calls["lshow_args"] = args
            return "LATEX_FROM_JULIA"

    class FakeMain:
        LAlatex = FakeLAlatex()

        @staticmethod
        def seval(expr):
            raise AssertionError("seval should not be used for non-numeric mixed data")

    monkeypatch.setitem(
        sys.modules,
        "juliacall",
        types.SimpleNamespace(Main=FakeMain),
    )
    monkeypatch.setattr(rendering, "latex_svg", lambda tex_body, **kwargs: "<svg/>")

    rendering.lshow_svg(["x", 1], [["x", 1], [2, 3]])

    assert calls["lshow_args"] == (["x", 1], [["x", 1], [2, 3]])
