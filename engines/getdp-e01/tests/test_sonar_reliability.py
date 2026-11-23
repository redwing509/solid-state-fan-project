"""Tests for the SonarCloud Reliability findings on PR #13 (t1296u).

These lock the fixes that failed the Quality Gate (Reliability Rating on
New Code): shell:S7688 in the runners, regex backtracking smells in the
table parsers, and float equality in check_e01.py. A1/A2 frozen numbers
must stay unchanged.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import pytest

E01 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E01))
import check_e01 as ce  # noqa: E402
import check_known as ck  # noqa: E402

# Pattern SonarCloud flagged as super-linear (python:S5852-class).
BACKTRACKING_FLOAT = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"
PARSER_FILES = [
    E01 / "check_e01.py",
    E01 / "check_known.py",
    E01 / "check_uni.py",
    E01 / "check_verify.py",
]
RUNNERS = [
    E01 / "run_e01.sh",
    E01 / "run_verify.sh",
]
OUT = E01 / "results" / "verify"

# Frozen official scores from a0ae277 / mail (bands not moved).
FROZEN_A1_ENERGY_PCT = 0.0007468228228065037
FROZEN_A1_V_PCT = 0.00016503783919588502
FROZEN_A2_I_PCT = 0.3295068433958895
FROZEN_A2_I_MEAN = [
    6.888718348211323e-05,
    6.782031007714363e-05,
    6.803515005094431e-05,
]


def _code_without_comments(line: str) -> str:
    # Bash: strip an unquoted # comment. Good enough for these short runners.
    return line.split("#", 1)[0]


def _single_bracket_or_test_lines(text: str):
    issues = []
    for i, line in enumerate(text.splitlines(), 1):
        code = _code_without_comments(line)
        cleaned = code.replace("[[", " ").replace("]]", " ")
        if re.search(r"(^|[\s;|&])test(\s|$)", cleaned) or re.search(
            r"(^|[\s;|&])\[\s", cleaned
        ):
            issues.append((i, line))
    return issues


def test_runners_use_double_brackets_not_test_or_single_brackets():
    """shell:S7688 — use [[ ]] instead of [ ] or test."""
    found = {}
    for path in RUNNERS:
        issues = _single_bracket_or_test_lines(path.read_text())
        if issues:
            found[path.name] = issues
    assert found == {}, found


def test_check_e01_does_not_test_current_with_float_equality():
    """python:S1244 — I != 0.0 (and == 0.0) must not remain in check_e01.py."""
    src = (E01 / "check_e01.py").read_text()
    assert "I != 0.0" not in src
    assert "I == 0.0" not in src
    assert re.search(r"\bI\s*!=\s*0(\.0)?\b", src) is None
    assert re.search(r"\bI\s*==\s*0(\.0)?\b", src) is None


def test_parsers_do_not_use_backtracking_float_regex():
    for path in PARSER_FILES:
        src = path.read_text()
        assert BACKTRACKING_FLOAT not in src, path.name
        # Any remaining findall of a digit-alternative float pattern is a miss.
        assert not re.search(
            r"re\.findall\(\s*r?['\"]\[-\+\]\?\(\?:\\d\+", src
        ), path.name


def test_floats_in_matches_old_regex_on_official_tables():
    import getdp_tables as gt

    samples = list(OUT.glob("cap_*/energy.dat"))
    samples += list(OUT.glob("cap_*/v_probe.dat"))
    samples += list(OUT.glob("uni_*/e_probe.dat"))
    samples += list(OUT.glob("uni_*/r_probe.dat"))
    samples += list(OUT.glob("uni_*/Q_rho.dat"))
    assert samples, "official verify tables should be present"
    for path in samples:
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            old = [float(x) for x in re.findall(BACKTRACKING_FLOAT, line)]
            assert gt.floats_in(line) == old, (path, line)


def test_floats_in_covers_signs_and_scientific_forms():
    import getdp_tables as gt

    line = "15 288114  -0.03 +.5 0  1.  .25  -4.5e-6 1e+3 0.3173943293338931"
    got = gt.floats_in(line)
    old = [float(x) for x in re.findall(BACKTRACKING_FLOAT, line)]
    assert got == old
    assert -0.03 in got
    assert 0.5 in got
    assert 1.0 in got
    assert 0.25 in got
    assert got[-3] == pytest.approx(-4.5e-6)
    assert got[-2] == pytest.approx(1000.0)


def test_node_count_reads_gmsh_mesh_info():
    import getdp_tables as gt

    for tag, n in (("f1", 13187), ("f0p5", 51113), ("f0p25", 202934)):
        text = (OUT / f"cap_{tag}" / "mesh_info.txt").read_text()
        assert gt.node_count(text) == n
        assert ck._nodes(OUT / f"cap_{tag}" / "mesh_info.txt") == n


def test_usable_current_rejects_zero_without_float_equality():
    assert ce.usable_current(8.226752e-05) is True
    assert ce.usable_current(-8.226752e-05) is True
    assert ce.usable_current(0.0) is False
    assert ce.usable_current(1e-30) is False
    assert ce.usable_current(None) is False
    assert ce.usable_current(math.inf) is False
    assert ce.usable_current(math.nan) is False


def test_one_marks_zero_contour_current_not_finite(tmp_path):
    (tmp_path / "ctr_e.dat").write_text(
        "1 1  5e-5 0 0  0 0 0  0 0 0\n"
        "1 1  0 5e-5 0  0 0 0  0 0 0\n"
    )
    (tmp_path / "ctr_r.dat").write_text(
        "1 1  5e-5 0 0  0 0 0  0\n"
        "1 1  0 5e-5 0  0 0 0  0\n"
    )
    rec = ce.one(tmp_path)
    assert rec["I_contour"] == pytest.approx(0.0, abs=1e-18)
    assert rec["finite"] is False


def test_A1_and_A2_frozen_reported_errors_unchanged():
    report = ck.score(OUT)
    assert report["known_solution_pass"]
    cap = report["capacitor"][-1]
    uni = report["unipolar"][-1]
    assert cap["rel_energy"] * 100 == pytest.approx(FROZEN_A1_ENERGY_PCT, rel=0, abs=1e-18)
    assert cap["rel_v"] * 100 == pytest.approx(FROZEN_A1_V_PCT, rel=0, abs=1e-18)
    assert uni["rel_I_mean"] * 100 == pytest.approx(FROZEN_A2_I_PCT, rel=0, abs=1e-18)
    assert [r["I_mean"] for r in report["unipolar"]] == pytest.approx(FROZEN_A2_I_MEAN)
