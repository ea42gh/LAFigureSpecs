import sympy as sym
import inspect


def test_decorate_ge_canonical_pivots_and_variable_types():
    import importlib
    ge_mod = importlib.import_module("LAFigureSpecs.ge")

    A = sym.Matrix([[1, 2], [3, 4]])
    tr = ge_mod.ge_trace(A, pivoting="partial")

    decor = ge_mod.decorate_ge(tr, index_base=1)

    assert decor["variable_types"] == [True, True]
    assert decor["pivot_locs"] == [
        ("(1-1)(1-1)", ""),
        ("(2-2)(2-2)", ""),
    ]
    assert decor["text_annotations"] == []
    assert decor["rowechelon_paths"]
    assert decor["callouts"] == []


def test_decorate_ge_returns_canonical_render_specs_only():
    import importlib
    ge_mod = importlib.import_module("LAFigureSpecs.ge")

    A = sym.Matrix([[1, 2], [3, 4]])
    tr = ge_mod.ge_trace(A, pivoting="partial")

    decor = ge_mod.decorate_ge(tr, index_base=1)

    assert decor["pivot_selectors"][-1] == {"grid": (2, 1), "entries": [(0, 0), (1, 1)]}
    assert decor["decorations"]
    assert decor["rowechelon_paths"]
    for removed in ("pivot_list", "bg_list", "path_list", "ref_path_list", "variable_summary"):
        assert removed not in decor


def test_decorate_ge_excludes_rhs_from_variable_types():
    import importlib
    ge_mod = importlib.import_module("LAFigureSpecs.ge")

    A = sym.Matrix([[1, 2], [3, 4]])
    rhs = sym.Matrix([[5], [6]])

    tr = ge_mod.ge_trace(A, rhs, pivoting="partial")
    assert tr.n_rhs == 1

    decor = ge_mod.decorate_ge(tr, index_base=1)

    # RHS columns must not be classified as variables.
    assert len(decor["variable_types"]) == A.cols
    assert decor["variable_types"] == [True, True]


def test_decorate_ge_signature_uses_rowechelon_path_grid_naming():
    import importlib
    ge_mod = importlib.import_module("LAFigureSpecs.ge")

    params = inspect.signature(ge_mod.decorate_ge).parameters

    assert "rowechelon_path_grid" in params
    assert "rowechelon_path_block_col" not in params
    assert "pivot_block_col" not in params
