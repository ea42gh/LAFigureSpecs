JupyterLab Notebooks
====================

Use this directory for notebooks that demonstrate LAFigureSpecs features.

Top-level API by problem type
-----------------------------
- `07_ge_top_level_functions.ipynb` — GE top-level API (`ge_trace`, `ge_spec`, `ge_svg`, `ge_bundle`, `show_ge`)
- `08_qr_top_level_functions.ipynb` — QR top-level API (`compute_qr_matrices`, `qr_spec`, `qr_svg`, `qr_stack_svg`, `qr_figure`, `qr_bundle`)
- `09_eig_svd_top_level_functions.ipynb` — Eigen/SVD top-level API (`eig_spec`, `svd_spec`, `eig_bundle`, `svd_bundle`)
- `10_backsubstitution_top_level_functions.ipynb` - system/backsub text helpers
- `11_formatting_and_renderers.ipynb` - formatting selectors + low-level `render_*` entrypoints
- `12_show_ge_class.ipynb` - stateful `ShowGE` helper (REF/RREF + solutions + matrix accessors)
- `13_latex_fragment_rendering.ipynb` - generic `latex_svg`, `latex_document_svg`, and Julia `lshow_svg`

Guidelines
----------
- Keep notebooks short and focused.
- Include a brief header cell describing the goal.
- Avoid large binary outputs in version control.
