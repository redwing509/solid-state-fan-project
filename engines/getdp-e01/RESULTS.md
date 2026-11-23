# E-01 GetDP known-solution results (t1244u)

**Host:** mail (`/opt/fan-tools/bin/{gmsh,getdp}`, Gmsh 4.15.2, GetDP 3.5.0).  
**When scored:** Saturday, 21 Nov 2026, 11:32 PM America/Los_Angeles (Pacific Time), after the accepted A2 re-run finished on mail. Official small result files were also copied to the box at `/workspace/fan-third-engine/e01/results/verify/`.  
**Authorization:** James t1244u. **PUSH=0.** No Fan PR. Model-only. Ownership warning unchanged. Running Fan r8 (mail) and e40k (vps3) jobs were left alone.

Pass rules were written in `METHOD.md` before the accepted unipolar re-run was scored. Official scorer: `check_known.py`. Tests: `tests/test_known_solution.py` (8 passed).

## A1. Vacuum coaxial capacitor — PASS

Exact energy `1.728320874489e-11` J/m, probe `V` `0.317393805514` V (same formulas as `../SMOKE-TEST.md`).

| Mesh | Nodes | Energy rel. error | Probe `V` rel. error |
|---|---:|---:|---:|
| lc_factor 1 | 13,187 | 0.0118% | 0.00128% |
| lc_factor 0.5 | 51,113 | 0.00298% | 0.000795% |
| lc_factor 0.25 (finest) | 202,934 | **0.000747%** | **0.000165%** |

Apparent order of the energy error: 1.98 then 2.00. Finest energy and `V` are well under the 1% band; errors decrease under refinement.

## A2. Coaxial unipolar drift — PASS

Exact current `I' = 6.78117058395794e-05` A/m (shooting solution in `scripts/coaxial_verification.py`; BVP agrees to relative difference `6e-13`). Reported current is the mean of five volume samples `I(r) = 2π r μ ρ |E|`.

| Mesh | Nodes | Mean `I'` (A/m) | Rel. error vs exact |
|---|---:|---:|---:|
| lc_factor 1 | 7,975 | 6.888718e-05 | 1.586% |
| lc_factor 0.5 | 30,927 | 6.782031e-05 | 0.0127% |
| lc_factor 0.25 (finest) | 119,025 | 6.803515e-05 | **0.330%** |

Finest-mesh error **0.330%** (≤ 1%). Finest-two relative change **0.316%** (≤ 2%). Apparent order from the first refinement is greater than 0.5. The mean-current error is not monotone (medium 0.013%, fine 0.330%). The five radial samples on the fine mesh lie between 0.05% and 1.11%. Domain-integrated charge is stable (2.3280e-07, 2.3283e-07, 2.3284e-07 C/m). The 0.25% Validation_Plan engineering target is not the pass line.

**Known-solution check: PASS.**

## What this does not cover

The Nov 1 wire–plate GetDP comparison to OpenFOAM `8.226752e-05` A/m (METHOD.md steps B and C, Q-01 F-4 agreement test, pre-registered ≤ 5% current rule) is **not** done. A coarse smoke was started on mail at 11:44 PM Pacific Time and failed immediately with `Error : Field[] expects XYZ coordinates as argument` while evaluating `V_laplace[] = ScalarField[1]` (GetDP 3.5.0 needs the point in `[]`, official form `ScalarField[XYZ[]]{1}`). That process is not running. `run_e01.sh` is corrected to emit `ScalarField[XYZ[]]{1}` and to pass `-pos Map Contour` in one invocation. Known-solution A1/A2 do not use `GmshRead`/`ScalarField` and are unchanged. Bands were not moved.

## Reproducing the score

From this directory, with the saved probe files in `results/verify/`:

```
python3 check_known.py results/verify
python3 -m pytest -q tests/test_known_solution.py
```

Re-solving the meshes needs Gmsh 4.15.2 and GetDP 3.5.0 (`run_verify.sh`, nice 19) on a host that already has `/opt/fan-tools`. Do not start a duplicate if a verify or smoke job is already running.

# E-01 Nov 1 wire–plate third-engine result (t1300u)

**Host:** the box (8 CPU), `nice 19`, the same pinned binaries as mail (`getdp` SHA-256 `a357510b…2fcd`, `gmsh` `9dccade5…2c7f`, identical to `/opt/fan-tools/bin` on mail). No Fan runner slot on mail or vps3 was used; running OpenFOAM jobs were not touched.
**When:** wire–plate study 22 Nov 2026, 11:01:51–11:24:25 PM Pacific Time (`results/logs-r2/`); A2 re-verification finished 23 Nov 2026, 12:38 AM Pacific Time.
**Rules:** written in `METHOD.md` ("Wire–plate start-up fix and study rules") and committed at `efe4a2f` (11:01:42 PM; the same commit was `211787b` before the rebase onto `e29696f`, with an identical `engines/getdp-e01` tree) before any scored run. Bands were not moved.

## Why the earlier wire–plate run was rejected

`study-t1277u` on mail (22 Nov 2026, 6:46 PM Pacific Time) ended rc=0 but was never scored. Its domain charge alternated between about `9.1e-14` and `4.46e-6` C/m on every other Picard step (a period-2 limit cycle of the lagged reaction term), and step 40 landed on the collapsed branch (`I_contour ≈ 1e-16` A/m). Re-scored with `check_e01.py` it fails. The accepted fix adds the backward-Euler time term `(ρ − ρ_prev)/Δt`, which vanishes at steady state.

## Rule 1 — A2 re-verified with the changed formulation: PASS

`results/verify-r2/`, 600 steps of `Δt = 1e-4` s, every mesh settled (`I_vol` change over the last 100 steps ≤ 5e-13).

| Mesh | Nodes | Mean `I'` (A/m) | Rel. error vs exact `6.78117058395794e-05` |
|---|---:|---:|---:|
| lc_factor 1 | 7,975 | 6.888718e-05 | 1.586% |
| lc_factor 0.5 | 30,927 | 6.782031e-05 | 0.0127% |
| lc_factor 0.25 | 119,025 | 6.803515e-05 | **0.330%** |

Identical to the frozen plain-Picard A2 (relative difference < 1e-9), as expected when the time term cancels at steady state. Finest-two change 0.316%. The independent weak current `I_vol` on the finest mesh is 6.781317e-05 A/m (0.002% from exact).

## Rules 2 and 3 — wire–plate study: PASS

`results/study-r2/`, OpenFOAM original half-domain (`x = 0…0.32` m, `y = −0.02004…0.06` m, symmetry at `x = 0`), wire 39.5 µm at 7540 V and `ρ = 1.743e-4` C/m³, plate at 0 V, natural/outflow right and top, `μ = 2.3e-4`, `ε0 = 8.85419e-12`. Same BCs and domain as OpenFOAM.

| Mesh | Nodes | `I_contour` at r = 5 r_w (A/m) | `I_vol` (A/m) | Domain charge (C/m) | Settle change (last 100 steps) |
|---|---:|---:|---:|---:|---:|
| lc_factor 1 | 2,297 | 8.238091e-05 | 8.200263e-05 | 9.4353e-08 | 1.8e-05 |
| lc_factor 0.5 | 8,670 | 8.206228e-05 | 8.224772e-05 | 9.4164e-08 | 1.8e-05 |
| lc_factor 0.25 | 33,671 | 8.211425e-05 | 8.221098e-05 | 9.4123e-08 | 1.8e-05 |

- Richardson `I_inf` = **8.212437e-05 A/m**; observed order 2.62; finest-two change 0.063%. This is the frozen scoring statistic. The supplemental fourth mesh below (contour 8.218815e-05, above this value) shows the extrapolation is **not** a valid continuum estimate; it is superseded for reporting by the converged weak current, and only the pass/fail verdict rests on it.
- Gap to OpenFOAM `8.226752e-05`: **−0.174%** (rule ≤ 5%). Gap to box FV `8.218217e-05` (infinite half-plane, context only): −0.070%.
- Convergence is **oscillatory** (coarse→medium down, medium→fine up). Richardson is therefore only indicative. Every mesh is within 0.25% of OpenFOAM, and the full three-mesh range is 0.39%, so the verdict does not depend on the extrapolation.
- On the finest mesh the contour current and the independent weak current differ by 0.12%.
- The settle column refers to the near-wire current `I_vol` (rule 2). The total domain charge is still rising slowly at `t = 0.06` s (about +0.47% to +0.51% over the last 100 steps on each mesh) because far-field ions are still filling the slow-drift corners. That is the same sample time as OpenFOAM. The wire current has settled (`I_vol` change 1.8e-5; the `Δt` check agrees to 3.4e-7).
- Scorer gates (added after review r1, stricter only): `e01_pass` also requires the A2 r2 gate (`a2_r2_pass`), exactly 600 monitored steps on each mesh, every requested mesh present, and, because convergence is oscillatory, every mesh inside the same 5% band (max mesh gap 0.249%). Re-score unchanged: PASS.
- **Frozen E-01 rule: PASS.** Scorer: `python3 check_e01.py results/study-r2` (writes `E01_SUMMARY.json`).

## Rule 4 — time-step check (coarse mesh, reported only)

`Δt = 5e-5` s, 1200 steps (`results/dtcheck-r2/`, wrapper `results/dtcheck-r2/wireplate-dt5e-5.pro`, which differs from `study/wireplate.pro` only in `n_steps = 1200` and `inv_dt = 2.0e4`; run in a scratch copy of this tree and copied in; score with `python3 check_e01.py --steps 1200 results/dtcheck-r2 f1`): `I_contour` 8.238094e-05 vs 8.238091e-05, relative difference 3.4e-7 (≤ 0.5%).

## What this is and is not

Three independent numerical methods (box finite-volume, OpenFOAM finite-volume, GetDP finite-element) now give the Nov 1 fixed-injection unipolar half-domain current within about 0.25% of each other on every GetDP mesh (see the supplemental section for the converged estimate). GetDP and OpenFOAM used an identical domain and BCs. This is numerical verification of the fixed-injection model only. It is not experimental validation, a Kaptzov/Peek corona-onset result, thrust, airflow, or efficiency. A supplemental fourth mesh is reported below; it is not part of the rule.

## Supplemental fourth mesh (lc_factor 0.125, outside the frozen rule)

`results/study-r2-extra/wp_f0p125` (132,230 nodes, 600 steps, settled; box, nice 19, 22 Nov 2026 11:25:59 PM to 23 Nov 2026 1:01:41 AM Pacific Time, per `results/logs-r2/wp_0.125.log`). Same inputs and scorer.

| Mesh | `I_contour` (A/m) | `I_vol` (A/m) |
|---|---:|---:|
| lc_factor 1 | 8.238091e-05 | 8.200263e-05 |
| lc_factor 0.5 | 8.206228e-05 | 8.224772e-05 |
| lc_factor 0.25 | 8.211425e-05 | 8.221098e-05 |
| lc_factor 0.125 | 8.218815e-05 | 8.221054e-05 |

- The weak current `I_vol` is mesh-converged: the change from lc 0.25 to 0.125 is 0.0005%. Its converged value 8.2211e-05 A/m is −0.069% from OpenFOAM and +0.035% from box FV.
- The official point-sampled contour current is **not** in the asymptotic range. Its last three values rise with growing differences (apparent order negative), so a Richardson value from lc 0.5/0.25/0.125 is not meaningful. It stays within 0.25% of OpenFOAM on all four meshes (−0.096% on the finest), and it approaches the converged `I_vol` as the mesh is refined.
- So the frozen-rule PASS above stands. For reporting, the GetDP wire current is 8.221e-05 A/m from `I_vol`, the estimator that converged. `I_vol` was chosen as the reporting estimator after the data were seen; it is not the frozen official contour current.
- Its uncertainty is an **empirical estimate** of about ±0.1% for mesh error only, not a proven bound on the continuum error (the two estimators on the two finest meshes span 8.211425–8.221098e-05, a full width of 0.118%; both could share a larger common error). The independent anchors are the A2 known-solution check (0.330% contour-style, 0.002% weak current) and the other two engines. It excludes time-step error (the `Δt` check moved the contour by 3.4e-7) and does not mean the domain charge is steady (it still rises about 0.5% per 100 steps at `t = 0.06` s, OpenFOAM's sample time).
- On that basis the three values are OpenFOAM 8.226752e-05, GetDP 8.221054e-05 and box FV 8.218217e-05: a spread of 0.104%, set by OpenFOAM vs box FV, with GetDP between them. Box FV used an infinite half-plane, not the identical domain, so it is context only. Given GetDP's ±0.1%, the agreement is best stated as about 0.1–0.2%.
- Scorer record for this mesh: `results/study-r2-extra/E01_SUMMARY.json` (`python3 check_e01.py results/study-r2-extra f0p125`; a single mesh never scores a pass).
