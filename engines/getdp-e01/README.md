# GetDP E-01 third-engine known-solution check

Gmsh 4.15.2 + GetDP 3.5.0 verification of the fixed-injection unipolar formulation against analytic coaxial solutions (James t1244u / build-queue Q-01).

- Method and pre-registered pass rules: `METHOD.md`
- Results (A1 and A2 **PASS**; finest unipolar current error 0.330%): `RESULTS.md`
- Official scorer: `check_known.py`
- Tests: `tests/test_known_solution.py`, `tests/ACCEPTANCE.md`
- Inputs: `verify/`, `unipolar.pro`
- Solver runner (mail or vps3 `/opt/fan-tools`, nice 19): `run_verify.sh`

This is model-only numerical verification. It is not a fan, corona, airflow, or commercial result. Fan PUSH=0 is the default; this branch is pushed only under James t1301u after the full review set, and merging needs his yes. The project owner reviews evidence before any inclusion. The Fan job-ownership warning is unchanged; do not disturb running `fan-grokbot-*` OpenFOAM containers.

The Nov 1 wire–plate study (steps B and C) is done: frozen ≤ 5% rule **PASS** against OpenFOAM on the identical domain (every mesh within 0.25%; Richardson 8.212437e-05 A/m is the frozen scoring statistic only). A supplemental fourth mesh gives a converged weak current of 8.221e-05 A/m (about ±0.1% mesh error), −0.069% from OpenFOAM and +0.035% from box FV. Passed after the backward-Euler start-up fix and an A2 re-verification. Runner: `run_e01.sh` (`SRC=study`); scorer: `check_e01.py`; tests: `tests/test_wireplate.py`. See `RESULTS.md`.
