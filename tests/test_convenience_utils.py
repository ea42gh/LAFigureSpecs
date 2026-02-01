from la_figures.convenience_utils import make_bundle, norm_padding, norm_str, resolve_output_dir


def test_norm_str_handles_symbols_and_colons():
    assert norm_str(":foo") == "foo"
    assert norm_str("Symbol(:bar)") == "bar"
    assert norm_str("Symbol('baz')") == "baz"
    assert norm_str("  trim  ") == "trim"


def test_norm_str_passthrough_none():
    assert norm_str(None) is None


def test_norm_padding_normalizes_sequences():
    assert norm_padding((1, 2, 3, 4)) == (1, 2, 3, 4)
    assert norm_padding([1, 2, 3, 4]) == (1, 2, 3, 4)
    assert norm_padding([1, 2]) == (1, 2)


def test_norm_padding_passthrough_none():
    assert norm_padding(None) is None


def test_resolve_output_dir_alias_rules():
    assert resolve_output_dir(output_dir="out", tmp_dir="tmp") == "out"
    assert resolve_output_dir(output_dir=None, tmp_dir="tmp") == "tmp"
    assert resolve_output_dir(output_dir=None, tmp_dir=None) is None


def test_make_bundle_contract_defaults():
    out = make_bundle(spec={"a": 1}, tex="% tex", svg=None)
    assert out["spec"] == {"a": 1}
    assert out["tex"] == "% tex"
    assert out["svg"] is None
    assert out["data"] == {}
    assert out["render_error"] is None
