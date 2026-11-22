# E-01 GetDP known-solution: pre-stated pass band (t1244u)

The pass rules below are those written in `METHOD.md` **before** the accepted GetDP unipolar re-run was scored. They are model-only numerical verification of the GetDP formulation against analytic solutions. They are not a fan, corona-onset, airflow, ozone, or commercial-performance result. PUSH=0. No Fan PR until James asks. The project owner reviews evidence before any inclusion. The Fan job-ownership warning is unchanged; running OpenFOAM r8/e40k containers were not touched.

## A1. Vacuum coaxial capacitor (Poisson only)

Geometry: `a = 0.01` m at 1 V, `b = 0.05` m at 0 V, `ε0 = 8.854187818e-12` F/m. Exact energy, probe `V` and `E` as in `../../SMOKE-TEST.md`. Three meshes, characteristic length halved twice.

| Check | Pass line |
|---|---|
| Finest-mesh energy vs formula | relative error ≤ 1% |
| Finest-mesh probe `V` vs formula | relative error ≤ 1% |
| Energy and probe `V` errors | must not increase from coarsest to finest |
| Apparent order of the energy error on the first refinement | > 0.5 where defined |

## A2. Coaxial unipolar drift (Poisson + charge conservation)

Geometry: `a = 0.001` m, `b = 0.1` m, `V(a) = 30 kV`, `V(b) = 0`, `ρ(a) = 1e-5` C/m³, `μ = 1.8e-4` m²/(V s), `ε0 = 8.854e-12` F/m. Exact current `I' = 6.78117058395794e-05` A/m from the shooting solution in `scripts/coaxial_verification.py` (BVP cross-check relative difference `6e-13`). Current is the mean of volume samples `I(r) = 2π r μ ρ |E|` at `r = 0.002, 0.005, 0.01, 0.02, 0.05` m.

| Check | Pass line |
|---|---|
| Finest-mesh mean volume-sample current vs exact `I'` | relative error ≤ 1% |
| Relative change between the finest two currents | ≤ 2% |
| Apparent order of the current error on the first refinement | > 0.5 where defined |
| Independent shooting vs BVP current (existing coaxial script) | relative difference < 1e-10 |

The 0.25% Validation_Plan engineering target is reported but is **not** the pass/fail line for this first GetDP check.

Official scorer: `check_known.py` (and `check_uni.py` for A2 alone).
