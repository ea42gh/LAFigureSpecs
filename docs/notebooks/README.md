JupyterLab Notebooks
====================

Use this directory for notebooks that demonstrate la_figures features.

Top-level API by problem type
-----------------------------
- `07_ge_top_level_functions.ipynb` — GE top-level API (`ge_trace`, `ge_tbl_*`, `ge`, `show_ge`)
- `08_qr_top_level_functions.ipynb` — QR top-level API (`compute_qr_matrices`, `qr_tbl_*`, `qr`)
- `09_eig_svd_top_level_functions.ipynb` — Eigen/SVD top-level API (`eig_tbl_*`, `svd_tbl_*`)
- `10_backsubstitution_top_level_functions.ipynb` - system/backsub text helpers
- `11_formatting_and_renderers.ipynb` - formatting selectors + low-level `render_*` entrypoints
- `12_show_ge_class.ipynb` - stateful `ShowGE` helper (REF/RREF + solutions)
- `13_latex_fragment_rendering.ipynb` - generic `latex_svg`, `latex_document_svg`, and Julia `lshow_svg`

Guidelines
----------
- Keep notebooks short and focused.
- Include a brief header cell describing the goal.
- Avoid large binary outputs in version control.
