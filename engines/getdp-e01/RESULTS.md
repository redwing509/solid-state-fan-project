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
