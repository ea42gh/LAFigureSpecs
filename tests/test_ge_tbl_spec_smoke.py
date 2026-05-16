import sympy as sym


def test_ge_tbl_spec_and_tex_smoke():
    import pytest

    pytest.importorskip("matrixlayout")
    import la_figures

    A = sym.Matrix([[1, 2], [3, 4]])

    spec = la_figures.ge_tbl_spec(A)
    assert isinstance(spec, dict)
    assert "matrices" in spec
    assert "n_rhs" in spec
    assert spec["n_rhs"] == 0

    tex = la_figures.ge_tbl_tex(A)
    assert "\\begin{NiceArray}" in tex
    assert "\\end{NiceArray}" in tex

    spec = la_figures.ge_tbl_spec(A, array_names=True)
    assert spec.get("callouts")

    spec = la_figures.ge_tbl_spec(A, show_pivots=True)
    assert spec.get("codebefore")
    assert spec.get("rowechelon_paths")


def test_ge_tbl_layout_spec_uses_typed_layout():
    import pytest

    pytest.importorskip("matrixlayout")
    from la_figures.ge_convenience import ge_tbl_layout_spec
    from matrixlayout.specs import GEGridSpec, GELayoutSpec
    from matrixlayout.ge import render_ge_tex

    A = sym.Matrix([[1, 2], [3, 4]])
    spec = ge_tbl_layout_spec(A, show_pivots=True)

    assert isinstance(spec, GEGridSpec)
    assert isinstance(spec.layout, GELayoutSpec)
    tex = render_ge_tex(spec=spec)
    assert "\\begin{NiceArray}" in tex


def test_ge_tbl_spec_variable_summary_labels():
    import la_figures

    A = sym.Matrix([[1, 2], [3, 4]])
    spec = la_figures.ge_tbl_spec(
        A,
        variable_summary=[True, False],
        variable_colors=("blue", "orange"),
    )

    labels = spec.get("variable_labels") or []
    assert labels
    rows = labels[0]["labels"]
    assert rows[0] == [
        r"\textcolor{blue}{\ensuremath{\Uparrow}}",
        r"\textcolor{orange}{\ensuremath{\uparrow}}",
    ]
    assert rows[1] == [
        r"\textcolor{blue}{\ensuremath{x_{1}}}",
        r"\textcolor{orange}{\ensuremath{x_{2}}}",
    ]


def test_ge_tbl_spec_rhs_vline():
    import la_figures

    A = sym.Matrix([[1, 2], [3, 4]])
    spec = la_figures.ge_tbl_spec(A, rhs=[5, 6])

    decorations = spec.get("decorations") or []
    assert {"grid": (0, 1), "vlines": 2} in decorations
    assert {"grid": (1, 1), "vlines": 2} in decorations


def test_ge_tbl_spec_layout_and_bundle_match_tex():
    import pytest

    pytest.importorskip("matrixlayout")
    import la_figures
    from la_figures.ge_convenience import ge_tbl_layout_spec
    from matrixlayout.ge import render_ge_tex

    A = sym.Matrix([[1, 2], [3, 4]])
    rhs = sym.Matrix([[5], [6]])

    spec = la_figures.ge_tbl_spec(A, ref_rhs=rhs, show_pivots=True)
    layout_spec = ge_tbl_layout_spec(A, ref_rhs=rhs, show_pivots=True)
    bundle = la_figures.ge_tbl_bundle(A, ref_rhs=rhs, show_pivots=True)

    tex_spec = render_ge_tex(**spec)
    tex_layout = render_ge_tex(spec=layout_spec)
    tex_bundle = render_ge_tex(**bundle["spec"])

    assert tex_spec == tex_layout
    assert tex_spec == tex_bundle


def test_ge_tbl_spec_dict_roundtrip_render_ge_svg_accepts_spec():
    import pytest

    pytest.importorskip("matrixlayout")
    pytest.importorskip("jupyter_tikz")
    import la_figures
    from matrixlayout.ge import render_ge_svg

    A = sym.Matrix([[1, 2], [3, 4]])
    rhs = sym.Matrix([[5], [6]])

    spec = la_figures.ge_tbl_spec(A, ref_rhs=rhs, show_pivots=True, array_names=True)
    svg = render_ge_svg(spec=spec, toolchain_name="pdftex_dvisvgm", crop="tight", padding=(1, 1, 1, 1))
    assert isinstance(svg, str)
    assert "<svg" in svg


def test_ge_tbl_spec_sets_create_extra_nodes_for_array_names():
    import la_figures

    A = sym.Matrix([[1, 2], [3, 4]])
    rhs = sym.Matrix([[5], [6]])

    spec = la_figures.ge_tbl_spec(A, ref_rhs=rhs, show_pivots=True, array_names=True)
    assert spec.get("create_extra_nodes") is True


def test_ge_tbl_spec_rowechelon_paths_per_layer():
    import la_figures

    A = sym.Matrix([[1, 2], [3, 4]])
    spec = la_figures.ge_tbl_spec(A, show_pivots=True)

    rowechelon_paths = spec.get("rowechelon_paths") or []
    assert rowechelon_paths
    assert all(p.startswith(r"\draw") for p in rowechelon_paths)
    assert all(not p.startswith(r"\tikz") for p in rowechelon_paths)


def test_ge_tbl_spec_rowechelon_paths_do_not_nest_tikz_in_rendered_tex():
    import pytest

    pytest.importorskip("matrixlayout")
    import la_figures
    from matrixlayout.ge import render_ge_tex

    A = sym.Matrix([[1, 2], [1, 2], [3, 4]])
    spec = la_figures.ge_tbl_spec(A, gj=False, show_pivots=True)
    tex = render_ge_tex(spec=spec)

    assert spec.get("rowechelon_paths")
    assert r"\tikz \draw" not in tex
    assert r"\draw[blue" in tex
    assert tex.count(r"\begin{tikzpicture}") == 1
