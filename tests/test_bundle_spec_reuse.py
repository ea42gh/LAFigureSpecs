def test_eig_tbl_bundle_builds_spec_once(monkeypatch):
    import LAFigureSpecs.convenience as conv

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
    import LAFigureSpecs.convenience as conv

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


def test_svd_tbl_bundle_passes_matrix_factor_out(monkeypatch):
    import LAFigureSpecs.convenience as conv

    render_calls = {}

    def fake_spec(*args, **kwargs):
        return {"lambda": [1], "ma": [1], "evecs": [[[1]]], "A": [[1]], "sz": (1, 1)}

    def fake_tex(spec, **kwargs):
        render_calls["tex"] = kwargs
        return "tex"

    def fake_svg(spec, **kwargs):
        render_calls["svg"] = kwargs
        return "<svg/>"

    monkeypatch.setattr(conv, "svd_tbl_spec", fake_spec)
    monkeypatch.setattr(conv, "_render_eig_tex_from_spec", fake_tex)
    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", fake_svg)

    out = conv.svd_tbl_bundle([[1]], matrix_factor_out={"sigma_matrix": True, "u": True})
    assert out["tex"] == "tex"
    assert out["svg"] == "<svg/>"
    assert render_calls["tex"]["matrix_factor_out"] == {"sigma_matrix": True, "u": True}
    assert render_calls["svg"]["matrix_factor_out"] == {"sigma_matrix": True, "u": True}


def test_svd_bundle_alias_passes_matrix_factor_out(monkeypatch):
    import LAFigureSpecs
    import LAFigureSpecs.convenience as conv

    render_calls = {}

    def fake_spec(*args, **kwargs):
        return {"lambda": [1], "ma": [1], "evecs": [[[1]]], "A": [[1]], "sz": (1, 1)}

    def fake_tex(spec, **kwargs):
        render_calls["tex"] = kwargs
        return "tex"

    def fake_svg(spec, **kwargs):
        render_calls["svg"] = kwargs
        return "<svg/>"

    monkeypatch.setattr(conv, "svd_tbl_spec", fake_spec)
    monkeypatch.setattr(conv, "_render_eig_tex_from_spec", fake_tex)
    monkeypatch.setattr(conv, "_render_eig_svg_from_spec", fake_svg)

    out = LAFigureSpecs.svd_bundle([[1]], matrix_factor_out={"sigma_matrix": True, "u": True})
    assert out["tex"] == "tex"
    assert out["svg"] == "<svg/>"
    assert render_calls["tex"]["matrix_factor_out"] == {"sigma_matrix": True, "u": True}
    assert render_calls["svg"]["matrix_factor_out"] == {"sigma_matrix": True, "u": True}


def test_qr_tbl_bundle_builds_spec_once(monkeypatch):
    import LAFigureSpecs.convenience_qr as conv

    calls = {"n": 0}

    def fake_spec(*args, **kwargs):
        calls["n"] += 1
        return {
            "matrices": [[None, [[1]]]],
            "array_names": True,
            "fig_scale": None,
            "body_preamble": "",
            "document_preamble": "",
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

    out = conv.qr_tbl_bundle([[1]])
    assert out["tex"] == "tex"
    assert out["svg"] == "<svg/>"
    assert calls["n"] == 1
