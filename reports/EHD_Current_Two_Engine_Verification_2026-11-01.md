# EHD current two-engine verification (E-01, 2026-11-01)

**Scope.** Fixed-injection unipolar drift current on the wire–plate geometry (E-01), compared between an independent box finite-volume engine and OpenFOAM. This is a numerical verification of *integrated wire current per unit length on the half-domain*. It is **not** a thrust, airflow or efficiency result, **not** a performance gain, and **not** experimental validation. Electrode voltage is distinct from the 110/220/330/440 VAC supply inputs. Simulation is model-only.

**Tolerance (written in `AGREEMENT-PLAN.md` on 2026-11-01 at 8:45 PM PST, before further comparison).** Engines agree when Richardson-extrapolated wire current per unit length differs by <= 5%, both engines pass their analytic tests, both show mesh convergence (observed order > 0.5, finest two grids within 2%), and boundary conditions and domain are identical.

**Headline numbers (Nov 1 analysis, original OpenFOAM domain).** Box Richardson current 8.218217e-05 A/m; OpenFOAM Richardson current 8.226752e-05 A/m; gap **+0.104%**. After a refine-2 far-domain correction: OpenFOAM 8.234240e-05 A/m, gap **+0.195%**. Both are inside the 5% current band. Formal agreement under the pre-registered rule was **not** declared on Nov 1, because the domains were not identical (see below).

Sources for the headline: `analysis-2120/summary.txt` and the JSON it was built from (`analysis-2120/currents.json`, `fan-ehd-2nd-engine-20261101/result.json`). A machine-readable copy of those numbers is in `results/ehd-current-verification-20261101/summary.json`. Recompute: `python3 scripts/ehd_current_two_engine_verification.py` (exit 0 = recorded values reproduced).

## Engines (independent)

- *Box FV engine* (`ehd_bipolar.py`, job 240, 2026-11-01 5:57:17 PM PST). Finite-volume solution of Poisson + `div(rho * mu * E) = 0` with fixed `rho` at the wire, on a bipolar conformal grid, using numpy/scipy. Independent of OpenFOAM. The docstring records inputs copied from the mail corrected-baseline `job.json` / `0/*` / `blockMeshDict`: `V = 7540` V, `mu = 2.3e-4` m^2/(V s), `rho_wire = 1.743e-4` C/m^3, `r_wire = 39.5` um, plate `20.04` mm below the wire. Domain: infinite half-plane (`u = -TAU0` at the wire, `u = 0` at the plate, `v` in `(0, pi)` with Neumann symmetry walls). `eps0 = 8.8541878128e-12` F/m. The box run used `N = M` in `{50, 100, 200, 400}`; Richardson extrapolation uses the last three grids, as in the script. numpy/scipy package versions: NOT FOUND in the run record.

- *OpenFOAM 4.1* (`Build : 4.1` in `log.checkMesh`; dictionaries are labelled Version 4.x; container image `gpuq/fan-11-ehd-convergence:20261024`, environment `/opt/openfoam4`). Headline mesh series E2/E4/E8 used `ehdOnlyFoam`, an electrostatics-only build of `buoyantBoussinesqPimpleEHDFoam` with the PIMPLE flow loop removed (`mail-of/run_eonly.sh`). Charge transport in this solver is recorded there as `rhoFlux = -mobil*snGrad(phi)` and independent of `U`. Control runs C2/F2 used the full `buoyantBoussinesqPimpleEHDFoam` (`mail-of/run_agree.sh`). Fan-11 / corrected-baseline full-solver currents at `t = 10` s are the M1/M2/M4 entries in `currents.json` (same extraction method; M1 matches the `fan-ehd-ref` reference 7.226778e-05 A/m).

Current extraction for OpenFOAM is `analysis-2120/patchcur.py`, the same method as `fan-ehd-ref/extract.py`: face flux `curDens . Sf`, summed per patch and divided by z-depth `0.3` m, giving A/m. Wire current is `-hole`; plate current is `down`.

## Case setup (from the case files)

Geometry (`mail-of/bm` and `of-runs/out-eonly/E8/system/blockMeshDict`, `convertToMeters 0.001`):

- Wire radius 0.0395 mm (39.5 um). Collector plate at `y = -20.04` mm, `elecPot = 0`.
- Original OpenFOAM box: `x = 0` (patch `left`, `symmetryPlane`) to `x = 320` mm (`right`, `zeroGradient`); `y = -20.04` mm to `y = +60` mm (`up`, `zeroGradient`); spanwise depth `z = 300` mm (`depth_m = 0.3` in `currents.json`). This is a half-domain; the box engine is also a half-plane. A full-wire current would be twice these values; all numbers below are half-domain.
- Far-domain variant (`mail-of/mkfar.py`): the same wire/plate, outer box stretched to `x = 3200` mm and `y = +600` mm, with some block counts increased. Used only for the refine-2 domain correction (C2 vs F2).

Electrical boundary conditions (E4 time `0.06`, fields `elecPot` and `chargeDens`, consistent with the scripts):

- `hole` (wire): `elecPot` fixed 7540 V; `chargeDens` fixed 0.0001743 C/m^3.
- `down` (plate): `elecPot` fixed 0 V; `chargeDens` `zeroGradient`.
- `right` and `up`: `zeroGradient` on both fields.
- `left`: `symmetryPlane`.

Material properties (`out-eonly/E4/constant/EHDproperties`): `epsilon0 = 8.85419e-12`, `mobil = 0.00023` m^2/(V s).

Time discretisation for the E2/E4/E8 and C2/F2 short runs (`E2/system/controlDict` and `run_eonly.sh`): `deltaT = 2e-05` s, `adjustTimeStep no`, E-series `endTime = 0.06` s with writes every 0.02 s; C2/F2 continued to 0.1 s. Solver tolerances in the E2 `fvSolution` used for that series: `elecPot` and `chargeDens` absolute tolerance `1e-06` (final `relTol 0`).

Meshes (OpenFOAM original domain, `log.checkMesh`, Mesh OK):

| series | cells | role |
|---|---|---|
| base `mail-of/bm` (refine 1) | 4700 (from the hex sizes in `bm`) | starting `blockMeshDict`; M1 is this density at `t = 10` s |
| E2 / C2 | 18800 | refine 2, used in the Richardson set |
| E4 | 75200 | refine 4 |
| E8 | 300800 | refine 8 |

Far-domain refine 2 (F2 / GF2) has 32900 cells (`GF2/log.checkMesh`). Box engine grids are `N x M` cells in computational coordinates: 100, 200 and 400 on a side for the Richardson set (50 was also run and is reported, but not used in the extrapolation).

## Grid-convergence and the two-engine current comparison

Richardson extrapolation uses refinement ratio 2 and

`p = log(|(I_coarse - I_mid) / (I_mid - I_fine)|) / log(2)`

`I_inf = I_fine + (I_fine - I_mid) / (2^p - 1)`

as implemented in `ehd_bipolar.py`. `summary.txt` reports the OpenFOAM finest-two difference as 0.964% and the box as 0.111%. Those percentages match `100 * |I_fine - I_mid| / I_fine` on the rounded currents in that file.

### OpenFOAM, original domain, e-only, t = 0.06 s (`currents.json`, `summary.txt`)

| mesh | cells | I_wire (A/m) | I_plate (A/m) |
|---|---|---|---|
| E2 (refine 2) | 18800 | 7.859547575875263e-05 | 7.855149653292896e-05 |
| E4 (refine 4) | 75200 | 8.111873724384423e-05 | 8.107737519048302e-05 |
| E8 (refine 8) | 300800 | 8.190812961504308e-05 | 8.186985587440794e-05 |

- Observed order `p = 1.676`. Richardson `I_inf = 8.226752e-05` A/m. Finest-two difference 0.964% (under the 2% mesh-convergence band).
- E8 plate/wire imbalance 0.047%.
- Short e-only runs match the full-solver `t = 10` s controls: C2 at 0.1 s vs M2, relative difference 7.89e-07; E2 at 0.06 s vs M2, 2.75e-05; E4 at 0.06 s vs M4, 3.89e-05. E8 current changed by -5.61e-05 relatively from 0.04 s to 0.06 s.

The older coarse reference M1 at `t = 10` s is 7.226778e-05 A/m. That is 12.16% below the OpenFOAM Richardson value and 13.85% below the box N=400 current. The apparent +13.8% engine gap against M1 is therefore mostly OpenFOAM mesh error on the coarsest grid, not an engine disagreement. A three-level Richardson set that includes M1 (M1/M2/M4 at t = 10 s) gives a different `p = 1.326` and `I_inf = 8.278831e-05` A/m and is recorded in `summary.txt` only as a control; the headline OpenFOAM value uses E2/E4/E8 at 0.06 s.

### Box FV engine (`result.json`)

| N (= M) | I_wire (A/m) | I_plate (A/m) | charge-balance \|I_w-I_p\|/I_w | iterations |
|---|---|---|---|---|
| 50 | 8.289654357830299e-05 | 8.289653888709143e-05 | 5.66e-08 | 286 |
| 100 | 8.254712905417516e-05 | 8.254712375663017e-05 | 6.42e-08 | 300 |
| 200 | 8.236732520057252e-05 | 8.236731966071697e-05 | 6.73e-08 | 314 |
| 400 | 8.227610548117171e-05 | 8.227609960026789e-05 | 7.15e-08 | 327 |

- Richardson on N = 100/200/400: `p = 0.979`, `I_inf = 8.218217e-05` A/m. Finest-two difference 0.111%. Observed order is above the pre-registered 0.5 floor but is first-order, not second-order.
- Box GCI for this set: NOT FOUND (not computed in the Nov 1 files).

### Gap on the original OpenFOAM domain

`(I_OF_Rich - I_box_Rich) / I_box_Rich = +0.104%` (`summary.txt`: "Gap OF_Rich vs Box_Rich: +0.104%"). Recomputed from the JSON values: +0.103856%.

## Domain correction

The box engine is an infinite half-plane. OpenFOAM is a finite box with `zeroGradient` on the far faces. That mismatch was the reason for the correction.

At refine 2, C2 is the original 320 mm x 60 mm box and F2 is the 10x far domain (3200 mm x 600 mm). Using the currents in `currents.json` / `summary.txt`:

| time (s) | C2 I_wire (A/m) | F2 I_wire (A/m) | (F2/C2) - 1 |
|---|---|---|---|
| 0.06 | 7.859406624198424e-05 | 7.867173223983376e-05 | +0.0988% |
| 0.08 | 7.859354644005608e-05 | 7.866490984081711e-05 | +0.0908% |
| 0.10 | 7.859337963376164e-05 | 7.866490984081711e-05 | +0.0910% |

`summary.txt` records the domain effect as **+0.091%** (F2/C2 at refine 2, 10x far) and applies it to the original-domain Richardson value:

`8.226752e-05 * (F2 / C2)` at t = 0.1 s = **8.234240e-05** A/m.

That domain-corrected OpenFOAM value vs the box Richardson current is **+0.195%**.

F2's I_wire is identical at 0.08 s and 0.1 s. `summary.txt` and `AGREEMENT-PLAN.md` record that F2 stalled (`chargeDens` 0-iteration solves). The 9:55 PM PST plan entry therefore called the +0.09% domain estimate unreliable and kept "identical domain" as not met until a later far-domain series (agree3 / agree5) could be used. The +0.195% figure is the Nov 1 recorded correction, with that qualification.

## Formal agreement status on Nov 1

From `AGREEMENT-PLAN.md` (9:21 PM and 9:55 PM PST, and the 9:30 PM update), after these numbers were in hand:

1. Richardson current within 5%: met numerically (+0.10%, or +0.20% with the domain correction).
2. Analytic tests: box PASS (N=60 and N=120 after the T4 wire-face label fix in job 247). OpenFOAM Gauss low-charge test PASS at far-domain refine 8 (GF8 1.36530e-10 vs exact 1.37181e-10 A/m, -0.47%, tolerance 1%).
3. Mesh convergence: OpenFOAM PASS (`p = 1.68`, finest-two 0.96%); box PASS (`p = 0.98`, finest-two 0.11%).
4. Identical boundary conditions and domain: **not met** (finite box vs infinite half-plane; F2 stalled; H4/H8 then agree3 were still pending).

The plan's conclusion on Nov 1 was: engines do **not** yet formally agree under the pre-registered rule, and nothing was pushed. This write-up records the current comparison and that status. It does not reopen the formal agreement decision.

## Supporting context: agree5 OpenFOAM far-domain mesh study (not a two-engine comparison)

On 2026-11-08, OpenFOAM-only job `fan-agree5-20261105` reran the far-domain E-01 meshes at solver tolerance `1e-12` (`RESULT.md`, `SUMMARY_agree5.json`). All three meshes exited rc=0 at t = 0.06 s (`status.txt`: HT2 3893 s, HT4 26573 s, HT8 201773 s).

At t = 0.06 s (`SUMMARY_agree5.json` / `RESULT.md`):

| mesh | cells | I_wire |
|---|---|---|
| HT2 | 131600 | 8.120481613395171e-05 |
| HT4 | 526400 | 8.199640717392026e-05 |
| HT8 | 2105600 | 8.220753122306827e-05 |

- Richardson `I_inf = 8.22779059061176e-05` (reported in `RESULT.md` as 8.22779e-05 A). Observed order `p = 1.90666` (reported as 1.907). Finest-two change 0.257%. `RESULT.md` records GCI_fine with Fs = 1.25 as 0.117%, and says this meets a provisional <= 0.25% integrated-current target. Time settling from 0.04 s to 0.06 s is 0.056% on every mesh. Charge balance on HT8: plate/wire = 0.99858 (0.14% gap).

`RESULT.md` also records that this study and the earlier agree3 far-domain study (tolerance 1e-6) extrapolate to nearly the same current: agree5 `I_inf` 8.2278e-05 vs agree3 far 8.2223e-05, +0.07%.

**This agree5 series was not formally compared to the box engine.** No Nov 8 (or later) file in the agreement set records a box FV rerun, or a new box-vs-OpenFOAM gap, against the agree5 meshes or the 1e-12 tolerance. A side-by-side of the separately produced numbers — agree5 `I_inf` 8.22779059061176e-05 vs the Nov 1 box Richardson 8.21821717617474e-05 — is a relative difference of +0.117%. That arithmetic is not a completed two-engine agreement run.

## Limits

- Model-only numerical verification of *current*. Not thrust, not efficiency, not free-fan airflow, not a performance gain.
- Fixed injected wire charge; no corona-onset or Kaptzov condition in this comparison.
- Half-domain current per unit length (A/m in the Nov 1 files; agree5 labels the same class of extracted current as A).
- OpenFOAM and the box engine did not use identical far-field domains on Nov 1. The +0.195% figure uses a stalled refine-2 far run as a correction, which the Nov 1 plan itself marked as unreliable for closing the formal rule.
- Box observed order is about 1, not 2. Box GCI was not computed.
- Agree5 is OpenFOAM-only supporting context, not a second-engine check.
- No experimental measurement is cited.

## Source files

Nov 1 analysis (box copies under `/workspace/self-jobs/`):

- `fan-ehd-agree-20261101/analysis-2120/summary.txt`
- `fan-ehd-agree-20261101/analysis-2120/currents.json` (and `spec.json`, `patchcur.py`)
- `fan-ehd-agree-20261101/AGREEMENT-PLAN.md`
- `fan-ehd-2nd-engine-20261101/result.json`, `ehd_bipolar.py`, `run.log`
- `boxqueue/done/240-fan-ehd-second-engine-crosscheck.sh` and `boxqueue/logs/240-fan-ehd-second-engine-crosscheck.log`
- OpenFOAM case inputs: `mail-of/{bm,mkfar.py,run_eonly.sh,run_agree.sh,launch.sh}`, `out-eonly/E4/constant/EHDproperties`, `of-runs/out-eonly/E2/system/{controlDict,fvSolution}`, `of-runs/out-eonly/E8/system/blockMeshDict`, `of-runs/out-eonly/E{2,4,8}/log.checkMesh`, E4 `0.06/{elecPot,chargeDens}`
- Reference current write-up: `fan-ehd-ref/README.md`

Agree5 (mail, not copied into this PR as raw fields):

- `/opt/fan-research/fan-agree5-20261105/out/extract/RESULT.md`
- `/opt/fan-research/fan-agree5-20261105/out/extract/SUMMARY_agree5.json`
- `/opt/fan-research/fan-agree5-20261105/out/status.txt`
