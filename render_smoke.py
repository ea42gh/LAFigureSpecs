import os
import sys

import sympy as sym

import la_figures as lf


def main() -> int:
    outdir = os.environ.get("LA_FIGURES_SMOKE_OUT", "/tmp/la/smoke/la_figures")
    os.makedirs(outdir, exist_ok=True)
    print("la_figures smoke render ->", outdir)
    print("python:", sys.version.split()[0])
    print("sympy:", sym.__version__)
    print("la_figures:", getattr(lf, "__version__", "unknown"))
    try:
        import matrixlayout

        print("matrixlayout:", getattr(matrixlayout, "__version__", "unknown"))
    except Exception as exc:
        print("matrixlayout: import failed:", exc)

    A = sym.Matrix([[1, 2], [3, 4]])
    b = sym.Matrix([[5], [6]])
    svg = lf.ge_tbl_svg(A, ref_rhs=b, output_dir=outdir)
    print("svg length:", len(svg))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
