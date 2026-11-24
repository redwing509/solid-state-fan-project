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
# the runs; the bands come from METHOD.md and were frozen at efe4a2f (211787b before the rebase).
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


# Review follow-ups (Claude r1 findings 5/6, CodeRabbit r1 majors 2/3).
def _fake_mesh(d: Path, I: float, steps: int = 600):
    """Write a minimal settled mesh directory with a uniform radial current."""
    import math
    d.mkdir(parents=True)
    el, rl = [], []
    for k in range(37):
        th = -math.pi / 2 + math.pi * k / 36
        x, y = ce.RP * math.cos(th), ce.RP * math.sin(th)
        E = 1e6
        rho = I / (math.pi * ce.RP * ce.MU * E)
        el.append(f"15 1  {x} {y} 0  0 0 0   {E*math.cos(th)} {E*math.sin(th)} 0")
        rl.append(f"15 1  {x} {y} 0  0 0 0   {rho}")
    (d / "ctr_e.dat").write_text("\n".join(el) + "\n")
    (d / "ctr_r.dat").write_text("\n".join(rl) + "\n")
    (d / "monitor_I.dat").write_text("".join(f" 0 {I}\n" for _ in range(steps)))


def _a2_ok(monkeypatch, ok=True):
    monkeypatch.setattr(ce, "a2_r2_pass", lambda *_a, **_k: ok)


def test_scorer_requires_expected_step_count(tmp_path):
    _fake_mesh(tmp_path / "wp_f1", 8.2e-5, steps=300)
    assert ce.one(tmp_path / "wp_f1")["settled"] is False


def test_scorer_fails_when_a_requested_mesh_is_missing(tmp_path, monkeypatch):
    _a2_ok(monkeypatch)
    _fake_mesh(tmp_path / "wp_f1", 8.30e-5)
    _fake_mesh(tmp_path / "wp_f0p25", 8.22e-5)
    rep = ce.score(tmp_path, ["f1", "f0p5", "f0p25"])
    assert rep["e01_pass"] is False
    assert rep["missing"] == ["f0p5"]


def test_scorer_requires_a2_reverification(tmp_path, monkeypatch):
    for t, f in (("f1", 1.010), ("f0p5", 1.004), ("f0p25", 1.002)):
        _fake_mesh(tmp_path / f"wp_{t}", f * ce.I_OF)
    _a2_ok(monkeypatch, True)
    assert ce.score(tmp_path, ["f1", "f0p5", "f0p25"])["e01_pass"] is True
    _a2_ok(monkeypatch, False)
    assert ce.score(tmp_path, ["f1", "f0p5", "f0p25"])["e01_pass"] is False


def test_oscillatory_study_needs_every_mesh_in_band(tmp_path, monkeypatch):
    """CodeRabbit r1 example: (1.029, 1.059, 1.049) * I_OF must not pass."""
    _a2_ok(monkeypatch)
    for t, f in (("f1", 1.029), ("f0p5", 1.059), ("f0p25", 1.049)):
        _fake_mesh(tmp_path / f"wp_{t}", f * ce.I_OF)
    rep = ce.score(tmp_path, ["f1", "f0p5", "f0p25"])
    assert rep["oscillatory"] is True
    assert rep["e01_pass"] is False


def test_official_a2_r2_gate_passes_on_saved_files():
    assert ce.a2_r2_pass(VERIFY_R2) is True


def test_runner_clears_all_old_outputs_before_solve():
    src = (E01 / "run_e01.sh").read_text()
    assert "rm -f monitor_" in src
    for name in ("ctr_e.dat", "ctr_r.dat", "I_vol.dat", "Q_rho.dat"):
        assert name in src.split("--- Unipolar solve ---", 1)[1].split("nice -n 19", 1)[0], name


# Review r2 follow-ups (Claude r2 findings 1-3).
def _fake_a2(root: Path, means, steps=600):
    for t, m in zip(("f1", "f0p5", "f0p25"), means):
        d = root / f"uni_{t}"
        d.mkdir(parents=True)
        for r in ce.A2_SAMPLES:
            (d / f"I_r{r}.dat").write_text(f"15 1  0.01 0 0  0 0 0   {m}\n")
        (d / "monitor_I.dat").write_text("".join(f" 0 {m}\n" for _ in range(steps)))


def test_a2_gate_requires_apparent_order(tmp_path):
    ex = ce.A2_EXACT
    _fake_a2(tmp_path / "bad", [ex * 1.001, ex * 1.005, ex * 1.004])
    assert ce.a2_r2_pass(tmp_path / "bad") is False
    _fake_a2(tmp_path / "good", [ex * 1.016, ex * 1.0001, ex * 1.0033])
    assert ce.a2_r2_pass(tmp_path / "good") is True


def test_summary_records_expected_steps(tmp_path, monkeypatch):
    _a2_ok(monkeypatch)
    _fake_mesh(tmp_path / "wp_f1", 8.2e-5, steps=1200)
    rep = ce.score(tmp_path, ["f1"], expected_steps=1200)
    assert rep["expected_steps"] == 1200


def test_tags_must_run_coarse_to_fine_by_halving(tmp_path, monkeypatch):
    _a2_ok(monkeypatch)
    for t, f in (("f1", 1.010), ("f0p5", 1.004), ("f0p25", 1.002)):
        _fake_mesh(tmp_path / f"wp_{t}", f * ce.I_OF)
    assert ce.score(tmp_path, ["f0p25", "f0p5", "f1"])["e01_pass"] is False
    assert ce.score(tmp_path, ["f1", "f1", "f0p25"])["e01_pass"] is False
    assert ce.score(tmp_path, ["f1", "f0p5", "f0p25"])["e01_pass"] is True


def test_runner_removes_old_laplace_guess_before_presolve():
    src = (E01 / "run_e01.sh").read_text()
    pre = src.split('echo "--- Laplace pre-solve ---"', 1)[1].split("nice -n 19", 1)[0]
    assert "rm -f v_init.pos" in pre


# Review r3 follow-ups (CodeRabbit r3, Claude r3 low).
def test_halving_order_directly():
    assert ce.halving_order(["f1", "f0p5", "f0p25"])
    assert ce.halving_order(["f0p5", "f0p25", "f0p125"])
    assert not ce.halving_order(["f1", "f0p25", "f0p5"])
    assert not ce.halving_order(["f1", "f1", "f0p5"])
    assert not ce.halving_order(["f1", "fnan", "f0p25"])


def test_empty_a2_sample_file_is_rejected_not_raised(tmp_path):
    ex = ce.A2_EXACT
    _fake_a2(tmp_path, [ex * 1.016, ex * 1.0001, ex * 1.0033])
    (tmp_path / "uni_f0p5" / "I_r002.dat").write_text("\n  \n")
    assert ce.a2_r2_pass(tmp_path) is False


def test_nan_final_field_in_a2_sample_is_rejected(tmp_path):
    ex = ce.A2_EXACT
    _fake_a2(tmp_path, [ex * 1.016, ex * 1.0001, ex * 1.0033])
    (tmp_path / "uni_f0p25" / "I_r002.dat").write_text(
        f"15 1  0.01 0 0  0 0 0   {ex * 1.25} nan\n")
    assert ce.a2_r2_pass(tmp_path) is False


def test_settle_window_is_the_last_0p01_s_for_any_step_count(tmp_path):
    """dt check (1200 steps): the window must cover 200 steps, not 100."""
    d = tmp_path / "wp_f1"
    _fake_mesh(d, 8.2e-5, steps=1200)
    vals = [1.02 * 8.2e-5] * 1099 + [8.2e-5] * 101
    (d / "monitor_I.dat").write_text("".join(f" 0 {v}\n" for v in vals))
    assert ce.one(d, expected_steps=1200)["settled"] is False
