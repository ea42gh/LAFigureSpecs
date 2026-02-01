"""Convenience wrappers for QR/Gram–Schmidt figures."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .formatting import latexify
from .convenience_utils import make_bundle, norm_str, norm_padding, resolve_output_dir
from .qr import gram_schmidt_qr_matrices, qr_tbl_spec, qr_tbl_spec_from_matrices


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
        array_names=spec["array_names"],
        fig_scale=spec["fig_scale"],
        preamble=spec["preamble"],
        extension=spec["extension"],
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
    output_dir: Optional[Any],
    tmp_dir: Optional[Any],
) -> str:
    from matrixlayout.qr import render_qr_svg

    resolved_output_dir = resolve_output_dir(output_dir=output_dir, tmp_dir=tmp_dir)
    return render_qr_svg(
        matrices=spec["matrices"],
        formatter=formatter,
        array_names=spec["array_names"],
        fig_scale=spec["fig_scale"],
        preamble=spec["preamble"],
        extension=spec["extension"],
        nice_options=spec["nice_options"],
        label_color=spec["label_color"],
        label_text_color=spec["label_text_color"],
        known_zero_color=spec["known_zero_color"],
        decorators=spec.get("decorators"),
        strict=spec.get("strict") if strict is None else strict,
        toolchain_name=norm_str(toolchain_name),
        crop=norm_str(crop),
        padding=norm_padding(padding),
        frame=frame,
        output_dir=resolved_output_dir,
    )


def qr_tbl_tex(
    A: Any,
    W: Any,
    *,
    array_names: Any = True,
    formatter: Any = latexify,
    fig_scale: Optional[Any] = None,
    preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    extension: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
) -> str:
    """Compute + render: build a QR spec from ``A, W`` and return TeX."""

    spec = qr_tbl_spec(
        A,
        W,
        array_names=array_names,
        fig_scale=fig_scale,
        preamble=preamble,
        extension=extension,
        nice_options=nice_options,
        label_color=label_color,
        label_text_color=label_text_color,
        known_zero_color=known_zero_color,
        decorators=decorators,
        strict=strict,
    )

    return _render_qr_tex_from_spec(spec, formatter=formatter, strict=strict)


def qr_tbl_svg(
    A: Any,
    W: Any,
    *,
    array_names: Any = True,
    formatter: Any = latexify,
    fig_scale: Optional[Any] = None,
    preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    extension: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
    toolchain_name: Optional[Any] = None,
    crop: Any = "tight",
    padding: Any = (2, 2, 2, 2),
    frame: Any = None,
    tmp_dir: Optional[Any] = None,
    output_dir: Optional[Any] = None,
) -> str:
    """Compute + render: build a QR spec from ``A, W`` and return SVG."""

    spec = qr_tbl_spec(
        A,
        W,
        array_names=array_names,
        fig_scale=fig_scale,
        preamble=preamble,
        extension=extension,
        nice_options=nice_options,
        label_color=label_color,
        label_text_color=label_text_color,
        known_zero_color=known_zero_color,
        decorators=decorators,
        strict=strict,
    )

    return _render_qr_svg_from_spec(
        spec,
        formatter=formatter,
        strict=strict,
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        output_dir=output_dir,
        tmp_dir=tmp_dir,
    )


def qr_tbl_bundle(
    A: Any,
    W: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Bundle: compute once, then return a standardized bundle contract."""

    spec = qr_tbl_spec(A, W, **kwargs)
    tex = _render_qr_tex_from_spec(
        spec,
        formatter=kwargs.get("formatter", latexify),
        strict=kwargs.get("strict"),
    )
    svg = None
    render_error = None
    try:
        svg = _render_qr_svg_from_spec(
            spec,
            formatter=kwargs.get("formatter", latexify),
            strict=kwargs.get("strict"),
            toolchain_name=kwargs.get("toolchain_name"),
            crop=kwargs.get("crop", "tight"),
            padding=kwargs.get("padding", (2, 2, 2, 2)),
            frame=kwargs.get("frame"),
            output_dir=kwargs.get("output_dir"),
            tmp_dir=kwargs.get("tmp_dir"),
        )
    except Exception as e:
        svg = None
        render_error = str(e)
    return make_bundle(spec=spec, tex=tex, svg=svg, data={}, render_error=render_error)


def qr(
    matrices: Any,
    *,
    formatter: Any = latexify,
    array_names: Any = True,
    fig_scale: Optional[Any] = None,
    preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    extension: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
    toolchain_name: Optional[Any] = None,
    crop: Any = "tight",
    padding: Any = (2, 2, 2, 2),
    frame: Any = None,
    tmp_dir: Optional[Any] = None,
    output_dir: Optional[Any] = None,
) -> str:
    """Render-only wrapper: render SVG from a precomputed QR matrix stack."""

    spec = qr_tbl_spec_from_matrices(
        matrices,
        array_names=array_names,
        fig_scale=fig_scale,
        preamble=preamble,
        extension=extension,
        nice_options=nice_options,
        label_color=label_color,
        label_text_color=label_text_color,
        known_zero_color=known_zero_color,
        decorators=decorators,
        strict=strict,
    )

    return _render_qr_svg_from_spec(
        spec,
        formatter=formatter,
        strict=strict,
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        output_dir=output_dir,
        tmp_dir=tmp_dir,
    )


def gram_schmidt_qr(
    A: Any,
    W: Any,
    *,
    formatter: Any = latexify,
    array_names: Any = True,
    allow_rank_deficient: bool = False,
    rank_deficient: Optional[str] = None,
    fig_scale: Optional[Any] = None,
    preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    extension: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
    toolchain_name: Optional[Any] = None,
    crop: Any = "tight",
    padding: Any = (2, 2, 2, 2),
    frame: Any = None,
    tmp_dir: Optional[Any] = None,
    output_dir: Optional[Any] = None,
) -> str:
    """Compute + render: build Gram–Schmidt QR matrices and return SVG."""

    matrices = gram_schmidt_qr_matrices(
        A,
        W,
        allow_rank_deficient=allow_rank_deficient,
        rank_deficient=rank_deficient,
    )
    spec = qr_tbl_spec_from_matrices(
        matrices,
        array_names=array_names,
        fig_scale=fig_scale,
        preamble=preamble,
        extension=extension,
        nice_options=nice_options,
        label_color=label_color,
        label_text_color=label_text_color,
        known_zero_color=known_zero_color,
        decorators=decorators,
        strict=strict,
    )

    return _render_qr_svg_from_spec(
        spec,
        formatter=formatter,
        strict=strict,
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        output_dir=output_dir,
        tmp_dir=tmp_dir,
    )
