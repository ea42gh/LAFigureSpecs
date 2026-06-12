import re

import pytest
import sympy as sym


def _extract_mat_format(tex: str) -> str:
    start = tex.find(r"\begin{NiceArray")
    if start < 0:
        return ""
    i = start + len(r"\begin{NiceArray")
    if i < len(tex) and tex[i] == "}":
        i += 1
    # Skip optional [..]
    if i < len(tex) and tex[i] == "[":
        depth = 1
        i += 1
        while i < len(tex) and depth:
            if tex[i] == "[":
                depth += 1
            elif tex[i] == "]":
                depth -= 1
            i += 1
    # Skip whitespace
    while i < len(tex) and tex[i].isspace():
        i += 1
    if i >= len(tex) or tex[i] != "{":
        return ""
    i += 1
    brace = 1
    buf = []
    while i < len(tex) and brace:
        ch = tex[i]
        if ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
            if brace == 0:
                i += 1
                break
        if brace:
            buf.append(ch)
        i += 1
    return "".join(buf).strip()


def _extract_mat_rep(tex: str) -> str:
    start = tex.find(r"\Body%")
    if start < 0:
        return ""
    start = start + len(r"\Body%")
    end = tex.find(r"\CodeAfter", start)
    if end < 0:
        body = tex[start:]
    else:
        body = tex[start:end]
    # Drop template comment markers emitted after the body (e.g., "%% %").
    body = re.sub(r"\s*%+\s*$", "", body, flags=re.MULTILINE)
    return body.strip()


def _submatrix_spans(tex: str):
    spans = []
    for line in tex.splitlines():
        if "\\SubMatrix" not in line:
            continue
        start = line.find("(")
        end = line.find(")", start + 1)
        if start < 0 or end < 0:
            continue
        inner = line[start + 1 : end]
        m = re.search(r"\{([^}]+)\}\{([^}]+)\}", inner)
        if not m:
            continue
        spans.append(f"{{{m.group(1)}}}{{{m.group(2)}}}")
    return spans


def _count_nonempty_blocks(matrices):
    count = 0
    for row in matrices:
        for mat in row:
            if mat is None:
                continue
            try:
                h, w = mat.shape
                if int(h) > 0 and int(w) > 0:
                    count += 1
            except Exception:
                if mat:
                    count += 1
    return count


@pytest.mark.parametrize(
    "A",
    [
        sym.Matrix([[1, 2], [3, 4]]),
        sym.Matrix([[1, 2], [3, 4], [5, 6]]),
        sym.Matrix([[1, 2], [2, 4]]),
    ],
)
def test_qr_layout_matches_legacy(A):
    import LAFigureSpecs
    from matrixlayout.qr import render_qr_tex

    matrices = LAFigureSpecs.compute_qr_matrices(A)
    new = render_qr_tex(matrices=matrices, formatter=str)

    assert _extract_mat_format(new)
    assert _extract_mat_rep(new)
    assert "W^T W" in new
    assert "v_1" in new
    assert len(_submatrix_spans(new)) == _count_nonempty_blocks(matrices)
