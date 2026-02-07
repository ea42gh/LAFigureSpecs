from la_figures.ge_convenience import _legacy_bg_list_to_codebefore


def test_legacy_bg_uses_block_padding_for_right_align():
    matrices = [
        [None, [[1, 2]]],
        [[[1, 2, 3]], [[1, 2]]],
        [[[1, 2]], [[1, 2]]],
    ]
    bg_list = [[2, 0, [(0, 0)], "yellow!35", 1]]
    codebefore = _legacy_bg_list_to_codebefore(matrices, bg_list)
    assert codebefore
    # Column 0 has width 3 (from row 1), but row 2 col 0 is width 2.
    # With default block_align=auto (right), the leftmost entry is shifted by 1.
    assert "(3-2)" in codebefore[0]


def test_legacy_ge_disables_format_nrhs_when_using_decorations(monkeypatch):
    import la_figures.ge_convenience as ge_conv
    import matrixlayout.ge as ml_ge

    captured = {}

    def fake_render_ge_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_render_ge_svg)

    matrices = [
        [None, [[1, 2], [3, 4]]],
        [[[1, 0], [0, 1]], [[5, 6], [7, 8]]],
    ]
    ge_conv.ge(
        matrices,
        Nrhs=1,
        variable_summary=[True, False],
    )
    assert captured.get("format_nrhs") is False
    decorations = captured.get("decorations") or []
    assert decorations
