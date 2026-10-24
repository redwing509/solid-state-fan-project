# thermal1d — Verification report

Date: 2026-10-24 (PDT). Engine version 1.0.0. Generated from `results/verification.json`
(`python -m thermal1d verify`; same checks run by `pytest tests` and in CI).

**Result: 34/34 checks pass (17 test cases V1–V17).**
Tolerances were fixed in `ACCEPTANCE_CRITERIA.md`, committed (6b5c3b6, 2026-10-24 13:26 PDT) before the suite
was first run; none were changed afterwards.

This is **code verification** (are the equations solved correctly) and **solution verification** for the Fan baseline
(numerical-uncertainty estimate). It is **not validation**: no experimental data are involved.

## Method

1. *Exact-solution tests* (V1–V4): steady problems whose exact solution lies in the discrete space; error must be at round-off.
2. *Analytic transient tests* (V5–V9): semi-infinite solid (constant flux, step temperature), finite slab Fourier series
   with the baseline's own BC types, lumped-capacitance exponential.
3. *Order of accuracy*: lumped ODE time order (V10); Method of Manufactured Solutions (Roache 2002; Salari & Knupp 2000)
   with variable k(x), rho*c(x), source, time-dependent flux and Robin BCs, 4 grids/steps at r = 2 (V11 space, V12 time).
4. *Conservation* (V13): discrete global energy balance with mixed BCs and source, both time schemes.
5. *Published benchmark* (V14): Incropera, DeWitt, Bergman & Lavine, *Fundamentals of Heat and Mass Transfer*, 6th ed.,
   Example 5.1 (thermocouple junction).
6. *Solution verification of the Fan baseline* (V15–V16): three grids / time steps, r = 2, Richardson extrapolation and
   Grid Convergence Index with Fs = 1.25 (Roache 1994, 1998; Celik et al. 2008, ASME J. Fluids Eng. 130:078001;
   ASME V&V 20-2009), plus closed-form sanity (V17).

## Results

| ID | Test | Metric | Value | Tolerance | Result |
|---|---|---|---|---|---|
| V1 | steady Dirichlet-Dirichlet | max |err| K | 1.137e-12 | 1e-09 | PASS |
| V2 | steady flux + Dirichlet | max |err| K | 2.058e-11 | 1e-09 | PASS |
| V3 | steady convective BC Bi=0.1 | max |err| K | 4.377e-12 | 1e-09 | PASS |
| V3 | steady convective BC Bi=1 | max |err| K | 5.230e-12 | 1e-09 | PASS |
| V3 | steady convective BC Bi=10 | max |err| K | 1.876e-12 | 1e-09 | PASS |
| V4 | steady uniform generation | max |err| K | 7.162e-12 | 1e-08 | PASS |
| V5 | semi-infinite constant flux: surface rise | rel err | 5.625e-05 | 0.005 | PASS |
| V5 | semi-infinite constant flux: profile | max |err| / rise | 5.625e-05 | 0.005 | PASS |
| V6 | semi-infinite step surface temperature | max |err| / |Ts-Ti| | 1.808e-05 | 0.01 | PASS |
| V7 | slab flux+Dirichlet Fourier series Fo=0.05 | max |err| / (qL/k) | 4.617e-06 | 0.001 | PASS |
| V7 | slab flux+Dirichlet Fourier series Fo=0.2 | max |err| / (qL/k) | 2.462e-06 | 0.001 | PASS |
| V7 | slab flux+Dirichlet Fourier series Fo=1 | max |err| / (qL/k) | 7.424e-07 | 0.001 | PASS |
| V7 | slab flux+Dirichlet Fourier series Fo=3 | max |err| / (qL/k) | 1.292e-08 | 0.001 | PASS |
| V8 | slab cooling Fourier series Fo=0.05 | max |err| / |Ti-Tw| | 1.022e-04 | 0.005 | PASS |
| V8 | slab cooling Fourier series Fo=0.2 | max |err| / |Ti-Tw| | 8.830e-05 | 0.005 | PASS |
| V8 | slab cooling Fourier series Fo=1 | max |err| / |Ti-Tw| | 1.679e-07 | 0.005 | PASS |
| V9 | lumped capacitance exponential (CN, dt=tau/100) | max rel err of (T-Tinf) | 4.167e-05 | 0.0001 | PASS |
| V10 | lumped time order theta=1.0 | observed order | 5.287e-02 | 0.1 | PASS |
| V10 | lumped time order theta=0.5 | observed order | 1.667e-03 | 0.1 | PASS |
| V11 | MMS space order (L_inf) | |p - 2| | 5.420e-04 | 0.1 | PASS |
| V11 | MMS space order (L_2) | |p - 2| | 2.575e-04 | 0.1 | PASS |
| V12 | MMS time order theta=1.0 | |p - 1| | 5.983e-03 | 0.1 | PASS |
| V12 | MMS time order theta=0.5 | |p - 2| | 2.187e-02 | 0.1 | PASS |
| V13 | global energy conservation theta=0.5 (flux+Dirichlet+source) | |dE - Q| / scale | 3.814e-14 | 1e-10 | PASS |
| V13 | global energy conservation theta=0.5 (flux+Robin+source) | |dE - Q| / scale | 3.568e-14 | 1e-10 | PASS |
| V13 | global energy conservation theta=1.0 (flux+Dirichlet+source) | |dE - Q| / scale | 4.874e-14 | 1e-10 | PASS |
| V13 | global energy conservation theta=1.0 (flux+Robin+source) | |dE - Q| / scale | 4.175e-14 | 1e-10 | PASS |
| V14 | Incropera Ex. 5.1: junction diameter D (book 0.706 mm) | rel err | 1.666e-04 | 0.005 | PASS |
| V14 | Incropera Ex. 5.1: time to 199 C (book 5.2 s) | abs err s | 3.521e-02 | 0.05 | PASS |
| V15 | baseline grid convergence T_wall_K | GCI_fine | 3.625e-06 | 0.001 | PASS |
| V15 | baseline grid convergence T_mean_K | GCI_fine | 1.808e-10 | 0.001 | PASS |
| V16 | baseline time-step convergence T_wall | GCI_fine | 1.210e-10 | 0.001 | PASS |
| V17 | baseline T_wall vs semi-infinite closed form | |err| K | 1.261e-03 | 0.05 | PASS |
| V17 | baseline T_mean vs q t/(rho c H) | |err| K | 2.985e-05 | 0.01 | PASS |

## Observed order of accuracy

| Test | Expected | Observed (least squares) | Pairwise |
|---|---|---|---|
| V10 lumped, implicit Euler | 1 | 1.0529 | 1.0873, 1.0479, 1.0251 |
| V10 lumped, Crank–Nicolson | 2 | 1.9983 | 1.9960, 1.9990, 1.9998 |
| V11 MMS space, L_inf | 2 | 1.9995 | 1.9981, 2.0003, 1.9997 |
| V11 MMS space, L_2 | 2 | 2.0003 | 2.0006, 2.0002, 2.0000 |
| V12 MMS time, implicit Euler | 1 | 0.9940 | 0.9889, 0.9949, 0.9979 |
| V12 MMS time, Crank–Nicolson | 2 | 1.9781 | 1.9729, 1.9695, 1.9949 |

## Richardson extrapolation and GCI for the Fan baseline (t = 10 s)

| Quantity | Solutions (fine, medium, coarse) | Observed p | Extrapolated | GCI_fine | Asymptotic ratio |
|---|---|---|---|---|---|
| T_wall, grid 512/256/128 | 434.8061, 434.8023, 434.7872 K | 2.0003 | 434.80737 K | 3.62e-06 | 1.0000087 |
| T_mean, grid 512/256/128 | 319.0721, 319.0721, 319.0721 K | 2.0047 | 319.072067 K | 1.81e-10 | 1.0000000 |
| T_wall, time step (r = 2) | 434.8061057, 434.8061052, 434.8061050 K | 2.0006 | 434.806105 K | 1.21e-10 | 1.0000000 |

Numerical uncertainty of the baseline wall temperature is therefore ~0.002 K (GCI 3.6e-6 relative), far below the
1–2 % comparison tolerances. Closed forms: T_wall = 300 + (2q/k)sqrt(alpha t/pi) = 434.8074 K
(semi-infinite; the top boundary at 80 mm is ~6 diffusion lengths away), T_mean = 300 + q t/(rho c H) = 319.0721 K.

## References

- Carslaw, H.S. & Jaeger, J.C. (1959) *Conduction of Heat in Solids*, 2nd ed., Oxford (§2.9, §3.3).
- Incropera, F.P., DeWitt, D.P., Bergman, T.L. & Lavine, A.S. (2007) *Fundamentals of Heat and Mass Transfer*, 6th ed., Wiley (Ch. 3; Eqs. 5.6, 5.57, 5.58; Example 5.1).
- Roache, P.J. (1994) Perspective: a method for uniform reporting of grid refinement studies. *J. Fluids Eng.* 116:405–413.
- Roache, P.J. (1998) *Verification and Validation in Computational Science and Engineering*, Hermosa.
- Roache, P.J. (2002) Code verification by the method of manufactured solutions. *J. Fluids Eng.* 124:4–10.
- Salari, K. & Knupp, P. (2000) Code verification by the method of manufactured solutions. Sandia SAND2000-1444.
- Celik, I.B. et al. (2008) Procedure for estimation and reporting of uncertainty due to discretization in CFD applications. *J. Fluids Eng.* 130:078001.
- ASME V&V 20-2009, *Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer*.

## Limitations of this verification

- Covers linear conduction with the BC types implemented; T-dependent properties, radiation and advection are not
  implemented and therefore not verified.
- V14 is a lumped benchmark (exercises `thermal1d.lumped`, not the PDE solver); PDE benchmarks are the analytic cases V5–V8.
- The full suite uses SciPy's banded solver; the NumPy Thomas fallback is checked against a dense solve (unit test) only.
- No validation against measurements.

## What thermal1d can and cannot be compared to

- **Can:** any conduction-dominated 1-D problem; the flow-off (EHD-off, no gravity) limit of the Fan legacy-air300 thermal
  case — compared with OpenFOAM's EHD-off control in `results/COMPARISON.md` (B1).
- **Cannot:** the EHD-on case (ionic wind advects heat out of the domain), buoyant cases, or anything where the plate
  temperature varies strongly along the wall. Such comparisons are reported only as bounds (B2) and must not be cited as
  an independent second-engine confirmation.
