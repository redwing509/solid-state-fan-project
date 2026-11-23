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
I_BOX = 8.218217e-05  # box FV Richardson (infinite half-plane), context only

CURRENT_ABS_MIN = 1e-18  # A/m; below this is treated as no current
SETTLE_WINDOW = 100      # steps (t 0.05 -> 0.06 s at dt = 1e-4 s); METHOD.md
SETTLE_TOL = 1e-3        # 0.1% relative change of I_vol over the window
EXPECTED_STEPS = 600     # dt = 1e-4 s to t = 0.06 s (METHOD.md); dt check uses 1200
A2_EXACT = 6.78117058395794e-05  # coaxial known solution, A/m (METHOD.md A2)
A2_SAMPLES = ("002", "005", "01", "02", "05")


def usable_current(I):
    return I is not None and math.isfinite(I) and abs(I) > CURRENT_ABS_MIN


def monitor_settled(values, window=SETTLE_WINDOW, tol=SETTLE_TOL):
    """Return (ok, rel_change) for the last `window` steps of a monitor series.

    rel_change = (max - min) / |last| over the final window + 1 values. A
    short, non-finite or zero series is never settled.
    """
    vals = list(values)
    if len(vals) < window + 1:
        return False, math.inf
    tail = vals[-(window + 1):]
    if not all(math.isfinite(v) for v in tail):
        return False, math.inf
    last = tail[-1]
    if abs(last) <= CURRENT_ABS_MIN:
        return False, math.inf
    change = (max(tail) - min(tail)) / abs(last)
    return change <= tol, change


def oscillatory(Ic, Im, If_):
    """True when successive mesh differences change sign."""
    return (Ic - Im) * (Im - If_) < 0


def monitor_series(path: Path):
    if not path.is_file():
        return []
    out = []
    for ln in path.read_text().splitlines():
        n = floats_in(ln)
        if n:
            out.append(n[-1])
    return out


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

def a2_r2_pass(verify_dir: Path, expected_steps=EXPECTED_STEPS):
    """Rule 1 gate: A2 re-solved with the current formulation passes its band."""
    means = []
    for t in ("f1", "f0p5", "f0p25"):
        d = Path(verify_dir) / f"uni_{t}"
        vals = []
        for r in A2_SAMPLES:
            v = last_scalar(d / f"I_r{r}.dat")
            if v is None or not math.isfinite(v):
                return False
            vals.append(v)
        mon = monitor_series(d / "monitor_I.dat")
        if len(mon) != expected_steps or not monitor_settled(mon)[0]:
            return False
        means.append(sum(vals) / len(vals))
    fine, med = means[-1], means[-2]
    if abs(fine - A2_EXACT) / A2_EXACT > 0.01 or abs(fine - med) / abs(fine) > 0.02:
        return False
    # Same apparent-order condition as check_uni.py (METHOD.md A2).
    e0 = abs(means[0] - A2_EXACT) / A2_EXACT
    e1 = abs(means[1] - A2_EXACT) / A2_EXACT
    if e0 > 0 and e1 > 0:
        return math.log(e0 / e1) / math.log(2) > 0.5
    return e1 < e0


def tag_factor(tag: str):
    """'f0p25' -> 0.25; None if the tag is not an lc_factor tag."""
    try:
        return float(tag.lstrip("f").replace("p", "."))
    except ValueError:
        return None


def halving_order(tags) -> bool:
    """Tags must run coarse -> fine with the mesh size halved each step."""
    f = [tag_factor(t) for t in tags]
    if any(x is None or x <= 0 for x in f):
        return False
    return all(abs(a / b - 2.0) < 1e-9 for a, b in zip(f, f[1:]))


def one(d: Path, expected_steps=EXPECTED_STEPS):
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
    mon = monitor_series(d / "monitor_I.dat")
    ok, change = monitor_settled(mon)
    ok = ok and len(mon) == expected_steps
    rec.update(
        n_steps=len(mon),
        I_vol=mon[-1] if mon else None,
        settled=ok,
        settle_change=None if not math.isfinite(change) else change,
    )
    return rec

def score(root: Path, tags, verify_dir=None, expected_steps=EXPECTED_STEPS):
    """Apply the frozen E-01 rule. Every requested mesh must exist."""
    root = Path(root)
    verify_dir = Path(verify_dir) if verify_dir else root.parent / "verify-r2"
    rows, missing = [], []
    for t in tags:
        d = root / f"wp_{t}" if (root / f"wp_{t}").is_dir() else root / t
        if not d.is_dir():
            missing.append(t)
            continue
        rows.append(dict(tag=t, **one(d, expected_steps)))
    a2_ok = a2_r2_pass(verify_dir)
    order_ok = halving_order(tags)
    report = dict(openfoam_I=I_OF, meshes=rows, missing=missing,
                  expected_steps=expected_steps, tags_halving=order_ok,
                  a2_r2_pass=a2_ok, e01_pass=False)
    if missing:
        print(f"missing mesh directories: {missing}", file=sys.stderr)
    if (order_ok and not missing and len(rows) == 3
            and all(usable_current(r["I_contour"]) for r in rows)):
        Ic, Im, If_ = (r["I_contour"] for r in rows)
        change = abs(If_ - Im) / abs(If_)
        try:
            p = math.log(abs((Ic - Im) / (Im - If_))) / math.log(2)
            Iinf = If_ + (If_ - Im) / (2**p - 1)
        except (ValueError, ZeroDivisionError):
            p, Iinf = None, None
        gap = None if Iinf is None else abs(Iinf - I_OF) / I_OF
        osc = oscillatory(Ic, Im, If_)
        mesh_gaps = [abs(r["I_contour"] - I_OF) / I_OF for r in rows]
        # Richardson assumes monotone convergence; when the differences change
        # sign, every mesh must also be inside the same 5% band (stricter only).
        band_ok = (not osc) or max(mesh_gaps) <= 0.05
        settled = all(r["settled"] for r in rows)
        ok = (a2_ok and settled and band_ok and Iinf is not None and gap <= 0.05
              and p is not None and p > 0.5 and change <= 0.02)
        report.update(p=p, I_inf=Iinf, rel_gap_OF=gap, finest_two_change=change,
                      oscillatory=osc, max_mesh_gap_OF=max(mesh_gaps),
                      all_settled=settled,
                      rel_gap_box_fv=None if Iinf is None else abs(Iinf - I_BOX) / I_BOX,
                      e01_pass=ok)
    return report


def main():
    args = sys.argv[1:]
    steps = EXPECTED_STEPS
    if len(args) >= 2 and args[0] == "--steps":
        steps = int(args[1])
        args = args[2:]
    root = Path(args[0]) if args else Path(__file__).resolve().parent / "results" / "study-r2"
    tags = args[1:] or ["f1", "f0p5", "f0p25"]
    report = score(root, tags, expected_steps=steps)
    (root / "E01_SUMMARY.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
