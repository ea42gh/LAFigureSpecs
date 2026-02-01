def test_eig_tbl_bundle_builds_spec_once(monkeypatch):
    import la_figures.convenience as conv

    calls = {"n": 0}

    def fake_spec(*args, **kwargs):
        calls["n"] += 1
        return {"lambda": [1], "ma": [1], "evecs": [[[1]]], "A": [[1]]}

    monkeypatch.setattr(conv, "eig_tbl_spec", fake_spec)
    monkeypatch.setattr(conv, "_render_eig_tex_from_spec", lambda *a, **k: "tex")
    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", lambda *a, **k: "<svg/>")

    out = conv.eig_tbl_bundle([[1]])
    assert out["tex"] == "tex"
    assert out["svg"] == "<svg/>"
    assert calls["n"] == 1


def test_svd_tbl_bundle_builds_spec_once(monkeypatch):
    import la_figures.convenience as conv

    calls = {"n": 0}

    def fake_spec(*args, **kwargs):
        calls["n"] += 1
        return {"lambda": [1], "ma": [1], "evecs": [[[1]]], "A": [[1]], "sz": (1, 1)}

    monkeypatch.setattr(conv, "svd_tbl_spec", fake_spec)
    monkeypatch.setattr(conv, "_render_eig_tex_from_spec", lambda *a, **k: "tex")
    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", lambda *a, **k: "<svg/>")

    out = conv.svd_tbl_bundle([[1]])
    assert out["tex"] == "tex"
    assert out["svg"] == "<svg/>"
    assert calls["n"] == 1


def test_qr_tbl_bundle_builds_spec_once(monkeypatch):
    import la_figures.convenience_qr as conv

    calls = {"n": 0}

    def fake_spec(*args, **kwargs):
        calls["n"] += 1
        return {
            "matrices": [[None, [[1]]]],
            "array_names": True,
            "fig_scale": None,
            "preamble": "",
            "extension": "",
            "nice_options": "",
            "label_color": "blue",
            "label_text_color": "red",
            "known_zero_color": "brown",
            "decorators": None,
            "strict": False,
        }

    monkeypatch.setattr(conv, "qr_tbl_spec", fake_spec)
    monkeypatch.setattr(conv, "_render_qr_tex_from_spec", lambda *a, **k: "tex")
    monkeypatch.setattr(conv, "_render_qr_svg_from_spec", lambda *a, **k: "<svg/>")

    out = conv.qr_tbl_bundle([[1]], [[1]])
    assert out["tex"] == "tex"
    assert out["svg"] == "<svg/>"
    assert calls["n"] == 1
