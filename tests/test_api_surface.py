def test_public_api_contains_canonical_render_names():
    import LAFigureSpecs

    assert "ge" in LAFigureSpecs.__all__
    assert "qr" in LAFigureSpecs.__all__
    assert "render_ge_svg" in LAFigureSpecs.__all__
    assert "render_qr_svg" in LAFigureSpecs.__all__
    assert "render_eig_svg" in LAFigureSpecs.__all__
    assert "latex_svg" in LAFigureSpecs.__all__
    assert "latex_document_svg" in LAFigureSpecs.__all__
    assert "lshow_svg" in LAFigureSpecs.__all__


def test_public_api_does_not_export_legacy_aliases():
    import LAFigureSpecs

    assert "svg" not in LAFigureSpecs.__all__
    assert "qr_svg" not in LAFigureSpecs.__all__


def test_bundle_return_contracts_have_spec_tex_svg_keys():
    import LAFigureSpecs

    ge_bundle = LAFigureSpecs.ge_tbl_bundle([[1, 0], [0, 1]])
    assert {"spec", "tex", "svg", "data", "render_error"}.issubset(ge_bundle.keys())
    assert "trace" not in ge_bundle and "decor" not in ge_bundle and "layers" not in ge_bundle
    assert {"trace", "decor", "layers", "typed_layout"}.issubset(ge_bundle["data"].keys())

    eig_bundle = LAFigureSpecs.eig_tbl_bundle([[1, 0], [0, 1]])
    assert {"spec", "tex", "svg", "data", "render_error"}.issubset(eig_bundle.keys())

    svd_bundle = LAFigureSpecs.svd_tbl_bundle([[1, 0], [0, 1]])
    assert {"spec", "tex", "svg", "data", "render_error"}.issubset(svd_bundle.keys())

    qr_bundle = LAFigureSpecs.qr_tbl_bundle([[1, 0], [0, 1]])
    assert {"spec", "tex", "svg", "data", "render_error"}.issubset(qr_bundle.keys())
