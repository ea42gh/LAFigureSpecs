"""Convenience wrappers that produce TeX/SVG from :mod:`LAFigureSpecs` specs.

The core LAFigureSpecs API returns *spec dictionaries* intended to be consumed by
:mod:`matrixlayout`. These wrappers exist to make interactive use (including
Julia via PyCall/PythonCall) more ergonomic by providing single-call helpers.

Design constraints:
- Keep argument types "interop friendly": strings, numbers, and nested lists / tuples.
- Normalize Julia Symbols (often stringifying as ":name") to plain strings.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Union

from .formatting import latexify
from .convenience_utils import make_bundle, norm_str, resolve_crop_padding, resolve_render_svg_opts

from .eig import eig_spec
from .svd import svd_spec

_UNSET = object()

def _julia_str(x: Any) -> Any:
    """Alias for :func:`norm_str` used by Julia interop tests."""

    return norm_str(x)


def _filter_tex_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Remove kwargs only used by SVG renderers."""

    skip = {
        "output_dir",
        "output_stem",
        "toolchain_name",
        "crop",
        "padding",
        "frame",
        "exact_bbox",
        "render_opts",
    }
    return {k: v for k, v in kwargs.items() if k not in skip}



def _render_eig_tex_from_spec(
    spec: Dict[str, Any],
    *,
    case: Any,
    formatter: Any,
    color: Any,
    mmLambda: int,
    mmSigma: Optional[int],
    mmS: int,
    mmU: Optional[int],
    mmV: Optional[int],
    mmQ: Optional[int],
    fig_scale: Optional[Union[int, float]],
    body_preamble: str,
    sz: Optional[Tuple[int, int]],
    factor_out: Optional[Any],
    decorators: Optional[Any],
    strict: Optional[bool],
) -> str:
    import matrixlayout

    return matrixlayout.render_eig_tex(
        spec,
        case=norm_str(case),
        formatter=formatter,
        color=norm_str(color),
        mmLambda=mmLambda,
        mmSigma=mmSigma,
        mmS=mmS,
        mmU=mmU,
        mmV=mmV,
        mmQ=mmQ,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        sz=sz,
        factor_out=factor_out,
        decorators=decorators,
        strict=bool(strict) if strict is not None else False,
    )


def _render_eig_svg_from_spec(
    spec: Dict[str, Any],
    *,
    case: Any,
    formatter: Any,
    color: Any,
    mmLambda: int,
    mmSigma: Optional[int],
    mmS: int,
    mmU: Optional[int],
    mmV: Optional[int],
    mmQ: Optional[int],
    fig_scale: Optional[Union[int, float]],
    body_preamble: str,
    sz: Optional[Tuple[int, int]],
    factor_out: Optional[Any],
    decorators: Optional[Any],
    strict: Optional[bool],
    toolchain_name: Optional[Any],
    crop: Any,
    padding: Any,
    frame: Any,
    exact_bbox: Optional[bool],
    output_dir: Optional[Any],
    render_opts: Optional[Dict[str, Any]],
) -> str:
    import matrixlayout

    opts = resolve_render_svg_opts(
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        exact_bbox=exact_bbox,
        output_dir=output_dir,
        render_opts=render_opts,
    )
    return matrixlayout.render_eig_svg(
        spec,
        case=norm_str(case),
        formatter=formatter,
        color=norm_str(color),
        mmLambda=mmLambda,
        mmSigma=mmSigma,
        mmS=mmS,
        mmU=mmU,
        mmV=mmV,
        mmQ=mmQ,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        sz=sz,
        factor_out=factor_out,
        decorators=decorators,
        strict=bool(strict) if strict is not None else False,
        **opts,
    )


def eig_tex(
    A: Any,
    *,
    normal: bool = False,
    Ascale: Optional[Any] = None,
    eig_digits: Optional[int] = None,
    vec_digits: Optional[int] = None,
    case: Optional[Any] = None,
    formatter: Any = latexify,
    color: Any = "blue",
    mmLambda: int = 8,
    mmSigma: Optional[int] = None,
    mmS: int = 4,
    mmU: Optional[int] = None,
    mmV: Optional[int] = None,
    mmQ: Optional[int] = None,
    fig_scale: Optional[Union[int, float]] = None,
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 1pt}" + "\n",
    factor_out: Optional[Any] = None,
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
) -> str:
    """Compute + render: build an eigen spec from ``A`` and return TeX."""

    if case is None:
        case = "Q" if normal else "S"

    spec = eig_spec(
        A,
        normal=normal,
        Ascale=Ascale,
        eig_digits=eig_digits,
        vec_digits=vec_digits,
    )

    return _render_eig_tex_from_spec(
        spec,
        case=case,
        formatter=formatter,
        color=color,
        mmLambda=mmLambda,
        mmSigma=mmSigma,
        mmS=mmS,
        mmU=mmU,
        mmV=mmV,
        mmQ=mmQ,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        sz=None,
        factor_out=factor_out,
        decorators=decorators,
        strict=strict,
    )


def eig_svg(
    A: Any,
    *,
    normal: bool = False,
    Ascale: Optional[Any] = None,
    eig_digits: Optional[int] = None,
    vec_digits: Optional[int] = None,
    case: Optional[Any] = None,
    formatter: Any = latexify,
    color: Any = "blue",
    mmLambda: int = 8,
    mmSigma: Optional[int] = None,
    mmS: int = 4,
    mmU: Optional[int] = None,
    mmV: Optional[int] = None,
    mmQ: Optional[int] = None,
    fig_scale: Optional[Union[int, float]] = None,
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 1pt}" + "\n",
    sz: Optional[Tuple[int, int]] = None,
    factor_out: Optional[Any] = None,
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
    """Compute + render: build an eigen spec from ``A`` and return SVG."""

    if case is None:
        case = "Q" if normal else "S"

    spec = eig_spec(
        A,
        normal=normal,
        Ascale=Ascale,
        eig_digits=eig_digits,
        vec_digits=vec_digits,
    )
    crop, padding = resolve_crop_padding(
        crop_is_unset=crop is _UNSET,
        crop=crop,
        padding_is_unset=padding is _UNSET,
        padding=padding,
        render_opts=render_opts,
    )

    return _render_eig_svg_from_spec(
        spec,
        case=case,
        formatter=formatter,
        color=color,
        mmLambda=mmLambda,
        mmSigma=mmSigma,
        mmS=mmS,
        mmU=mmU,
        mmV=mmV,
        mmQ=mmQ,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        sz=sz,
        factor_out=factor_out,
        decorators=decorators,
        strict=strict,
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        exact_bbox=exact_bbox,
        output_dir=output_dir,
        render_opts=render_opts,
    )


def eig_bundle(
    A: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Bundle: compute once, then return a standardized bundle contract."""

    case = kwargs.get("case")
    normal = kwargs.get("normal", False)
    if case is None:
        case = "Q" if normal else "S"

    spec = eig_spec(
        A,
        normal=normal,
        Ascale=kwargs.get("Ascale"),
        eig_digits=kwargs.get("eig_digits"),
        vec_digits=kwargs.get("vec_digits"),
    )

    tex = _render_eig_tex_from_spec(
        spec,
        case=case,
        formatter=kwargs.get("formatter", latexify),
        color=kwargs.get("color", "blue"),
        mmLambda=kwargs.get("mmLambda", 8),
        mmSigma=kwargs.get("mmSigma"),
        mmS=kwargs.get("mmS", 4),
        mmU=kwargs.get("mmU"),
        mmV=kwargs.get("mmV"),
        mmQ=kwargs.get("mmQ"),
        fig_scale=kwargs.get("fig_scale"),
        body_preamble=kwargs.get("body_preamble", r" \NiceMatrixOptions{cell-space-limits = 1pt}" + "\n"),
        sz=kwargs.get("sz"),
        factor_out=kwargs.get("factor_out"),
        decorators=kwargs.get("decorators"),
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
        svg = _render_eig_svg_from_spec(
            spec,
            case=case,
            formatter=kwargs.get("formatter", latexify),
            color=kwargs.get("color", "blue"),
            mmLambda=kwargs.get("mmLambda", 8),
            mmSigma=kwargs.get("mmSigma"),
            mmS=kwargs.get("mmS", 4),
            mmU=kwargs.get("mmU"),
            mmV=kwargs.get("mmV"),
            mmQ=kwargs.get("mmQ"),
            fig_scale=kwargs.get("fig_scale"),
            body_preamble=kwargs.get("body_preamble", r" \NiceMatrixOptions{cell-space-limits = 1pt}" + "\n"),
            sz=kwargs.get("sz"),
            factor_out=kwargs.get("factor_out"),
            decorators=kwargs.get("decorators"),
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
        # SVG rendering depends on external toolchains; keep bundle usable without them.
        svg = None
        render_error = str(e)

    return make_bundle(spec=spec, tex=tex, svg=svg, data={}, render_error=render_error)


def svd_tex(
    A: Any,
    *,
    Ascale: Optional[Any] = None,
    eig_digits: Optional[int] = None,
    sigma_digits: Optional[int] = None,
    vec_digits: Optional[int] = None,
    formatter: Any = latexify,
    color: Any = "blue",
    mmLambda: int = 8,
    mmSigma: Optional[int] = None,
    mmS: int = 4,
    mmU: Optional[int] = None,
    mmV: Optional[int] = None,
    mmQ: Optional[int] = None,
    fig_scale: Optional[Union[int, float]] = None,
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 1pt}" + "\n",
    sz: Optional[Tuple[int, int]] = None,
    factor_out: Optional[Any] = None,
    decorators: Optional[Any] = None,
    strict: Optional[bool] = None,
) -> str:
    """Compute + render: build an SVD spec from ``A`` and return TeX."""

    spec = svd_spec(
        A,
        Ascale=Ascale,
        eig_digits=eig_digits,
        sigma_digits=sigma_digits,
        vec_digits=vec_digits,
    )
    if sz is None:
        sz = spec.get("sz")

    return _render_eig_tex_from_spec(
        spec,
        case="SVD",
        formatter=formatter,
        color=color,
        mmLambda=mmLambda,
        mmSigma=mmSigma,
        mmS=mmS,
        mmU=mmU,
        mmV=mmV,
        mmQ=mmQ,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        sz=sz,
        factor_out=factor_out,
        decorators=decorators,
        strict=strict,
    )


def svd_svg(
    A: Any,
    *,
    Ascale: Optional[Any] = None,
    eig_digits: Optional[int] = None,
    sigma_digits: Optional[int] = None,
    vec_digits: Optional[int] = None,
    formatter: Any = latexify,
    color: Any = "blue",
    mmLambda: int = 8,
    mmSigma: Optional[int] = None,
    mmS: int = 4,
    mmU: Optional[int] = None,
    mmV: Optional[int] = None,
    mmQ: Optional[int] = None,
    fig_scale: Optional[Union[int, float]] = None,
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 1pt}" + "\n",
    sz: Optional[Tuple[int, int]] = None,
    factor_out: Optional[Any] = None,
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
    """Compute + render: build an SVD spec from ``A`` and return SVG."""

    spec = svd_spec(
        A,
        Ascale=Ascale,
        eig_digits=eig_digits,
        sigma_digits=sigma_digits,
        vec_digits=vec_digits,
    )
    if sz is None:
        sz = spec.get("sz")
    crop, padding = resolve_crop_padding(
        crop_is_unset=crop is _UNSET,
        crop=crop,
        padding_is_unset=padding is _UNSET,
        padding=padding,
        render_opts=render_opts,
    )
    if exact_bbox is None:
        exact_bbox = True

    return _render_eig_svg_from_spec(
        spec,
        case="SVD",
        formatter=formatter,
        color=color,
        mmLambda=mmLambda,
        mmSigma=mmSigma,
        mmS=mmS,
        mmU=mmU,
        mmV=mmV,
        mmQ=mmQ,
        fig_scale=fig_scale,
        body_preamble=body_preamble,
        sz=sz,
        factor_out=factor_out,
        decorators=decorators,
        strict=strict,
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        exact_bbox=exact_bbox,
        output_dir=output_dir,
        render_opts=render_opts,
    )


def svd_bundle(A: Any, **kwargs: Any) -> Dict[str, Any]:
    """Bundle: compute once, then return a standardized bundle contract."""

    if "sigma2_digits" in kwargs:
        raise TypeError("sigma2_digits is removed; use eig_digits instead.")

    spec = svd_spec(
        A,
        Ascale=kwargs.get("Ascale"),
        eig_digits=kwargs.get("eig_digits"),
        sigma_digits=kwargs.get("sigma_digits"),
        vec_digits=kwargs.get("vec_digits"),
    )
    sz = kwargs.get("sz", spec.get("sz"))
    tex = _render_eig_tex_from_spec(
        spec,
        case="SVD",
        formatter=kwargs.get("formatter", latexify),
        color=kwargs.get("color", "blue"),
        mmLambda=kwargs.get("mmLambda", 8),
        mmSigma=kwargs.get("mmSigma"),
        mmS=kwargs.get("mmS", 4),
        mmU=kwargs.get("mmU"),
        mmV=kwargs.get("mmV"),
        mmQ=kwargs.get("mmQ"),
        fig_scale=kwargs.get("fig_scale"),
        body_preamble=kwargs.get("body_preamble", r" \NiceMatrixOptions{cell-space-limits = 1pt}" + "\n"),
        sz=sz,
        factor_out=kwargs.get("factor_out"),
        decorators=kwargs.get("decorators"),
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
        svg = _render_eig_svg_from_spec(
            spec,
            case="SVD",
            formatter=kwargs.get("formatter", latexify),
            color=kwargs.get("color", "blue"),
            mmLambda=kwargs.get("mmLambda", 8),
            mmSigma=kwargs.get("mmSigma"),
            mmS=kwargs.get("mmS", 4),
            mmU=kwargs.get("mmU"),
            mmV=kwargs.get("mmV"),
            mmQ=kwargs.get("mmQ"),
            fig_scale=kwargs.get("fig_scale"),
            body_preamble=kwargs.get("body_preamble", r" \NiceMatrixOptions{cell-space-limits = 1pt}" + "\n"),
            sz=sz,
            factor_out=kwargs.get("factor_out"),
            decorators=kwargs.get("decorators"),
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
