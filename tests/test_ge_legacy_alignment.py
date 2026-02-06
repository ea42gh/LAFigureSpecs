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
    assert "(3-2-medium)" in codebefore[0]
