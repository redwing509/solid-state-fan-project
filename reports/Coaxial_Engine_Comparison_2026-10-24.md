# Coaxial electrical cross-check: OpenFOAM v2412 vs SciPy BVP vs exact (2026-10-24)

**Scope.** Fixed-injection, steady unipolar drift between a 1 mm wire and a 100 mm outer cylinder (eps0 = 8.854e-12 F/m).
36 cases: voltage 10/20/30/40 kV x ion mobility 1.5/1.8/2.3e-4 m^2/(V s) x injected charge 0.5/1/2e-5 C/m^3.
This verifies the numerics of the reduced electrical model only. It is **not** fan, corona-onset, airflow or material validation, and the
electrode voltages are distinct from the 110/220/330/440 VAC supply inputs.

**Engines (independent).**
- *Exact*: closed-form field + adaptive quadrature + Brent shooting on the emitter field (`coaxial_verification.json`, `shooting_current_A_per_m`).
- *SciPy BVP*: log-radius Poisson/current-conservation collocation with unknown current (`bvp_current_A_per_m`).
- *OpenFOAM v2412*: queue runs on mail (`openfoam_v2412_coaxial_runs.json`, job + result per run; current = |outer-patch I| / (0.01 m depth x 1/4 sector)).
  Primary run per case: mesh_n 192, linearUpwind. All 6 variants (48/96/192 x upwind/linearUpwind, 216 runs) were also gated.

**Tolerance (stated before running the comparison).** Each engine's current within **1 %** of exact, and the engines within **1 %** of each other.
A case passes only if the primary run *and every* OpenFOAM variant pass.

## Result: 36/36 cases pass

| Metric | Max over 36 cases |
|---|---|
| SciPy BVP vs exact | 6.76e-13 |
| OpenFOAM (192, linearUpwind) vs exact | 1.26e-04 (0.0126 %) |
| OpenFOAM (192, linearUpwind) vs SciPy BVP | 1.26e-04 |
| Worst of all 216 OpenFOAM runs vs exact | 6.60e-03 (0.660 %) |
| Worst of all 216 OpenFOAM runs vs SciPy BVP | 6.60e-03 |

Worst primary case: 40 kV, mobility 0.00018, injection 5e-06.
Worst variant overall: 48/upwind at 10 kV, mobility 0.00023, injection 2e-05 (coarsest meshes carry the largest error, as expected).

Per-case numbers: `results/coaxial-electrical/coaxial_engine_comparison.csv`. Reproduce: `python3 scripts/compare_coaxial_engines.py` (exit 0 = all pass).

**Limitations.** Fixed injected space charge; no corona onset or ionization chemistry; no diffusion or airflow (electric_force off).
OpenFOAM inputs are the 2026-10-21/22 queue results (snapshot 2026-10-22 06:32 UTC); no new compute was run for this comparison.
