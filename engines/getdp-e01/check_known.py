#!/usr/bin/env python3
"""Official A1+A2 known-solution scorer for GetDP E-01 (t1244u).

Pass rules are those pre-registered in METHOD.md, applied to saved GetDP
probe/energy files. A2 current is the mean of volume samples
I(r) = 2*pi*r*mu*rho*|E|, not the Dirichlet-edge integral (which vanishes
for first-order {d v} on this mesh).
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

I_EX = 6.78117058395794e-05
EA_EX = 5.995871213257002e6
MU = 1.8e-4
A, B, V0, RHOA, EPS0 = 0.001, 0.1, 30000.0, 1e-5, 8.854e-12
RADII = [("r002", 0.002), ("r005", 0.005), ("probe", 0.01), ("r02", 0.02), ("r05", 0.05)]

# A1: same constants as SMOKE-TEST.md / official GetDP eps0
EPS0_CAP = 8.854187818e-12
A_CAP, B_CAP, V0_CAP = 0.01, 0.05, 1.0
R_PROBE_CAP = 0.03
C_EX = 2 * math.pi * EPS0_CAP / math.log(B_CAP / A_CAP)
W_EX = 0.5 * C_EX * V0_CAP ** 2
V_PROBE_EX = V0_CAP * math.log(B_CAP / R_PROBE_CAP) / math.log(B_CAP / A_CAP)
E_PROBE_EX = V0_CAP / (R_PROBE_CAP * math.log(B_CAP / A_CAP))

TAGS = ["f1", "f0p5", "f0p25"]  # coarse -> fine


def E_exact(r, Ea=EA_EX):
    Ip = 2 * math.pi * A * MU * RHOA * Ea
    C = Ip / (2 * math.pi * EPS0 * MU)
    return math.sqrt((A * Ea / r) ** 2 + C * (1.0 - (A / r) ** 2))


def last_nums(path: Path):
    if not path.is_file():
        return []
    text = path.read_text().strip().splitlines()
    if not text:
        return []
    return [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", text[-1])]


def last_scalar(path: Path):
    n = last_nums(path)
    return n[-1] if n else None


def e_vec(path: Path):
    n = last_nums(path)
    if len(n) >= 9:
        return n[8], n[9], n[10] if len(n) > 10 else 0.0
    return None


def observed_order(e_coarse, e_fine, ratio=2.0):
    if e_coarse is None or e_fine is None or e_coarse <= 0 or e_fine <= 0:
        return None
    return math.log(e_coarse / e_fine) / math.log(ratio)


def score_capacitor(out: Path):
    rows = []
    for t in TAGS:
        d = out / f"cap_{t}"
        w = last_scalar(d / "energy.dat")
        v = last_scalar(d / "v_probe.dat")
        ev = e_vec(d / "e_probe.dat")
        ex = ev[0] if ev else None
        rows.append(dict(
            tag=t,
            nodes=_nodes(d / "mesh_info.txt"),
            energy=w,
            v_probe=v,
            ex_probe=ex,
            rel_energy=None if w is None else abs(w - W_EX) / W_EX,
            rel_v=None if v is None else abs(v - V_PROBE_EX) / V_PROBE_EX,
            rel_ex=None if ex is None else abs(ex - E_PROBE_EX) / E_PROBE_EX,
        ))
    reasons = []
    ok = True
    if any(r["rel_energy"] is None or r["rel_v"] is None for r in rows):
        ok = False
        reasons.append("missing capacitor energy or probe V")
        return rows, ok, reasons, None
    finest = rows[-1]
    if finest["rel_energy"] > 0.01:
        ok = False
        reasons.append(f"finest energy error {finest['rel_energy']*100:.4f}% > 1%")
    if finest["rel_v"] > 0.01:
        ok = False
        reasons.append(f"finest probe V error {finest['rel_v']*100:.4f}% > 1%")
    if finest["rel_energy"] > rows[0]["rel_energy"] * 1.01:
        ok = False
        reasons.append("energy error increased from coarsest to finest mesh")
    if finest["rel_v"] > rows[0]["rel_v"] * 1.01:
        ok = False
        reasons.append("probe V error increased from coarsest to finest mesh")
    p = observed_order(rows[0]["rel_energy"], rows[1]["rel_energy"])
    if p is not None and p <= 0.5:
        ok = False
        reasons.append(f"energy-error apparent order {p:.3f} <= 0.5")
    return rows, ok, reasons, p


def _nodes(path: Path):
    if not path.is_file():
        return None
    m = re.search(r"(\d+)\s+nodes", path.read_text())
    return int(m.group(1)) if m else None


def score_unipolar(out: Path):
    rows = []
    for t in TAGS:
        d = out / f"uni_{t}"
        samples = []
        for name, r in RADII:
            if name == "probe":
                ev, rv, vv = e_vec(d / "e_probe.dat"), last_scalar(d / "r_probe.dat"), last_scalar(d / "v_probe.dat")
            else:
                ev, rv, vv = e_vec(d / f"e_{name}.dat"), last_scalar(d / f"r_{name}.dat"), last_scalar(d / f"v_{name}.dat")
            if ev is None or rv is None:
                samples.append(dict(r=r, missing=True))
                continue
            emag = math.sqrt(ev[0] ** 2 + ev[1] ** 2 + ev[2] ** 2)
            I = 2 * math.pi * r * MU * rv * emag
            samples.append(dict(
                r=r, V=vv, rho=rv, Ex=ev[0], Ey=ev[1], Emag=emag,
                E_exact=E_exact(r), I=I, rel_I=abs(I - I_EX) / I_EX,
                rel_E=abs(emag - E_exact(r)) / E_exact(r),
            ))
        usable = [s for s in samples if not s.get("missing")]
        I_mean = sum(s["I"] for s in usable) / len(usable) if usable else None
        rows.append(dict(
            tag=t,
            nodes=_nodes(d / "mesh_info.txt"),
            Q_rho=last_scalar(d / "Q_rho.dat"),
            I_emitter_boundary=last_scalar(d / "I_emitter.dat"),
            I_mean=I_mean,
            rel_I_mean=None if I_mean is None else abs(I_mean - I_EX) / I_EX,
            samples=samples,
        ))
    reasons, ok = [], True
    if any(r["I_mean"] is None for r in rows):
        ok = False
        reasons.append("missing I_mean")
        return rows, ok, reasons, None, None
    finest = rows[-1]
    if finest["rel_I_mean"] > 0.01:
        ok = False
        reasons.append(f"finest mean current error {finest['rel_I_mean']*100:.3f}% > 1%")
    change = abs(rows[-1]["I_mean"] - rows[-2]["I_mean"]) / abs(rows[-1]["I_mean"])
    if change > 0.02:
        ok = False
        reasons.append(f"finest-two change {change*100:.3f}% > 2%")
    p = observed_order(rows[0]["rel_I_mean"], rows[1]["rel_I_mean"])
    if p is not None and p <= 0.5:
        ok = False
        reasons.append(f"apparent order {p:.3f} <= 0.5")
    elif p is None and rows[1]["rel_I_mean"] is not None and rows[0]["rel_I_mean"] is not None and rows[1]["rel_I_mean"] >= rows[0]["rel_I_mean"]:
        ok = False
        reasons.append("current error did not decrease on first refinement")
    return rows, ok, reasons, p, change


def score(out: Path):
    cap_rows, cap_ok, cap_reasons, cap_p = score_capacitor(out)
    uni_rows, uni_ok, uni_reasons, uni_p, uni_change = score_unipolar(out)
    report = dict(
        title="GetDP E-01 known-solution check (t1244u)",
        host="mail",
        tools="Gmsh 4.15.2 + GetDP 3.5.0 at /opt/fan-tools",
        exact_cap=dict(energy=W_EX, v_probe=V_PROBE_EX, e_probe=E_PROBE_EX, C=C_EX),
        exact_uni=dict(I_A_per_m=I_EX, Ea_V_m=EA_EX),
        pass_band=dict(
            a1_finest_energy_and_V=0.01,
            a2_finest_mean_current=0.01,
            a2_finest_two_change=0.02,
            min_apparent_order=0.5,
        ),
        capacitor=cap_rows,
        capacitor_pass=cap_ok,
        capacitor_reasons=cap_reasons,
        capacitor_order_first_refinement=cap_p,
        unipolar=uni_rows,
        unipolar_pass=uni_ok,
        unipolar_reasons=uni_reasons,
        unipolar_order_first_refinement=uni_p,
        unipolar_finest_two_change=uni_change,
        known_solution_pass=bool(cap_ok and uni_ok),
    )
    return report


def main():
    root = Path(__file__).resolve().parent
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "results" / "verify"
    report = score(out)
    (out / "SUMMARY.json").write_text(json.dumps(report, indent=2) + "\n")
    finest = report["unipolar"][-1] if report["unipolar"] else {}
    cap_f = report["capacitor"][-1] if report["capacitor"] else {}
    print(json.dumps({
        "known_solution_pass": report["known_solution_pass"],
        "capacitor_pass": report["capacitor_pass"],
        "unipolar_pass": report["unipolar_pass"],
        "A1_finest_energy_error_pct": None if not cap_f else cap_f["rel_energy"] * 100,
        "A1_finest_V_error_pct": None if not cap_f else cap_f["rel_v"] * 100,
        "A2_finest_mean_current_error_pct": None if not finest else finest["rel_I_mean"] * 100,
        "A2_I_mean": [r["I_mean"] for r in report["unipolar"]],
        "A2_rel": [r["rel_I_mean"] for r in report["unipolar"]],
        "capacitor_reasons": report["capacitor_reasons"],
        "unipolar_reasons": report["unipolar_reasons"],
    }, indent=2))
    sys.exit(0 if report["known_solution_pass"] else 1)


if __name__ == "__main__":
    main()
