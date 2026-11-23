# Coaxial reduced model: test results (queue item 9, 2026-10-24)

Status: **EXECUTED + VERIFIED (numerics, 2 independent methods + closed form)**. Not VALIDATED: no corona onset, airflow or experiment.
Tolerances pre-stated in ACCEPTANCE.md (commit 5ad6737). `pytest tests/coaxial`: **45/45 pass** (Python 3.12, scipy local).

| ID | Result |
|---|---|
| C1 | 36/36 cases: shooting vs BVP current, field L2 and potential L2 all < 1e-4 |
| C2 | Recomputed currents match the published coaxial_verification.json to <= 1e-8 (refactor did not change results) |
| C3 | rho -> 0: emitter field = Laplace V/(a ln(b/a)) within 1e-6 |
| C4 | BVP y(t) matches the first integral y^2 = y0^2 + k(e^{2t}-1) within 1e-6 (3 cases) |
| C5 | Fixed meshes N = 11/21/41/81/161: current error 1.24e-5, 7.8e-7, 4.9e-8, 3.1e-9, 1.9e-10; observed order **p = 4.00 / 4.02** (4th-order collocation as expected) |
| C6 | Adaptive tol 1e-3...1e-9: every error <= 4.9e-9 (criterion 1e-4) |
| C7 | Initial mesh 50/100/200/400 at tol 1e-9: spread <= 1e-9 |

Numbers: `mesh_study_result.json` (regenerate with `python tests/coaxial/mesh_study.py --out ...`).

## Disclosed deviation in method (tolerances unchanged)
ACCEPTANCE.md C5 said fixed meshes would be enforced with "tol set loose". In the first run that gave errors stuck at 2.8e-3 and p ~ 0. The reason is that scipy's solve_bvp scales its inner Newton tolerance with `tol`, so the loose tol measured Newton under-convergence, not mesh error. The fixed mesh is now enforced with `max_nodes = N` at tol 1e-9 and accepts scipy status 1 (node limit reached after Newton converged on the given mesh). The node count is still asserted unchanged. The C5 thresholds were not changed.

## Code change
`scripts/coaxial_verification.py`: method 2 was moved into `solve_log_radius_bvp()` and `bvp_current_from_solution()`, so tests can vary the mesh and tolerance. `compare()` behaviour is unchanged (C2). CI: `.github/workflows/coaxial.yml`.
