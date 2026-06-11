"""Legacy GE layout compatibility helpers.

These helpers preserve old ``LAFigureSpecs.ge(...)`` callback and decoration
behavior while the public wrappers migrate toward typed matrixlayout specs.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .formatting import make_decorator


def _matrix_shape(mat: Any) -> Tuple[int, int]:
    if mat is None:
        return (0, 0)
    if hasattr(mat, "shape"):
        try:
            shp = mat.shape
            if len(shp) == 2:
                return int(shp[0]), int(shp[1])
        except Exception:
            pass
    if isinstance(mat, (list, tuple)):
        rows = list(mat)
        if not rows:
            return (0, 0)
        if isinstance(rows[0], (list, tuple)):
            return (len(rows), max((len(r) for r in rows), default=0))
        return (len(rows), 1)
    return (0, 0)


def _grid_offsets(
    matrices: Sequence[Sequence[Any]],
    *,
    index_base: int = 1,
) -> Tuple[List[int], List[int], List[int], List[int]]:
    grid: List[List[Any]] = [list(r) for r in (matrices or [])]
    if not grid:
        return ([], [], [], [])
    n_block_rows = len(grid)
    n_block_cols = max((len(r) for r in grid), default=0)
    for r in range(n_block_rows):
        if len(grid[r]) < n_block_cols:
            grid[r].extend([None] * (n_block_cols - len(grid[r])))

    block_heights = [0] * n_block_rows
    block_widths = [0] * n_block_cols
    for br in range(n_block_rows):
        for bc in range(n_block_cols):
            h, w = _matrix_shape(grid[br][bc])
            block_heights[br] = max(block_heights[br], h)
            block_widths[bc] = max(block_widths[bc], w)

    max_h = max(block_heights) if block_heights else 0
    for bc in range(n_block_cols):
        if block_widths[bc] == 0 and max_h > 0:
            block_widths[bc] = max_h

    row_starts: List[int] = []
    acc = int(index_base)
    for h in block_heights:
        row_starts.append(acc)
        acc += h
    col_starts: List[int] = []
    acc = int(index_base)
    for w in block_widths:
        col_starts.append(acc)
        acc += w

    return block_heights, block_widths, row_starts, col_starts


def _block_pad_left(width: int, actual: int, block_align: Optional[str]) -> int:
    if actual <= 0 or width <= actual:
        return 0
    mode = (block_align or "auto").strip().lower()
    if mode in ("left", "l", "none"):
        return 0
    if mode in ("center", "centre", "c"):
        return (width - actual) // 2
    if mode in ("right", "r", "auto"):
        return width - actual
    raise ValueError(f"Invalid block_align: {block_align!r} (expected left/right/center/auto)")


def _block_pad_top(height: int, actual: int, block_valign: Optional[str]) -> int:
    if actual <= 0 or height <= actual:
        return 0
    mode = (block_valign or "bottom").strip().lower()
    if mode in ("top", "t", "none"):
        return 0
    if mode in ("center", "centre", "c"):
        return (height - actual) // 2
    if mode in ("bottom", "b", "auto"):
        return height - actual
    raise ValueError(f"Invalid block_valign: {block_valign!r} (expected top/bottom/center/auto)")


def _grid_block_padding(
    matrices: Sequence[Sequence[Any]],
    *,
    block_align: Optional[str] = None,
    block_valign: Optional[str] = None,
    index_base: int = 1,
) -> Tuple[List[int], List[int], List[int], List[int], List[List[int]], List[List[int]], List[List[int]], List[List[int]]]:
    grid: List[List[Any]] = [list(r) for r in (matrices or [])]
    if not grid:
        return ([], [], [], [], [], [], [], [])
    n_block_rows = len(grid)
    n_block_cols = max((len(r) for r in grid), default=0)
    for r in range(n_block_rows):
        if len(grid[r]) < n_block_cols:
            grid[r].extend([None] * (n_block_cols - len(grid[r])))

    block_heights = [0] * n_block_rows
    block_widths = [0] * n_block_cols
    cell_heights: List[List[int]] = [[0] * n_block_cols for _ in range(n_block_rows)]
    cell_widths: List[List[int]] = [[0] * n_block_cols for _ in range(n_block_rows)]
    for br in range(n_block_rows):
        for bc in range(n_block_cols):
            h, w = _matrix_shape(grid[br][bc])
            cell_heights[br][bc] = h
            cell_widths[br][bc] = w
            block_heights[br] = max(block_heights[br], h)
            block_widths[bc] = max(block_widths[bc], w)

    max_h = max(block_heights) if block_heights else 0
    for bc in range(n_block_cols):
        if block_widths[bc] == 0 and max_h > 0:
            block_widths[bc] = max_h

    row_starts: List[int] = []
    acc = int(index_base)
    for h in block_heights:
        row_starts.append(acc)
        acc += h
    col_starts: List[int] = []
    acc = int(index_base)
    for w in block_widths:
        col_starts.append(acc)
        acc += w

    pad_left: List[List[int]] = [[0] * n_block_cols for _ in range(n_block_rows)]
    pad_top: List[List[int]] = [[0] * n_block_cols for _ in range(n_block_rows)]
    for br in range(n_block_rows):
        for bc in range(n_block_cols):
            h = cell_heights[br][bc]
            w = cell_widths[br][bc]
            if h == 0 or w == 0:
                continue
            pad_left[br][bc] = _block_pad_left(block_widths[bc], w, block_align)
            pad_top[br][bc] = _block_pad_top(block_heights[br], h, block_valign)

    return block_heights, block_widths, row_starts, col_starts, pad_left, pad_top, cell_heights, cell_widths


def _grid_cell_coord(
    matrices: Sequence[Sequence[Any]],
    *,
    gM: int,
    gN: int,
    i: int,
    j: int,
    index_base: int = 1,
    block_align: Optional[str] = None,
    block_valign: Optional[str] = None,
) -> str:
    (
        block_heights,
        block_widths,
        row_starts,
        col_starts,
        pad_left,
        pad_top,
        cell_heights,
        cell_widths,
    ) = _grid_block_padding(
        matrices,
        block_align=block_align,
        block_valign=block_valign,
        index_base=index_base,
    )
    if gM >= len(row_starts) or gN >= len(col_starts):
        raise ValueError("grid position out of range")
    rr = row_starts[gM] + pad_top[gM][gN] + int(i)
    cc = col_starts[gN] + pad_left[gM][gN] + int(j)
    max_h = cell_heights[gM][gN] or block_heights[gM]
    max_w = cell_widths[gM][gN] or block_widths[gN]
    if max_h and int(i) >= max_h:
        rr = row_starts[gM] + pad_top[gM][gN] + max_h - 1
    if max_w and int(j) >= max_w:
        cc = col_starts[gN] + pad_left[gM][gN] + max_w - 1
    return f"({rr}-{cc})"


def _array_name_specs(
    n_rows: int,
    lhs: str,
    rhs: Sequence[str],
    *,
    start_index: Optional[int],
    array_name_indices: bool = True,
) -> List[Tuple[Tuple[int, int], str, str]]:
    names: List[List[str]] = [["", ""] for _ in range(n_rows)]
    label_start_index = start_index if array_name_indices else None

    def _pe(i: int) -> str:
        if label_start_index is None:
            return " ".join([f" {lhs}" for _ in range(i, 0, -1)])
        return " ".join([f" {lhs}_{k + label_start_index - 1}" for k in range(i, 0, -1)])

    def _pa(e_prod: str, i: int) -> str:
        rr = list(rhs)
        if i > 0 and rr and rr[-1] == "I":
            rr[-1] = ""
        return r" \mid ".join([e_prod + " " + k for k in rr])

    for i in range(n_rows):
        if label_start_index is None:
            names[i][0] = f"{lhs}"
        else:
            names[i][0] = f"{lhs}_{label_start_index + i - 1}"

        e_prod = _pe(i)
        names[i][1] = _pa(e_prod, i)

    if len(rhs) > 1:
        for i in range(n_rows):
            names[i][1] = r"\left( " + names[i][1] + r" \right)"

    for i in range(n_rows):
        for j in range(2):
            names[i][j] = r"\mathbf{ " + names[i][j] + " }"

    terms: List[Tuple[Tuple[int, int], str, str]] = [((0, 1), "ar", "$" + names[0][1] + "$")]
    for i in range(1, n_rows):
        terms.append(((i, 0), "al", "$" + names[i][0] + "$"))
        terms.append(((i, 1), "ar", "$" + names[i][1] + "$"))
    return terms


def _n_rhs_count(n_rhs: Any) -> int:
    if n_rhs is None:
        return 0
    if isinstance(n_rhs, (list, tuple)):
        return int(sum(int(x) for x in n_rhs))
    try:
        import numpy as np

        if isinstance(n_rhs, np.ndarray):
            return int(np.sum(n_rhs))
    except Exception:
        pass
    try:
        return int(n_rhs)
    except Exception:
        return 0


def _coerce_rhs_labels(rhs_list: Sequence[str], n_rhs: Any) -> List[str]:
    labels = list(rhs_list)
    count = _n_rhs_count(n_rhs)
    if count <= 0:
        return labels
    default_rhs = "b" if count == 1 else "B"
    if len(labels) <= 1:
        return [labels[0] if labels else "A", default_rhs]
    last = labels[-1]
    if count == 1 and last == "B":
        labels[-1] = "b"
    elif count > 1 and last == "b":
        labels[-1] = "B"
    return labels


def _name_specs_to_callouts(
    matrices: Sequence[Sequence[Any]],
    name_specs: Sequence[Tuple[Tuple[int, int], str, str]],
    *,
    color: str = "blue",
    legacy_submatrix_names: bool = True,
) -> List[Dict[str, Any]]:
    from matrixlayout.ge import grid_submatrix_spans

    spans = grid_submatrix_spans(matrices, legacy_submatrix_names=legacy_submatrix_names)
    name_map = {(s.block_row, s.block_col): s.name for s in spans}

    def _strip_math(s: str) -> Tuple[str, bool]:
        s = str(s).strip()
        if len(s) >= 2 and s[0] == "$" and s[-1] == "$":
            return s[1:-1].strip(), True
        return s, False

    anchor_map = {
        "a": ("auto", "north"),
        "al": ("left", "north"),
        "ar": ("right", "north"),
        "b": ("auto", "south"),
        "bl": ("left", "south"),
        "br": ("right", "south"),
    }

    out: List[Dict[str, Any]] = []
    for (gM, gN), pos, txt in name_specs:
        name = name_map.get((gM, gN))
        if not name:
            continue
        side, anchor = anchor_map.get(pos, ("auto", "north"))
        label, had_math = _strip_math(txt)
        out.append(
            {
                "name": name,
                "label": label,
                "side": side,
                "anchor": anchor,
                "angle_deg": -35.0,
                "length_mm": 6.0,
                "label_shift_y_mm": 1.0,
                "color": color,
                "math_mode": had_math,
            }
        )
    return out


def _legacy_ref_path_list_to_rowechelon_paths(
    matrices: Sequence[Sequence[Any]],
    ref_path_list: Sequence[Any],
    *,
    legacy_submatrix_names: bool = True,
) -> List[str]:
    out: List[str] = []
    from matrixlayout.ge import grid_submatrix_spans

    spans = grid_submatrix_spans(matrices, legacy_submatrix_names=legacy_submatrix_names)
    span_map = {(s.block_row, s.block_col): s for s in spans}
    for spec in ref_path_list:
        if not isinstance(spec, (list, tuple)) or len(spec) < 3:
            continue
        gM, gN = int(spec[0]), int(spec[1])
        pivots = spec[2]
        case = spec[3] if len(spec) > 3 else "hh"
        color = spec[4] if len(spec) > 4 else "blue,line width=0.4mm"
        adj = spec[5] if len(spec) > 5 else 0.1
        left_pad = spec[6] if len(spec) > 6 else 0.0
        span = span_map.get((gM, gN))
        if span is None:
            continue
        shape = (span.row_end - span.row_start + 1, span.col_end - span.col_start + 1)
        if not pivots:
            continue

        tlr = span.row_start - 1
        tlc = span.col_start - 1
        name = span.name

        def coords(
            i: int,
            j: int,
            *,
            shape: Tuple[int, int] = shape,
            gN: int = gN,
            tlr: int = tlr,
            tlc: int = tlc,
            left_pad: float = left_pad,
            adj: float = adj,
        ) -> str:
            if i >= shape[0]:
                if gN == 0 and j == 0:
                    x = r"\x1"
                else:
                    x = r"\x2" if j >= shape[1] else r"\x4"
                y = r"\y2"
                p = f"({x},{y})"
            elif j >= shape[1]:
                x = r"\x2"
                y = r"\y4"
                p = f"({x},{y})"
            elif j == 0:
                x = r"\x1"
                y = r"\y1" if i == 0 else r"\y3"
                p = f"({x},{y})"
            else:
                x = f"{i + 1 + tlr}"
                y = f"{j + 1 + tlc}"
                p = f"({x}-|{y})"

            if j == 0 and left_pad:
                p = f"($ {p} + (-{left_pad:2},0) $)"
            elif j != 0 and j < shape[1] and adj != 0:
                p = f"($ {p} + ({adj:2},0) $)"
            return p

        cur = pivots[0]
        ll = [cur] if (case == "vv") or (case == "vh") else []
        for nxt in pivots[1:]:
            if cur[0] != nxt[0]:
                cur = (cur[0] + 1, cur[1])
                ll.append(cur)
            if nxt[1] != cur[1]:
                cur = (cur[0], nxt[1])
                ll.append(cur)
            if cur != nxt:
                ll.append(nxt)
            cur = nxt

        if len(ll) == 0 and case == "hv":
            ll = [(pivots[0][0] + 1, pivots[0][0]), (shape[0], pivots[0][1])]

        if (case == "hh") or (case == "vh"):
            if cur[0] != shape[0]:
                cur = (cur[0] + 1, cur[1])
                ll.append(cur)
            ll.append((cur[0], shape[1]))
        else:
            ll.append((shape[0], cur[1]))

        corners = (
            f"let \\p1 = ({name}.north west), "
            f"\\p2 = ({name}.south east), "
        )

        if (case == "vv") or (case == "vh"):
            p3 = f"\\p3 = ({ll[1][0] + tlr + 1}-|{ll[1][1] + tlc + 1}), "
        else:
            p3 = f"\\p3 = ({ll[0][0] + tlr + 1}-|{ll[0][1] + tlc + 1}), "

        if (case == "vh") or (case == "hh"):
            i, j = ll[-2]
            p4 = f"\\p4 = ({i + tlr + 1}-|{j + tlc + 1}) in "
        else:
            i, j = ll[-1]
            p4 = f"\\p4 = ({i + tlr + 1}-|{j + tlc + 1}) in "

        cmd = "\\draw[" + color + "] " + corners + p3 + p4 + " -- ".join(
            [coords(*p) for p in ll]
        ) + ";"
        out.append(cmd)
    return out


def _legacy_pivot_list_to_pivot_locs(
    matrices: Sequence[Sequence[Any]],
    pivot_list: Sequence[Any],
    *,
    index_base: int = 1,
    pivot_style: str = "",
    block_align: Optional[str] = None,
    block_valign: Optional[str] = None,
) -> List[Tuple[str, str]]:
    _, _, row_starts, col_starts = _grid_offsets(matrices, index_base=index_base)

    out: List[Tuple[str, str]] = []
    for spec in pivot_list:
        if not spec or len(spec) < 2:
            continue
        grid, pivots = spec[0], spec[1]
        if not isinstance(grid, (list, tuple)) or len(grid) != 2:
            continue
        gM, gN = int(grid[0]), int(grid[1])
        if gM < 0 or gN < 0:
            continue
        if gM >= len(row_starts) or gN >= len(col_starts):
            continue
        for (i, j) in pivots:
            coord = _grid_cell_coord(
                matrices,
                gM=gM,
                gN=gN,
                i=int(i),
                j=int(j),
                index_base=index_base,
                block_align=block_align,
                block_valign=block_valign,
            )
            out.append((f"{coord}{coord}", pivot_style))
    return out


def _pivot_list_to_decorators(
    pivot_list: Sequence[Any],
    *,
    pivot_text_color: str = "red",
) -> List[Dict[str, Any]]:
    decorators: List[Dict[str, Any]] = []
    dec = make_decorator(boxed=True, bf=True, text_color=pivot_text_color)
    for spec in pivot_list:
        if not spec or len(spec) < 2:
            continue
        grid, pivots = spec[0], spec[1]
        if not isinstance(grid, (list, tuple)) or len(grid) != 2:
            continue
        gM, gN = int(grid[0]), int(grid[1])
        if not isinstance(pivots, (list, tuple)):
            continue
        decorators.append({"grid": (gM, gN), "entries": list(pivots), "decorator": dec})
    return decorators


def _legacy_bg_list_to_codebefore(
    matrices: Sequence[Sequence[Any]],
    bg_list: Sequence[Any],
    *,
    block_align: Optional[str] = None,
    block_valign: Optional[str] = None,
) -> List[str]:
    codebefore: List[str] = []

    def _rule_coord(row: int, col: int) -> str:
        return f"({row}-|{col})"

    def _medium_coord(row: int, col: int) -> str:
        return f"({row}-{col}-medium)"

    def _emit_spec(spec: Sequence[Any]) -> None:
        if not spec or len(spec) < 4:
            return
        gM, gN = int(spec[0]), int(spec[1])
        entries = spec[2]
        color = spec[3]
        pt = spec[4] if len(spec) > 4 else 0
        if not isinstance(entries, (list, tuple)):
            entries = [entries]
        for entry in entries:
            cmd_1 = rf"\tikz \node [fill={color}, inner sep = {pt}pt, fit = "
            if isinstance(entry, (list, tuple)) and len(entry) == 2 and all(isinstance(x, (list, tuple)) for x in entry):
                (i0, j0), (i1, j1) = entry
                c0 = _grid_cell_coord(
                    matrices,
                    gM=gM,
                    gN=gN,
                    i=int(i0),
                    j=int(j0),
                    index_base=1,
                    block_align=block_align,
                    block_valign=block_valign,
                )
                c1 = _grid_cell_coord(
                    matrices,
                    gM=gM,
                    gN=gN,
                    i=int(i1),
                    j=int(j1),
                    index_base=1,
                    block_align=block_align,
                    block_valign=block_valign,
                )
                r0, c0_idx = (int(part) for part in c0.strip("()").split("-"))
                r1, c1_idx = (int(part) for part in c1.strip("()").split("-"))
                if r0 == r1 and c0_idx == c1_idx:
                    cmd_2 = _medium_coord(r0, c0_idx)
                elif c0_idx == c1_idx:
                    cmd_2 = f"{_medium_coord(r0, c0_idx)} {_medium_coord(r1, c1_idx)}"
                else:
                    cmd_2 = f"{_rule_coord(r0, c0_idx)} {_rule_coord(r1 + 1, c1_idx + 1)}"
            else:
                i0, j0 = entry
                c0 = _grid_cell_coord(
                    matrices,
                    gM=gM,
                    gN=gN,
                    i=int(i0),
                    j=int(j0),
                    index_base=1,
                    block_align=block_align,
                    block_valign=block_valign,
                )
                r0, c0_idx = (int(part) for part in c0.strip("()").split("-"))
                cmd_2 = _medium_coord(r0, c0_idx)
            codebefore.append(cmd_1 + cmd_2 + " ] {} ;")

    for spec in bg_list:
        if isinstance(spec, list) and spec and all(isinstance(elem, list) for elem in spec):
            for s in spec:
                _emit_spec(s)
        else:
            _emit_spec(spec)
    return codebefore



def _resolve_output_targets(
    *,
    keep_file: Optional[str],
    output_dir: Optional[Any],
    output_stem: Optional[str],
) -> Tuple[Optional[Any], Optional[Any], Optional[str]]:
    from pathlib import Path

    resolved_output_stem: Optional[str] = output_stem
    if keep_file and resolved_output_stem is None:
        p = Path(str(keep_file))
        suffix = p.suffix.lower()
        resolved_output_stem = p.stem if suffix in (".tex", ".svg", ".pdf", ".dvi", ".xdv") else p.name
    # Always render on a container-local scratch filesystem so latexmk sees
    # consistent mtimes. output_dir/keep_file are preserve targets, not the live
    # TeX workdir.
    scratch_root = Path("/tmp/la/run")
    scratch_root.mkdir(parents=True, exist_ok=True)
    render_dir = Path(tempfile.mkdtemp(prefix="matrixlayout_render_", dir=str(scratch_root)))
    return str(render_dir), output_dir, resolved_output_stem


def _legacy_find_artifact_source_base(
    output_dir: Any,
    output_stem: str,
    artifact_exts: Sequence[str],
):
    root = Path(str(output_dir))
    direct = root / output_stem
    if any(direct.with_suffix(ext).exists() for ext in artifact_exts):
        return direct

    candidates: List[Path] = []
    for ext in artifact_exts:
        candidates.extend(root.rglob(f"{output_stem}{ext}"))
    if not candidates:
        return direct

    candidates.sort(key=lambda p: (len(p.parts), str(p)))
    first = candidates[0]
    return first.with_suffix("")


def _preserve_output_artifacts(
    *,
    keep_file: Optional[str],
    render_dir: Optional[Any],
    output_dir: Optional[Any],
    output_stem: str,
) -> None:
    if render_dir is None:
        return
    from pathlib import Path

    artifact_exts = (".svg", ".tex", ".pdf", ".dvi", ".xdv", ".log", ".aux", ".fls", ".fdb_latexmk", ".stdout.txt", ".stderr.txt")
    source_base = _legacy_find_artifact_source_base(render_dir, output_stem, artifact_exts)

    if output_dir:
        output_target_dir = Path(str(output_dir))
        output_target_dir.mkdir(parents=True, exist_ok=True)
        for ext in artifact_exts:
            src = source_base.with_suffix(ext)
            if src.exists():
                shutil.copy2(src, output_target_dir / src.name)

    if not keep_file:
        return

    target = Path(str(keep_file))
    suffix = target.suffix.lower()
    if suffix in artifact_exts:
        target_base = target.with_suffix("")
    else:
        target_base = target

    target_base.parent.mkdir(parents=True, exist_ok=True)
    for ext in artifact_exts:
        src = source_base.with_suffix(ext)
        if src.exists():
            shutil.copy2(src, target_base.with_suffix(ext))


def _normalize_legacy_bg_specs(bg_for_entries: Any) -> List[Any]:
    if bg_for_entries is None:
        return []
    specs = bg_for_entries
    if isinstance(specs, list) and specs and all(isinstance(elem, list) for elem in specs):
        if len(specs) == 5 and not any(isinstance(e, list) for e in specs[0:2]):
            return [specs]
        return specs
    if isinstance(specs, list):
        return specs
    return [specs]


def _legacy_bg_for_entries_to_codebefore(
    matrices: Sequence[Sequence[Any]],
    bg_for_entries: Any,
    *,
    block_align: Optional[str] = None,
    block_valign: Optional[str] = None,
) -> List[str]:
    specs = _normalize_legacy_bg_specs(bg_for_entries)
    if not specs:
        return []
    return _legacy_bg_list_to_codebefore(
        matrices,
        specs,
        block_align=block_align,
        block_valign=block_valign,
    )


def _legacy_comment_list_to_text_annotations(
    matrices: Sequence[Sequence[Any]],
    comment_list: Optional[Any],
    *,
    comment_shift_x_mm: float,
    comment_shift_y_mm: float,
    color: str,
) -> List[Tuple[str, str, str]]:
    if not comment_list:
        return []
    _, block_widths, row_starts, col_starts = _grid_offsets(matrices, index_base=1)
    if not (block_widths and col_starts):
        return []
    last_col_start = col_starts[-1]
    last_col_width = block_widths[-1]
    comment_col = last_col_start + max(last_col_width - 1, 0)
    out: List[Tuple[str, str, str]] = []
    for g, txt in enumerate(comment_list):
        if g >= len(row_starts):
            break
        row = row_starts[g]
        coord = f"({row}-{comment_col}.east)"
        style = f"right,align=left,text={color}, xshift={comment_shift_x_mm}mm"
        if comment_shift_y_mm:
            style += f", yshift={comment_shift_y_mm}mm"
        out.append((coord, r"\qquad " + str(txt), style))
    return out


def _legacy_ref_paths_to_rowechelon_paths(
    matrices: Sequence[Sequence[Any]],
    ref_path_list: Optional[Any],
) -> List[str]:
    if not ref_path_list:
        return []
    specs = ref_path_list if isinstance(ref_path_list, list) else [ref_path_list]
    return _legacy_ref_path_list_to_rowechelon_paths(matrices, specs, legacy_submatrix_names=True)


def _array_name_callouts(
    matrices: Sequence[Sequence[Any]],
    *,
    array_names: Optional[Any],
    n_rhs: Any,
    start_index: Optional[int],
    array_name_indices: bool = True,
) -> List[Dict[str, Any]]:
    if array_names is None:
        return []
    if isinstance(array_names, dict) and "name_specs" in array_names:
        name_specs = array_names.get("name_specs") or []
        return _name_specs_to_callouts(matrices, name_specs, color="blue")
    explicit_names = array_names is not True
    try:
        lhs, rhs = array_names
        rhs_list = list(rhs)
    except Exception:
        lhs, rhs_list = "E", ["A"]
    rhs_list = [str(x) for x in rhs_list]
    if not explicit_names:
        rhs_list = _coerce_rhs_labels(rhs_list, n_rhs)
    n_rows = len(matrices or [])
    name_specs = _array_name_specs(
        n_rows,
        str(lhs),
        rhs_list,
        start_index=start_index,
        array_name_indices=array_name_indices,
    )
    return _name_specs_to_callouts(matrices, name_specs, color="blue")


class _LegacyFuncAdapter:
    """Adapter exposing legacy mutator methods expected by old ``func=`` hooks."""

    def __init__(
        self,
        *,
        matrices: Sequence[Sequence[Any]],
        codebefore: List[str],
        text_annotations: List[Tuple[str, str, str]],
        rowechelon_paths: List[str],
        comment_shift_x_mm: float,
        comment_shift_y_mm: float,
        mark_medium_nodes: Any,
    ) -> None:
        self._matrices = matrices
        self.codebefore = codebefore
        self.text_annotations = text_annotations
        self.rowechelon_paths = rowechelon_paths
        self._comment_shift_x_mm = comment_shift_x_mm
        self._comment_shift_y_mm = comment_shift_y_mm
        self._mark_medium_nodes = mark_medium_nodes

    def nm_background(self, gM: int, gN: int, loc_list: Any, color: str = "red!15", pt: int = 0) -> None:
        self._mark_medium_nodes()
        self.codebefore.extend(
            _legacy_bg_for_entries_to_codebefore(self._matrices, [(gM, gN, loc_list, color, pt)])
        )

    def nm_add_rowechelon_path(
        self,
        gM: int,
        gN: int,
        pivots: Any,
        case: str = "hh",
        color: str = "blue,line width=0.4mm",
        adj: float = 0.1,
    ) -> None:
        specs = [(gM, gN, pivots, case, color, adj)]
        self.rowechelon_paths.extend(
            _legacy_ref_path_list_to_rowechelon_paths(self._matrices, specs, legacy_submatrix_names=True)
        )

    def nm_text(self, txt_list: Any, color: str = "violet") -> None:
        self.text_annotations.extend(
            _legacy_comment_list_to_text_annotations(
                self._matrices,
                txt_list,
                comment_shift_x_mm=self._comment_shift_x_mm,
                comment_shift_y_mm=self._comment_shift_y_mm,
                color=str(color),
            )
        )
