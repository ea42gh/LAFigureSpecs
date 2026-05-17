import pytest
import builtins

from LAFigureSpecs.formatting import (
    decorate_tex_entries,
    decorator_bf,
    decorator_bg,
    decorator_box,
    decorator_color,
    latexify,
    make_decorator,
    sel_all,
    sel_box,
    sel_col,
    sel_cols,
    sel_entry,
    sel_row,
    sel_rows,
    sel_vec,
    sel_vec_range,
)


def test_latexify_string_passthrough():
    assert latexify(r"\alpha + 1") == r"\alpha + 1"


def test_latexify_numbers():
    assert latexify(3) == "3"
    assert latexify(1.2300) == "1.23"


def test_latexify_tuple_rational():
    assert latexify((1, 2)) == r"\frac{1}{2}"


def test_latexify_sympy_objects():
    sym = pytest.importorskip("sympy")
    assert latexify(sym.pi) == r"\pi"
    assert latexify(sym.Rational(1, 2)) == r"\frac{1}{2}"
    assert latexify(sym.Symbol("x")) == "x"


def test_latexify_fraction_bool_and_fallback_object():
    from fractions import Fraction

    class Thing:
        def __str__(self):
            return "thing"

    assert latexify(Fraction(2, 3)) == r"\frac{2}{3}"
    assert latexify(True) == "True"
    assert latexify(Thing()) == "thing"


def test_decorator_helpers_return_tex_transformers():
    assert decorator_box()("x") == r"\color{black}{\boxed{x}}"
    assert decorator_box(color="red")("x") == r"\color{black}{\colorboxed{red}{x}}"
    assert decorator_color("blue")("x") == r"\color{blue}{x}"
    assert decorator_bg("yellow!20")("x") == r"\colorbox{yellow!20}{x}"
    assert decorator_bf()("x") == r"\color{black}{\mathbf{x}}"

    dec = make_decorator(text_color="green", bg_color="yellow", bf=True, move_right=True, delim="|")
    assert dec("x") == r"|\mathrlap{\color{green}{\colorbox{yellow}{\ensuremath{\mathbf{x}}}}}|"


def test_selector_helpers_match_matrixlayout_shapes():
    assert sel_entry(1, 2) == (1, 2)
    assert sel_box((0, 1), (2, 3)) == ((0, 1), (2, 3))
    assert sel_row(2) == {"row": 2}
    assert sel_col(3) == {"col": 3}
    assert sel_rows([0, 2]) == {"rows": [0, 2]}
    assert sel_cols([1, 3]) == {"cols": [1, 3]}
    assert sel_all() == {"all": True}
    assert sel_vec(1, 2, 3) == (1, 2, 3)
    assert sel_vec_range((0, 1, 2), (3, 4, 5)) == ((0, 1, 2), (3, 4, 5))


def test_decorate_tex_entries_updates_selected_entries_only():
    matrices = [[None, [[1, 2], [3, 4]]]]

    out = decorate_tex_entries(
        matrices,
        0,
        1,
        decorator_color("red"),
        entries=[sel_entry(0, 1), sel_entry(4, 4)],
    )

    assert out[0][1][0][0] == 1
    assert out[0][1][0][1] == r"\color{red}{2}"
    assert out[0][1][1][0] == 3
    assert out[0][1][1][1] == 4


def test_decorate_tex_entries_handles_none_target_and_bad_grid():
    matrices = [[None]]

    assert decorate_tex_entries(matrices, 0, 0, decorator_bf()) == [[None]]
    with pytest.raises(IndexError):
        decorate_tex_entries(matrices, 1, 0, decorator_bf())


def test_local_latexify_fallback_when_matrixlayout_formatting_unavailable(monkeypatch):
    from fractions import Fraction

    original_import = builtins.__import__

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "matrixlayout.formatting":
            raise ImportError("blocked for fallback coverage")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    assert latexify("x") == "x"
    assert latexify((3, 5)) == r"\frac{3}{5}"
    assert latexify(Fraction(7, 11)) == r"\frac{7}{11}"
    assert latexify(2.5) == "2.5"
    assert latexify(True) == "True"

    sym = pytest.importorskip("sympy")
    assert latexify(sym.Symbol("z") + 1) == "z + 1"


def test_selector_fallbacks_when_matrixlayout_formatting_unavailable(monkeypatch):
    original_import = builtins.__import__

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "matrixlayout.formatting":
            raise ImportError("blocked for fallback coverage")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    assert sel_entry("1", "2") == (1, 2)
    assert sel_box(["0", "1"], ("2", "3")) == (("0", "1"), ("2", "3"))
    assert sel_row("4") == {"row": 4}
    assert sel_col("5") == {"col": 5}
    assert sel_rows(["0", 2]) == {"rows": [0, 2]}
    assert sel_cols(["1", 3]) == {"cols": [1, 3]}
    assert sel_all() == {"all": True}
    assert sel_vec("1", "2", "3") == (1, 2, 3)
    assert sel_vec_range(["0", "1", "2"], ("3", "4", "5")) == (("0", "1", "2"), ("3", "4", "5"))


def test_decorator_fallbacks_raise_without_matrixlayout_formatting(monkeypatch):
    original_import = builtins.__import__

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "matrixlayout.formatting":
            raise ImportError("blocked for fallback coverage")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    with pytest.raises(RuntimeError, match="matrixlayout is required"):
        make_decorator(text_color="red")
    with pytest.raises(RuntimeError, match="matrixlayout is required"):
        decorator_box()("x")
    with pytest.raises(RuntimeError, match="matrixlayout is required"):
        decorator_box(color="red")("x")
    with pytest.raises(RuntimeError, match="matrixlayout is required"):
        decorator_color("red")("x")
    with pytest.raises(RuntimeError, match="matrixlayout is required"):
        decorator_bg("yellow")("x")
    with pytest.raises(RuntimeError, match="matrixlayout is required"):
        decorator_bf()("x")
    with pytest.raises(RuntimeError, match="matrixlayout is required"):
        decorate_tex_entries([[1]], 0, 0, lambda x: x)
