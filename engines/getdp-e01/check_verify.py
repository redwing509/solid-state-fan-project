#!/usr/bin/env python3
"""Legacy helper. Official A1+A2 scorer is check_known.py (volume-sample current).

This file still reports capacitor energy/V and the Dirichlet-edge I_emitter,
which is identically zero on these first-order meshes and is not the pass metric.
"""
from __future__ import annotations
import json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "verify"

# A1 exact (SMOKE-TEST.md / official GetDP eps0)
EPS0_CAP = 8.854187818e-12
A_CAP, B_CAP, V0_CAP = 0.01, 0.05, 1.0
C_EX = 2 * math.pi * EPS0_CAP / math.log(B_CAP / A_CAP)
W_EX = 0.5 * C_EX * V0_CAP ** 2
V_PROBE_EX = V0_CAP * math.log(B_CAP / 0.03) / math.log(B_CAP / A_CAP)
E_PROBE_EX = V0_CAP / (0.03 * math.log(B_CAP / A_CAP))

# A2 exact from coaxial_verification.py shooting (METHOD.md)
I_EX = 6.78117058395794e-05
EA_EX = 5.995871213257002e6
# probe at r=0.01 m
def E_exact(r, Ea=EA_EX, a=0.001, mu=1.8e-4, rho_a=1e-5, eps0=8.854e-12):
    Ip = 2 * math.pi * a * mu * rho_a * Ea
    C = Ip / (2 * math.pi * eps0 * mu)
    return math.sqrt((a * Ea / r) ** 2 + C * (1.0 - (a / r) ** 2))
# V at 0.01 by integrating would need quad; we only require current for the pass line.

def last_number(path: Path):
    if not path.is_file():
        return None
    text = path.read_text().strip().splitlines()
    if not text:
        return None
    line = text[-1].strip()
    nums = re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", line)
    return float(nums[-1]) if nums else None

def probe_scalar(path: Path):
    # v_probe.dat: several columns, last is the value (see smoke)
    return last_number(path)

def probe_ex(path: Path):
    if not path.is_file():
        return None
    line = path.read_text().strip().splitlines()[-1]
    nums = [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", line)]
    # after coordinates, the vector Ex Ey Ez — take the first vector component if present
    # smoke: 15 18214  0.03 0 0  0 0 0   20.74 ...
    if len(nums) >= 9:
        return nums[8], (nums[9] if len(nums) > 9 else 0.0)
    if len(nums) >= 3:
        return nums[-3], nums[-2]
    return None

def order(e_coarse, e_fine, ratio=2.0):
    if e_coarse is None or e_fine is None or e_fine <= 0 or e_coarse <= 0:
        return None
    return math.log(e_coarse / e_fine) / math.log(ratio)

tags = ["f1", "f0p5", "f0p25"]  # coarse -> fine; lc_factor 1, 0.5, 0.25
# Wait: smaller lc_factor = finer mesh. f1 is coarsest, f0p25 finest.

cap = []
for t in tags:
    d = OUT / f"cap_{t}"
    w = last_number(d / "energy.dat")
    v = probe_scalar(d / "v_probe.dat")
    e = probe_ex(d / "e_probe.dat")
    ex = e[0] if e else None
    rec = dict(
        tag=t, dir=str(d),
        energy=w, v_probe=v, ex_probe=ex,
        rel_energy=None if w is None else abs(w - W_EX) / W_EX,
        rel_v=None if v is None else abs(v - V_PROBE_EX) / V_PROBE_EX,
        rel_ex=None if ex is None else abs(ex - E_PROBE_EX) / E_PROBE_EX,
        log_tail=(d / "getdp.log").read_text()[-1500:] if (d / "getdp.log").is_file() else None,
    )
    cap.append(rec)

uni = []
for t in tags:
    d = OUT / f"uni_{t}"
    iw = last_number(d / "I_emitter.dat")
    ic = last_number(d / "I_collector.dat")
    rec = dict(
        tag=t, dir=str(d),
        I_emitter=iw, I_collector=ic,
        rel_I=None if iw is None else abs(iw - I_EX) / I_EX,
        imbalance=None if not iw or not ic else abs(iw - ic) / max(abs(iw), abs(ic)),
        log_tail=(d / "getdp.log").read_text()[-2000:] if (d / "getdp.log").is_file() else None,
    )
    uni.append(rec)

# pass rules
cap_ok = all(r["rel_energy"] is not None and r["rel_energy"] <= 0.01
             and r["rel_v"] is not None and r["rel_v"] <= 0.01 for r in cap)
# errors must not increase (energy)
if cap and all(r["rel_energy"] is not None for r in cap):
    cap_ok = cap_ok and cap[-1]["rel_energy"] <= cap[0]["rel_energy"] * 1.01
cap_p = order(cap[0]["rel_energy"], cap[1]["rel_energy"]) if cap_ok and cap[0]["rel_energy"] and cap[1]["rel_energy"] else None
if cap_p is not None:
    cap_ok = cap_ok and cap_p > 0.5

uni_ok = True
reasons = []
if not uni or any(r["I_emitter"] is None for r in uni):
    uni_ok = False
    reasons.append("missing I_emitter on one or more meshes")
else:
    finest = uni[-1]
    if finest["rel_I"] > 0.01:
        uni_ok = False
        reasons.append(f"finest current error {finest['rel_I']*100:.3f}% > 1%")
    denom = abs(uni[-1]["I_emitter"])
    if denom == 0:
        uni_ok = False
        reasons.append("I_emitter is zero; use check_known.py volume-sample current")
        change = None
    else:
        change = abs(uni[-1]["I_emitter"] - uni[-2]["I_emitter"]) / denom
        if change > 0.02:
            uni_ok = False
            reasons.append(f"finest-two change {change*100:.3f}% > 2%")
    p = order(uni[0]["rel_I"], uni[1]["rel_I"])
    if p is not None and p <= 0.5:
        uni_ok = False
        reasons.append(f"apparent order {p:.3f} <= 0.5")
    elif p is None and uni[0]["rel_I"] and uni[1]["rel_I"] and uni[1]["rel_I"] >= uni[0]["rel_I"]:
        uni_ok = False
        reasons.append("current error did not decrease on first refinement")

report = dict(
    title="GetDP known-solution check (t1244u)",
    exact_cap=dict(energy=W_EX, v_probe=V_PROBE_EX, e_probe=E_PROBE_EX),
    exact_uni=dict(I_A_per_m=I_EX, Ea_V_m=EA_EX),
    capacitor=cap,
    unipolar=uni,
    capacitor_pass=cap_ok,
    unipolar_pass=uni_ok,
    unipolar_reasons=reasons,
    proceed_to_e01=bool(cap_ok and uni_ok),
)
(OUT / "SUMMARY.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
print(json.dumps({k: report[k] for k in ("capacitor_pass", "unipolar_pass", "proceed_to_e01", "unipolar_reasons")}, indent=2))
for r in cap:
    print("CAP", r["tag"], "relE", r["rel_energy"], "relV", r["rel_v"], "relEx", r["rel_ex"])
for r in uni:
    print("UNI", r["tag"], "I", r["I_emitter"], "relI", r["rel_I"], "imb", r["imbalance"])
sys.exit(0 if report["proceed_to_e01"] else 1)
