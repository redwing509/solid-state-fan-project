# thermal1d acceptance criteria (written and committed BEFORE the verification suite and the OpenFOAM comparison were run)

Date: 2026-10-24 (PDT). Author: Grok Bot (supervisor) for the Solid State Fan project.
These tolerances are fixed in advance. They must not be loosened after seeing results; any change
needs a new dated section explaining why.

## A. Code verification (pytest suite `tests/`)

| ID | Test | Reference | Metric | Tolerance |
|---|---|---|---|---|
| V1 | Steady conduction, Dirichlet-Dirichlet | linear profile (Incropera Ch. 3) | max abs error | <= 1e-9 K |
| V2 | Steady conduction, inward flux + Dirichlet (baseline BC type) | linear profile | max abs error | <= 1e-9 K |
| V3 | Steady plane wall with convective (Robin) BC, Bi = 0.1, 1, 10 | Incropera Ch. 3 closed form | max abs error | <= 1e-9 K |
| V4 | Steady plane wall with uniform generation | parabolic profile (Incropera Eq. 3.41 form) | max abs error | <= 1e-8 K |
| V5 | Semi-infinite solid, constant surface flux | Carslaw & Jaeger 2.9; Incropera Eq. 5.58 | surface-rise rel. error; profile max error / surface rise | <= 0.5 % each (N = 400 over 12 sqrt(alpha t)) |
| V6 | Semi-infinite solid, step surface temperature | erfc solution (Incropera Eq. 5.57) | max error / abs(Ts - Ti) at Fo-equivalent t | <= 1 % |
| V7 | Slab, inward flux at x=0 and Dirichlet at x=L (baseline BC type), Fourier series | separation of variables, 400 terms | max error / (qL/k), at Fo = 0.05, 0.2, 1, 3 | <= 0.1 % (N = 256) |
| V8 | Slab cooling, both faces at T_w, Fourier series | Carslaw & Jaeger 3.3 | max error / abs(Ti - Tw), Fo >= 0.05 | <= 0.5 % (N = 256) |
| V9 | Lumped capacitance exponential | Incropera Eq. 5.6 | max rel. error of (T - T_inf) at dt = tau/100, CN | <= 1e-4 |
| V10 | Lumped-capacitance time order | exact exponential | observed order, implicit Euler / CN | 1 +/- 0.1 and 2 +/- 0.1 |
| V11 | MMS, space: variable k(x), rho_c(x), time-dependent flux (left) and Robin (right) BCs, source | manufactured T(x,t) | observed order (L_inf and L_2), 4 grids r = 2 | 2 +/- 0.1 |
| V12 | MMS, time: same problem, fixed fine grid | manufactured T | observed order, Euler / CN | 1 +/- 0.1 and 2 +/- 0.1 |
| V13 | Global energy conservation (mixed BCs + source, theta = 0.5 and 1) | discrete balance | abs(dE - integral of heat input) / integral of abs(heat input) | <= 1e-10 |
| V14 | Published benchmark: Incropera et al., 6th ed., Example 5.1 (thermocouple junction: h = 400 W/m2K, k = 20 W/mK, c = 400 J/kgK, rho = 8500 kg/m3, tau = 1 s; gas 200 C, initial 25 C) | book: D = 0.706 mm; t to 199 C = 5.2 s | D rel. error; t abs error | <= 0.5 %; <= 0.05 s (book's 2-sig-fig rounding) |
| V15 | Grid convergence of the baseline (T_wall and T_mean at 10 s), 3 grids r = 2 (128/256/512 cells, dt proportional to h, CN), Richardson + GCI (Roache; Celik et al. 2008) | - | observed order p; asymptotic ratio GCI_23/(r^p GCI_12); GCI_fine | p in [1.8, 2.2]; ratio 1 +/- 0.05; GCI_fine <= 0.1 % |
| V16 | Time-step convergence of the baseline (T_wall at 10 s), 3 steps r = 2, CN | - | observed order; GCI_fine | p in [1.8, 2.2] or GCI_fine <= 0.01 %; GCI_fine <= 0.1 % |
| V17 | Baseline sanity vs closed form: T_wall(10 s) vs semi-infinite flux solution; T_mean vs q t/(rho c H) | Carslaw & Jaeger 2.9 | abs error | <= 0.05 K; <= 0.01 K |

Note on V15/V16: T_wall under a suddenly applied flux has a sqrt(t) start-up; the formal order is still 2 in space and time at t = 10 s, which is what is tested.

## B. Cross-check against OpenFOAM (buoyantBoussinesqPimpleEHDFoam, OF 4, legacy EHD benchmark, corrected inputs)

Quantities at t = 10 s: wall heat flux on `down`; peak temperature, taken as the plate (wall-face)
temperature T_P + g*d (OpenFOAM cell value plus imposed gradient times cell-centre-to-face distance),
plus the raw maximum cell value for information; volume-weighted mean T of the domain.
thermal1d is not tuned, refitted or re-gridded after seeing OpenFOAM numbers.

### B1. Conduction control (same physics): OpenFOAM with the EHD drive off (0 V, zero injected charge), maxDeltaT 0.005 s

thermal1d solves exactly this problem (left symmetry and right zeroGradient are adiabatic without flow; the 0.0395 mm adiabatic wire is negligible).
Tolerance basis: OpenFOAM uses implicit Euler (first order in time) and a 0.57 mm uniform near-wall cell size in y, plus the wall
extrapolation T_P + g*d; estimated discretisation error well below 1 % of the 135 K rise.

| Quantity | Tolerance |
|---|---|
| wall heat flux | abs diff <= 1 % |
| peak (plate) temperature rise above 300 K | rel. diff <= 2 % |
| mean temperature rise above 300 K | rel. diff <= 1 % |
| plate-temperature uniformity along x (OF) | max-min <= 2 % of rise (confirms 1-D behaviour) |

### B2. EHD-on corrected baseline (`thermal-fix-20261024/corrected-baseline`)

Different physics: the ionic wind advects heat, which a 1-D conduction model cannot represent. Same tolerances as B1
are applied and reported, but disagreement is expected and is reported as such; thermal1d is the zero-flow limit, so it
is expected to bound the OpenFOAM plate temperature from above. B2 can NOT be cited as an independent cross-check of the EHD result.

### Merge rule (2-engine rule)

Merge `engines/thermal1d` to main only if every A test passes AND every B1 criterion passes. B2 is reported honestly
but does not gate the merge, and the PR/README must state that thermal1d is not a second engine for the EHD-driven case.
