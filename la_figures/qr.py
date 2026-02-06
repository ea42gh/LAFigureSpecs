"""QR/Gram–Schmidt helpers (algorithmic layer)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Iterator, List, Tuple

import sympy as sym

from ._sympy_utils import to_sympy_matrix


class QRGridMatrices(dict):
    """Dict-like container that also supports tuple unpacking in a fixed order."""

    _order = ("A", "W", "WtA", "WtW", "S", "Qt", "Q", "R")

    def __iter__(self) -> Iterator[Any]:
        for key in self._order:
            yield self.get(key)

    def as_tuple(self) -> tuple:
        return tuple(self.get(k) for k in self._order)

    def as_dict(self) -> Dict[str, Any]:
        return {k: self.get(k) for k in self._order}

def compute_qr_matrices(A: Any) -> Sequence[Sequence[sym.Matrix]]:
    """Return the matrix grid used by the QR layout.

    Parameters
    ----------
    A:
        Original matrix.
    """

    A_mat = to_sympy_matrix(A)
    if A_mat is None:
        raise ValueError("compute_qr_matrices requires non-empty A")
    W_mat = naive_gram_schmidt_w(A_mat, scale_lcd=True)

    WtW = W_mat.T @ W_mat
    WtA = W_mat.T @ A_mat
    diag = []
    for x in sym.Matrix.diagonal(WtW):
        diag.append(1 if x == 0 else 1 / sym.sqrt(x))
    S = sym.Matrix.diag(diag)

    Qt = S * W_mat.T
    R = S * WtA

    return [
        [None, None, A_mat, W_mat],
        [None, W_mat.T, WtA, WtW],
        [S, Qt, R, None],
    ]


def gram_schmidt_qr_matrices(
    A: Any,
    *,
    allow_rank_deficient: bool = False,
    rank_deficient: Optional[str] = None,
) -> Sequence[Sequence[sym.Matrix]]:
    """Return the QR grid using Gram–Schmidt-style scaling.

    If ``rank_deficient`` is set, it selects the fallback behavior when
    ``W^T W`` is singular:
      - "drop": drop dependent columns from W (and corresponding A columns).
      - "pinv": use the pseudo-inverse.
      - "diag": invert only nonzero diagonals.
    If ``allow_rank_deficient`` is True and no ``rank_deficient`` mode is set,
    it falls back to "pinv".
    """

    A_mat = to_sympy_matrix(A)
    if A_mat is None:
        raise ValueError("gram_schmidt_qr_matrices requires non-empty A")
    W_mat = naive_gram_schmidt_w(A_mat, scale_lcd=True)

    mode = (rank_deficient or "").strip().lower() or None
    orig_cols = W_mat.cols
    if mode == "drop":
        pivots = list(W_mat.rref()[1])
        if pivots:
            W_mat = W_mat[:, pivots]
            if A_mat.cols == orig_cols:
                A_mat = A_mat[:, pivots]

    WtW = W_mat.T @ W_mat
    WtA = W_mat.T @ A_mat
    diag_entries = list(sym.Matrix.diagonal(WtW))
    if mode is None and not allow_rank_deficient:
        if any(d == 0 for d in diag_entries):
            raise ValueError("W^T W is singular; set rank_deficient or allow_rank_deficient")
    try:
        S = sym.Matrix(WtW)**(-1)
    except Exception as exc:
        if mode is None and allow_rank_deficient:
            mode = "pinv"
        handled = False
        if mode == "pinv":
            pinv = getattr(WtW, "pinv", None)
            if callable(pinv):
                try:
                    S = pinv()
                    handled = True
                except Exception:
                    mode = "diag"
            else:
                mode = "diag"
        if mode == "diag":
            S = sym.zeros(*WtW.shape)
            n = min(WtW.shape)
            for i in range(n):
                if WtW[i, i] != 0:
                    S[i, i] = 1 / WtW[i, i]
            handled = True
        if not handled:
            raise ValueError("W^T W is singular; set rank_deficient or allow_rank_deficient") from exc

    S = sym.Matrix(S)
    for i in range(min(S.shape)):
        S[i, i] = sym.sqrt(S[i, i]) if S[i, i] != 0 else 1

    Qt = S * W_mat.T
    R = S * WtA

    return [
        [None, None, A_mat, W_mat],
        [None, W_mat.T, WtA, WtW],
        [S, Qt, R, None],
    ]


def qr_matrices_from_grid(mats: Sequence[Sequence[sym.Matrix]]) -> Dict[str, Any]:
    """Extract QR-related matrices from a Gram–Schmidt QR grid.

    Returns a dict with keys: A, W, WtA, WtW, S, Qt, Q, R.
    """

    grid = list(mats)
    row1, row2, row3 = (list(r) for r in grid)
    A = row1[2]
    W = row1[3]
    WtA = row2[2]
    WtW = row2[3]
    S = row3[0]
    Qt = row3[1]
    R = row3[2]
    Q = Qt.T if Qt is not None else None
    return QRGridMatrices(A=A, W=W, WtA=WtA, WtW=WtW, S=S, Qt=Qt, Q=Q, R=R)


def qr_matrices_dict_from_grid(mats: Sequence[Sequence[sym.Matrix]]) -> Dict[str, Any]:
    """Return QR matrices as a plain dict for JSON-friendly usage."""
    return qr_matrices_from_grid(mats).as_dict()


def naive_gram_schmidt_w(A: Any, *, scale_lcd: bool = True) -> sym.Matrix:
    """Naive Gram–Schmidt to produce orthogonal (not normalized) columns W.

    If a column is dependent, keep a zero column in W.
    If scale_lcd is True, scale each nonzero column by the LCD of its entries.
    """

    A_mat = to_sympy_matrix(A)
    if A_mat is None:
        raise ValueError("naive_gram_schmidt_w requires non-empty A")

    m, n = A_mat.shape
    W_cols: List[sym.Matrix] = []

    def _col_lcd(v: sym.Matrix) -> int:
        denoms: List[int] = []
        for i in range(v.rows):
            val = sym.simplify(v[i, 0])
            if val == 0:
                continue
            rat = sym.Rational(val)
            denoms.append(int(rat.q))
        if not denoms:
            return 1
        if len(denoms) == 1:
            return int(denoms[0])
        return int(sym.ilcm(*denoms))

    for j in range(n):
        v = sym.Matrix(A_mat[:, j])
        for w in W_cols:
            denom = (w.T * w)[0]
            if denom != 0:
                v = v - (w.T * v)[0] / denom * w
        if v.norm() == 0:
            W_cols.append(sym.zeros(m, 1))
            continue
        if scale_lcd:
            lcd = _col_lcd(v)
            v = sym.simplify(lcd * v)
        W_cols.append(v)

    return sym.Matrix.hstack(*W_cols) if W_cols else sym.zeros(m, 0)


def naive_qr(
    A: Any,
    *,
    max_iter: int = 1000,
    tol: float = 1e-10,
) -> tuple[sym.Matrix, sym.Matrix, float]:
    """Naive QR algorithm for Schur-like triangularization.

    Parameters
    ----------
    A:
        Input square matrix.
    max_iter:
        Maximum number of QR iterations.
    tol:
        Convergence tolerance on strict lower-triangular entries.
    """

    A_mat = to_sympy_matrix(A)
    if A_mat is None:
        raise ValueError("naive_qr requires a non-empty square matrix")
    n, m = A_mat.shape
    if n != m:
        raise ValueError("naive_qr requires a square matrix")

    Q_total = sym.eye(n)
    Ak = sym.Matrix(A_mat)
    conv = sym.oo

    def _lower_max_abs(mat: sym.Matrix) -> float:
        if mat.rows == 0:
            return 0.0
        max_val = 0
        for i in range(1, mat.rows):
            for j in range(0, min(i, mat.cols)):
                val = sym.Abs(mat[i, j])
                if val > max_val:
                    max_val = val
        try:
            return float(max_val)
        except Exception:
            return float(sym.N(max_val))

    for _ in range(int(max_iter)):
        Qk, Rk = Ak.QRdecomposition()
        Ak = sym.Matrix(Rk) * sym.Matrix(Qk)
        Q_total = sym.Matrix(Q_total) * sym.Matrix(Qk)
        conv = _lower_max_abs(Ak)
        if conv < tol:
            break

    return Q_total, Ak, float(conv)


def qr_tbl_spec(
    A: Any,
    *,
    array_names: Any = True,
    fig_scale: Optional[Any] = None,
    preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    extension: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Dict[str, Any]:
    """Return a layout spec for :func:`matrixlayout.qr.render_qr_tex`."""

    matrices = compute_qr_matrices(A)
    return {
        "matrices": matrices,
        "array_names": array_names,
        "fig_scale": fig_scale,
        "preamble": preamble,
        "extension": extension,
        "nice_options": nice_options,
        "label_color": label_color,
        "label_text_color": label_text_color,
        "known_zero_color": known_zero_color,
        "decorators": decorators,
        "strict": strict,
        "create_extra_nodes": True if array_names else None,
    }


def qr_tbl_layout_spec(
    A: Any,
    *,
    array_names: Any = True,
    fig_scale: Optional[Any] = None,
    preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    extension: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Any:
    """Return a typed QR layout spec (``QRGridSpec``) for matrixlayout."""

    from matrixlayout.specs import QRGridSpec

    spec = qr_tbl_spec(
        A,
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
    return QRGridSpec.from_dict(spec)


def qr_tbl_spec_from_matrices(
    matrices: Sequence[Sequence[Any]],
    *,
    array_names: Any = True,
    fig_scale: Optional[Any] = None,
    preamble: str = r" \NiceMatrixOptions{cell-space-limits = 2pt}" + "\n",
    extension: str = "",
    nice_options: Optional[str] = "vlines-in-sub-matrix = I",
    label_color: str = "blue",
    label_text_color: str = "red",
    known_zero_color: str = "brown",
    decorators: Optional[Sequence[Any]] = None,
    strict: Optional[bool] = None,
) -> Dict[str, Any]:
    """Return a layout spec from a precomputed matrix grid."""

    return {
        "matrices": matrices,
        "array_names": array_names,
        "fig_scale": fig_scale,
        "preamble": preamble,
        "extension": extension,
        "nice_options": nice_options,
        "label_color": label_color,
        "label_text_color": label_text_color,
        "known_zero_color": known_zero_color,
        "decorators": decorators,
        "strict": strict,
    }
