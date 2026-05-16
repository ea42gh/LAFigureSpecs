"""Generic LaTeX fragment/document rendering helpers."""

from __future__ import annotations

from numbers import Number
from typing import Any, Dict, Mapping, Optional


DEFAULT_TEX_PACKAGES = "amsmath,amssymb,mathtools,xcolor,systeme,cascade,nicematrix"


def _is_numpy_array(value: Any) -> bool:
    try:
        import numpy as np  # type: ignore
    except Exception:
        return False
    return isinstance(value, np.ndarray)


def _is_1d_numeric_sequence(value: Any) -> bool:
    if not isinstance(value, (list, tuple)) or not value:
        return False
    return all(isinstance(item, Number) and not isinstance(item, bool) for item in value)


def _is_2d_numeric_sequence(value: Any) -> bool:
    if not isinstance(value, (list, tuple)) or not value:
        return False
    if not all(isinstance(row, (list, tuple)) for row in value):
        return False
    row_len = len(value[0])
    if row_len == 0:
        return False
    for row in value:
        if len(row) != row_len:
            return False
        if not all(isinstance(item, Number) and not isinstance(item, bool) for item in row):
            return False
    return True


def _format_julia_number(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, complex):
        real = _format_julia_number(value.real)
        imag_abs = _format_julia_number(abs(value.imag))
        sign = "+" if value.imag >= 0 else "-"
        return f"({real} {sign} {imag_abs}im)"
    if isinstance(value, float):
        return format(value, ".17g")
    return str(value)


def _list_to_julia_vector(value: list[Any], jl: Any) -> Any:
    expr = "[" + ", ".join(_format_julia_number(item) for item in value) + "]"
    return jl.seval(expr)


def _list_to_julia_matrix(value: list[list[Any]], jl: Any) -> Any:
    rows = [" ".join(_format_julia_number(item) for item in row) for row in value]
    expr = "[" + "; ".join(rows) + "]"
    return jl.seval(expr)


def _maybe_to_julia_array(value: Any, jl: Any) -> Any:
    if _is_numpy_array(value):
        value = value.tolist()
    if _is_2d_numeric_sequence(value):
        return _list_to_julia_matrix(list(value), jl)
    if _is_1d_numeric_sequence(value):
        return _list_to_julia_vector(list(value), jl)
    return value


def _convert_lshow_args(args: tuple[Any, ...], jl: Any) -> tuple[Any, ...]:
    return tuple(_maybe_to_julia_array(arg, jl) for arg in args)


def latex_svg(
    tex_body: str,
    *,
    preamble: str | None = None,
    tex_packages: str | None = DEFAULT_TEX_PACKAGES,
    tikz_libraries: str | None = None,
    pgfplots_libraries: str | None = None,
    no_tikz: bool = True,
    scale: float = 1.0,
    no_jinja: bool = True,
    toolchain_name: str | None = None,
    crop: str | None = "tight",
    padding: Any = (2, 2, 2, 2),
    frame: Any = None,
    exact_bbox: bool | None = None,
    output_dir: Any = None,
    output_stem: str = "output",
    render_opts: Optional[Mapping[str, Any]] = None,
) -> str:
    """Wrap a LaTeX fragment in a standalone document and render it to SVG."""
    from jupyter_tikz import TexFragment
    from matrixlayout.render import render_svg as _render_svg

    if preamble:
        frag = TexFragment(
            tex_body,
            preamble=preamble,
            scale=scale,
            no_jinja=no_jinja,
        )
    else:
        frag = TexFragment(
            tex_body,
            tex_packages=tex_packages,
            tikz_libraries=tikz_libraries,
            pgfplots_libraries=pgfplots_libraries,
            no_tikz=no_tikz,
            scale=scale,
            no_jinja=no_jinja,
        )

    opts: Dict[str, Any] = dict(render_opts or {})
    if toolchain_name is not None:
        opts["toolchain_name"] = toolchain_name
    if crop is not None:
        opts["crop"] = crop
    if padding is not None:
        opts["padding"] = padding
    if frame is not None:
        opts["frame"] = frame
    if output_dir is not None:
        opts["output_dir"] = output_dir
    if output_stem is not None:
        opts["output_stem"] = output_stem
    if exact_bbox is not None:
        opts["exact_bbox"] = exact_bbox
    return _render_svg(frag.full_latex, **opts)


def latex_document_svg(
    tex_document: str,
    *,
    toolchain_name: str | None = None,
    crop: str | None = "tight",
    padding: Any = (2, 2, 2, 2),
    frame: Any = None,
    exact_bbox: bool | None = None,
    output_dir: Any = None,
    output_stem: str = "output",
    render_opts: Optional[Mapping[str, Any]] = None,
) -> str:
    """Render a full LaTeX document to SVG."""
    from matrixlayout.render import render_svg as _render_svg

    opts: Dict[str, Any] = dict(render_opts or {})
    if toolchain_name is not None:
        opts["toolchain_name"] = toolchain_name
    if crop is not None:
        opts["crop"] = crop
    if padding is not None:
        opts["padding"] = padding
    if frame is not None:
        opts["frame"] = frame
    if output_dir is not None:
        opts["output_dir"] = output_dir
    if output_stem is not None:
        opts["output_stem"] = output_stem
    if exact_bbox is not None:
        opts["exact_bbox"] = exact_bbox
    return _render_svg(tex_document, **opts)


__all__ = ["latex_svg", "latex_document_svg"]


def lshow_svg(
    *args: Any,
    lshow_kwargs: Optional[Mapping[str, Any]] = None,
    preamble: str | None = None,
    tex_packages: str | None = DEFAULT_TEX_PACKAGES,
    tikz_libraries: str | None = None,
    pgfplots_libraries: str | None = None,
    no_tikz: bool = True,
    scale: float = 1.0,
    no_jinja: bool = True,
    toolchain_name: str | None = None,
    crop: str | None = "tight",
    padding: Any = (2, 2, 2, 2),
    frame: Any = None,
    exact_bbox: bool | None = None,
    output_dir: Any = None,
    output_stem: str = "output",
    render_opts: Optional[Mapping[str, Any]] = None,
) -> str:
    """Render Julia ``LAlatex.L_show(...)`` output to SVG via juliacall."""
    try:
        from juliacall import Main as jl
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "juliacall is required for lshow_svg. Install it and ensure the Julia package LAlatex is available."
        ) from e

    latex = jl.LAlatex.L_show(*_convert_lshow_args(args, jl), **dict(lshow_kwargs or {}))
    return latex_svg(
        str(latex),
        preamble=preamble,
        tex_packages=tex_packages,
        tikz_libraries=tikz_libraries,
        pgfplots_libraries=pgfplots_libraries,
        no_tikz=no_tikz,
        scale=scale,
        no_jinja=no_jinja,
        toolchain_name=toolchain_name,
        crop=crop,
        padding=padding,
        frame=frame,
        exact_bbox=exact_bbox,
        output_dir=output_dir,
        output_stem=output_stem,
        render_opts=render_opts,
    )


__all__ = [
    "latex_svg",
    "latex_document_svg",
    "lshow_svg",
]
