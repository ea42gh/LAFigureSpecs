from __future__ import annotations

from typing import Any, Dict

import la_figures.convenience as lf_conv
import la_figures.convenience_qr as lf_qr
import la_figures.ge_convenience as lf_ge
import matrixlayout.qr as ml_qr
import matrixlayout.ge as ml_ge


def _fake_render_ge_svg(*args, **kwargs):
    return ("<svg/>", args, kwargs)


def test_eig_tbl_svg_passes_render_opts(monkeypatch):
    recorded: Dict[str, Any] = {}

    def fake_render_eig_svg(*args, **kwargs):
        recorded.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(lf_conv, "_import_render_eig_svg", lambda: fake_render_eig_svg)

    svg = lf_conv.eig_tbl_svg(
        [[1, 0], [0, 1]],
        render_opts={"crop": "page", "padding": (1, 1, 1, 1)},
        crop="tight",
        padding=(2, 2, 2, 2),
        frame=True,
        exact_bbox=True,
        output_dir="/tmp/opts",
    )

    assert svg == "<svg/>"
    assert recorded["crop"] == "tight"
    assert recorded["padding"] == (2, 2, 2, 2)
    assert recorded["frame"] is True
    assert recorded["exact_bbox"] is True


def test_qr_tbl_svg_passes_render_opts(monkeypatch):
    recorded: Dict[str, Any] = {}

    def fake_render_qr_svg(*args, **kwargs):
        recorded.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_qr, "render_qr_svg", fake_render_qr_svg)

    svg = lf_qr.qr_tbl_svg(
        [[1, 0], [0, 1]],
        render_opts={"crop": "page", "padding": (1, 1, 1, 1)},
        crop="tight",
        padding=(2, 2, 2, 2),
        exact_bbox=True,
    )

    assert svg == "<svg/>"
    assert recorded["crop"] == "tight"
    assert recorded["padding"] == (2, 2, 2, 2)
    assert recorded["exact_bbox"] is True


def test_ge_tbl_svg_passes_render_opts(monkeypatch):
    recorded: Dict[str, Any] = {}

    def fake_render_ge_svg(*args, **kwargs):
        recorded.update(kwargs)
        return "<svg/>"

    monkeypatch.setattr(ml_ge, "render_ge_svg", fake_render_ge_svg)

    svg = lf_ge.ge_tbl_svg(
        [[1, 0], [0, 1]],
        render_opts={"crop": "page", "padding": (1, 1, 1, 1)},
        crop="tight",
        padding=(2, 2, 2, 2),
        exact_bbox=True,
    )

    assert svg == "<svg/>"
    assert recorded["crop"] == "tight"
    assert recorded["padding"] == (2, 2, 2, 2)
    assert recorded["exact_bbox"] is True
