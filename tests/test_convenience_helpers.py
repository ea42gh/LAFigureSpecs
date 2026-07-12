def test_filter_tex_kwargs_removes_svg_only_options():
    import LAFigureSpecs.convenience as conv

    kwargs = {
        "output_dir": "out",
        "toolchain_name": "pdftex_dvisvgm",
        "crop": "tight",
        "padding": (1, 1, 1, 1),
        "frame": None,
        "normal": True,
        "mmLambda": 7,
    }
    out = conv._filter_tex_kwargs(kwargs)
    assert "output_dir" not in out
    assert "toolchain_name" not in out
    assert "crop" not in out
    assert "padding" not in out
    assert "frame" not in out
    assert out["normal"] is True
    assert out["mmLambda"] == 7


def test_julia_str_normalizes_symbol_like_strings():
    import LAFigureSpecs.convenience as conv

    assert conv._julia_str(":foo") == "foo"
    assert conv._julia_str("Symbol(:bar)") == "bar"


def test_eig_svg_passes_matrix_specific_spacing(monkeypatch):
    import LAFigureSpecs.convenience as conv

    calls = {}

    def fake_render(spec, **kwargs):
        calls["spec"] = spec
        calls["kwargs"] = kwargs
        return "<svg/>"

    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", fake_render)

    svg = conv.eig_svg([[1, 0], [0, 1]], normal=True, mmLambda=10, mmQ=6)

    assert svg == "<svg/>"
    assert calls["kwargs"]["mmLambda"] == 10
    assert calls["kwargs"]["mmQ"] == 6
    assert calls["kwargs"]["mmSigma"] is None
    assert calls["kwargs"]["mmU"] is None
    assert calls["kwargs"]["mmV"] is None


def test_svd_svg_passes_matrix_specific_spacing(monkeypatch):
    import LAFigureSpecs.convenience as conv

    calls = {}

    def fake_render(spec, **kwargs):
        calls["spec"] = spec
        calls["kwargs"] = kwargs
        return "<svg/>"

    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", fake_render)

    svg = conv.svd_svg([[1, 0], [0, 1]], mmSigma=9, mmU=5, mmV=7)

    assert svg == "<svg/>"
    assert calls["kwargs"]["mmSigma"] == 9
    assert calls["kwargs"]["mmU"] == 5
    assert calls["kwargs"]["mmV"] == 7
