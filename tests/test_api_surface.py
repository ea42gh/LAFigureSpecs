def test_public_api_contains_canonical_render_names():
    import la_figures

    assert "ge" in la_figures.__all__
    assert "qr" in la_figures.__all__
    assert "render_ge_svg" in la_figures.__all__
    assert "render_qr_svg" in la_figures.__all__
    assert "render_eig_svg" in la_figures.__all__


def test_public_api_does_not_export_legacy_aliases():
    import la_figures

    assert "svg" not in la_figures.__all__
    assert "qr_svg" not in la_figures.__all__


def test_bundle_return_contracts_have_spec_tex_svg_keys():
    import la_figures

    ge_bundle = la_figures.ge_tbl_bundle([[1, 0], [0, 1]])
    assert set(["spec", "tex", "svg", "data", "render_error"]).issubset(ge_bundle.keys())
    assert "trace" not in ge_bundle and "decor" not in ge_bundle and "layers" not in ge_bundle
    assert set(["trace", "decor", "layers", "typed_layout"]).issubset(ge_bundle["data"].keys())

    eig_bundle = la_figures.eig_tbl_bundle([[1, 0], [0, 1]])
    assert set(["spec", "tex", "svg", "data", "render_error"]).issubset(eig_bundle.keys())

    svd_bundle = la_figures.svd_tbl_bundle([[1, 0], [0, 1]])
    assert set(["spec", "tex", "svg", "data", "render_error"]).issubset(svd_bundle.keys())

    qr_bundle = la_figures.qr_tbl_bundle([[1, 0], [0, 1]])
    assert set(["spec", "tex", "svg", "data", "render_error"]).issubset(qr_bundle.keys())
