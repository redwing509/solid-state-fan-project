# GetDP E-01 third-engine known-solution check

Gmsh 4.15.2 + GetDP 3.5.0 verification of the fixed-injection unipolar formulation against analytic coaxial solutions (James t1244u / build-queue Q-01).

- Method and pre-registered pass rules: `METHOD.md`
- Results (A1 and A2 **PASS**; finest unipolar current error 0.330%): `RESULTS.md`
- Official scorer: `check_known.py`
- Tests: `tests/test_known_solution.py`, `tests/ACCEPTANCE.md`
- Inputs: `verify/`, `unipolar.pro`
- Solver runner (mail or vps3 `/opt/fan-tools`, nice 19): `run_verify.sh`

This is model-only numerical verification. It is not a fan, corona, airflow, or commercial result. **PUSH=0.** No Fan PR until James asks. The project owner reviews evidence before any inclusion. The Fan job-ownership warning is unchanged; do not disturb running `fan-grokbot-*` OpenFOAM containers.

The Nov 1 wire–plate agreement study (steps B and C) is not complete. See `RESULTS.md`.
