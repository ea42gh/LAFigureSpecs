def test_public_api_contains_canonical_render_names():
    import LAFigureSpecs

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
    assert "solutions" in LAFigureSpecs.__all__
    assert "render_ge_svg" in LAFigureSpecs.__all__
    assert "render_qr_svg" in LAFigureSpecs.__all__
    assert "render_eig_svg" in LAFigureSpecs.__all__
    assert "latex_svg" in LAFigureSpecs.__all__
    assert "latex_document_svg" in LAFigureSpecs.__all__
    assert "lshow_svg" in LAFigureSpecs.__all__


def test_public_api_does_not_export_legacy_names():
    import LAFigureSpecs
    import LAFigureSpecs.convenience_ge as convenience_ge

    assert "svg" not in LAFigureSpecs.__all__
    assert "ge" not in LAFigureSpecs.__all__
    assert "qr" not in LAFigureSpecs.__all__
    assert not any("_tbl" in name for name in LAFigureSpecs.__all__)
    assert "gram_schmidt_qr" not in LAFigureSpecs.__all__
    assert not hasattr(LAFigureSpecs, "gram_schmidt_qr")
    assert "rhs_block" not in LAFigureSpecs.__all__
    assert not hasattr(LAFigureSpecs, "rhs_block")
    assert "decorate_ge" not in LAFigureSpecs.__all__
    assert not hasattr(LAFigureSpecs, "decorate_ge")
    assert "ge_stack_svg" not in LAFigureSpecs.__all__
    assert "qr_stack_svg" not in LAFigureSpecs.__all__
    assert not hasattr(LAFigureSpecs, "ge_stack_svg")
    assert not hasattr(LAFigureSpecs, "qr_stack_svg")
    assert "ge_stack_svg" not in convenience_ge.__all__
    assert not hasattr(convenience_ge, "ge_stack_svg")


def test_ge_paths_exports_only_canonical_helper():
    import LAFigureSpecs.ge_paths as ge_paths

    assert "rowechelon_paths_from_specs" in ge_paths.__all__
    assert "rowechelon_paths_from_legacy_tuples" not in ge_paths.__all__
    assert not hasattr(ge_paths, "rowechelon_paths_from_legacy_tuples")


def test_canonical_names_point_to_existing_top_level_helpers():
    import LAFigureSpecs

    from LAFigureSpecs.ge_convenience import ge_svg

    assert LAFigureSpecs.ge_svg is ge_svg
    from LAFigureSpecs.convenience_qr import qr_figure, qr_svg

    assert LAFigureSpecs.qr_svg is qr_svg
    assert LAFigureSpecs.qr_figure is qr_figure


def test_bundle_return_contracts_have_spec_tex_svg_keys():
    import LAFigureSpecs

    ge_bundle = LAFigureSpecs.ge_bundle([[1, 0], [0, 1]])
    assert {"spec", "tex", "svg", "data", "render_error"}.issubset(ge_bundle.keys())
    assert "trace" not in ge_bundle and "decor" not in ge_bundle and "layers" not in ge_bundle
    assert {"trace", "decor", "layers", "typed_layout"}.issubset(ge_bundle["data"].keys())

    eig_bundle = LAFigureSpecs.eig_bundle([[1, 0], [0, 1]])
    assert {"spec", "tex", "svg", "data", "render_error"}.issubset(eig_bundle.keys())

    svd_bundle = LAFigureSpecs.svd_bundle([[1, 0], [0, 1]])
    assert {"spec", "tex", "svg", "data", "render_error"}.issubset(svd_bundle.keys())

    qr_bundle = LAFigureSpecs.qr_bundle([[1, 0], [0, 1]])
    assert {"spec", "tex", "svg", "data", "render_error"}.issubset(qr_bundle.keys())


def test_svd_high_level_apis_reject_removed_sigma2_digits_alias():
    import pytest

    import LAFigureSpecs

    with pytest.raises(TypeError, match="sigma2_digits"):
        LAFigureSpecs.svd_spec([[1, 0], [0, 1]], sigma2_digits=0)
    with pytest.raises(TypeError, match="sigma2_digits"):
        LAFigureSpecs.svd_tex([[1, 0], [0, 1]], sigma2_digits=0)
    with pytest.raises(TypeError, match="sigma2_digits"):
        LAFigureSpecs.svd_svg([[1, 0], [0, 1]], sigma2_digits=0)
    with pytest.raises(TypeError, match="eig_digits"):
        LAFigureSpecs.svd_bundle([[1, 0], [0, 1]], sigma2_digits=0)
