from LAFigureSpecs.ge_convenience import _legacy_bg_list_to_codebefore


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


def test_legacy_vertical_column_highlights_use_medium_nodes():
    matrices = [
        [None, [[1, 2], [3, 4], [5, 6]]],
    ]
    bg_list = [[0, 1, [((0, 1), (2, 1))], "yellow!40", 1]]
    codebefore = _legacy_bg_list_to_codebefore(matrices, bg_list)
    assert codebefore
    assert "fit = (1-2-medium) (3-2-medium)" in codebefore[0]


def test_legacy_ge_disables_format_nrhs_when_using_decorations(monkeypatch):
    import LAFigureSpecs.ge_convenience as ge_conv
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


def test_legacy_ge_supports_nrhs_list(monkeypatch):
    import LAFigureSpecs.ge_convenience as ge_conv
    import matrixlayout.ge as ml_ge

    captured = {}

    def fake_render_ge_svg(**kwargs):
        captured.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_render_ge_svg)

    matrices = [
        [None, [[1, 2, 3, 4, 5, 6, 7, 8]]],
    ]
    ge_conv.ge(
        matrices,
        Nrhs=[2, 3, 1],
        variable_summary=[True, False, False, False, False],
    )
    decorations = captured.get("decorations") or []
    assert decorations
    # A has 8 cols; rhs blocks 2,3,1 => A width 2, splits at 2, 4, 7.
    assert decorations[0]["vlines"] == [2, 4, 7]
