def test_filter_tex_kwargs_removes_svg_only_options():
    import LAFigureSpecs.convenience as conv

    kwargs = {
        "output_dir": "out",
        "tmp_dir": "tmp",
        "toolchain_name": "pdftex_dvisvgm",
        "crop": "tight",
        "padding": (1, 1, 1, 1),
        "frame": None,
        "normal": True,
        "mmLambda": 7,
    }
    out = conv._filter_tex_kwargs(kwargs)
    assert "output_dir" not in out
    assert "tmp_dir" not in out
    assert "toolchain_name" not in out
    assert "crop" not in out
    assert "padding" not in out
    assert "frame" not in out
    assert out["normal"] is True
    assert out["mmLambda"] == 7


def test_julia_str_aliases_norm_str():
    import LAFigureSpecs.convenience as conv

    assert conv._julia_str(":foo") == "foo"
    assert conv._julia_str("Symbol(:bar)") == "bar"
