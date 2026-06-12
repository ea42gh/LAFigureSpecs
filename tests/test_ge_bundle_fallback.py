def test_ge_bundle_falls_back_to_render_ge_tex(monkeypatch):
    import LAFigureSpecs.ge_convenience as ge_conv

    class _NoGridBundle:
        def __call__(self, **kwargs):
            raise ImportError("grid_bundle unavailable")

    monkeypatch.setattr("matrixlayout.ge.grid_bundle", _NoGridBundle())
    monkeypatch.setattr("matrixlayout.ge.render_ge_tex", lambda **kwargs: "% tex fallback")

    out = ge_conv.ge_bundle([[1, 0], [0, 1]])
    assert "spec" in out
    assert out["tex"] == "% tex fallback"
