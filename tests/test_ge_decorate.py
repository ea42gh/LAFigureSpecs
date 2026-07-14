import sympy as sym
import inspect


def test_decorate_ge_canonical_pivots_and_variable_types():
    import importlib
    ge_mod = importlib.import_module("LAFigureSpecs.ge")

    A = sym.Matrix([[1, 2], [3, 4]])
    tr = ge_mod.ge_trace(A, pivoting="partial")

    decor = ge_mod.decorate_ge(tr, index_base=1)

    assert decor["variable_types"] == [True, True]
    assert decor["variable_summary"] == [True, True]
    assert decor["pivot_locs"] == [
        ("(1-1)(1-1)", ""),
        ("(2-2)(2-2)", ""),
    ]
    assert decor["text_annotations"] == []
    assert decor["rowechelon_paths"]
    assert decor["callouts"] == []


def test_decorate_ge_retains_julia_compatibility_lists():
    import importlib
    ge_mod = importlib.import_module("LAFigureSpecs.ge")

    A = sym.Matrix([[1, 2], [3, 4]])
    tr = ge_mod.ge_trace(A, pivoting="partial")

    decor = ge_mod.decorate_ge(tr, index_base=1)

    assert decor["pivot_list"][-1][1] == [(0, 0), (1, 1)]
    assert decor["bg_list"]
    assert decor["decorations"]
    assert decor["ref_path_list"] == decor["path_list"]
    assert decor["rowechelon_paths"] == [
        {
            "grid": (spec[0], spec[1]),
            "pivots": spec[2],
            "case": spec[3],
            "color": spec[4],
        }
        for spec in decor["ref_path_list"]
    ]


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


def test_decorate_ge_signature_uses_grid_naming():
    import importlib
    ge_mod = importlib.import_module("LAFigureSpecs.ge")

    params = inspect.signature(ge_mod.decorate_ge).parameters

    assert "ref_path_grid" in params
    assert "ref_path_block_col" not in params
    assert "pivot_block_col" not in params
