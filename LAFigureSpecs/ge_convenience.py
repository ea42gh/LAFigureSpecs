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
from ._ge_legacy_compat import (
    _coerce_rhs_labels,
    _grid_offsets,
    _legacy_array_name_callouts,
    _legacy_array_name_specs,
    _legacy_bg_for_entries_to_codebefore,
    _legacy_bg_list_to_codebefore,
    _legacy_comment_list_to_txt_with_locs,
    _legacy_name_specs_to_callouts,
    _legacy_pivot_list_to_pivot_locs,
    _legacy_ref_path_list_to_rowechelon_paths,
    _legacy_ref_paths_to_rowechelon_paths,
    _LegacyFuncAdapter,
    _matrix_shape,
    _pivot_list_to_decorators,
    _preserve_legacy_keep_file_artifacts,
    _resolve_legacy_output_targets,
)


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
    _, block_widths, row_starts, _ = _grid_offsets(matrices, index_base=1)
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


def _build_typed_layout_spec(
    *,
    pivot_locs: Optional[Any],
    txt_with_locs: Optional[Any],
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
    typed_txt = [TextAt(*item) for item in (txt_with_locs or [])]
    typed_paths = [RowEchelonPath(str(p)) for p in (rowechelon_paths or [])]

    return GELayoutSpec(
        nice_options=nice_options,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        pivot_locs=typed_pivots,
        txt_with_locs=typed_txt,
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
    ref_A: Any,
    ref_rhs: Any = None,
    *,
    rhs: Any = None,
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
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Dict[str, Any]:
    # Julia interop typically passes the RHS as a keyword named `rhs`.
    # Keep the internal naming (`ref_rhs`) but accept `rhs` as an alias.
    if (ref_rhs is not None) and (rhs is not None):
        raise TypeError("Provide only one of ref_rhs or rhs")
    if ref_rhs is None:
        ref_rhs = rhs

    document_preamble = _merge_document_preamble(document_preamble, row_stretch)

    tr: GETrace = ge_trace(ref_A, ref_rhs, pivoting=cast(Literal["none", "partial"], pivoting), gj=gj)

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
            rhs_list = _coerce_rhs_labels(rhs_list, tr.n_rhs)
        name_specs = _legacy_array_name_specs(len(layers["matrices"]), str(lhs), rhs_list, start_index=index_base)
        extra_callouts = _legacy_name_specs_to_callouts(
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
    codebefore: List[str] = _legacy_bg_list_to_codebefore(layers["matrices"], bg_list) if bg_list else []

    ref_path_list = decor.get("ref_path_list") or []
    rowechelon_paths = (
        _legacy_ref_path_list_to_rowechelon_paths(
            layers["matrices"],
            ref_path_list,
            legacy_submatrix_names=False,
        )
        if ref_path_list
        else decor.get("rowechelon_paths") or []
    )

    pivot_decorators: List[Dict[str, Any]] = []
    if pivots_enabled and decor.get("pivot_list"):
        pivot_decorators = _pivot_list_to_decorators(
            decor.get("pivot_list") or [],
            pivot_text_color=pivot_text_color,
        )

    if pivot_decorators:
        if decorators is None:
            decorators = pivot_decorators
        else:
            decorators = list(decorators) + pivot_decorators

    txt_with_locs = list(decor.get("txt_with_locs") or [])
    variable_labels: Optional[List[Dict[str, Any]]] = None
    eff_variable_summary = variable_summary
    if eff_variable_summary is None:
        eff_variable_summary = decor.get("variable_types") or decor.get("variable_summary")
    if eff_variable_summary:
        variable_labels = _variable_summary_label_rows(
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
            _, w = _matrix_shape(mat)
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
        "txt_with_locs": txt_with_locs,
        "variable_labels": variable_labels,
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
        txt_with_locs=txt_with_locs,
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


def ge_tbl_spec(
    ref_A: Any,
    ref_rhs: Any = None,
    *,
    rhs: Any = None,
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
        ref_A,
        ref_rhs,
        rhs=rhs,
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
        decorators=decorators,
        fig_scale=fig_scale,
        variable_summary=variable_summary,
        variable_colors=variable_colors,
        rhs_status=rhs_status,
        strict=bool(strict) if strict is not None else False,
    )["spec"]


def ge_tbl_layout_spec(
    ref_A: Any,
    ref_rhs: Any = None,
    *,
    rhs: Any = None,
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
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Any:
    """Return a typed GE grid spec (``GEGridSpec``) for matrixlayout."""

    bundle = _build_ge_bundle(
        ref_A,
        ref_rhs,
        rhs=rhs,
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
        "variable_labels": bundle["spec"].get("variable_labels"),
        "decorators": bundle["spec"].get("decorators"),
        "decorations": bundle["spec"].get("decorations"),
        "format_nrhs": bundle["spec"].get("format_nrhs"),
    }
    from matrixlayout.specs import GEGridSpec

    return GEGridSpec.from_dict(spec, allow_extra=True)


def ge(
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
    array_names: Optional[Any] = None,
    specs: Optional[Any] = None,
    start_index: Optional[int] = 1,
    func: Optional[Any] = None,
    fig_scale: Optional[Any] = None,
    outer_hspace_mm: int = 9,
    tmp_dir: Optional[str] = None,
    keep_file: Optional[str] = None,
    output_dir: Optional[Any] = None,
    output_stem: Optional[str] = None,
    frame: Any = None,
    decorators: Optional[Sequence[Any]] = None,
    decorations: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
    **render_opts: Any,
) -> str:
    """Convenience wrapper for the GE rendering surface."""
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

    preserve_dir = output_dir if output_dir is not None else tmp_dir
    output_dir, output_stem = _resolve_legacy_output_targets(
        keep_file=keep_file,
        tmp_dir=tmp_dir,
        output_dir=output_dir,
        output_stem=output_stem,
    )

    block_align = render_opts.get("block_align")
    block_valign = render_opts.get("block_valign")

    pivot_style = f"draw={pivot_text_color}, inner sep=2pt, outer sep=0pt" if pivot_text_color else ""
    pivot_locs = (
        _legacy_pivot_list_to_pivot_locs(
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

    codebefore = _legacy_bg_for_entries_to_codebefore(
        matrices,
        bg_for_entries,
        block_align=block_align,
        block_valign=block_valign,
    )
    needs_medium_nodes = bool(codebefore)

    txt_with_locs = _legacy_comment_list_to_txt_with_locs(
        matrices,
        comment_list,
        comment_shift_x_mm=comment_shift_x_mm,
        comment_shift_y_mm=comment_shift_y_mm,
        color="violet",
    )

    variable_labels: Optional[List[Dict[str, Any]]] = None
    if variable_summary:
        variable_labels = _variable_summary_label_rows(
            matrices,
            variable_summary,
            variable_colors,
            rhs_status=rhs_status,
        )

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
            _, w = _matrix_shape(mat)
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

    rowechelon_paths: List[str] = _legacy_ref_paths_to_rowechelon_paths(matrices, ref_path_list)

    callouts = _legacy_array_name_callouts(
        matrices,
        array_names=array_names,
        n_rhs=n_rhs,
        start_index=start_index,
    )

    if func is not None:
        def _mark_medium_nodes() -> None:
            nonlocal needs_medium_nodes
            needs_medium_nodes = True

        func(
            _LegacyFuncAdapter(
                matrices=matrices,
                codebefore=codebefore,
                txt_with_locs=txt_with_locs,
                rowechelon_paths=rowechelon_paths,
                comment_shift_x_mm=comment_shift_x_mm,
                comment_shift_y_mm=comment_shift_y_mm,
                mark_medium_nodes=_mark_medium_nodes,
            )
        )

    from matrixlayout.ge import render_ge_svg

    svg = render_ge_svg(
        matrices=matrices,
        n_rhs=n_rhs,
        formatter=formatter,
        outer_hspace_mm=outer_hspace_mm,
        legacy_submatrix_names=True,
        legacy_format=True,
        pivot_locs=pivot_locs,
        codebefore=codebefore,
        txt_with_locs=txt_with_locs,
        variable_labels=variable_labels,
        rowechelon_paths=rowechelon_paths,
        callouts=callouts or None,
        create_extra_nodes=True if (ref_path_list or needs_medium_nodes) else None,
        create_medium_nodes=True if (ref_path_list or needs_medium_nodes) else None,
        decorations=render_decorations or None,
        format_nrhs=False if generated_decorations else True,
        fig_scale=fig_scale,
        body_preamble=body_preamble or "",
        document_preamble=document_preamble or "",
        decorators=decorators,
        strict=bool(strict) if strict is not None else False,
        output_dir=output_dir,
        output_stem=output_stem or "output",
        frame=frame,
        **render_opts,
    )
    _preserve_legacy_keep_file_artifacts(
        keep_file=keep_file,
        tmp_dir=preserve_dir,
        output_dir=output_dir,
        output_stem=output_stem or "output",
    )
    return svg


def show_ge(*args: Any, **kwargs: Any) -> Any:
    """Render GE and return a displayable SVG object when possible."""
    svg = ge(*args, **kwargs)
    try:
        from IPython.display import SVG

        return SVG(svg)
    except Exception:
        return svg


def ge_tbl_bundle(
    ref_A: Any,
    ref_rhs: Any = None,
    *,
    rhs: Any = None,
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
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Dict[str, Any]:
    """Bundle: compute once, then return a standardized bundle contract."""

    computed = _build_ge_bundle(
        ref_A,
        ref_rhs,
        rhs=rhs,
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


def ge_tbl_tex(
    ref_A: Any,
    ref_rhs: Any = None,
    *,
    rhs: Any = None,
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
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> str:
    """Compute + render: build GE data from reference inputs and return TeX."""

    return ge_tbl_bundle(
        ref_A,
        ref_rhs,
        rhs=rhs,
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
        decorators=decorators,
        fig_scale=fig_scale,
        variable_summary=variable_summary,
        variable_colors=variable_colors,
        rhs_status=rhs_status,
        strict=bool(strict) if strict is not None else False,
    )["tex"]


def ge_tbl_svg(
    ref_A: Any,
    ref_rhs: Any = None,
    *,
    rhs: Any = None,
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
    tmp_dir: Optional[Any] = None,
    output_dir: Optional[Any] = None,
    render_opts: Optional[Dict[str, Any]] = None,
    callouts: Optional[Any] = None,
    array_names: Optional[Any] = None,
    decorators: Optional[Sequence[Any]] = None,
    fig_scale: Optional[Any] = None,
    variable_summary: Optional[Any] = None,
    variable_colors: Sequence[str] = ("red", "black"),
    rhs_status: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> str:
    """Compute + render: build GE data from reference inputs and return SVG."""

    spec = ge_tbl_spec(
        ref_A,
        ref_rhs,
        rhs=rhs,
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
        tmp_dir=tmp_dir,
        render_opts=render_opts,
    )
    return render_ge_svg(**spec, **opts)
