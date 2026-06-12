def test_public_api_contains_canonical_render_names():
    import LAFigureSpecs

    assert "ge" in LAFigureSpecs.__all__
    assert "qr" in LAFigureSpecs.__all__
    assert "ge_svg" in LAFigureSpecs.__all__
    assert "qr_svg" in LAFigureSpecs.__all__
    assert "eig_svg" in LAFigureSpecs.__all__
    assert "svd_svg" in LAFigureSpecs.__all__
    assert "ge_spec" in LAFigureSpecs.__all__
    assert "qr_spec" in LAFigureSpecs.__all__
    assert "eig_spec" in LAFigureSpecs.__all__
    assert "svd_spec" in LAFigureSpecs.__all__
    assert "ge_tex" in LAFigureSpecs.__all__
    assert "qr_tex" in LAFigureSpecs.__all__
    assert "eig_tex" in LAFigureSpecs.__all__
    assert "svd_tex" in LAFigureSpecs.__all__
    assert "qr_figure" in LAFigureSpecs.__all__
    assert "ge_bundle" in LAFigureSpecs.__all__
    assert "qr_bundle" in LAFigureSpecs.__all__
    assert "eig_bundle" in LAFigureSpecs.__all__
    assert "svd_bundle" in LAFigureSpecs.__all__
    assert "ShowGE" in LAFigureSpecs.__all__
    assert "ref" in LAFigureSpecs.__all__
    assert "lhs_matrix" in LAFigureSpecs.__all__
    assert "rhs_matrix" in LAFigureSpecs.__all__
    assert "rhs_column" in LAFigureSpecs.__all__
    assert "show_layout" in LAFigureSpecs.__all__
    assert "show_system" in LAFigureSpecs.__all__
    assert "show_backsubstitution" in LAFigureSpecs.__all__
    assert "show_solution" in LAFigureSpecs.__all__
    assert "rhs_block" in LAFigureSpecs.__all__
    assert "solutions" in LAFigureSpecs.__all__
    assert "render_ge_svg" in LAFigureSpecs.__all__
    assert "render_qr_svg" in LAFigureSpecs.__all__
    assert "render_eig_svg" in LAFigureSpecs.__all__
    assert "latex_svg" in LAFigureSpecs.__all__
    assert "latex_document_svg" in LAFigureSpecs.__all__
    assert "lshow_svg" in LAFigureSpecs.__all__


def test_public_api_does_not_export_legacy_aliases():
    import LAFigureSpecs

    assert "svg" not in LAFigureSpecs.__all__


def test_canonical_aliases_point_to_existing_top_level_helpers():
    import LAFigureSpecs

    assert LAFigureSpecs.ge_svg is LAFigureSpecs.ge
    assert LAFigureSpecs.qr_svg is LAFigureSpecs.qr
    assert LAFigureSpecs.eig_svg is LAFigureSpecs.eig_tbl_svg
    assert LAFigureSpecs.svd_svg is LAFigureSpecs.svd_tbl_svg
    assert LAFigureSpecs.ge_spec is LAFigureSpecs.ge_tbl_spec
    assert LAFigureSpecs.qr_spec is LAFigureSpecs.qr_tbl_spec
    assert LAFigureSpecs.eig_spec is LAFigureSpecs.eig_tbl_spec
    assert LAFigureSpecs.svd_spec is LAFigureSpecs.svd_tbl_spec
    assert LAFigureSpecs.ge_tex is LAFigureSpecs.ge_tbl_tex
    assert LAFigureSpecs.qr_tex is LAFigureSpecs.qr_tbl_tex
    assert LAFigureSpecs.eig_tex is LAFigureSpecs.eig_tbl_tex
    assert LAFigureSpecs.svd_tex is LAFigureSpecs.svd_tbl_tex
    assert LAFigureSpecs.qr_figure is LAFigureSpecs.gram_schmidt_qr
    assert LAFigureSpecs.ge_bundle is LAFigureSpecs.ge_tbl_bundle
    assert LAFigureSpecs.qr_bundle is LAFigureSpecs.qr_tbl_bundle
    assert LAFigureSpecs.eig_bundle is LAFigureSpecs.eig_tbl_bundle
    assert LAFigureSpecs.svd_bundle is LAFigureSpecs.svd_tbl_bundle


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
