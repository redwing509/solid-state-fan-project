"""Coaxial reduced electrical model tests. Tolerances: tests/coaxial/ACCEPTANCE.md (pre-stated)."""
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("coaxial_verification", ROOT / "scripts" / "coaxial_verification.py")
cv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cv)

PUBLISHED = json.loads((ROOT / "results" / "coaxial-electrical" / "coaxial_verification.json").read_text())
CASES = [(c["electrode_voltage_V"], c["injected_charge_C_m3"], c["ion_mobility_m2_V_s"]) for c in PUBLISHED["cases"]]
BASE = (30000.0, 1e-5, 1.8e-4)


@pytest.fixture(scope="module")
def rows():
    return {(v, q, m): cv.compare(v, q, m) for v, q, m in CASES}


def test_case_count():
    assert len(CASES) == 36


@pytest.mark.parametrize("case", CASES, ids=lambda c: f"{c[0]/1e3:.0f}kV-{c[1]:.1e}-{c[2]:.1e}")
def test_C1_shooting_vs_bvp(rows, case):
    r = rows[case]
    assert r["relative_current_error"] < 1e-4
    assert r["relative_field_L2_error"] < 1e-4
    assert r["relative_potential_L2_error"] < 1e-4
    assert r["passed"]


def test_C2_regression_vs_published(rows):
    worst = 0.0
    for c in PUBLISHED["cases"]:
        r = rows[(c["electrode_voltage_V"], c["injected_charge_C_m3"], c["ion_mobility_m2_V_s"])]
        for k in ("shooting_current_A_per_m", "bvp_current_A_per_m"):
            worst = max(worst, abs(r[k] - c[k]) / abs(c[k]))
    assert worst <= 1e-8, worst


def test_C3_space_charge_free_limit():
    v = 30000.0
    r = cv.compare(v, 1e-14, 1.8e-4)
    laplace = v / (cv.A * math.log(cv.B / cv.A))
    assert abs(r["shooting_emitter_field_V_m"] - laplace) / laplace <= 1e-6


@pytest.mark.parametrize("case", [BASE, (10000.0, 2e-5, 2.3e-4), (40000.0, 0.5e-5, 1.5e-4)])
def test_C4_closed_form_first_integral(case):
    v, q, m = case
    sol, length = cv.solve_log_radius_bvp(v, q)
    t = np.linspace(0, length, 401)
    y = sol.sol(t)[1]
    k = sol.p[0]
    y_exact = np.sqrt(y[0] ** 2 + k * (np.exp(2 * t) - 1.0))
    assert np.max(np.abs(y - y_exact) / y_exact) <= 1e-6


def _shooting_current(v, q, m):
    return cv.compare(v, q, m)["shooting_current_A_per_m"]


def mesh_study(case=BASE, meshes=(11, 21, 41, 81, 161)):
    v, q, m = case
    ref = _shooting_current(v, q, m)
    out = []
    for n in meshes:
        # tol stays tight so scipy's inner Newton tolerance (scaled by tol) is tight; max_nodes=n refuses refinement
        sol, _ = cv.solve_log_radius_bvp(v, q, n_mesh=n, tol=1e-9, bc_tol=1e-11, max_nodes=n, allow_max_nodes=True)
        assert sol.x.size == n, "solver inserted nodes; study is not on a fixed mesh"
        out.append(dict(n=n, current=cv.bvp_current_from_solution(sol, v, m),
                        rel_err=abs(cv.bvp_current_from_solution(sol, v, m) - ref) / ref))
    e = [o["rel_err"] for o in out]
    p = math.log((e[-3]) / (e[-2])) / math.log(2.0) if e[-2] > 0 else float("inf")
    p_fine = math.log((e[-2]) / (e[-1])) / math.log(2.0) if e[-1] > 0 else float("inf")
    return out, p, p_fine, ref


def test_C5_fixed_mesh_convergence():
    out, p, p_fine, _ = mesh_study()
    e = [o["rel_err"] for o in out]
    assert all(e[i + 1] < e[i] for i in range(len(e) - 1)), e
    # observed order on the finest triplet (Celik: p from the three finest meshes);
    # here computed from errors vs the shooting reference
    assert min(p, p_fine) >= 3.5 or e[-1] < 1e-12, (p, p_fine, e)
    assert e[-1] <= 1e-8, e


def test_C6_tolerance_sweep():
    v, q, m = BASE
    ref = _shooting_current(v, q, m)
    errs = {}
    for tol in (1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9):
        sol, _ = cv.solve_log_radius_bvp(v, q, tol=tol)
        errs[tol] = abs(cv.bvp_current_from_solution(sol, v, m) - ref) / ref
    assert all(errs[t] <= 1e-4 for t in errs if t <= 1e-6), errs
    assert errs[1e-9] <= errs[1e-3], errs


def test_C7_initial_mesh_independence():
    v, q, m = BASE
    cur = []
    for n in (50, 100, 200, 400):
        sol, _ = cv.solve_log_radius_bvp(v, q, n_mesh=n)
        cur.append(cv.bvp_current_from_solution(sol, v, m))
    assert (max(cur) - min(cur)) / np.mean(cur) <= 1e-9, cur
