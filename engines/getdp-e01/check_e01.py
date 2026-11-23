#!/usr/bin/env python3
"""Half-domain current from a sampled semicircle at r=5*r_wire."""
from __future__ import annotations
import json, math, sys
from pathlib import Path

from getdp_tables import floats_in

RW = 39.5e-6
RP = 5 * RW
MU = 2.3e-4
I_OF = 8.226752e-05  # OpenFOAM Richardson, A/m, half-domain

CURRENT_ABS_MIN = 1e-18  # A/m; below this is treated as no current


def usable_current(I):
    return I is not None and math.isfinite(I) and abs(I) > CURRENT_ABS_MIN


def nums(line: str):
    return floats_in(line)

def load_pairs(e_path: Path, r_path: Path):
    elines = [ln for ln in e_path.read_text().splitlines() if ln.strip()]
    rlines = [ln for ln in r_path.read_text().splitlines() if ln.strip()]
    pts = []
    for el, rl in zip(elines, rlines):
        ev, rv = nums(el), nums(rl)
        # Table: ids, x y z, zeros, then vector or scalar
        if len(ev) < 11 or len(rv) < 9:
            # try last values
            if len(ev) >= 6 and len(rv) >= 4:
                x, y = ev[2], ev[3]
                Ex, Ey, Ez = ev[-3], ev[-2], ev[-1]
                rho = rv[-1]
            else:
                continue
        else:
            x, y = ev[2], ev[3]
            Ex, Ey, Ez = ev[8], ev[9], ev[10]
            rho = rv[8] if len(rv) > 8 else rv[-1]
        pts.append((x, y, Ex, Ey, Ez, rho))
    return pts

def current(pts):
    # I = int rho mu (E·n) ds, n = (x,y)/r, ds = r dθ, θ from -pi/2 to pi/2
    if len(pts) < 2:
        return None
    acc = 0.0
    for i in range(len(pts) - 1):
        x1,y1,Ex1,Ey1,Ez1,rho1 = pts[i]
        x2,y2,Ex2,Ey2,Ez2,rho2 = pts[i+1]
        th1, th2 = math.atan2(y1, x1), math.atan2(y2, x2)
        def flux(x,y,Ex,Ey,rho):
            r = math.hypot(x, y)
            nrm = (Ex * x + Ey * y) / r  # E·n
            return rho * MU * nrm * r   # integrand in dθ, times r (=ds/dθ)
        f1, f2 = flux(x1,y1,Ex1,Ey1,rho1), flux(x2,y2,Ex2,Ey2,rho2)
        acc += 0.5 * (f1 + f2) * (th2 - th1)
    return acc

def last_scalar(path: Path):
    if not path.is_file():
        return None
    n = nums(path.read_text().strip().splitlines()[-1])
    return n[-1] if n else None

def one(d: Path):
    pts = load_pairs(d / "ctr_e.dat", d / "ctr_r.dat") if (d/"ctr_e.dat").is_file() else []
    I = current(pts) if pts else None
    rec = dict(
        dir=str(d), n_pts=len(pts),
        I_contour=I,
        rel_OF=None if I is None else abs(I - I_OF) / I_OF,
        I_emitter=last_scalar(d / "I_emitter.dat"),
        I_collector=last_scalar(d / "I_collector.dat"),
        Q_rho=last_scalar(d / "Q_rho.dat"),
        v_probe=last_scalar(d / "v_probe.dat"),
        r_probe=last_scalar(d / "r_probe.dat"),
        v_laplace_probe=last_scalar(d / "v_laplace_probe.dat"),
        finite=usable_current(I),
    )
    return rec

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "results" / "smoke"
    tags = sys.argv[2:] or ["f1", "f0p5", "f0p25"]
    rows = []
    for t in tags:
        d = root / f"wp_{t}" if (root / f"wp_{t}").is_dir() else root / t
        if not d.is_dir():
            continue
        rows.append(dict(tag=t, **one(d)))
    report = dict(openfoam_I=I_OF, meshes=rows)
    if len(rows) >= 3 and all(r["I_contour"] for r in rows):
        Ic, Im, If_ = (rows[0]["I_contour"], rows[1]["I_contour"], rows[2]["I_contour"])
        change = abs(If_ - Im) / abs(If_)
        try:
            p = math.log(abs((Ic - Im) / (Im - If_))) / math.log(2)
            Iinf = If_ + (If_ - Im) / (2**p - 1)
        except (ValueError, ZeroDivisionError):
            p, Iinf = None, None
        gap = None if Iinf is None else abs(Iinf - I_OF) / I_OF
        ok = (Iinf is not None and gap <= 0.05 and p is not None and p > 0.5 and change <= 0.02)
        report.update(p=p, I_inf=Iinf, rel_gap_OF=gap, finest_two_change=change, e01_pass=ok)
    (root / "E01_SUMMARY.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
