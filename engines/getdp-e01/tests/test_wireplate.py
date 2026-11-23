"""E-01 wire-plate start-up fix (t1300u): tests written before the fix.

The mail study-t1277u run alternated between a collapsed and a flooded
charge on every other Picard step. These tests lock the detector for that
limit cycle, the cancelling backward-Euler time term, and the runner hygiene.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

E01 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E01))
import check_e01 as ce  # noqa: E402

# Recorded domain charge (C/m) from the coarse mail/box run, steps 1..6.
PERIOD_TWO_Q = [7.607254213447046e-14, 4.464336211791412e-06,
                9.096295640290601e-14, 4.464292526579693e-06,
                9.09629569207903e-14, 4.464292558935927e-06] * 20


def test_monitor_settled_rejects_period_two_limit_cycle():
    ok, change = ce.monitor_settled(PERIOD_TWO_Q, window=100, tol=1e-3)
    assert not ok
    assert change > 1.0


def test_monitor_settled_accepts_a_converged_tail():
    tail = [8.2e-05 * (1 - 0.5 ** (k / 10)) for k in range(1, 601)]
    ok, change = ce.monitor_settled(tail, window=100, tol=1e-3)
    assert ok, change


def test_monitor_settled_rejects_short_or_nonfinite_series():
    assert not ce.monitor_settled([1.0] * 50, window=100, tol=1e-3)[0]
    assert not ce.monitor_settled([1.0] * 200 + [float("nan")], window=100, tol=1e-3)[0]


def _code(text: str) -> str:
    return "\n".join(ln.split("//", 1)[0] for ln in text.splitlines())


def test_unipolar_has_cancelling_backward_euler_terms():
    src = _code((E01 / "unipolar.pro").read_text())
    assert re.search(r"\[\s*inv_dt\s*\*\s*Dof\{r\}\s*,\s*\{r\}\s*\]", src)
    assert re.search(r"\[\s*-inv_dt\s*\*\s*\{r\}\s*,\s*\{r\}\s*\]", src)


def test_wrappers_set_time_step_and_step_count():
    for rel in ("study/wireplate.pro", "smoke/wireplate.pro", "verify/coaxial_unipolar.pro"):
        src = _code((E01 / rel).read_text())
        assert re.search(r"^inv_dt\s*=\s*1(\.0*)?e4;", src, re.M), rel
        assert re.search(r"^n_steps\s*=\s*600;", src, re.M), rel


def test_runner_clears_stale_monitor_files():
    for rel in ("run_e01.sh", "run_verify.sh"):
        assert "rm -f monitor_" in (E01 / rel).read_text(), rel


def test_oscillatory_convergence_is_flagged():
    assert ce.oscillatory(1.0, 2.0, 1.5)
    assert not ce.oscillatory(1.0, 1.5, 1.6)


# Official scored results (results/study-r2, results/verify-r2), written after
# the runs; the bands come from METHOD.md and were frozen at 211787b.
STUDY = E01 / "results" / "study-r2"
VERIFY_R2 = E01 / "results" / "verify-r2"


def _study_report():
    rows = [ce.one(STUDY / f"wp_{t}") for t in ("f1", "f0p5", "f0p25")]
    return rows


def test_official_wireplate_meshes_are_settled_600_steps():
    for rec in _study_report():
        assert rec["n_steps"] == 600, rec["dir"]
        assert rec["settled"], rec
        assert rec["n_pts"] == 37, rec["dir"]


def test_official_wireplate_study_passes_frozen_rule():
    import math
    Ic, Im, If_ = (r["I_contour"] for r in _study_report())
    p = math.log(abs((Ic - Im) / (Im - If_))) / math.log(2)
    Iinf = If_ + (If_ - Im) / (2 ** p - 1)
    assert abs(Iinf - ce.I_OF) / ce.I_OF <= 0.05
    assert p > 0.5
    assert abs(If_ - Im) / abs(If_) <= 0.02
    # Reported, not part of the rule: convergence is oscillatory.
    assert ce.oscillatory(Ic, Im, If_)


def test_contour_and_volume_currents_agree_on_finest_mesh():
    fin = _study_report()[-1]
    assert abs(fin["I_contour"] - fin["I_vol"]) / fin["I_contour"] < 0.005


def test_A2_reverified_with_changed_formulation():
    """Rule 1: A2 re-solved with the time term still passes the frozen band."""
    exact = 6.78117058395794e-05
    means = []
    for t in ("f1", "f0p5", "f0p25"):
        d = VERIFY_R2 / f"uni_{t}"
        vals = []
        for r in ("002", "005", "01", "02", "05"):
            lines = [ln for ln in (d / f"I_r{r}.dat").read_text().splitlines() if ln.strip()]
            vals.append(ce.floats_in(lines[-1])[-1])
        means.append(sum(vals) / len(vals))
        mon = ce.monitor_series(d / "monitor_I.dat")
        assert len(mon) == 600 and ce.monitor_settled(mon)[0], t
    assert abs(means[-1] - exact) / exact <= 0.01
    assert abs(means[-1] - means[-2]) / abs(means[-1]) <= 0.02
    # Same steady answer as the frozen plain-Picard A2 (time term cancels).
    for got, frozen in zip(means, (6.888718348211323e-05, 6.782031007714363e-05,
                                   6.803515005094431e-05)):
        assert abs(got - frozen) / frozen < 1e-9
