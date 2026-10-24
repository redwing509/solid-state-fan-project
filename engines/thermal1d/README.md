# thermal1d — Solid State Fan in-house 1-D transient conduction engine

**Verification status: code-verified to the project peer-review rule** (17 pre-registered tests, 34 checks, all pass —
see [VERIFICATION.md](VERIFICATION.md); tolerances were committed in [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md)
before any test was run). **Validation against experiment: none.** Code verification shows the equations are solved
correctly; it says nothing about whether conduction-only physics describes a real fan.

**Scope of the OpenFOAM cross-check (read this before citing it).** thermal1d is an independent second engine for the
*flow-off (pure conduction) limit* of the corrected legacy-air300 thermal case, and it agrees with OpenFOAM's EHD-off
control run within the pre-stated tolerances (B1 PASS). It is **not** a second engine for the EHD-driven case: with the
ionic wind on, heat is advected out of the domain and the two engines are expected to, and do, disagree (B2, reported
for information). See [results/COMPARISON.md](results/COMPARISON.md).

## Equations

    rho*c(x) dT/dt = d/dx( k(x) dT/dx ) + s(x,t),   x in [x0, xN],  t in (0, t_end]

Boundary conditions at either end: Dirichlet `T = T_b(t)`; prescribed inward heat flux `-k dT/dn = q(t)`
(Neumann, flux into the domain positive); convective (Robin) `-k dT/dn = h (T_inf - T)`.
A lumped-capacitance ODE `rho c V dT/dt = h A (T_inf - T)` is provided separately (`thermal1d.lumped`).

## Assumptions

- Conduction only: no advection, no radiation, no phase change; constant (or prescribed x-dependent) properties.
- One spatial dimension. Lateral boundaries of the modelled problem must be adiabatic and the source/boundary data
  uniform in the lateral direction (checked a posteriori in the cross-check via the OpenFOAM plate-temperature uniformity).
- For the Fan baseline: k = rho0*Cp0*nu/Pr, which is exactly what the OpenFOAM solver's laminar `alphaEff = nu/Pr` implies
  (0.02 W/m K, equal to the documented `kf`).

## Discretisation

- Vertex-centred finite volume on a (possibly non-uniform) node set; nodes on both boundaries; half control volumes at the
  ends. Face conductivity = k at the interval midpoint; nodal rho*c. Second order in space.
- theta-method in time: theta = 1 implicit Euler (first order), theta = 0.5 Crank–Nicolson (second order; default).
  Unconditionally stable for the linear problem.
- Tridiagonal system solved with `scipy.linalg.solve_banded` when SciPy is installed, else a NumPy Thomas algorithm
  (both covered by tests).
- Energy bookkeeping: boundary heat rates (Dirichlet heat flow from the discrete residual) are integrated with the same theta
  weighting, so the discrete energy balance closes to round-off (test V13).

## Boundary conditions used for the Fan baseline (`inputs/legacy_air300_corrected.json`)

| Fan / OpenFOAM patch | OpenFOAM BC | thermal1d |
|---|---|---|
| `down` heated plate, y = −20.04 mm | fixedGradient 9350 K/m | inward flux q = k·9350 = 187 W/m² at x = 0 |
| `up`, y = 60 mm | fixedValue 300 K | Dirichlet 300 K at x = H = 80.04 mm |
| `left` (symmetryPlane), `right` (zeroGradient) | — | adiabatic in the flow-off limit → 1-D |
| `hole` wire, r = 0.0395 mm | zeroGradient | neglected (adiabatic, area ratio ~1e-3) |

Initial T = 300 K, t_end = 10 s. Only documented case inputs are used; no OpenFOAM output field is read by the model.

## Limitations

- Cannot represent advection (ionic wind / EHD flow, buoyancy). Any result with flow is outside its scope; it is an upper
  bound on the plate temperature for an imposed-flux wall only if the flow removes heat.
- 1-D: no wire geometry, no lateral conduction, no edge effects.
- Linear only (no T-dependent properties, no radiation).
- Verified, not validated.

## Install and reproduce

    cd engines/thermal1d
    python -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt
    python -m pytest -v tests                 # full verification suite, ~30 s
    python -m thermal1d verify                # writes results/verification.json and prints the table
    python -m thermal1d baseline              # Fan corrected baseline, 1024 cells, dt 5e-4 s, CN
    python -m thermal1d compare               # cross-check vs stored OpenFOAM metrics -> results/comparison.json

Re-deriving the OpenFOAM metrics (needs the OpenFOAM case directories; mesh and fields are ASCII):

    python scripts/extract_openfoam_metrics.py <case_dir> 10 --k 0.02 --out results/openfoam/<name>_t10_metrics.json

Re-running the OpenFOAM EHD-off control (on the research host, same pinned image and resource limits as the corrected
baseline, under the `ai-job` lock): `scripts/run_openfoam_ehd_off_control.sh` (refuses to overwrite an existing output).

## Layout

    thermal1d/solver.py        FV theta-method solver (Problem, Boundary, solve, steady)
    thermal1d/analytic.py      closed-form references (Carslaw & Jaeger; Incropera)
    thermal1d/lumped.py        lumped capacitance (exact and theta-method)
    thermal1d/gci.py           Richardson extrapolation, GCI (Roache; Celik et al. 2008)
    thermal1d/verification.py  V1–V17 test cases
    thermal1d/baseline.py      Fan corrected baseline driver
    thermal1d/compare.py       OpenFOAM comparison with pre-stated tolerances
    tests/                     pytest wrappers (run in CI: .github/workflows/thermal1d.yml)
    inputs/                    documented case inputs
    results/                   verification.json, comparison.json, COMPARISON.md, openfoam/ (extracted metrics + run manifests)
    scripts/                   OpenFOAM metric extractor and EHD-off control launcher
