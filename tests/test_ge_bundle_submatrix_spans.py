import sympy as sym


def test_ge_bundle_includes_submatrix_spans_metadata():
    import pytest

    # The spans metadata depends on the matrixlayout bundle API.
    pytest.importorskip("matrixlayout")
    import LAFigureSpecs

    A = sym.Matrix([[1, 2], [3, 4]])

    bundle = LAFigureSpecs.ge_bundle(A)
    assert isinstance(bundle, dict)
    assert "tex" in bundle
    assert "spec" in bundle
    assert "data" in bundle

    spans = bundle["data"].get("submatrix_spans")
    assert isinstance(spans, list)
    assert spans, "expected at least one SubMatrix span"

    names = {s.get("name") for s in spans}
    # In the legacy 2-column GE-grid layout, the initial layer includes A0.
    assert "A0" in names

    # Convenience fields for notebook authors.
    a0 = next(s for s in spans if s.get("name") == "A0")
    assert a0["left_delim_node"] == "A0-left"
    assert a0["right_delim_node"] == "A0-right"
