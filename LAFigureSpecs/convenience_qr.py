"""Convenience wrappers for QR/Gram–Schmidt figures."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .formatting import latexify
from .convenience_utils import make_bundle, resolve_crop_padding, resolve_render_svg_opts
from .qr import gram_schmidt_qr_matrices, qr_spec, qr_spec_from_matrices

_UNSET = object()
_QR_SPEC_KEYS = {
    "callouts",
    "array_names",
    "fig_scale",
    "body_preamble",
    "document_preamble",
    "nice_options",
    "label_color",
    "label_text_color",
    "known_zero_color",
    "decorators",
    "strict",
}


def _render_qr_tex_from_spec(
    spec: Dict[str, Any],
    *,
    formatter: Any,
    strict: Optional[bool],
) -> str:
    from matrixlayout.qr import render_qr_tex

    return render_qr_tex(
        matrices=spec["matrices"],
        formatter=formatter,
        callouts=spec.get("callouts"),
        array_names=spec["array_names"],
        fig_scale=spec["fig_scale"],
        body_preamble=spec.get("body_preamble") or "",
        document_preamble=spec.get("document_preamble") or "",
        nice_options=spec["nice_options"],
        label_color=spec["label_color"],
        label_text_color=spec["label_text_color"],
        known_zero_color=spec["known_zero_color"],
        decorators=spec.get("decorators"),
        strict=spec.get("strict") if strict is None else strict,
    )


def _render_qr_svg_from_spec(
    spec: Dict[str, Any],
    *,
    formatter: Any,
    strict: Optional[bool],
    toolchain_name: Optional[Any],
    crop: Any,
    padding: Any,
    frame: Any,
    exact_bbox: Optional[bool],
    output_dir: Optional[Any],
    render_opts: Optional[Dict[str, Any]],
) -> str:
    from matrixlayout.qr import render_qr_svg

    opts = resolve_render_svg_opts(
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        exact_bbox=exact_bbox,
        output_dir=output_dir,
        render_opts=render_opts,
    )
    return render_qr_svg(
        matrices=spec["matrices"],
        formatter=formatter,
        callouts=spec.get("callouts"),
        array_names=spec["array_names"],
        fig_scale=spec["fig_scale"],
        body_preamble=spec.get("body_preamble") or "",
        document_preamble=spec.get("document_preamble") or "",
        nice_options=spec["nice_options"],
        label_color=spec["label_color"],
        label_text_color=spec["label_text_color"],
        known_zero_color=spec["known_zero_color"],
        decorators=spec.get("decorators"),
        strict=spec.get("strict") if strict is None else strict,
        **opts,
    )


def qr_tex(
    A: Any,
    *,
    callouts: Optional[Any] = None,
    array_names: Any = True,
    formatter: Any = latexify,
    fig_scale: Optional[Any] = None,
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    document_preamble: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
) -> str:
    """Compute + render: build a QR spec from ``A`` and return TeX."""

    spec = qr_spec(
        A,
        callouts=callouts,
        array_names=array_names,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        nice_options=nice_options,
        label_color=label_color,
        label_text_color=label_text_color,
        known_zero_color=known_zero_color,
        decorators=decorators,
        strict=strict,
    )

    return _render_qr_tex_from_spec(spec, formatter=formatter, strict=strict)


def qr_svg(
    A: Any,
    *,
    callouts: Optional[Any] = None,
    array_names: Any = True,
    formatter: Any = latexify,
    fig_scale: Optional[Any] = None,
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    document_preamble: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
    toolchain_name: Optional[Any] = None,
    crop: Any = _UNSET,
    padding: Any = _UNSET,
    frame: Any = None,
    exact_bbox: Optional[bool] = None,
    output_dir: Optional[Any] = None,
    render_opts: Optional[Dict[str, Any]] = None,
) -> str:
    """Compute + render: build a QR spec from ``A`` and return SVG."""

    spec = qr_spec(
        A,
        callouts=callouts,
        array_names=array_names,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        nice_options=nice_options,
        label_color=label_color,
        label_text_color=label_text_color,
        known_zero_color=known_zero_color,
        decorators=decorators,
        strict=strict,
    )
    crop, padding = resolve_crop_padding(
        crop_is_unset=crop is _UNSET,
        crop=crop,
        padding_is_unset=padding is _UNSET,
        padding=padding,
        render_opts=render_opts,
    )

    return _render_qr_svg_from_spec(
        spec,
        formatter=formatter,
        strict=strict,
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        exact_bbox=exact_bbox,
        output_dir=output_dir,
        render_opts=render_opts,
    )


def qr_bundle(
    A: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Bundle: compute once, then return a standardized bundle contract."""

    spec_kwargs = {k: kwargs[k] for k in _QR_SPEC_KEYS if k in kwargs}
    spec = qr_spec(A, **spec_kwargs)
    tex = _render_qr_tex_from_spec(
        spec,
        formatter=kwargs.get("formatter", latexify),
        strict=kwargs.get("strict"),
    )
    svg = None
    render_error = None
    try:
        render_opts = kwargs.get("render_opts")
        crop, padding = resolve_crop_padding(
            crop_is_unset="crop" not in kwargs,
            crop=kwargs.get("crop"),
            padding_is_unset="padding" not in kwargs,
            padding=kwargs.get("padding"),
            render_opts=render_opts,
        )
        svg = _render_qr_svg_from_spec(
            spec,
            formatter=kwargs.get("formatter", latexify),
            strict=kwargs.get("strict"),
            toolchain_name=kwargs.get("toolchain_name"),
            crop=crop,
            padding=padding,
            frame=kwargs.get("frame"),
            exact_bbox=kwargs.get("exact_bbox"),
            output_dir=kwargs.get("output_dir"),
            render_opts=render_opts,
        )
    except Exception as e:
        svg = None
        render_error = str(e)
    return make_bundle(spec=spec, tex=tex, svg=svg, data={}, render_error=render_error)


def qr_stack_svg(
    matrices: Any,
    *,
    formatter: Any = latexify,
    callouts: Optional[Any] = None,
    array_names: Any = True,
    fig_scale: Optional[Any] = None,
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    document_preamble: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
    toolchain_name: Optional[Any] = None,
    crop: Any = _UNSET,
    padding: Any = _UNSET,
    frame: Any = None,
    exact_bbox: Optional[bool] = None,
    output_dir: Optional[Any] = None,
    render_opts: Optional[Dict[str, Any]] = None,
) -> str:
    """Render-only wrapper: render SVG from a precomputed QR matrix stack."""

    spec = qr_spec_from_matrices(
        matrices,
        callouts=callouts,
        array_names=array_names,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        nice_options=nice_options,
        label_color=label_color,
        label_text_color=label_text_color,
        known_zero_color=known_zero_color,
        decorators=decorators,
        strict=strict,
    )
    crop, padding = resolve_crop_padding(
        crop_is_unset=crop is _UNSET,
        crop=crop,
        padding_is_unset=padding is _UNSET,
        padding=padding,
        render_opts=render_opts,
    )

    return _render_qr_svg_from_spec(
        spec,
        formatter=formatter,
        strict=strict,
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        exact_bbox=exact_bbox,
        output_dir=output_dir,
        render_opts=render_opts,
    )


def qr_figure(
    A: Any,
    *,
    formatter: Any = latexify,
    callouts: Optional[Any] = None,
    array_names: Any = True,
    allow_rank_deficient: bool = False,
    rank_deficient: Optional[str] = None,
    fig_scale: Optional[Any] = None,
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    document_preamble: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
    toolchain_name: Optional[Any] = None,
    crop: Any = _UNSET,
    padding: Any = _UNSET,
    frame: Any = None,
    exact_bbox: Optional[bool] = None,
    output_dir: Optional[Any] = None,
    render_opts: Optional[Dict[str, Any]] = None,
) -> str:
    """Compute + render: build Gram–Schmidt QR matrices and return SVG."""

    matrices = gram_schmidt_qr_matrices(
        A,
        allow_rank_deficient=allow_rank_deficient,
        rank_deficient=rank_deficient,
    )
    spec = qr_spec_from_matrices(
        matrices,
        callouts=callouts,
        array_names=array_names,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        document_preamble=document_preamble,
        nice_options=nice_options,
        label_color=label_color,
        label_text_color=label_text_color,
        known_zero_color=known_zero_color,
        decorators=decorators,
        strict=strict,
    )
    crop, padding = resolve_crop_padding(
        crop_is_unset=crop is _UNSET,
        crop=crop,
        padding_is_unset=padding is _UNSET,
        padding=padding,
        render_opts=render_opts,
    )

    return _render_qr_svg_from_spec(
        spec,
        formatter=formatter,
        strict=strict,
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        exact_bbox=exact_bbox,
        output_dir=output_dir,
        render_opts=render_opts,
    )
