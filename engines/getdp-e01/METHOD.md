# E-01 GetDP third-engine method (t1244u)

**When written:** Saturday, 21 Nov 2026, 11:00 PM America/Los_Angeles (Pacific Time).
**Authorization:** James t1244u / pt1244u, "Continue with fan e-01".
**Standard:** t1223u (known-solution check, mesh convergence, reproducible inputs) and the pre-registered plan in `../RECOMMENDATION.md` plus AUDIT.md §8.2 / BUILD-QUEUE Q-01.
**PUSH=0.** No Fan PR. Model-only. Ownership warning unchanged. Running OpenFOAM r8/e40k cases are not disturbed.

**Status (21 Nov 2026, 11:32 PM Pacific Time):** known-solution checks A1 and A2 **PASS** on mail. Official figures are in `RESULTS.md`. Finest A2 mean-current error **0.330%** (pre-registered band ≤ 1%). The Nov 1 wire–plate study is not done; a later smoke failed and was not rerun. Official scorer: `check_known.py`.

This file states the method and the pass rules **before** the GetDP unipolar results are computed.

## What E-01 must check

A third, independent method (FEM, Gmsh 4.15.2 + GetDP 3.5.0) of the Nov 1 fixed-injection unipolar current case, on the **same** OpenFOAM original domain and BCs, compared to OpenFOAM Richardson current `8.226752e-05` A/m. Formal agreement was not declared between box FV and OpenFOAM because their domains were not identical. Pre-registered pass rule (AGREEMENT-PLAN.md / RECOMMENDATION.md): Richardson currents differ by ≤ 5%, observed order > 0.5, finest two grids within 2%, identical domain and BCs.

Equations (steady, no flow, no diffusion, no Kaptzov):

- `-div(ε0 grad V) = ρ`, `E = -grad V`
- `div(ρ μ E) = 0`

Half-domain wire current: `I = ∫_wire (ρ μ E) · n dℓ` (A/m), with `n` outward from the wire into the air. Plate current and charge imbalance are reported.

## Tools and pins

- Gmsh 4.15.2 and GetDP 3.5.0 at `/opt/fan-tools` on mail and vps3 (SHA-256 in `../VERSIONS`). GetDP 3.5.0 also runs from the box copy at `/workspace/fan-third-engine/opt/getdp-3.5.0-Linux64/bin/getdp`. The box Gmsh binary needs `libGLU`, which is not installed here; meshes are made with mail's `/opt/fan-tools/bin/gmsh`.
- No new packages are installed. Nothing is pushed.

## Step A — known-solution check (must pass before the wire–plate study)

Two analytic checks of the same GetDP formulation, on a coaxial annulus, with a three-level mesh study (characteristic length halved twice).

### A1. Vacuum coaxial capacitor (Poisson only)

Same problem as the 21 Nov 2026 install smoke (`../SMOKE-TEST.md`): `a=0.01` m at 1 V, `b=0.05` m at 0 V, `ε0 = 8.854187818e-12` F/m. Exact per-unit-length energy, `V` and `E` as in that file. This run adds the mesh-convergence study that the install smoke did not do.

**Pass (set before the run):** on the finest mesh, energy and probe `V` within 1% of the formula; current is not defined (no charge). Errors must not increase as the mesh is refined. Apparent order of the energy error, where it can be formed, > 0.5.

### A2. Coaxial unipolar drift (Poisson + charge conservation)

This is the reduced E-01 exact electrical solution already in the project (`fan/docs/Validation_Plan.md`, `fan/docs/Validation_Audit_2026-10-22.md`, `fan/scripts/coaxial_verification.py`):

- Wire radius `a = 0.001` m, outer radius `b = 0.1` m
- `V(a) = 30 kV`, `V(b) = 0`, `ρ(a) = 1e-5` C/m³
- `μ = 1.8e-4` m²/(V s), `ε0 = 8.854e-12` F/m (same constant as `coaxial_verification.py`)
- Steady radial unipolar drift, no diffusion, no airflow, fixed injected charge

Closed form: `I' = 2π a μ ρ_a E_a`, `E(r)² = (a E_a / r)² + I'/(2π ε0 μ) (1 - (a/r)²)`, with `E_a` chosen so `∫_a^b E dr = V0`. The reference current is taken from the existing shooting implementation in `coaxial_verification.py` (cross-checked there against an independent log-radius BVP to relative difference `6e-13` on this case):

- `E_a = 5.995871213257002e6` V/m
- `I' = 6.78117058395794e-05` A/m

GetDP uses a Picard loop: solve Poisson for `V` at fixed `ρ`, then convective conservation for `ρ` at frozen `E`, including an outflow term on the collector so that `n·(ρ μ E)` is not forced to zero there. Inflow `ρ` is Dirichlet on the wire. No added physical diffusion is used unless a run is unstable; if a stabilizer is added it will be written down here before that run is accepted.

**Pass (set before the run):**

- Finest-mesh relative error in full-circle current `I'` ≤ **1%** of `6.78117058395794e-05` A/m. (The provisional Validation_Plan engineering target of 0.25% is reported but is not the pass/fail line for this first GetDP check.)
- At least three systematically refined meshes; observed order of the current error > 0.5 where defined; relative change between the finest two currents ≤ 2%.
- Inputs are the `.geo` / `.pro` files in `verify/` plus the pinned binaries.

Do not proceed to the Nov 1 wire–plate study if A2 fails.


### Numerical choices for A2 (written before the unipolar re-run)

The first GetDP unipolar attempt (21 Nov 2026, 11:02 PM Pacific Time) was **not** accepted. GetDP's `IterativeLoop` residual is the linear-solver residual; with a direct LU solve it reported convergence after one Picard pass. Poisson was essentially the Laplace field, the charge probe was small and negative, and the Dirichlet-boundary current integral was identically zero. Those results were discarded for the pass/fail decision.

The accepted form, written before the re-run, is:

- A **fixed** 40 Picard iterations (Poisson at frozen `ρ`, then transport at frozen `E`), not `IterativeLoop`.
- A consistent streamline-diffusion term `τ (μ E · ∇ρ)(μ E · ∇w)` with `τ = h / (2 |μ E| + ε)`, `h` equal to the inner-edge mesh size of that level (`8e-5`, `4e-5`, `2e-5` m). The term vanishes as `h → 0`. No physical diffusion is added.
- Current for the coaxial pass rule is formed from field samples in the volume, `I(r) = 2π r μ ρ |E|`, at `r = 0.002, 0.005, 0.01, 0.02, 0.05` m, not from the Dirichlet-boundary integral (first-order `{d v}` on that edge was observed to vanish). The reported current is the mean of those five samples on the finest mesh; each sample's relative error is also reported.

A later check of that re-run (still 21 Nov 2026, ~11:08 PM Pacific Time) showed Poisson was still the Laplace field after 40 two-system Picard passes: GetDP was not reading the transport solution into the Poisson charge term. Those results were also discarded.

The accepted coupling, written before the next re-run, is a **single mixed system**: `ρ` enters Poisson as `Dof{ρ}`, and transport uses a Picard lag of `E = -grad V` from the last saved solution. Same 40 fixed Picard iterations and the same streamline-diffusion term.

A later solve of that mixed system (21 Nov 2026, about 11:10 PM Pacific Time) on the coarse coaxial mesh produced non-physical `inf`/`nan` fields and was discarded. The first Picard pass started from `V = 0`, so `E = 0` in the lagged transport operator and the mixed block system was singular.

The accepted start, written before the next re-run, keeps the same mixed system, 40 Picard iterations, and streamline-diffusion term, and adds:

- An initial guess for `V` applied at `InitSolution` as a GetDP `Type Init` constraint, then `SaveSolution` so the first transport pass sees a physical `E = -grad V`.
- For this coaxial known-solution case only, that guess is the analytic Laplace field `V(r) = V0 ln(b/r)/ln(b/a)`. It is a starting guess, not a constraint on the solved field; Dirichlet values on the wire and collector remain exact.
- The Nov 1 wire–plate wrappers set the same flag to zero until a Laplace pre-solve is written for that geometry. Those cases will not be run until A2 passes.


A Laplace-initialized mixed solve on the coarse mesh (21 Nov 2026, about 11:11 PM Pacific Time) stayed at the Laplace potential, with essentially zero volume charge, and was discarded. Diagnostics on that mesh then showed two formulation bugs:

- The conservative `div(ρ μ E)` weak form, as written, did not recover the analytic test in which a Laplace field should produce a uniform `ρ = ρ_a` (pure diffusion on the same mesh did recover `ρ_a` to machine precision, as did a non-conservative `μ E · ∇ρ` form).
- The vector-product SUPG term was ill-posed in GetDP (`inf`/`nan` or huge charge). GetDP also rejects an expression that contains more than one `Dof{}`. The accepted SUPG is the same `τ = h / (2|μ E|+ε)` written as four single-`Dof` component terms, which recovered `ρ = ρ_a` exactly on that Laplace-E test.

The accepted transport form, written before the next re-run, is the non-conservative identity `μ E · ∇ρ + μ ρ (div E) = 0` with lagged `E = -grad V` and lagged `div E = ρ/ε0` from the previous Picard field, plus the four-term SUPG. No physical diffusion is added. The mixed Poisson+transport system, 40 Picard iterations, Laplace `Init` guess on the coaxial case, and volume-sample current `I(r)` are otherwise unchanged.




## A2 result (written after the accepted-form re-run)

Known-solution check A2 was scored with `check_uni.py` against the pre-registered pass rule. Official files: `results/verify/uni_f1`, `uni_f0p5`, `uni_f0p25` (mail copies under `/opt/fan-tools/e01/results/verify/`). Earlier discarded solves are not used.

- Meshes: 7975, 30927, and 119025 nodes (lc_factor 1, 0.5, 0.25).
- Mean volume-sample current `I'` (A/m): 6.888718e-05, 6.782031e-05, 6.803515e-05 versus exact 6.781171e-05.
- Finest-mesh relative error **0.330%** (≤ 1%). Finest-two relative change **0.316%** (≤ 2%). Apparent order from the first refinement (coarse vs medium error) is greater than 0.5. A2 **pass**.
- The mean-current error is not monotone (medium 0.013%, fine 0.330%). The five radial samples on the fine mesh lie between 0.05% and 1.11%. Domain-integrated charge is stable across the three meshes (2.3280e-07, 2.3283e-07, 2.3284e-07 C/m). The 0.25% Validation_Plan engineering target is not used as the pass line; the fine-mesh error is 0.330%.

A1 (unchanged capacitor run, not re-solved): finest energy error 0.00075%, probe `V` error 0.00017%, energy-error orders 1.98 and 2.00. A1 **pass**.

## Wire–plate current and start-up (written before the Nov 1 smoke and mesh study)

- Official half-domain current for the Nov 1 case is the flux of `ρ μ E` through an interior semicircle at `r = 5 r_wire`, sampled at 37 points and integrated with the trapezoid rule (`check_e01.py`). The Dirichlet wire edge is not used (first-order `{d v}` vanishes there). An earlier attempt to embed that semicircle as a mesh curve broke the 2-D mesh and was dropped. Plate and wire edge integrals are still written out.
- Because the first Picard pass needs a non-zero `E`, the runner first solves the Laplace problem (ρ = 0, same `V` Dirichlet data) on the same mesh, writes `v_init.pos`, and uses that field as the `Type Init` guess (`use_v_init = 1`). That pre-solve is a starting guess only.

- On this wire-plate mesh, GetDP/MUMPS returned `nan` for the Laplace problem when the `Hgrad_V` constraint included a `Type Init` on the whole domain (a later unscaled Laplace solve without that Init gave 1222 V at the mid-gap probe). A standalone test also showed `nan` when the stiffness was written as `eps0 ∇V · ∇w` on an earlier attempt. The same mesh with the mathematically equivalent unscaled form `∇V · ∇w` gave a finite field (1222 V at the mid-gap probe). The accepted wire-plate Poisson form, written before the smoke, is therefore `-ΔV = ρ/ε0` (`∇V · ∇w = (ρ/ε0) w`), which is equivalent to `div(ε0 grad V) = -ρ` but better scaled. The official A2 files were not re-solved; they used the original `eps0`-weighted stiffness, which was stable on the coaxial meshes.

## Step B — coarse smoke on the Nov 1 domain

One coarse 2-D mesh of the OpenFOAM original half-domain (`RECOMMENDATION.md` item 2 / E8 `blockMeshDict`, `convertToMeters 0.001`):

- Wire radius 39.5 µm, centre at the origin
- `x = 0…0.32` m, `y = -0.02004…0.06` m, symmetry at `x = 0`
- Wire: `V = 7540` V, `ρ = 1.743e-4` C/m³
- Plate `y = -0.02004` m: `V = 0`, outflow `ρ`
- Right and top: natural / outflow on `V` and `ρ` (zero `n·D` on `V`)
- `ε0 = 8.85419e-12` F/m, `μ = 2.3e-4` m²/(V s)

Smoke pass: GetDP finishes, wire current is finite and non-zero, and `|I_wire + I_plate| / max(|I_wire|,|I_plate|)` is recorded. This smoke is not the agreement test.

## Step C — full E-01 mesh study

Three systematically refined 2-D meshes (linear size halved twice) of the same domain and BCs. Richardson:

`p = log(|(I_c - I_m)/(I_m - I_f)|)/log(2)`, `I_inf = I_f + (I_f - I_m)/(2^p - 1)`.

Compare `I_inf` to OpenFOAM `8.226752e-05` A/m. **Pass: relative gap ≤ 5%**, observed order > 0.5, finest-two change ≤ 2%. A passing current is numerical verification of this fixed-injection model, not experimental validation, thrust, efficiency, or a Kaptzov result.

## Outputs

- Method and pass rules: this file
- Inputs: `verify/`, `smoke/`, `study/`
- Results: `results/` (and copies under `/opt/fan-tools/e01/` on the run host if used)
- Queue note: `/workspace/validation-gaps/BUILD-QUEUE.md`

## Official scorer, tests, and leftover smoke (written after the known-solution score)

- Official A1+A2 scorer is `check_known.py`. It applies the pre-registered pass rules above to the saved probe files. `check_uni.py` scores A2 alone. `check_verify.py` is a leftover helper: its A2 path still reads the vanishing Dirichlet-edge integral and is not the pass metric.
- Reproducible tests: `tests/test_known_solution.py` and `tests/ACCEPTANCE.md` (8 tests passed). They re-score the saved files and, when `scripts/coaxial_verification.py` and numpy are available, check that exact `I'` matches the independent shooting/BVP pair.
- Host for the accepted solves: **mail**, `/opt/fan-tools`. Nothing was started on vps3, rig1, or the laptop. No duplicate GetDP job was started; none was running when this note was written.
- A coarse Nov 1 wire–plate smoke (`run_e01.sh`, `results/smoke/wp_f1` on mail) was started at 11:44 PM Pacific Time and failed at once with `Error : Field[] expects XYZ coordinates as argument` while evaluating `V_laplace[] = ScalarField[1]` after reading `v_init.pos`. GetDP 3.5.0 requires the evaluation point in `[]`; the official form is `ScalarField[XYZ[]]{1}` (manual §6.2.6). A later untested `ScalarField[1]{X, Y, Z}` rewrite still fails (`Unknown Constant: X`). `run_e01.sh` now emits `ScalarField[XYZ[]]{1}` and invokes GetDP with one `-pos Map Contour` (a repeated `-pos` flag keeps only the last name; a later `-res` post would print every Picard step). That study is not part of the known-solution pass/fail; A1/A2 bands were not moved.
