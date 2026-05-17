"""Eigen-decomposition description objects for :mod:`matrixlayout`.

The functions in this module compute eigenvalues/eigenvectors and package them
into a *description object* (a plain dictionary) suitable for
``matrixlayout.render_eig_tex``.

This module intentionally contains *algorithmic* logic (it may call SymPy
decompositions). It does not render.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import sympy as sym

from ._sympy_utils import to_sympy_matrix
from .gram_schmidt import q_gram_schmidt


def _maybe_round(x: Any, digits: Optional[int]) -> Any:
    """Round a scalar-like value if ``digits`` is provided.

    This uses Python's ``round`` directly when possible and leaves
    non-roundable symbolic values as-is.
    """

    if digits is None:
        return x
    try:
        return round(x) if digits == 0 else round(x, digits)
    except Exception:
        return x


def _maybe_round_vectors(vecs: List[sym.Matrix], digits: Optional[int]) -> List[sym.Matrix]:
    """Round vector entries elementwise if ``digits`` is provided."""

    if digits is None:
        return vecs

    out: List[sym.Matrix] = []
    for v in vecs:
        vv = sym.Matrix(v)
        out.append(vv.applyfunc(lambda t: _maybe_round(t, digits)))
    return out


def _factor_out_denominator(A: sym.Matrix) -> tuple[Any, sym.Matrix]:
    denoms: List[int] = []
    for entry in A:
        den = sym.denom(sym.simplify(entry))
        if isinstance(den, sym.Integer):
            denoms.append(int(den))
        elif getattr(den, "is_integer", False):
            try:
                denoms.append(int(den))
            except Exception:
                return sym.Integer(1), A
        else:
            return sym.Integer(1), A
    if not denoms:
        return sym.Integer(1), A
    if len(denoms) == 1:
        d = sym.Integer(denoms[0])
    else:
        d = sym.ilcm(*denoms)
    return d, sym.simplify(d * A)


def eig_tbl_spec(
    A: Any,
    *,
    normal: bool = False,
    Ascale: Optional[Any] = None,
    eig_digits: Optional[int] = None,
    vec_digits: Optional[int] = None,
) -> Dict[str, Any]:
    """Compute the eigen-table description object consumed by matrixlayout.

    Parameters
    ----------
    A:
        Square matrix (array-like). Converted to a SymPy Matrix.
    normal:
        If true, compute an orthonormal basis within each eigenspace (``qvecs``).
    Ascale:
        If provided, eigenvalues are divided by ``Ascale``.
    eig_digits, vec_digits:
        Optional rounding controls.

    Returns
    -------
    dict
        Keys:
          - ``lambda``: distinct eigenvalues (ordered by the current policy)
          - ``ma``: corresponding algebraic multiplicities
          - ``evecs``: eigenvector groups (list per eigenvalue)
          - ``qvecs``: (optional) orthonormal eigenvector groups
    """

    A = to_sympy_matrix(A)
    if A is None:
        raise ValueError("A must not be None")

    d, Aint = _factor_out_denominator(A)
    A = Aint
    if Ascale is None:
        Ascale = d

    if A.rows != A.cols:
        raise ValueError(f"eig_tbl_spec requires a square matrix; got shape {A.shape}")

    eig: Dict[str, Any] = {
        "lambda": [],
        "ma": [],
        "evecs": [],
    }
    if normal:
        eig["qvecs"] = []

    res = A.eigenvects()
    for (e, m, vecs) in res:
        e_scaled = e if Ascale is None else (e / Ascale)
        e_scaled = _maybe_round(e_scaled, eig_digits)
        vecs2 = [sym.Matrix(v) for v in vecs]
        vecs2 = _maybe_round_vectors(vecs2, vec_digits)

        # Insert at 0 to reverse the order returned by SymPy.
        eig["lambda"].insert(0, e_scaled)
        eig["ma"].insert(0, int(m))
        eig["evecs"].insert(0, vecs2)

        if normal:
            eig["qvecs"].insert(0, q_gram_schmidt(vecs2))

    return eig


EigenvectsResult = Iterable[Tuple[Any, int, Sequence[sym.Matrix]]]


def eig_spec_from_eigenvects(
    eigenvects: EigenvectsResult,
    *,
    normal: bool = False,
    Ascale: Optional[Any] = None,
    eig_digits: Optional[int] = None,
    vec_digits: Optional[int] = None,
    order: str = "legacy",
) -> Dict[str, Any]:
    """Convert a precomputed eigenvects-style result into a matrixlayout spec.

    Parameters
    ----------
    eigenvects:
        An iterable of ``(e, m, vecs)`` triples, as produced by
        ``sympy.Matrix.eigenvects()``.
    normal, Ascale, eig_digits, vec_digits:
        Behave as in :func:`eig_tbl_spec`.
    order:
        - ``"legacy"`` (default): reverse SymPy's eigenvects order.
        - ``"sympy"``: preserve SymPy's order.
    """

    eig: Dict[str, Any] = {
        "lambda": [],
        "ma": [],
        "evecs": [],
    }
    if normal:
        eig["qvecs"] = []

    # Collect once so we can reverse deterministically.
    triples: List[Tuple[Any, int, List[sym.Matrix]]] = []
    for (e, m, vecs) in eigenvects:
        vecs2 = [sym.Matrix(v) for v in vecs]
        triples.append((e, int(m), vecs2))

    if order not in {"legacy", "sympy"}:
        raise ValueError(f"order must be 'legacy' or 'sympy'; got {order!r}")

    if order == "legacy":
        triples = list(reversed(triples))

    for (e, m, vecs2) in triples:
        e_scaled = e if Ascale is None else (e / Ascale)
        e_scaled = _maybe_round(e_scaled, eig_digits)
        vecs2 = _maybe_round_vectors(vecs2, vec_digits)

        eig["lambda"].append(e_scaled)
        eig["ma"].append(int(m))
        eig["evecs"].append(vecs2)
        if normal:
            eig["qvecs"].append(q_gram_schmidt(vecs2))

    return eig


def eig_matrices_from_spec(
    eig: Dict[str, Any],
    *,
    orthonormal: bool = True,
) -> Tuple[sym.Matrix, sym.Matrix]:
    """Assemble (Λ, V) from an eigen-table spec dictionary.

    Parameters
    ----------
    eig:
        Spec dict as returned by :func:`eig_tbl_spec` or :func:`eig_spec_from_eigenvects`.
    orthonormal:
        Use ``qvecs`` when present; otherwise fall back to ``evecs``.
    """

    lambdas = list(eig.get("lambda", []))
    mas = [int(m) for m in eig.get("ma", [])]
    vec_key = "qvecs" if orthonormal and eig.get("qvecs") is not None else "evecs"
    groups = list(eig.get(vec_key, []))

    cols: List[sym.Matrix] = []
    full_lambda: List[Any] = []
    for lam, m, vecs in zip(lambdas, mas, groups, strict=False):
        full_lambda.extend([lam] * m)
        cols.extend([sym.Matrix(v) for v in vecs])

    V = sym.Matrix.hstack(*cols) if cols else sym.Matrix([])
    Λ = sym.diag(*full_lambda) if full_lambda else sym.Matrix([])
    return Λ, V


@dataclass(frozen=True)
class EigenDecomposition:
    """A small container for a computed eigendecomposition and options."""

    A: sym.Matrix
    eigenvects: List[Tuple[Any, int, List[sym.Matrix]]]
    normal: bool = False
    Ascale: Optional[Any] = None
    eig_digits: Optional[int] = None
    vec_digits: Optional[int] = None

    def to_spec(self, *, order: str = "legacy") -> Dict[str, Any]:
        return eig_spec_from_eigenvects(
            self.eigenvects,
            normal=self.normal,
            Ascale=self.Ascale,
            eig_digits=self.eig_digits,
            vec_digits=self.vec_digits,
            order=order,
        )


def eigendecomposition(
    A: Any,
    *,
    normal: bool = False,
    Ascale: Optional[Any] = None,
    eig_digits: Optional[int] = None,
    vec_digits: Optional[int] = None,
) -> EigenDecomposition:
    """Compute and return an :class:`EigenDecomposition`.

    This is useful when callers (including Julia code) want to compute
    eigen-information once and later derive multiple specs (different ordering,
    rounding, or presentation options).
    """

    A2 = to_sympy_matrix(A)
    if A2 is None:
        raise ValueError("A must not be None")
    d, Aint = _factor_out_denominator(A2)
    A2 = Aint
    if Ascale is None:
        Ascale = d
    if A2.rows != A2.cols:
        raise ValueError(f"eigendecomposition requires a square matrix; got shape {A2.shape}")

    ev_raw = A2.eigenvects()
    ev: List[Tuple[Any, int, List[sym.Matrix]]] = []
    for (e, m, vecs) in ev_raw:
        ev.append((e, int(m), [sym.Matrix(v) for v in vecs]))

    return EigenDecomposition(
        A=A2,
        eigenvects=ev,
        normal=normal,
        Ascale=Ascale,
        eig_digits=eig_digits,
        vec_digits=vec_digits,
    )
