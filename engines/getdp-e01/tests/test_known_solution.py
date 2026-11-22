"""GetDP E-01 known-solution tests. Tolerances: tests/ACCEPTANCE.md and METHOD.md."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

E01 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E01))
import check_known as ck  # noqa: E402

OUT = E01 / "results" / "verify"
I_EX = ck.I_EX
EA_EX = ck.EA_EX

# Optional independent reference (present when this tree lives in the fan repo).
def _coaxial_verification():
    candidates = [
        E01.parents[1] / "scripts" / "coaxial_verification.py",  # engines/getdp-e01 in the fan repo
        Path("/workspace/fan/scripts/coaxial_verification.py"),
    ]
    for p in candidates:
        if p.is_file():
            try:
                import numpy  # noqa: F401
            except ImportError:
                return None
            spec = importlib.util.spec_from_file_location("coaxial_verification", p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None


def test_exact_current_matches_shooting_reference():
    cv = _coaxial_verification()
    if cv is None:
        pytest.skip("scripts/coaxial_verification.py not available")
    r = cv.compare(30000.0, 1e-5, 1.8e-4)
    assert r["shooting_current_A_per_m"] == I_EX
    assert r["shooting_emitter_field_V_m"] == EA_EX
    assert r["relative_current_error"] < 1e-10
    assert r["passed"]


def test_closed_form_field_at_wire_equals_Ea():
    assert ck.E_exact(ck.A) == pytest.approx(EA_EX, rel=0, abs=0)


def test_I_of_r_recovers_exact_current_on_the_analytic_field():
    # I(r) = 2*pi*r*mu*rho(r)*E(r) is constant and equals I' when rho and E are exact.
    # At the wire, rho = rho_a, E = Ea.
    I_wire = 2 * math.pi * ck.A * ck.MU * ck.RHOA * EA_EX
    assert I_wire == pytest.approx(I_EX, rel=1e-15)


def test_capacitor_exact_energy_matches_formula():
    assert ck.W_EX == pytest.approx(0.5 * ck.C_EX * ck.V0_CAP ** 2, rel=0, abs=0)
    assert ck.C_EX == pytest.approx(2 * math.pi * ck.EPS0_CAP / math.log(ck.B_CAP / ck.A_CAP), rel=0, abs=0)


def test_A1_and_A2_pass_pre_registered_band():
    report = ck.score(OUT)
    assert report["capacitor_pass"], report["capacitor_reasons"]
    assert report["unipolar_pass"], report["unipolar_reasons"]
    assert report["known_solution_pass"]
    cap = report["capacitor"][-1]
    uni = report["unipolar"][-1]
    assert cap["rel_energy"] <= 0.01
    assert cap["rel_v"] <= 0.01
    assert uni["rel_I_mean"] <= 0.01
    assert report["unipolar_finest_two_change"] <= 0.02
    assert report["capacitor_order_first_refinement"] > 0.5
    assert report["unipolar_order_first_refinement"] > 0.5


def test_A1_errors_do_not_grow_under_refinement():
    report = ck.score(OUT)
    e = [r["rel_energy"] for r in report["capacitor"]]
    v = [r["rel_v"] for r in report["capacitor"]]
    assert e[-1] <= e[0]
    assert v[-1] <= v[0]


def test_A2_fine_mesh_sample_errors_are_reported():
    report = ck.score(OUT)
    samples = report["unipolar"][-1]["samples"]
    assert len(samples) == 5
    assert all(not s.get("missing") for s in samples)
    # Documented: each fine-mesh sample is within 1.11% of exact I'.
    assert max(s["rel_I"] for s in samples) <= 0.012


def test_official_scorer_cli_exits_zero(tmp_path):
    import subprocess
    proc = subprocess.run(
        [sys.executable, str(E01 / "check_known.py"), str(OUT)],
        check=False, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "known_solution_pass" in proc.stdout
