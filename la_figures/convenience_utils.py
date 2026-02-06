"""Shared normalization helpers for convenience wrappers."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional


def norm_str(x: Any) -> Any:
    """Normalize Julia/PythonCall/PyCall string-like values."""
    if x is None:
        return None
    s = x if isinstance(x, str) else str(x)
    s = s.strip()
    if s.startswith(":"):
        return s[1:]
    if "Symbol(" in s:
        match = re.search(r"Symbol\((.*)\)", s)
        if match:
            inner = match.group(1).strip()
            if inner.startswith(":"):
                inner = inner[1:]
            if len(inner) >= 2 and inner[0] == inner[-1] and inner[0] in ("'", '"'):
                inner = inner[1:-1]
            return inner
    return s


def norm_padding(padding: Any) -> Any:
    """Normalize padding inputs into a 4-tuple when possible."""
    if padding is None:
        return None
    if isinstance(padding, tuple) and len(padding) == 4:
        return padding
    try:
        seq = list(padding)
    except Exception:
        return padding
    return tuple(seq)


def resolve_output_dir(*, output_dir: Any = None, tmp_dir: Any = None) -> Any:
    """Resolve output directory aliases.

    ``output_dir`` is canonical. When omitted, ``tmp_dir`` is treated as a
    synonym for backward compatibility.
    """
    if output_dir is not None:
        return output_dir
    if tmp_dir is not None:
        return tmp_dir
    return "/tmp/la/run"


def merge_render_opts(
    *,
    toolchain_name: Any = None,
    crop: Any = None,
    padding: Any = None,
    frame: Any = None,
    exact_bbox: Any = None,
    output_dir: Any = None,
    render_opts: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Merge render options with explicit keyword overrides."""
    opts: Dict[str, Any] = dict(render_opts or {})
    if toolchain_name is not None:
        opts["toolchain_name"] = norm_str(toolchain_name)
    if crop is not None:
        opts["crop"] = norm_str(crop)
    if padding is not None:
        opts["padding"] = norm_padding(padding)
    if frame is not None:
        opts["frame"] = frame
    if exact_bbox is not None:
        opts["exact_bbox"] = exact_bbox
    if output_dir is not None:
        opts["output_dir"] = output_dir
    return opts


def make_bundle(
    *,
    spec: Dict[str, Any],
    tex: str,
    svg: Optional[str],
    data: Optional[Dict[str, Any]] = None,
    render_error: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized convenience bundle contract.

    Canonical keys:
    - ``spec``: render spec dict
    - ``tex``: rendered TeX source
    - ``svg``: rendered SVG string or ``None`` if unavailable
    - ``data``: optional compute-time metadata/results
    - ``render_error``: optional SVG-render error text
    """
    return {
        "spec": spec,
        "tex": tex,
        "svg": svg,
        "data": data or {},
        "render_error": render_error,
    }


def bundle_summary(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize a bundle without dumping full SVG/TeX payloads."""
    return {
        "has_svg": bundle.get("svg") is not None,
        "has_error": bundle.get("render_error") is not None,
        "spec_keys": sorted((bundle.get("spec") or {}).keys()),
        "data_keys": sorted((bundle.get("data") or {}).keys()),
    }


__all__ = [
    "norm_str",
    "norm_padding",
    "resolve_output_dir",
    "merge_render_opts",
    "make_bundle",
    "bundle_summary",
]
