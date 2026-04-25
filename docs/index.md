# la_figures

la_figures provides linear algebra algorithms that produce layout specs for the
*matrixlayout* package. It does not render TeX or call toolchains.

## Scope

- Compute traces (GE, QR, eig/SVD) and assemble spec dictionaries.
- Provide convenience wrappers that render TeX to SVG via *matrixlayout* and *jupyter_tikz*.
- Normalize inputs from PythonCall/PyCall when needed.

## Reading Guide

- See `overview.md` for the layering model.
- See `getting-started.md` for minimal examples.
- See `specs.md` for the spec fields and parameters.
- See `interop.md` for Julia usage.
- See `notebooks/` for problem-type walkthroughs and top-level API notebooks.
- See `notebooks/13_latex_fragment_rendering.ipynb` for generic LaTeX and `LAlatex` SVG rendering.

## CLI quick checks

Run a smoke render to validate toolchains:

```
python render_smoke.py
```

Set `LA_FIGURES_SMOKE_OUT` to control the output directory.
