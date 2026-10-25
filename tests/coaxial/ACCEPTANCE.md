# Coaxial reduced electrical model: pre-stated test tolerances (verification queue item 9, 2026-10-24)

Committed BEFORE the tests in this directory were first run. Model under test: `scripts/coaxial_verification.py`
(steady unipolar drift, fixed injected charge, wire a = 1 mm, outer b = 100 mm). Labels: numerical VERIFICATION
of the reduced model only. It is not fan, corona-onset or airflow validation.

| ID | Check | Tolerance |
|---|---|---|
| C1 | All 36 published cases: shooting vs BVP relative current error, field L2, potential L2 | each < 1e-4 (as the script's own gate) |
| C2 | Regression: recomputed shooting and BVP currents vs `results/coaxial-electrical/coaxial_verification.json` | relative <= 1e-8 |
| C3 | Space-charge-free limit (rho = 1e-14 C/m^3): emitter field vs Laplace V/(a ln(b/a)) | relative <= 1e-6 |
| C4 | Closed form: with y = rE/V0, (y^2)' = 2k e^{2t} gives y(t)^2 = y0^2 + k(e^{2t} - 1); BVP y on 401 points vs this form | max relative <= 1e-6 |
| C5 | BVP mesh-resolution study, fixed meshes (no node insertion: max_nodes = N, tol set loose, node count asserted unchanged): N = 11, 21, 41, 81, 161 uniform in t, baseline case 30 kV / 1e-5 / 1.8e-4. Error of the current vs shooting | monotone decrease; observed order p on the finest three meshes >= 3.5 (4th-order collocation, so ~4 expected); error at N = 161 <= 1e-8 |
| C6 | Adaptive BVP tolerance sweep tol = 1e-3 ... 1e-9 (default mesh 200) | current error <= 1e-4 for every tol <= 1e-6, and error at 1e-9 <= error at 1e-3 |
| C7 | Initial-mesh independence at tol 1e-9: initial mesh 50, 100, 200, 400 | current spread <= 1e-9 relative |

CI: `.github/workflows/coaxial.yml` runs `pytest tests/coaxial` on Python 3.10 and 3.12 for pushes and PRs touching the model or tests.
