from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple, cast

from .ge import Pivoting, ge_trace, trace_to_layer_matrices
from .backsub import backsubstitution_tex, linear_system_tex, standard_solution_tex
from .ge_convenience import ge_svg
from ._ge_legacy_compat import (
    _legacy_bg_for_entries_to_codebefore,
    _legacy_pivot_list_to_pivot_locs,
    _legacy_ref_paths_to_rowechelon_paths,
    _name_specs_to_callouts,
)
from ._sympy_utils import to_sympy_col, to_sympy_matrix


def _show_svg(svg: str):
    try:
        from IPython.display import SVG, display
    except Exception:
        return svg
    return display(SVG(svg))


def _format_rhs_label(labels: Sequence[str]) -> str:
    if not labels:
        return ""
    if len(labels) > 1:
        return r"\left( " + r" \mid ".join(labels) + r" \right)"
    return labels[0]


def _normal_eq_name_specs(n_rows: int, rhs_labels: Sequence[str]) -> List[Tuple[Tuple[int, int], str, str]]:
    specs: List[Tuple[Tuple[int, int], str, str]] = []
    if n_rows <= 0:
        return specs
    rhs0 = _format_rhs_label(list(rhs_labels))
    specs.append(((0, 1), "ar", f"$\\mathbf{{ {rhs0} }}$"))
    if n_rows <= 1:
        return specs
    rhs1_labels = [rf"A^T {lbl}" for lbl in rhs_labels]
    rhs1 = _format_rhs_label(rhs1_labels)
    specs.append(((1, 0), "al", r"$\mathbf{ A^T }$"))
    specs.append(((1, 1), "ar", f"$\\mathbf{{ {rhs1} }}$"))
    for i in range(2, n_rows):
        prod = " ".join([f"E_{k}" for k in range(i - 1, 0, -1)])
        rhs_i_labels = [f"{prod} {lbl}" if prod else lbl for lbl in rhs1_labels]
        rhs_i = _format_rhs_label(rhs_i_labels)
        specs.append(((i, 0), "al", f"$\\mathbf{{ E_{i - 1} }}$"))
        specs.append(((i, 1), "ar", f"$\\mathbf{{ {rhs_i} }}$"))
    return specs


def _decorated_stack_render_kwargs(
    matrices: Sequence[Sequence[Any]],
    decor: Dict[str, Any],
    *,
    show_pivots: Optional[bool],
    pivot_text_color: str,
) -> Dict[str, Any]:
    """Convert ``decorate_ge`` compatibility output to canonical stack kwargs."""

    pivot_style = f"draw={pivot_text_color}, inner sep=2pt, outer sep=0pt" if pivot_text_color else ""
    pivot_locs = None
    if show_pivots and decor.get("pivot_list"):
        pivot_locs = _legacy_pivot_list_to_pivot_locs(
            matrices,
            decor.get("pivot_list") or [],
            index_base=1,
            pivot_style=pivot_style,
        )

    bg_specs = decor.get("bg_list") or []
    codebefore = _legacy_bg_for_entries_to_codebefore(matrices, bg_specs) if bg_specs else []

    ref_paths = decor.get("ref_path_list") or decor.get("path_list") or []
    rowechelon_paths = _legacy_ref_paths_to_rowechelon_paths(matrices, ref_paths) if ref_paths else []
    rowechelon_paths.extend(list(decor.get("rowechelon_paths") or []))

    return {
        "pivot_locs": pivot_locs,
        "codebefore": codebefore,
        "rowechelon_paths": rowechelon_paths,
    }


@dataclass
class ShowGE:
    """Notebook-friendly Gaussian-elimination helper (Python analogue of Julia ShowGE)."""

    A: Any
    rhs: Any = None
    normal_eq: bool = False
    pivoting: str = "none"
    gj: bool = False
    show_pivots: Optional[bool] = True
    index_base: int = 0
    pivot_style: str = ""
    pivot_text_color: str = "red"
    body_preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt, left-margin=6pt, right-margin=6pt}" + "\n"
    document_preamble: str = ""
    row_stretch: Optional[float] = None
    nice_options: str = ""
    outer_delims: bool = False
    outer_hspace_mm: int = 6
    cell_align: str = "r"
    callouts: Optional[Any] = None
    array_names: Optional[Any] = None
    decorators: Optional[Sequence[Any]] = None
    fig_scale: Optional[Any] = None
    variable_summary: Optional[Any] = None
    variable_colors: Sequence[str] = ("red", "black")
    strict: Optional[bool] = None
    status: str = "unknown"
    rhs_status: List[str] = field(default_factory=list)
    rhs_consistent: List[bool] = field(default_factory=list)

    _trace: Any = field(default=None, init=False, repr=False)
    _layers: Any = field(default=None, init=False, repr=False)
    _solution_cache: Dict[bool, Dict[str, Any]] = field(default_factory=dict, init=False, repr=False)

    def ref(self, *, gj: Optional[bool] = None, pivoting: Optional[str] = None):
        """Compute and cache the GE trace/layers (REF or RREF)."""
        if gj is not None:
            self.gj = bool(gj)
        if pivoting is not None:
            self.pivoting = str(pivoting)
        if self.normal_eq:
            A = to_sympy_matrix(self.A)
            b = to_sympy_col(self.rhs)
            if A is None:
                raise ValueError("A must not be None")
            At = A.T
            if b is None:
                A_aug = A
                AtA_aug = At * A
                n_rhs = 0
            else:
                A_aug = A.row_join(b)
                AtA = At * A
                Atb = At * b
                AtA_aug = AtA.row_join(Atb)
                n_rhs = Atb.shape[1]
            self._trace = ge_trace(
                AtA,
                Atb if b is not None else None,
                pivoting=cast(Pivoting, self.pivoting),
                gj=self.gj,
            )
            base_layers = trace_to_layer_matrices(self._trace, augmented=True)
            mats = [[None, A_aug], [At, AtA_aug]] + list(base_layers.get("matrices") or [])[1:]
            self._layers = dict(base_layers)
            self._layers["matrices"] = mats
            self._layers["n_rhs"] = n_rhs
        else:
            self._trace = ge_trace(self.A, self.rhs, pivoting=cast(Pivoting, self.pivoting), gj=self.gj)
            self._layers = trace_to_layer_matrices(self._trace, augmented=True)
        self._update_rhs_status()
        self._solution_cache.clear()
        return self

    def show_ref(self, *, gj: Optional[bool] = None, pivoting: Optional[str] = None):
        """Alias for ref (Julia-style naming)."""
        return self.ref(gj=gj, pivoting=pivoting)

    def _get_trace(self):
        if self._trace is None:
            self.ref()
        return self._trace

    def _get_layers(self):
        if self._layers is None:
            self.ref()
        return self._layers

    def _final_ref_mats(self) -> Tuple[Any, Any]:
        layers = self._get_layers()
        mats = layers.get("matrices") or []
        if not mats:
            return self.A, self.rhs
        last = mats[-1][1]
        nrhs = int(layers.get("n_rhs") or 0)
        if nrhs <= 0:
            return last, None
        return last[:, :-nrhs], last[:, -nrhs:]

    def _update_rhs_status(self) -> None:
        ref_A, rhs = self._final_ref_mats()
        if rhs is None:
            self.status = "none"
            self.rhs_status = []
            self.rhs_consistent = []
            return
        A = to_sympy_matrix(ref_A)
        b = to_sympy_matrix(rhs)
        if A is None or b is None:
            self.status = "unknown"
            self.rhs_status = []
            self.rhs_consistent = []
            return
        if b.cols == 1:
            rhs_cols = 1
        else:
            rhs_cols = b.cols
        rhs_status: List[str] = []
        for col in range(rhs_cols):
            inconsistent = False
            for i in range(A.rows):
                row_zero = True
                for j in range(A.cols):
                    if A[i, j] != 0:
                        row_zero = False
                        break
                if row_zero and b[i, col] != 0:
                    inconsistent = True
                    break
            rhs_status.append("inconsistent" if inconsistent else "consistent")
        self.rhs_status = rhs_status
        self.rhs_consistent = [s == "consistent" for s in rhs_status]
        if all(s == "consistent" for s in rhs_status):
            self.status = "consistent"
        elif all(s == "inconsistent" for s in rhs_status):
            self.status = "inconsistent"
        else:
            self.status = "mixed"

    def trace(self) -> Any:
        """Return (and cache) the GE trace."""
        return self._get_trace()

    def matrices(self) -> List[List[Any]]:
        """Return the GE layer matrices (augmented)."""
        return list(self._get_layers().get("matrices") or [])

    def _step_matrix(self, *, step: Any = "final"):
        """Return the augmented matrix stored at ``step`` in the GE stack."""
        layers = self._get_layers()
        mats = layers.get("matrices") or []
        if not mats:
            return None
        idx = len(mats) - 1 if step in ("final", None) else int(step)
        if idx < 0 or idx >= len(mats):
            raise IndexError("step out of range for GE stack")
        return mats[idx][1]

    def lhs_matrix(self, *, step: Any = "final"):
        """Return the left-hand coefficient matrix at ``step``."""
        Ab = self._step_matrix(step=step)
        if Ab is None:
            return None
        layers = self._get_layers()
        nrhs = int(layers.get("n_rhs") or 0)
        if nrhs <= 0:
            return Ab
        return Ab[:, :-nrhs]

    def rhs_matrix(self, *, step: Any = "final"):
        """Return the RHS matrix block at ``step``."""
        Ab = self._step_matrix(step=step)
        if Ab is None:
            return None
        layers = self._get_layers()
        nrhs = int(layers.get("n_rhs") or 0)
        if nrhs <= 0:
            return None
        return Ab[:, -nrhs:]

    def rhs_column(self, b_col: int = 0, *, step: Any = "final"):
        """Return RHS column ``b_col`` from the GE stack at ``step``."""
        rhs = self.rhs_matrix(step=step)
        if rhs is None:
            return None
        return rhs[:, int(b_col)]

    def solve(self, *, gj: Optional[bool] = None) -> Dict[str, Any]:
        """Solve the system and return pivot/free/solution data."""
        if gj is not None and bool(gj) != bool(self.gj):
            self.ref(gj=gj)
        gj = self.gj
        if gj in self._solution_cache:
            return self._solution_cache[gj]

        A = to_sympy_matrix(self.A)
        b = to_sympy_col(self.rhs)
        if A is None:
            raise ValueError("A must not be None")

        if b is None:
            rref_A, pivot_cols = A.rref()
            rref_b = None
            rhs_cols = 0
        else:
            Ab = A.row_join(b)
            rref_Ab, pivot_cols_ab = Ab.rref()
            rref_A = rref_Ab[:, 0 : A.shape[1]]
            rref_b = rref_Ab[:, A.shape[1] :]
            rhs_cols = rref_b.shape[1]
            pivot_cols = [c for c in pivot_cols_ab if c < rref_A.shape[1]]

        n = rref_A.shape[1]
        free_cols = [i for i in range(n) if i not in pivot_cols]

        # Particular solution (free vars = 0).
        import sympy as sym

        particular = sym.zeros(n, max(rhs_cols, 1))
        if rref_b is not None:
            for col in range(rhs_cols):
                for i, pc in enumerate(pivot_cols):
                    t = rref_b[i, col]
                    for j in range(pc + 1, n):
                        t = t - rref_A[i, j] * particular[j, col]
                    particular[pc, col] = t

        # Homogeneous basis.
        homogeneous: List[Any] = []
        for free in free_cols:
            vec = sym.zeros(n, 1)
            vec[free, 0] = sym.Integer(1)
            for i, pc in enumerate(pivot_cols):
                t = sym.Integer(0)
                for j in range(pc + 1, n):
                    t = t - rref_A[i, j] * vec[j, 0]
                vec[pc, 0] = t
            homogeneous.append(vec)
        if not homogeneous:
            homogeneous = [sym.zeros(n, 1)]

        result = {
            "gj": gj,
            "rref_A": rref_A,
            "rref_b": rref_b,
            "pivot_cols": list(pivot_cols),
            "free_cols": list(free_cols),
            "particular": particular,
            "homogeneous": homogeneous,
            "rhs_status": list(self.rhs_status),
            "rhs_consistent": list(self.rhs_consistent),
            "status": self.status,
        }
        self._solution_cache[gj] = result
        return result

    def particular_solution(self, *, gj: Optional[bool] = None):
        """Return a particular solution (free vars = 0)."""
        return self.solve(gj=gj)["particular"]

    def homogeneous_solution(self, *, gj: Optional[bool] = None):
        """Return a list of homogeneous basis vectors."""
        return self.solve(gj=gj)["homogeneous"]

    def show_layout(self, **render_opts: Any):
        array_names = self.array_names
        if array_names is None:
            rhs = to_sympy_matrix(self.rhs)
            if rhs is None:
                array_names = ["E", "A"]
            else:
                rhs_cols = rhs.shape[1] if hasattr(rhs, "shape") else 1
                if rhs_cols == 1:
                    array_names = ["E", ["A", "b"]]
                else:
                    array_names = ["E", ["A", "B"]]
        if self.normal_eq:
            from .ge import decorate_ge
            from .ge_convenience import _ge_stack_svg

            trace = self._get_trace()
            layers = self._get_layers()
            decor = decorate_ge(trace, index_base=self.index_base)
            var_summary = self.variable_summary
            if var_summary is None:
                var_summary = decor.get("basic_var")
            elif isinstance(var_summary, bool):
                var_summary = decor.get("basic_var") if var_summary else None
            callouts = self.callouts
            if callouts is None and not isinstance(array_names, dict):
                try:
                    _, rhs = array_names
                    rhs_labels = [str(x) for x in rhs]
                except Exception:
                    rhs_labels = ["A"]
                name_specs = _normal_eq_name_specs(len(layers.get("matrices") or []), rhs_labels)
                callouts = _name_specs_to_callouts(
                    layers.get("matrices") or [],
                    name_specs,
                    color="blue",
                    legacy_submatrix_names=True,
                )
            svg = _ge_stack_svg(
                layers.get("matrices"),
                n_rhs=layers.get("n_rhs") or 0,
                **_decorated_stack_render_kwargs(
                    layers.get("matrices") or [],
                    decor,
                    show_pivots=self.show_pivots,
                    pivot_text_color=self.pivot_text_color,
                ),
                variable_summary=var_summary,
                variable_colors=self.variable_colors,
                callouts=callouts,
                array_names=array_names if callouts is None else None,
                fig_scale=self.fig_scale,
                body_preamble=self.body_preamble,
                document_preamble=self.document_preamble,
                nice_options=self.nice_options,
                outer_hspace_mm=self.outer_hspace_mm,
                cell_align=self.cell_align,
                decorators=self.decorators,
                strict=self.strict,
                **render_opts,
            )
        else:
            layers = self._get_layers()
            mats = layers.get("matrices") or []
            if len(mats) > 1:
                from .ge import decorate_ge
                from .ge_convenience import _ge_stack_svg

                trace = self._get_trace()
                decor = decorate_ge(trace, index_base=self.index_base)
                var_summary = self.variable_summary
                if var_summary is None:
                    var_summary = decor.get("basic_var")
                elif isinstance(var_summary, bool):
                    var_summary = decor.get("basic_var") if var_summary else None
                svg = _ge_stack_svg(
                    mats,
                    n_rhs=layers.get("n_rhs") or 0,
                    **_decorated_stack_render_kwargs(
                        mats,
                        decor,
                        show_pivots=self.show_pivots,
                        pivot_text_color=self.pivot_text_color,
                    ),
                    variable_summary=var_summary,
                    variable_colors=self.variable_colors,
                    callouts=self.callouts,
                    array_names=array_names,
                    fig_scale=self.fig_scale,
                    body_preamble=self.body_preamble,
                    document_preamble=self.document_preamble,
                    nice_options=self.nice_options,
                    outer_hspace_mm=self.outer_hspace_mm,
                    cell_align=self.cell_align,
                    decorators=self.decorators,
                    strict=self.strict,
                    **render_opts,
                )
            else:
                svg = ge_svg(
                    self.A,
                    self.rhs,
                    pivoting=self.pivoting,
                    gj=self.gj,
                    show_pivots=self.show_pivots,
                    index_base=self.index_base,
                    pivot_style=self.pivot_style,
                    pivot_text_color=self.pivot_text_color,
                    body_preamble=self.body_preamble,
                    document_preamble=self.document_preamble,
                    row_stretch=self.row_stretch,
                    nice_options=self.nice_options,
                    outer_delims=self.outer_delims,
                    outer_hspace_mm=self.outer_hspace_mm,
                    cell_align=self.cell_align,
                    callouts=self.callouts,
                    array_names=array_names,
                    decorators=self.decorators,
                    fig_scale=self.fig_scale,
                    variable_summary=self.variable_summary,
                    variable_colors=self.variable_colors,
                    rhs_status=self.rhs_status,
                    strict=self.strict,
                    **render_opts,
                )
        return _show_svg(svg)

    def show_system(self, *, var_name: str = "x", **render_opts: Any):
        system_txt = linear_system_tex(self.A, self.rhs, var_name=var_name)
        from matrixlayout.backsubst import backsubst_svg

        opts = dict(render_opts)
        if "show_system" not in opts:
            opts["show_system"] = True
        if "show_cascade" not in opts:
            opts["show_cascade"] = False
        if "show_solution" not in opts:
            opts["show_solution"] = False

        svg = backsubst_svg(
            system_txt=system_txt,
            **opts,
        )
        return _show_svg(svg)

    def show_backsubstitution(self, *, var_name: str = "x", param_name: str = r"\alpha", **render_opts: Any):
        ref_A, rhs = self._final_ref_mats()
        if self.rhs_status and any(s == "inconsistent" for s in self.rhs_status):
            val = None
            if rhs is not None:
                A = to_sympy_matrix(ref_A)
                b = to_sympy_matrix(rhs)
                if A is not None and b is not None:
                    for col, s in enumerate(self.rhs_status):
                        if s != "inconsistent":
                            continue
                        for i in range(A.rows):
                            row_zero = True
                            for j in range(A.cols):
                                if A[i, j] != 0:
                                    row_zero = False
                                    break
                            if row_zero and b[i, col] != 0:
                                val = b[i, col]
                                break
                        if val is not None:
                            break
            rhs_txt = str(val) if val is not None else "?"
            cascade_txt = [rf"0 = {rhs_txt}", r"\text{No Solution}"]
        else:
            cascade_txt = backsubstitution_tex(ref_A, rhs, var_name=var_name, param_name=param_name)
        from matrixlayout.backsubst import backsubst_svg

        opts = dict(render_opts)
        if "show_system" not in opts:
            opts["show_system"] = False
        if "show_cascade" not in opts:
            opts["show_cascade"] = True
        if "show_solution" not in opts:
            opts["show_solution"] = False

        svg = backsubst_svg(
            cascade_txt=cascade_txt,
            **opts,
        )
        return _show_svg(svg)

    def show_solution(
        self,
        *,
        b_col: Optional[int] = None,
        var_name: str = "x",
        param_name: str = r"\alpha",
        **render_opts: Any,
    ):
        ref_A, rhs = self._final_ref_mats()
        if rhs is None:
            raise ValueError("show_solution requires a RHS.")

        rhs_cols = int(rhs.shape[1]) if hasattr(rhs, "shape") and len(rhs.shape) > 1 else 1
        if b_col is None:
            if rhs_cols != 1:
                raise ValueError("show_solution requires b_col when the RHS has multiple columns.")
            b_col = 0
        b_col = int(b_col)
        if b_col < 0 or b_col >= rhs_cols:
            raise IndexError("b_col out of range for the RHS block.")
        if self.rhs_status and b_col < len(self.rhs_status) and self.rhs_status[b_col] == "inconsistent":
            return []

        solution_txt = standard_solution_tex(ref_A, rhs[:, b_col], var_name=var_name, param_name=param_name)
        from matrixlayout.backsubst import backsubst_svg

        opts = dict(render_opts)
        if "show_system" not in opts:
            opts["show_system"] = False
        if "show_cascade" not in opts:
            opts["show_cascade"] = False
        if "show_solution" not in opts:
            opts["show_solution"] = True

        svg = backsubst_svg(
            solution_txt=solution_txt,
            **opts,
        )
        return _show_svg(svg)


def ref(show: ShowGE, *, gj: Optional[bool] = None, pivoting: Optional[str] = None):
    """Top-level wrapper for ``ShowGE.ref(...)``."""
    return show.ref(gj=gj, pivoting=pivoting)


def show_layout(show: ShowGE, **render_opts: Any):
    """Top-level wrapper for ``ShowGE.show_layout(...)``."""
    return show.show_layout(**render_opts)


def show_system(show: ShowGE, *, var_name: str = "x", **render_opts: Any):
    """Top-level wrapper for ``ShowGE.show_system(...)``."""
    return show.show_system(var_name=var_name, **render_opts)


def show_backsubstitution(
    show: ShowGE,
    *,
    var_name: str = "x",
    param_name: str = r"\alpha",
    **render_opts: Any,
):
    """Top-level wrapper for ``ShowGE.show_backsubstitution(...)``."""
    return show.show_backsubstitution(var_name=var_name, param_name=param_name, **render_opts)


def show_solution(
    show: ShowGE,
    *,
    b_col: Optional[int] = None,
    var_name: str = "x",
    param_name: str = r"\alpha",
    **render_opts: Any,
):
    """Top-level wrapper for ``ShowGE.show_solution(...)``."""
    return show.show_solution(b_col=b_col, var_name=var_name, param_name=param_name, **render_opts)


def lhs_matrix(show: ShowGE, *, step: Any = "final"):
    """Top-level wrapper for ``ShowGE.lhs_matrix(...)``."""
    return show.lhs_matrix(step=step)


def rhs_matrix(show: ShowGE, *, step: Any = "final"):
    """Top-level wrapper for ``ShowGE.rhs_matrix(...)``."""
    return show.rhs_matrix(step=step)


def rhs_column(show: ShowGE, b_col: int = 0, *, step: Any = "final"):
    """Top-level wrapper for ``ShowGE.rhs_column(...)``."""
    return show.rhs_column(b_col, step=step)


def solutions(show: ShowGE, *, gj: Optional[bool] = None):
    """Return ``(particular, homogeneous)`` from ``ShowGE.solve(...)``."""
    sol = show.solve(gj=gj)
    return sol["particular"], sol["homogeneous"]
