"""Convenience GE wrappers producing TeX/SVG.

This module is intentionally thin: it ties together

- :func:`LAFigureSpecs.ge.ge_trace` (algorithmic trace)
- :func:`LAFigureSpecs.ge.decorate_ge` (data-only decorations)
- :func:`LAFigureSpecs.ge.trace_to_layer_matrices` (matrix stack)
- :func:`matrixlayout.ge.render_ge_tex` / :func:`matrixlayout.ge.render_ge_svg` (layout/render)

The TeX helpers do **not** call any toolchains.
SVG helpers call the strict rendering boundary in :mod:`matrixlayout`.

All outputs are designed to remain Julia-friendly (primitives + nested lists/tuples)
so Julia can later compute traces/decorations and call the same renderer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Sequence, Tuple, cast

from .ge import GETrace, decorate_ge, ge_trace, trace_to_layer_matrices
from .formatting import latexify
from .convenience_utils import make_bundle, resolve_crop_padding, resolve_render_svg_opts
from . import _ge_legacy_compat as _ge_compat


if TYPE_CHECKING:
    from matrixlayout.specs import GELayoutSpec

_UNSET = object()


def _resolve_n_rhs(*, n_rhs: Any = _UNSET) -> Any:
    """Resolve the canonical ``n_rhs`` keyword default."""

    if n_rhs is not _UNSET:
        return n_rhs
    return 0


def _variable_summary_label_rows(
    matrices: Sequence[Sequence[Any]],
    variable_summary: Sequence[Any],
    variable_colors: Sequence[str],
    rhs_status: Optional[Sequence[Any]] = None,
) -> List[Dict[str, Any]]:
    _, block_widths, row_starts, _ = _ge_compat._grid_offsets(matrices, index_base=1)
    if not (block_widths and row_starts):
        return []
    n_block_rows = len(matrices or [])
    n_block_cols = max((len(r) for r in (matrices or [])), default=0)
    if n_block_rows == 0 or n_block_cols == 0:
        return []
    last_col_width = block_widths[-1]
    arrows: List[str] = []
    labels: List[str] = []
    for j, basic in enumerate(variable_summary):
        if j >= last_col_width:
            break
        arrow = r"\Uparrow" if basic is True else r"\uparrow"
        color = variable_colors[0] if basic is True else variable_colors[1]
        arrows.append(rf"\textcolor{{{color}}}{{\ensuremath{{{arrow}}}}}")
        labels.append(rf"\textcolor{{{color}}}{{\ensuremath{{x_{{{j+1}}}}}}}")
    rhs_count = max(0, last_col_width - len(arrows))
    if rhs_count > 0:
        rhs_marks: List[str] = []
        rhs_labels: List[str] = []
        for idx in range(rhs_count):
            status = None
            if rhs_status is not None and idx < len(rhs_status):
                status = rhs_status[idx]
            if status == "inconsistent" or status is True:
                rhs_marks.append(r"\textcolor{red}{\ensuremath{\times}}")
            else:
                rhs_marks.append("")
            rhs_labels.append("")
        arrows.extend(rhs_marks)
        labels.extend(rhs_labels)
    if not arrows:
        return []
    return [
        {
            "grid": (n_block_rows - 1, n_block_cols - 1),
            "labels": [arrows, labels],
        }
    ]


def _normalize_stack_text_annotations(
    matrices: Sequence[Sequence[Any]],
    text_annotations: Optional[Sequence[Any]],
    *,
    comment_shift_x_mm: float,
    comment_shift_y_mm: float,
) -> List[Any]:
    """Resolve high-level GE-stack text annotations to renderer coordinates."""

    if not text_annotations:
        return []

    _, block_widths, row_starts, col_starts = _ge_compat._grid_offsets(matrices, index_base=1)
    out: List[Any] = []
    for item in text_annotations:
        if not isinstance(item, dict) or "grid_row" not in item:
            out.append(item)
            continue

        if not (block_widths and row_starts and col_starts):
            raise ValueError("grid_row text_annotations require a non-empty GE matrix stack")

        grid_row = int(item["grid_row"])
        if grid_row < 0:
            grid_row += len(row_starts)
        if grid_row < 0 or grid_row >= len(row_starts):
            raise ValueError(f"text annotation grid_row out of range: {item['grid_row']!r}")

        grid_col = int(item.get("grid_col", len(block_widths) - 1))
        if grid_col < 0:
            grid_col += len(block_widths)
        if grid_col < 0 or grid_col >= len(block_widths):
            raise ValueError(f"text annotation grid_col out of range: {item.get('grid_col')!r}")

        side = str(item.get("side", "right")).strip().lower()
        if side not in {"right", "left"}:
            raise ValueError(f"text annotation side must be 'right' or 'left', got {side!r}")

        row = row_starts[grid_row]
        if side == "right":
            col = col_starts[grid_col] + max(block_widths[grid_col] - 1, 0)
            coord = f"({row}-{col}.east)"
            anchor = "right"
            x_default = comment_shift_x_mm
        else:
            col = col_starts[grid_col]
            coord = f"({row}-{col}.west)"
            anchor = "left"
            x_default = -comment_shift_x_mm

        shift = item.get("shift_mm")
        if shift is None:
            x_shift = float(item.get("shift_x_mm", x_default))
            y_shift = float(item.get("shift_y_mm", comment_shift_y_mm))
        else:
            x_shift, y_shift = shift
            x_shift = float(x_shift)
            y_shift = float(y_shift)

        if "style" in item and item["style"] is not None:
            style = str(item["style"])
        else:
            color = str(item.get("color", "violet"))
            style = f"{anchor},align=left,text={color}, xshift={x_shift}mm"
            if y_shift:
                style += f", yshift={y_shift}mm"

        out.append((coord, str(item.get("text", "")), style))

    return out


def _build_typed_layout_spec(
    *,
    pivot_locs: Optional[Any],
    text_annotations: Optional[Any],
    rowechelon_paths: Optional[Any],
    callouts: Optional[Any],
    nice_options: str,
    body_preamble: str,
    document_preamble: str,
    fig_scale: Optional[Any],
    outer_delims: bool,
) -> "GELayoutSpec":
    from matrixlayout.specs import GELayoutSpec, PivotBox, RowEchelonPath, TextAt

    typed_pivots = [PivotBox(*item) for item in (pivot_locs or [])]
    typed_text_annotations = [TextAt(*item) for item in (text_annotations or [])]
    typed_paths = [RowEchelonPath(str(p)) for p in (rowechelon_paths or [])]

    return GELayoutSpec(
        nice_options=nice_options,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        pivot_locs=typed_pivots,
        text_annotations=typed_text_annotations,
        rowechelon_paths=typed_paths,
        callouts=callouts,
        outer_delims=outer_delims,
    )


def _merge_document_preamble(document_preamble: str, row_stretch: Optional[float]) -> str:
    if row_stretch is None:
        return document_preamble
    cmd = rf"\renewcommand{{\arraystretch}}{{{row_stretch}}}"
    ext = document_preamble or ""
    if cmd in ext:
        return ext
    if ext and not ext.endswith("\n"):
        ext += "\n"
    return ext + cmd + "\n"


def _build_ge_bundle(
    A: Any,
    rhs: Any = None,
    *,
    # Default pivoting strategy must match expected behavior:
    # no pivoting unless explicitly requested.
    pivoting: str = "none",
    gj: bool = False,
    show_pivots: Optional[bool] = True,
    index_base: int = 1,
    pivot_style: str = "",
    pivot_text_color: str = "red",
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt, left-margin=6pt, right-margin=6pt}" + "\n",
    document_preamble: str = "",
    row_stretch: Optional[float] = None,
    nice_options: str = "",
    outer_delims: bool = False,
    outer_hspace_mm: int = 6,
    cell_align: str = "r",
    callouts: Optional[Any] = None,
    array_names: Optional[Any] = None,
    array_name_indices: bool = True,
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Dict[str, Any]:
    document_preamble = _merge_document_preamble(document_preamble, row_stretch)

    tr: GETrace = ge_trace(A, rhs, pivoting=cast(Literal["none", "partial"], pivoting), gj=gj)

    # Decorations are produced in *coefficient-matrix* coordinates.
    # We rebase pivot boxes to the final (last-layer) A-block in the GE grid.
    # Pivot toggle: tests and notebooks pass show_pivots=True/False.
    # - pivot_style controls explicit TikZ pivot boxes; otherwise we use entry decorators.
    pivots_enabled = bool(show_pivots)
    eff_pivot_style = str(pivot_style or "").strip()

    decor = decorate_ge(tr, index_base=index_base, pivot_style=eff_pivot_style)
    layers = trace_to_layer_matrices(tr, augmented=True)

    # Rebase pivot locations to the last layer and to the A-block column offset.
    pivot_positions = (decor.get("pivot_positions") or []) if pivots_enabled else []
    n_layers = len(layers.get("matrices") or [])
    m = int(getattr(tr.initial, "rows", 0) or 0)
    if m <= 0:
        # Fallback: infer from the first A-block.
        try:
            A0 = layers["matrices"][0][1]
            m = int(getattr(A0, "rows", 0) or len(A0))
        except Exception:
            m = 0
    row_off = (max(n_layers - 1, 0) * m)

    # E-block width (in columns). Prefer a concrete E if present; otherwise assume square m×m.
    Ew = 0
    for row in (layers.get("matrices") or []):
        if row and len(row) >= 1 and row[0] is not None:
            Ew = int(getattr(row[0], "cols", 0) or 0)
            break
    if Ew <= 0:
        Ew = m

    def _cell_global(r: int, c: int) -> str:
        rr = int(r) + row_off + int(index_base)
        cc = int(c) + Ew + int(index_base)
        return f"({rr}-{cc})"

    pivot_locs: List[Tuple[str, str]] = []
    if pivots_enabled and str(eff_pivot_style).strip():
        pivot_locs = [
            (f"{_cell_global(r, c)}{_cell_global(r, c)}", str(eff_pivot_style).strip())
            for (r, c) in pivot_positions
        ]

    extra_callouts: List[Dict[str, Any]] = []
    if array_names is not None:
        explicit_names = array_names is not True
        try:
            lhs, rhs = array_names
            rhs_list = list(rhs)
        except Exception:
            lhs, rhs_list = "E", ["A"]
        rhs_list = [str(x) for x in rhs_list]
        if not explicit_names:
            rhs_list = _ge_compat._coerce_rhs_labels(rhs_list, tr.n_rhs)
        name_specs = _ge_compat._array_name_specs(
            len(layers["matrices"]),
            str(lhs),
            rhs_list,
            start_index=index_base,
            array_name_indices=array_name_indices,
        )
        extra_callouts = _ge_compat._name_specs_to_callouts(
            layers["matrices"],
            name_specs,
            color="blue",
            legacy_submatrix_names=False,
        )

    if callouts is None or callouts is True:
        if extra_callouts:
            for item in extra_callouts:
                if "name" not in item:
                    item.pop("grid", None)
            callouts = extra_callouts
        else:
            callouts = callouts
    elif isinstance(callouts, list) and extra_callouts:
        callouts = list(callouts) + extra_callouts

    bg_list = decor.get("bg_list") or []
    codebefore: List[str] = _ge_compat._legacy_bg_list_to_codebefore(layers["matrices"], bg_list) if bg_list else []

    ref_path_list = decor.get("ref_path_list") or []
    rowechelon_paths = (
        _ge_compat._legacy_ref_path_list_to_rowechelon_paths(
            layers["matrices"],
            ref_path_list,
            legacy_submatrix_names=False,
        )
        if ref_path_list
        else decor.get("rowechelon_paths") or []
    )

    pivot_decorators: List[Dict[str, Any]] = []
    if pivots_enabled and decor.get("pivot_list"):
        pivot_decorators = _ge_compat._pivot_list_to_decorators(
            decor.get("pivot_list") or [],
            pivot_text_color=pivot_text_color,
        )

    if pivot_decorators:
        if decorators is None:
            decorators = pivot_decorators
        else:
            decorators = list(decorators) + pivot_decorators

    text_annotations = list(decor.get("text_annotations") or [])
    label_rows: Optional[List[Dict[str, Any]]] = None
    eff_variable_summary = variable_summary
    if eff_variable_summary is None:
        eff_variable_summary = decor.get("variable_types") or decor.get("variable_summary")
    if eff_variable_summary:
        label_rows = _variable_summary_label_rows(
            layers["matrices"],
            eff_variable_summary,
            variable_colors,
            rhs_status=rhs_status,
        )

    decorations: List[Dict[str, Any]] = []
    nrhs = int(tr.n_rhs or 0)
    if nrhs > 0:
        n_block_rows = len(layers["matrices"] or [])
        n_block_cols = max((len(r) for r in (layers["matrices"] or [])), default=0)
        last_col = n_block_cols - 1
        for br in range(n_block_rows):
            row = layers["matrices"][br] if br < n_block_rows else []
            mat = row[last_col] if 0 <= last_col < len(row) else None
            _, w = _ge_compat._matrix_shape(mat)
            split = w - nrhs
            if w <= 0 or split <= 0 or split >= w:
                continue
            decorations.append({"grid": (br, last_col), "vlines": split})

    spec: Dict[str, Any] = {
        "matrices": layers["matrices"],
        "n_rhs": int(tr.n_rhs or 0),
        "body_preamble": body_preamble,
        "document_preamble": document_preamble,
        "nice_options": nice_options,
        "pivot_locs": pivot_locs,
        "text_annotations": text_annotations,
        "label_rows": label_rows,
        "rowechelon_paths": rowechelon_paths,
        "callouts": callouts,
        "decorators": decorators,
        "decorations": decorations or None,
        "fig_scale": fig_scale,
        "outer_delims": bool(outer_delims),
        "outer_hspace_mm": int(outer_hspace_mm),
        "cell_align": str(cell_align),
        "format_nrhs": False if decorations else True,
        "strict": bool(strict) if strict is not None else False,
        "codebefore": codebefore,
        "create_cell_nodes": True if rowechelon_paths else None,
        "create_medium_nodes": True if codebefore else None,
        "create_extra_nodes": True if callouts else None,
    }

    typed_layout = _build_typed_layout_spec(
        pivot_locs=pivot_locs,
        text_annotations=text_annotations,
        rowechelon_paths=rowechelon_paths,
        callouts=callouts,
        nice_options=nice_options,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        fig_scale=fig_scale,
        outer_delims=bool(outer_delims),
    )

    return {
        "trace": tr,
        "decor": decor,
        "layers": layers,
        "spec": spec,
        "typed_layout": typed_layout,
    }


def ge_spec(
    A: Any,
    rhs: Any = None,
    *,
    pivoting: str = "none",
    gj: bool = False,
    show_pivots: Optional[bool] = True,
    index_base: int = 0,
    pivot_style: str = "",
    pivot_text_color: str = "red",
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt, left-margin=6pt, right-margin=6pt}" + "\n",
    document_preamble: str = "",
    row_stretch: Optional[float] = None,
    nice_options: str = "",
    outer_delims: bool = False,
    outer_hspace_mm: int = 6,
    cell_align: str = "r",
    callouts: Optional[Any] = None,
    array_names: Optional[Any] = None,
    array_name_indices: bool = True,
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Dict[str, Any]:
    """Return a layout spec for :func:`matrixlayout.ge.render_ge_tex`.

    The returned dict contains only primitives + nested lists.
    """

    return _build_ge_bundle(
        A,
        rhs,
        pivoting=pivoting,
        gj=gj,
        show_pivots=show_pivots,
        index_base=index_base,
        pivot_style=pivot_style,
        pivot_text_color=pivot_text_color,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        row_stretch=row_stretch,
        nice_options=nice_options,
        outer_delims=outer_delims,
        outer_hspace_mm=outer_hspace_mm,
        cell_align=cell_align,
        callouts=callouts,
        array_names=array_names,
        array_name_indices=array_name_indices,
        decorators=decorators,
        fig_scale=fig_scale,
        variable_summary=variable_summary,
        variable_colors=variable_colors,
        rhs_status=rhs_status,
        strict=bool(strict) if strict is not None else False,
    )["spec"]


def ge_layout_spec(
    A: Any,
    rhs: Any = None,
    *,
    pivoting: str = "none",
    gj: bool = False,
    show_pivots: Optional[bool] = True,
    index_base: int = 0,
    pivot_style: str = "",
    pivot_text_color: str = "red",
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt, left-margin=6pt, right-margin=6pt}" + "\n",
    document_preamble: str = "",
    row_stretch: Optional[float] = None,
    nice_options: str = "",
    outer_delims: bool = False,
    outer_hspace_mm: int = 6,
    cell_align: str = "r",
    callouts: Optional[Any] = None,
    array_names: Optional[Any] = None,
    array_name_indices: bool = True,
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Any:
    """Return a typed GE grid spec (``GEGridSpec``) for matrixlayout."""

    bundle = _build_ge_bundle(
        A,
        rhs,
        pivoting=pivoting,
        gj=gj,
        show_pivots=show_pivots,
        index_base=index_base,
        pivot_style=pivot_style,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        row_stretch=row_stretch,
        nice_options=nice_options,
        outer_delims=outer_delims,
        outer_hspace_mm=outer_hspace_mm,
        cell_align=cell_align,
        callouts=callouts,
        array_names=array_names,
        array_name_indices=array_name_indices,
        decorators=decorators,
        fig_scale=fig_scale,
        variable_summary=variable_summary,
        variable_colors=variable_colors,
        rhs_status=rhs_status,
        strict=bool(strict) if strict is not None else False,
    )

    spec = {
        "matrices": bundle["layers"]["matrices"],
        "n_rhs": int(bundle["trace"].n_rhs or 0),
        "layout": bundle["typed_layout"],
        "outer_hspace_mm": int(outer_hspace_mm),
        "cell_align": str(cell_align),
        "strict": bool(strict) if strict is not None else False,
        "codebefore": bundle["spec"].get("codebefore"),
        "create_cell_nodes": bundle["spec"].get("create_cell_nodes"),
        "create_medium_nodes": bundle["spec"].get("create_medium_nodes"),
        "label_rows": bundle["spec"].get("label_rows"),
        "decorators": bundle["spec"].get("decorators"),
        "decorations": bundle["spec"].get("decorations"),
        "format_nrhs": bundle["spec"].get("format_nrhs"),
    }
    from matrixlayout.specs import GEGridSpec

    return GEGridSpec.from_dict(spec, allow_extra=True)


def ge_stack_svg(
    matrices: Sequence[Sequence[Any]],
    *,
    n_rhs: Any = _UNSET,
    formatter: Any = latexify,
    pivot_list: Optional[Sequence[Any]] = None,
    bg_for_entries: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    pivot_text_color: str = "red",
    ref_path_list: Optional[Any] = None,
    comment_list: Optional[Any] = None,
    comment_shift_x_mm: float = 50.0,
    comment_shift_y_mm: float = 0.0,
    variable_summary: Optional[Any] = None,
    rhs_status: Optional[Sequence[Any]] = None,
    pivot_locs: Optional[Sequence[Any]] = None,
    codebefore: Optional[Sequence[str]] = None,
    text_annotations: Optional[Sequence[Any]] = None,
    label_rows: Optional[Sequence[Any]] = None,
    rowechelon_paths: Optional[Sequence[str]] = None,
    callouts: Optional[Any] = None,
    array_names: Optional[Any] = None,
    array_name_indices: bool = True,
    specs: Optional[Any] = None,
    start_index: Optional[int] = 1,
    func: Optional[Any] = None,
    fig_scale: Optional[Any] = None,
    outer_hspace_mm: int = 9,
    keep_file: Optional[str] = None,
    output_dir: Optional[Any] = None,
    output_stem: Optional[str] = None,
    frame: Any = None,
    decorators: Optional[Sequence[Any]] = None,
    decorations: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
    **render_opts: Any,
) -> str:
    """Render-only wrapper: render SVG from a precomputed GE matrix stack."""
    removed_tex_hooks = {"preamble", "extension"} & set(render_opts)
    if removed_tex_hooks:
        names = ", ".join(sorted(removed_tex_hooks))
        raise TypeError(
            f"Removed GE TeX hook alias(es): {names}. "
            "Use body_preamble= for document-body setup and document_preamble= for true LaTeX preamble insertion."
        )
    n_rhs = _resolve_n_rhs(n_rhs=n_rhs)
    body_preamble = render_opts.pop("body_preamble", None)
    document_preamble = render_opts.pop("document_preamble", None)

    # Allow a single matrix input by wrapping into a 1x2 grid: [None, A].
    # This preserves legacy expectations that the data matrix lives in col=1.
    if matrices is not None and not (
        isinstance(matrices, (list, tuple))
        and (not matrices or isinstance(matrices[0], (list, tuple)))
    ):
        matrices = [[None, matrices]]

    render_dir, preserve_output_dir, output_stem = _ge_compat._resolve_output_targets(
        keep_file=keep_file,
        output_dir=output_dir,
        output_stem=output_stem,
    )

    block_align = render_opts.get("block_align")
    block_valign = render_opts.get("block_valign")
    pivot_style = f"draw={pivot_text_color}, inner sep=2pt, outer sep=0pt" if pivot_text_color else ""
    pivot_locs = _normalize_stack_pivot_locs(
        matrices,
        pivot_locs,
        default_style=pivot_style,
        block_align=block_align,
        block_valign=block_valign,
    )
    rowechelon_paths = _normalize_stack_rowechelon_paths(matrices, rowechelon_paths)

    specs_callouts = _legacy_specs_to_callouts(specs)
    if specs_callouts:
        if callouts is None or callouts is False:
            callouts = specs_callouts
        elif callouts is True:
            callouts = specs_callouts
        elif isinstance(callouts, list):
            callouts = list(callouts) + specs_callouts

    render_inputs = _legacy_ge_stack_render_inputs(
        matrices,
        n_rhs=n_rhs,
        pivot_list=pivot_list,
        bg_for_entries=bg_for_entries,
        variable_colors=variable_colors,
        pivot_text_color=pivot_text_color,
        ref_path_list=ref_path_list,
        comment_list=comment_list,
        comment_shift_x_mm=comment_shift_x_mm,
        comment_shift_y_mm=comment_shift_y_mm,
        variable_summary=variable_summary,
        rhs_status=rhs_status,
        pivot_locs=pivot_locs,
        codebefore=codebefore,
        text_annotations=text_annotations,
        label_rows=label_rows,
        rowechelon_paths=rowechelon_paths,
        callouts=callouts,
        array_names=array_names,
        array_name_indices=array_name_indices,
        start_index=start_index,
        func=func,
        decorations=decorations,
        block_align=block_align,
        block_valign=block_valign,
    )

    from matrixlayout.ge import render_ge_svg

    svg = render_ge_svg(
        matrices=matrices,
        n_rhs=n_rhs,
        formatter=formatter,
        outer_hspace_mm=outer_hspace_mm,
        legacy_submatrix_names=True,
        legacy_format=True,
        fig_scale=fig_scale,
        body_preamble=body_preamble or "",
        document_preamble=document_preamble or "",
        decorators=decorators,
        strict=bool(strict) if strict is not None else False,
        output_dir=render_dir,
        output_stem=output_stem or "output",
        frame=frame,
        **render_inputs,
        **render_opts,
    )
    _ge_compat._preserve_output_artifacts(
        keep_file=keep_file,
        render_dir=render_dir,
        output_dir=preserve_output_dir,
        output_stem=output_stem or "output",
    )
    return svg


def _normalize_stack_pivot_locs(
    matrices: Sequence[Sequence[Any]],
    pivot_locs: Optional[Sequence[Any]],
    *,
    default_style: str,
    block_align: Optional[Any],
    block_valign: Optional[Any],
) -> Optional[List[Any]]:
    """Normalize grid/entry pivot selectors accepted by ``ge_stack_svg``."""

    if not pivot_locs:
        return None
    out: List[Any] = []
    for item in pivot_locs:
        if not isinstance(item, dict) or "grid" not in item or "entries" not in item:
            out.append(item)
            continue
        grid = item.get("grid")
        entries = item.get("entries") or []
        style = str(item.get("style", default_style))
        out.extend(
            _ge_compat._legacy_pivot_list_to_pivot_locs(
                matrices,
                [(grid, entries)],
                index_base=1,
                pivot_style=style,
                block_align=block_align,
                block_valign=block_valign,
            )
        )
    return out or None


def _normalize_stack_rowechelon_paths(
    matrices: Sequence[Sequence[Any]],
    rowechelon_paths: Optional[Sequence[Any]],
) -> Optional[List[Any]]:
    """Normalize structured row-echelon path selectors accepted by ``ge_stack_svg``."""

    if not rowechelon_paths:
        return None
    out: List[Any] = []
    for item in rowechelon_paths:
        if not isinstance(item, dict) or "grid" not in item:
            out.append(item)
            continue
        if "tikz" in item:
            out.append(item)
            continue
        grid = item.get("grid")
        pivots = item.get("pivots", item.get("entries", []))
        if not isinstance(grid, (list, tuple)) or len(grid) != 2:
            continue
        spec = [
            int(grid[0]),
            int(grid[1]),
            list(pivots or []),
            str(item.get("case", "hh")),
            str(item.get("color", "blue,line width=0.4mm")),
        ]
        if "adj" in item:
            spec.append(item.get("adj"))
        if "left_pad" in item:
            if "adj" not in item:
                spec.append(0.1)
            spec.append(item.get("left_pad"))
        out.extend(_ge_compat._legacy_ref_path_list_to_rowechelon_paths(matrices, [spec], legacy_submatrix_names=True))
    return out or None


def _legacy_specs_to_callouts(specs: Optional[Any]) -> List[Dict[str, Any]]:
    """Normalize old ``specs=`` matrix-label callouts for ``ge_stack_svg``."""

    if not specs:
        return []
    items = specs if isinstance(specs, (list, tuple)) else [specs]
    callouts: List[Dict[str, Any]] = []
    for item in items:
        try:
            spec = dict(item)
        except Exception:
            continue
        angle = spec.pop("angle", None)
        if angle is not None and "angle_deg" not in spec:
            spec["angle_deg"] = angle
        length = spec.pop("length", None)
        if length is not None and "length_mm" not in spec:
            spec["length_mm"] = length
        shift_x = spec.pop("label_shift_x_mm", None)
        shift_y = spec.pop("label_shift_y_mm", None)
        if (shift_x is not None or shift_y is not None) and "label_shift_mm" not in spec:
            spec["label_shift_mm"] = (0.0 if shift_x is None else shift_x, 0.0 if shift_y is None else shift_y)
        callouts.append(spec)
    return callouts


def _legacy_ge_stack_render_inputs(
    matrices: Sequence[Sequence[Any]],
    *,
    n_rhs: Any,
    pivot_list: Optional[Sequence[Any]],
    bg_for_entries: Optional[Any],
    variable_colors: Sequence[str],
    pivot_text_color: str,
    ref_path_list: Optional[Any],
    comment_list: Optional[Any],
    comment_shift_x_mm: float,
    comment_shift_y_mm: float,
    variable_summary: Optional[Any],
    rhs_status: Optional[Sequence[Any]],
    pivot_locs: Optional[Sequence[Any]],
    codebefore: Optional[Sequence[str]],
    text_annotations: Optional[Sequence[Any]],
    label_rows: Optional[Sequence[Any]],
    rowechelon_paths: Optional[Sequence[str]],
    callouts: Optional[Any],
    array_names: Optional[Any],
    array_name_indices: bool,
    start_index: Optional[int],
    func: Optional[Any],
    decorations: Optional[Sequence[Any]],
    block_align: Optional[Any],
    block_valign: Optional[Any],
) -> Dict[str, Any]:
    """Translate legacy GE wrapper inputs into canonical matrixlayout kwargs."""

    pivot_style = f"draw={pivot_text_color}, inner sep=2pt, outer sep=0pt" if pivot_text_color else ""
    legacy_pivot_locs = (
        _ge_compat._legacy_pivot_list_to_pivot_locs(
            matrices,
            pivot_list,
            index_base=1,
            pivot_style=pivot_style,
            block_align=block_align,
            block_valign=block_valign,
        )
        if pivot_list
        else None
    )
    render_pivot_locs: Optional[List[Any]] = None
    if pivot_locs or legacy_pivot_locs:
        render_pivot_locs = []
        if pivot_locs:
            render_pivot_locs.extend(list(pivot_locs))
        if legacy_pivot_locs:
            render_pivot_locs.extend(list(legacy_pivot_locs))

    legacy_codebefore = _ge_compat._legacy_bg_for_entries_to_codebefore(
        matrices,
        bg_for_entries,
        block_align=block_align,
        block_valign=block_valign,
    )
    render_codebefore: List[str] = []
    if codebefore:
        render_codebefore.extend(list(codebefore))
    render_codebefore.extend(legacy_codebefore)
    needs_medium_nodes = bool(render_codebefore)

    legacy_text_annotations = _ge_compat._legacy_comment_list_to_text_annotations(
        matrices,
        comment_list,
        comment_shift_x_mm=comment_shift_x_mm,
        comment_shift_y_mm=comment_shift_y_mm,
        color="violet",
    )
    render_text_annotations: List[Any] = []
    if text_annotations:
        render_text_annotations.extend(
            _normalize_stack_text_annotations(
                matrices,
                text_annotations,
                comment_shift_x_mm=comment_shift_x_mm,
                comment_shift_y_mm=comment_shift_y_mm,
            )
        )
    render_text_annotations.extend(legacy_text_annotations)

    render_label_rows: Optional[List[Any]] = list(label_rows) if label_rows else None
    if variable_summary:
        summary_label_rows = _variable_summary_label_rows(
            matrices,
            variable_summary,
            variable_colors,
            rhs_status=rhs_status,
        )
        if render_label_rows is None:
            render_label_rows = summary_label_rows
        else:
            render_label_rows.extend(summary_label_rows)

    generated_decorations: List[Dict[str, Any]] = []
    nrhs_total: int
    nrhs_splits: Optional[List[int]] = None
    if isinstance(n_rhs, (list, tuple)):
        try:
            nrhs_total = sum(int(x) for x in n_rhs)
        except Exception:
            nrhs_total = 0
        nrhs_splits = []
    else:
        nrhs_total = int(n_rhs or 0)
    if nrhs_total > 0:
        n_block_rows = len(matrices or [])
        n_block_cols = max((len(r) for r in (matrices or [])), default=0)
        last_col = n_block_cols - 1
        for br in range(n_block_rows):
            row = matrices[br] if br < n_block_rows else []
            mat = row[last_col] if 0 <= last_col < len(row) else None
            _, w = _ge_compat._matrix_shape(mat)
            if w <= 0:
                continue
            if nrhs_splits is not None:
                split = w - nrhs_total
                splits: List[int] = []
                if 0 < split < w:
                    splits.append(split)
                for k in n_rhs[:-1]:
                    split += int(k)
                    if 0 < split < w:
                        splits.append(split)
                if not splits:
                    continue
                generated_decorations.append({"grid": (br, last_col), "vlines": splits})
            else:
                split = w - nrhs_total
                if split <= 0 or split >= w:
                    continue
                generated_decorations.append({"grid": (br, last_col), "vlines": split})

    render_decorations: List[Any] = []
    if decorations:
        render_decorations.extend(list(decorations))
    render_decorations.extend(generated_decorations)

    legacy_rowechelon_paths: List[str] = _ge_compat._legacy_ref_paths_to_rowechelon_paths(matrices, ref_path_list)
    render_rowechelon_paths: List[str] = []
    if rowechelon_paths:
        render_rowechelon_paths.extend(list(rowechelon_paths))
    render_rowechelon_paths.extend(legacy_rowechelon_paths)

    generated_callouts = _ge_compat._array_name_callouts(
        matrices,
        array_names=array_names,
        n_rhs=n_rhs,
        start_index=start_index,
        array_name_indices=array_name_indices,
    )
    if callouts is None:
        render_callouts = generated_callouts
    elif isinstance(callouts, list) and generated_callouts:
        render_callouts = list(callouts) + generated_callouts
    else:
        render_callouts = callouts

    if func is not None:
        def _mark_medium_nodes() -> None:
            nonlocal needs_medium_nodes
            needs_medium_nodes = True

        func(
            _ge_compat._LegacyFuncAdapter(
                matrices=matrices,
                codebefore=render_codebefore,
                text_annotations=render_text_annotations,
                rowechelon_paths=render_rowechelon_paths,
                comment_shift_x_mm=comment_shift_x_mm,
                comment_shift_y_mm=comment_shift_y_mm,
                mark_medium_nodes=_mark_medium_nodes,
            )
        )

    return {
        "pivot_locs": render_pivot_locs,
        "codebefore": render_codebefore,
        "text_annotations": render_text_annotations,
        "label_rows": render_label_rows,
        "rowechelon_paths": render_rowechelon_paths,
        "callouts": render_callouts or None,
        "create_extra_nodes": True if (render_rowechelon_paths or needs_medium_nodes) else None,
        "create_medium_nodes": True if (render_rowechelon_paths or needs_medium_nodes) else None,
        "decorations": render_decorations or None,
        "format_nrhs": False if generated_decorations else True,
    }


def show_ge(*args: Any, **kwargs: Any) -> Any:
    """Render GE and return a displayable SVG object when possible."""
    svg = ge_stack_svg(*args, **kwargs)
    try:
        from IPython.display import SVG

        return SVG(svg)
    except Exception:
        return svg


def ge_bundle(
    A: Any,
    rhs: Any = None,
    *,
    pivoting: str = "none",
    gj: bool = False,
    show_pivots: Optional[bool] = True,
    index_base: int = 1,
    pivot_style: str = "",
    pivot_text_color: str = "red",
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt, left-margin=6pt, right-margin=6pt}" + "\n",
    document_preamble: str = "",
    row_stretch: Optional[float] = None,
    nice_options: str = "",
    outer_delims: bool = False,
    outer_hspace_mm: int = 6,
    cell_align: str = "r",
    callouts: Optional[Any] = None,
    array_names: Optional[Any] = None,
    array_name_indices: bool = True,
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Dict[str, Any]:
    """Bundle: compute once, then return a standardized bundle contract."""

    computed = _build_ge_bundle(
        A,
        rhs,
        pivoting=pivoting,
        gj=gj,
        show_pivots=show_pivots,
        index_base=index_base,
        pivot_style=pivot_style,
        pivot_text_color=pivot_text_color,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        row_stretch=row_stretch,
        nice_options=nice_options,
        outer_delims=outer_delims,
        outer_hspace_mm=outer_hspace_mm,
        cell_align=cell_align,
        callouts=callouts,
        array_names=array_names,
        array_name_indices=array_name_indices,
        decorators=decorators,
        fig_scale=fig_scale,
        variable_summary=variable_summary,
        variable_colors=variable_colors,
        rhs_status=rhs_status,
        strict=bool(strict) if strict is not None else False,
    )

    spec = computed["spec"]
    tex = ""
    svg = None
    render_error = None
    submatrix_spans: List[Dict[str, Any]] = []

    # Prefer the notebook-oriented bundle API when available. This avoids
    # regex-parsing generated TeX to discover \SubMatrix names.
    from dataclasses import asdict

    try:
        from matrixlayout.ge import grid_bundle

        gb = grid_bundle(**spec)
        tex = gb.tex
        submatrix_spans = [
            {
                **asdict(s),
                "left_delim_node": s.left_delim_node,
                "right_delim_node": s.right_delim_node,
                "start_token": s.start_token,
                "end_token": s.end_token,
            }
            for s in gb.submatrix_spans
        ]
    except ImportError:
        # Fall back to plain TeX generation for older matrixlayout versions.
        from matrixlayout.ge import render_ge_tex

        tex = render_ge_tex(**spec)

    try:
        from matrixlayout.ge import render_ge_svg

        svg = render_ge_svg(**spec)
    except Exception as e:
        svg = None
        render_error = str(e)

    data: Dict[str, Any] = {
        "trace": computed["trace"],
        "decor": computed["decor"],
        "layers": computed["layers"],
        "typed_layout": computed["typed_layout"],
    }
    if submatrix_spans:
        data["submatrix_spans"] = submatrix_spans

    return make_bundle(spec=spec, tex=tex, svg=svg, data=data, render_error=render_error)


def ge_tex(
    A: Any,
    rhs: Any = None,
    *,
    pivoting: str = "none",
    gj: bool = False,
    show_pivots: Optional[bool] = True,
    index_base: int = 1,
    pivot_style: str = "",
    pivot_text_color: str = "red",
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt, left-margin=6pt, right-margin=6pt}" + "\n",
    document_preamble: str = "",
    row_stretch: Optional[float] = None,
    nice_options: str = "",
    outer_delims: bool = False,
    outer_hspace_mm: int = 6,
    cell_align: str = "r",
    callouts: Optional[Any] = None,
    array_names: Optional[Any] = None,
    array_name_indices: bool = True,
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> str:
    """Compute + render: build GE data from reference inputs and return TeX."""

    return ge_bundle(
        A,
        rhs,
        pivoting=pivoting,
        gj=gj,
        show_pivots=show_pivots,
        index_base=index_base,
        pivot_style=pivot_style,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        row_stretch=row_stretch,
        nice_options=nice_options,
        outer_delims=outer_delims,
        outer_hspace_mm=outer_hspace_mm,
        cell_align=cell_align,
        callouts=callouts,
        array_names=array_names,
        array_name_indices=array_name_indices,
        decorators=decorators,
        fig_scale=fig_scale,
        variable_summary=variable_summary,
        variable_colors=variable_colors,
        rhs_status=rhs_status,
        strict=bool(strict) if strict is not None else False,
    )["tex"]


def ge_svg(
    A: Any,
    rhs: Any = None,
    *,
    pivoting: str = "none",
    gj: bool = False,
    show_pivots: Optional[bool] = False,
    index_base: int = 1,
    pivot_style: str = "",
    pivot_text_color: str = "red",
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 1pt}" + "\n",
    document_preamble: str = "",
    row_stretch: Optional[float] = None,
    nice_options: str = "",
    outer_delims: bool = False,
    outer_hspace_mm: int = 6,
    cell_align: str = "r",
    toolchain_name: Optional[str] = None,
    crop: Any = _UNSET,
    padding: Any = _UNSET,
    frame: Any = None,
    exact_bbox: Optional[bool] = None,
    output_dir: Optional[Any] = None,
    render_opts: Optional[Dict[str, Any]] = None,
    callouts: Optional[Any] = None,
    array_names: Optional[Any] = None,
    array_name_indices: bool = True,
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> str:
    """Compute + render: build GE data from reference inputs and return SVG."""

    spec = ge_spec(
        A,
        rhs,
        pivoting=pivoting,
        gj=gj,
        show_pivots=show_pivots,
        index_base=index_base,
        pivot_style=pivot_style,
        pivot_text_color=pivot_text_color,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        row_stretch=row_stretch,
        nice_options=nice_options,
        outer_delims=outer_delims,
        outer_hspace_mm=outer_hspace_mm,
        cell_align=cell_align,
        callouts=callouts,
        array_names=array_names,
        array_name_indices=array_name_indices,
        decorators=decorators,
        fig_scale=fig_scale,
        variable_summary=variable_summary,
        variable_colors=variable_colors,
        rhs_status=rhs_status,
        strict=bool(strict) if strict is not None else False,
    )
    crop, padding = resolve_crop_padding(
        crop_is_unset=crop is _UNSET,
        crop=crop,
        padding_is_unset=padding is _UNSET,
        padding=padding,
        render_opts=render_opts,
    )

    from matrixlayout.ge import render_ge_svg

    opts = resolve_render_svg_opts(
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        exact_bbox=exact_bbox,
        output_dir=output_dir,
        render_opts=render_opts,
    )
    return render_ge_svg(**spec, **opts)
