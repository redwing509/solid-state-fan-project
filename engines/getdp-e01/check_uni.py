#!/usr/bin/env python3
"""Coaxial unipolar current from volume samples I(r)=2*pi*r*mu*rho*|E| vs exact I'."""
from __future__ import annotations
import json, math, re, sys
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "results" / "verify"
I_EX = 6.78117058395794e-05
EA_EX = 5.995871213257002e6
MU = 1.8e-4
A, B, V0, RHOA, EPS0 = 0.001, 0.1, 30000.0, 1e-5, 8.854e-12
RADII = [("r002", 0.002), ("r005", 0.005), ("probe", 0.01), ("r02", 0.02), ("r05", 0.05)]

def E_exact(r, Ea=EA_EX):
    Ip = 2 * math.pi * A * MU * RHOA * Ea
    C = Ip / (2 * math.pi * EPS0 * MU)
    return math.sqrt((A * Ea / r) ** 2 + C * (1.0 - (A / r) ** 2))

def last_nums(path: Path):
    if not path.is_file():
        return []
    line = path.read_text().strip().splitlines()[-1]
    return [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", line)]

def last_scalar(path: Path):
    n = last_nums(path)
    return n[-1] if n else None

def e_vec(path: Path):
    n = last_nums(path)
    if len(n) >= 9:
        return n[8], n[9], n[10] if len(n) > 10 else 0.0
    return None

tags = ["f1", "f0p5", "f0p25"]
rows = []
for t in tags:
    d = OUT / f"uni_{t}"
    samples = []
    for name, r in RADII:
        if name == "probe":
            ev, rv = e_vec(d / "e_probe.dat"), last_scalar(d / "r_probe.dat")
            vv = last_scalar(d / "v_probe.dat")
        else:
            ev, rv = e_vec(d / f"e_{name}.dat"), last_scalar(d / f"r_{name}.dat")
            vv = last_scalar(d / f"v_{name}.dat")
        if ev is None or rv is None:
            samples.append(dict(r=r, missing=True))
            continue
        Emag = math.sqrt(ev[0]**2 + ev[1]**2 + ev[2]**2)
        I = 2 * math.pi * r * MU * rv * Emag  # signed via rho
        samples.append(dict(
            r=r, V=vv, rho=rv, Ex=ev[0], Ey=ev[1], Emag=Emag,
            E_exact=E_exact(r), I=I, rel_I=abs(I - I_EX) / I_EX,
            rel_E=abs(Emag - E_exact(r)) / E_exact(r),
        ))
    usable = [s for s in samples if not s.get("missing") and s["rho"] is not None]
    I_mean = sum(s["I"] for s in usable) / len(usable) if usable else None
    rows.append(dict(
        tag=t, Q_rho=last_scalar(d / "Q_rho.dat"),
        I_emitter_boundary=last_scalar(d / "I_emitter.dat"),
        I_mean=I_mean,
        rel_I_mean=None if I_mean is None else abs(I_mean - I_EX) / I_EX,
        samples=samples,
        log_has_for="For " in (d / "getdp.log").read_text() if (d / "getdp.log").is_file() else False,
    ))

reasons, ok = [], True
if any(r["I_mean"] is None for r in rows):
    ok = False
    reasons.append("missing I_mean")
else:
    finest = rows[-1]
    if finest["rel_I_mean"] > 0.01:
        ok = False
        reasons.append(f"finest mean current error {finest['rel_I_mean']*100:.3f}% > 1%")
    change = abs(rows[-1]["I_mean"] - rows[-2]["I_mean"]) / abs(rows[-1]["I_mean"])
    if change > 0.02:
        ok = False
        reasons.append(f"finest-two change {change*100:.3f}% > 2%")
    e0, e1 = rows[0]["rel_I_mean"], rows[1]["rel_I_mean"]
    if e0 and e1 and e1 > 0:
        p = math.log(e0 / e1) / math.log(2)
        if p <= 0.5:
            ok = False
            reasons.append(f"apparent order {p:.3f} <= 0.5")
    elif e1 is not None and e0 is not None and e1 >= e0:
        ok = False
        reasons.append("current error did not decrease on first refinement")

report = dict(exact_I=I_EX, meshes=rows, unipolar_pass=ok, reasons=reasons)
(OUT / "UNI_SUMMARY.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"unipolar_pass": ok, "reasons": reasons,
                  "I_mean": [r["I_mean"] for r in rows],
                  "rel": [r["rel_I_mean"] for r in rows]}, indent=2))
for r in rows:
    print("MESH", r["tag"], "I_mean", r["I_mean"], "rel", r["rel_I_mean"], "Q", r["Q_rho"])
    for s in r["samples"]:
        if s.get("missing"):
            print("  r", s["r"], "MISSING")
        else:
            print("  r", s["r"], "I", s["I"], "relI", round(s["rel_I"]*100, 3), "%",
                  "rho", s["rho"], "Emag", s["Emag"], "relE", round(s["rel_E"]*100, 3), "%", "V", s["V"])
sys.exit(0 if ok else 1)
