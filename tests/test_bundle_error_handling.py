def test_eig_bundle_sets_svg_none_on_render_failure(monkeypatch):
    import LAFigureSpecs.convenience as conv

    monkeypatch.setattr(
        conv,
        "_render_eig_svg_from_spec",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    out = conv.eig_bundle([[1, 0], [0, 1]])
    assert "spec" in out and "tex" in out and "svg" in out and "data" in out and "render_error" in out
    assert out["svg"] is None
    assert "boom" in out["render_error"]


def test_svd_bundle_sets_svg_none_on_render_failure(monkeypatch):
    import LAFigureSpecs.convenience as conv

    monkeypatch.setattr(
        conv,
        "_render_eig_svg_from_spec",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    out = conv.svd_bundle([[1, 0], [0, 1]])
    assert "spec" in out and "tex" in out and "svg" in out and "data" in out and "render_error" in out
    assert out["svg"] is None
    assert "boom" in out["render_error"]


def test_qr_bundle_sets_svg_none_on_render_failure(monkeypatch):
    import LAFigureSpecs.convenience_qr as conv

    monkeypatch.setattr(
        conv,
        "_render_qr_svg_from_spec",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    out = conv.qr_bundle([[1, 0], [0, 1]])
    assert "spec" in out and "tex" in out and "svg" in out and "data" in out and "render_error" in out
    assert out["svg"] is None
    assert "boom" in out["render_error"]
