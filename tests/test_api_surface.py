# mypy: disable-error-code="call-arg"

def test_public_api_exports_expected_names():
    import LAFigureSpecs

    expected = {
        "EigenDecomposition",
        "ShowGE",
        "__build__",
        "__version__",
        "backsubstitution_tex",
        "bundle_summary",
        "compute_qr_matrices",
        "decorate_tex_entries",
        "decorator_bf",
        "decorator_bg",
        "decorator_box",
        "decorator_color",
        "eig_bundle",
        "eig_matrices_from_spec",
        "eig_spec",
        "eig_spec_from_eigenvects",
        "eig_svg",
        "eig_tex",
        "eigendecomposition",
        "ge_bundle",
        "ge_layout_spec",
        "ge_spec",
        "ge_svg",
        "ge_tex",
        "ge_trace",
        "gram_schmidt_qr_matrices",
        "latex_document_svg",
        "latex_svg",
        "latexify",
        "lhs_matrix",
        "linear_system_tex",
        "lshow_svg",
        "make_decorator",
        "mm_to_px",
        "naive_gram_schmidt_w",
        "naive_qr",
        "px_to_mm",
        "qr_bundle",
        "qr_figure",
        "qr_layout_spec",
        "qr_matrices_dict_from_grid",
        "qr_matrices_from_grid",
        "qr_spec",
        "qr_spec_from_matrices",
        "qr_svg",
        "qr_tex",
        "ref",
        "rhs_column",
        "rhs_matrix",
        "sel_all",
        "sel_box",
        "sel_col",
        "sel_cols",
        "sel_entry",
        "sel_row",
        "sel_rows",
        "sel_vec",
        "sel_vec_range",
        "show_backsubstitution",
        "show_ge",
        "show_layout",
        "show_solution",
        "show_svg",
        "show_system",
        "solutions",
        "standard_solution_tex",
        "svd_bundle",
        "svd_matrices_from_spec",
        "svd_spec",
        "svd_spec_from_right_singular_vectors",
        "svd_svg",
        "svd_tex",
        "trace_to_layer_matrices",
    }
    assert set(LAFigureSpecs.__all__) == expected

def test_ge_paths_exports_only_canonical_helper():
    import LAFigureSpecs.ge_paths as ge_paths

    assert set(ge_paths.__all__) == {"rowechelon_paths_from_specs"}


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


def test_bundle_apis_reject_unknown_keywords():
    import pytest

    import LAFigureSpecs

    with pytest.raises(TypeError, match="unexpected keyword.*bogus"):
        LAFigureSpecs.eig_bundle([[1, 0], [0, 1]], bogus=True)
    with pytest.raises(TypeError, match="unexpected keyword.*bogus"):
        LAFigureSpecs.svd_bundle([[1, 0], [0, 1]], bogus=True)
    with pytest.raises(TypeError, match="unexpected keyword.*bogus"):
        LAFigureSpecs.qr_bundle([[1, 0], [0, 1]], bogus=True)



def test_api_docs_describe_bundle_keyword_contract():
    text = __import__('pathlib').Path('docs/api.md').read_text(encoding='utf-8')
    normalized = ' '.join(text.split())

    assert 'Bundle helpers accept the same documented compute/render options' in normalized
    assert 'unknown keywords raise `TypeError` instead of being ignored' in normalized
