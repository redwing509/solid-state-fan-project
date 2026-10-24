# fan-11 acceptance criteria (pre-registered 2026-10-24, before any run)

Case: upstream legacy EHD heated-plate benchmark (buoyantBoussinesqPimpleEHDFoam @ cfd66422, OpenFOAM
Foundation 4.1), **inputs unchanged** except mesh density, maxCo and decomposition. The thermal-input
discrepancy (127 vs 187 W/m², see Legacy_Benchmark_Review.md) is NOT fixed here: this is numerical
verification of the code as published, not validation.

Levels (uniform in-plane refinement, grading kept, r = 2): M1 4,700 cells (as published), M2 18,800, M4 75,200.
Time-step study on M2: maxCo 2 (base) / 1 / 0.5. Quantities at t = 10 s:
heated-plate area-average temperature `Tdown_mean` (patch `down`), max |U|, max T.

PASS requires all of:
- every run exits rc 0 with finite fields;
- GCI (Celik 2008, Fs = 1.25): monotone convergence, 0.5 <= p <= 4,
  GCI_fine <= 2 % for Tdown_mean and <= 5 % for max |U|;
- time-step: |maxCo 1 - maxCo 2| and |maxCo 0.5 - maxCo 2| <= 1 % for Tdown_mean and max |U|.
Otherwise the verdict is NOT-PASSED with the numbers reported; no re-tuning after seeing results.
Reporting: executed != verified (needs a second engine/agent to agree) != validated (needs experiment).
