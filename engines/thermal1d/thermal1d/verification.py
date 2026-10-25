"""Verification cases. Each returns a list of check dicts:
{id, name, metric, value, tol, pass, ...}. Tolerances mirror ACCEPTANCE_CRITERIA.md
(committed before the suite was run)."""
from __future__ import annotations

import math

import numpy as np

from . import analytic as A
from .baseline import run as run_baseline, load_inputs
from .gci import gci3, observed_order
from .lumped import lumped_exact, lumped_solve
from .solver import Boundary, Problem, solve, steady, uniform_grid


def _chk(id_, name, metric, value, tol, ok=None, **kw):
    ok = (value <= tol) if ok is None else ok
    return dict(id=id_, name=name, metric=metric, value=float(value), tol=tol, passed=bool(ok), **kw)


# ---------------------------------------------------------------- steady
def v1():
    x = uniform_grid(0, 0.05, 17)
    T = steady(Problem(x, 15.0, 1.0, Boundary("dirichlet", 400.0), Boundary("dirichlet", 300.0), 300.0))
    err = np.abs(T - (400 - 100 * x / 0.05)).max()
    return [_chk("V1", "steady Dirichlet-Dirichlet", "max |err| K", err, 1e-9)]


def v2():
    x = uniform_grid(0, 0.08004, 33); k = 0.02; q = 187.0
    T = steady(Problem(x, k, 1.0, Boundary("flux", q), Boundary("dirichlet", 300.0), 300.0))
    err = np.abs(T - (300 + q * (0.08004 - x) / k)).max()
    return [_chk("V2", "steady flux + Dirichlet", "max |err| K", err, 1e-9)]


def v3():
    out = []
    L, k, T1, Tinf = 0.1, 2.0, 500.0, 300.0
    for Bi in (0.1, 1.0, 10.0):
        h = Bi * k / L
        x = uniform_grid(0, L, 20)
        T = steady(Problem(x, k, 1.0, Boundary("dirichlet", T1), Boundary("robin", h=h, T_inf=Tinf), 300.0))
        err = np.abs(T - A.plane_wall_convective(x, L, T1, h, Tinf, k)).max()
        out.append(_chk("V3", f"steady convective BC Bi={Bi:g}", "max |err| K", err, 1e-9))
    return out


def v4():
    L, k, qd = 0.02, 0.5, 5e5
    x = uniform_grid(0, L, 25)
    T = steady(Problem(x, k, 1.0, Boundary("dirichlet", 320.0), Boundary("dirichlet", 300.0), 300.0,
                       source=lambda x, t: qd + 0 * x))
    err = np.abs(T - A.plane_wall_generation(x, L, qd, k, 320.0, 300.0)).max()
    return [_chk("V4", "steady uniform generation", "max |err| K", err, 1e-8)]


# ---------------------------------------------------------------- transient
def v5():
    k, rc, q, Ti, t = 0.02, 1225.0, 187.0, 300.0, 10.0
    al = k / rc; L = 12 * math.sqrt(al * t)
    x = uniform_grid(0, L, 400)
    r = solve(Problem(x, k, rc, Boundary("flux", q), Boundary("flux", 0.0), Ti), t, 2e-3)
    ex = A.semi_infinite_flux(x, t, q, k, al, Ti)
    rise = ex[0] - Ti
    return [_chk("V5", "semi-infinite constant flux: surface rise", "rel err", abs(r.T[-1][0] - ex[0]) / rise, 5e-3),
            _chk("V5", "semi-infinite constant flux: profile", "max |err| / rise", np.abs(r.T[-1] - ex).max() / rise, 5e-3)]


def v6():
    k, rc, Ts, Ti, t = 1.0, 1e6, 400.0, 300.0, 100.0
    al = k / rc; L = 12 * math.sqrt(al * t)
    x = uniform_grid(0, L, 400)
    r = solve(Problem(x, k, rc, Boundary("dirichlet", Ts), Boundary("flux", 0.0), Ti), t, 0.01, theta=1.0)
    ex = A.semi_infinite_temp(x, t, Ts, al, Ti)
    return [_chk("V6", "semi-infinite step surface temperature", "max |err| / |Ts-Ti|",
                 np.abs(r.T[-1] - ex).max() / abs(Ts - Ti), 1e-2)]


def v7():
    out = []
    L, k, rc, q, Ti = 0.08004, 0.02, 1225.0, 187.0, 300.0
    al = k / rc; x = uniform_grid(0, L, 256)
    tau = L * L / al
    Fos = (0.05, 0.2, 1.0, 3.0)
    r = solve(Problem(x, k, rc, Boundary("flux", q), Boundary("dirichlet", Ti), Ti), Fos[-1] * tau,
              tau / 4000, t_out=[F * tau for F in Fos])
    for F in Fos:
        i = int(np.argmin(np.abs(r.t - F * tau)))
        ex = A.slab_flux_dirichlet(x, r.t[i], L, q, k, al, Ti)
        out.append(_chk("V7", f"slab flux+Dirichlet Fourier series Fo={F:g}", "max |err| / (qL/k)",
                        np.abs(r.T[i] - ex).max() / (q * L / k), 1e-3))
    return out


def v8():
    out = []
    L, k, rc, Ti, Tw = 0.05, 1.0, 1e6, 400.0, 300.0
    al = k / rc; x = uniform_grid(0, L, 256); tau = L * L / al
    Fos = (0.05, 0.2, 1.0)
    r = solve(Problem(x, k, rc, Boundary("dirichlet", Tw), Boundary("dirichlet", Tw), Ti), Fos[-1] * tau,
              tau / 20000, theta=1.0, t_out=[F * tau for F in Fos])
    for F in Fos:
        i = int(np.argmin(np.abs(r.t - F * tau)))
        ex = A.slab_dirichlet_cooling(x, r.t[i], L, al, Ti, Tw)
        out.append(_chk("V8", f"slab cooling Fourier series Fo={F:g}", "max |err| / |Ti-Tw|",
                        np.abs(r.T[i] - ex).max() / abs(Ti - Tw), 5e-3))
    return out


def v9_v10():
    Ti, Tinf, tau = 25.0, 200.0, 1.0
    t, T = lumped_solve(Ti, Tinf, tau, 5.0, tau / 100)
    ex = lumped_exact(t, Ti, Tinf, tau)
    out = [_chk("V9", "lumped capacitance exponential (CN, dt=tau/100)", "max rel err of (T-Tinf)",
                (np.abs(T - ex) / np.abs(ex - Tinf)).max(), 1e-4)]
    for theta, p_exp in ((1.0, 1.0), (0.5, 2.0)):
        errs, hs = [], []
        for n in (20, 40, 80, 160):
            dt = 5.0 / n
            t, T = lumped_solve(Ti, Tinf, tau, 5.0, dt, theta=theta)
            errs.append(abs(T[-1] - lumped_exact(5.0, Ti, Tinf, tau))); hs.append(dt)
        p, pair = observed_order(errs, hs)
        out.append(_chk("V10", f"lumped time order theta={theta}", "observed order", abs(p - p_exp), 0.1,
                        observed=p, expected=p_exp, pairwise=pair, errors=errs))
    return out


# ---------------------------------------------------------------- MMS
def _mms():
    def Tm(x, t): return 1 + np.exp(-t / 2) * np.cos(3 * x) + 0.5 * x ** 2
    def Tx(x, t): return -3 * np.exp(-t / 2) * np.sin(3 * x) + x
    def Txx(x, t): return -9 * np.exp(-t / 2) * np.cos(3 * x) + 1
    def Tt(x, t): return -0.5 * np.exp(-t / 2) * np.cos(3 * x)
    def k(x): return 1 + 0.5 * np.sin(x)
    def kx(x): return 0.5 * np.cos(x)
    def rc(x): return 2 + np.cos(x)
    def s(x, t): return rc(x) * Tt(x, t) - (kx(x) * Tx(x, t) + k(x) * Txx(x, t))
    h = 3.0; L = 1.0
    def prob(n):
        return Problem(uniform_grid(0, L, n), k, rc,
                       Boundary("flux", lambda t: float(-k(0.0) * Tx(0.0, t))),
                       Boundary("robin", h=h, T_inf=lambda t: float(Tm(L, t) + k(L) * Tx(L, t) / h)),
                       lambda x: Tm(x, 0.0), source=s)
    return Tm, prob


def v11():
    Tm, prob = _mms(); t_end = 1.0
    eI, e2, hs = [], [], []
    for n in (20, 40, 80, 160):
        r = solve(prob(n), t_end, (1.0 / n) / 4)
        e = r.T[-1] - Tm(r.x, t_end)
        eI.append(np.abs(e).max()); e2.append(math.sqrt(np.dot(r.volumes, e * e))); hs.append(1.0 / n)
    out = []
    for nm, errs in (("L_inf", eI), ("L_2", e2)):
        p, pair = observed_order(errs, hs)
        out.append(_chk("V11", f"MMS space order ({nm})", "|p - 2|", abs(p - 2), 0.1,
                        observed=p, expected=2.0, pairwise=pair, errors=errs))
    return out


def v12():
    Tm, prob = _mms(); t_end = 1.0; n = 100
    ref = {th: solve(prob(n), t_end, 1e-4 if th == 0.5 else 1e-5, theta=th).T[-1] for th in (0.5, 1.0)}
    out = []
    for th, p_exp in ((1.0, 1.0), (0.5, 2.0)):
        errs, dts = [], []
        for nt in (10, 20, 40, 80):
            dt = t_end / nt
            errs.append(np.abs(solve(prob(n), t_end, dt, theta=th).T[-1] - ref[th]).max()); dts.append(dt)
        p, pair = observed_order(errs, dts)
        out.append(_chk("V12", f"MMS time order theta={th}", f"|p - {p_exp:g}|", abs(p - p_exp), 0.1,
                        observed=p, expected=p_exp, pairwise=pair, errors=errs))
    return out


def v13():
    out = []
    Tm, prob = _mms()
    for th in (0.5, 1.0):
        p = prob(64)
        p.right = Boundary("dirichlet", lambda t: 1.0 + 0.3 * math.sin(4 * t))  # Dirichlet path too
        r = solve(p, 2.0, 0.01, theta=th)
        # integral of |heat input| as scale: accumulate stepwise magnitudes via a second run of increments
        scale = abs(r.heat_in_left[-1]) + abs(r.heat_in_right[-1]) + abs(r.heat_in[-1]) + abs(r.energy[0])
        err = abs((r.energy[-1] - r.energy[0]) - r.heat_in[-1]) / scale
        out.append(_chk("V13", f"global energy conservation theta={th} (flux+Dirichlet+source)",
                        "|dE - Q| / scale", err, 1e-10))
        p2 = prob(64)
        r2 = solve(p2, 2.0, 0.01, theta=th)
        scale2 = abs(r2.heat_in_left[-1]) + abs(r2.heat_in_right[-1]) + abs(r2.heat_in[-1]) + abs(r2.energy[0])
        err2 = abs((r2.energy[-1] - r2.energy[0]) - r2.heat_in[-1]) / scale2
        out.append(_chk("V13", f"global energy conservation theta={th} (flux+Robin+source)",
                        "|dE - Q| / scale", err2, 1e-10))
    return out


def v14():
    """Incropera et al. 6th ed. Example 5.1 (thermocouple junction, lumped capacitance)."""
    h, k, c, rho, tau = 400.0, 20.0, 400.0, 8500.0, 1.0
    D = 6 * h * tau / (rho * c)                 # tau = rho c (D/6) / h for a sphere
    Bi = h * (D / 6) / k
    # time to reach 199 C from 25 C in 200 C gas, integrated numerically by thermal1d.lumped
    t, T = lumped_solve(25.0, 200.0, tau, 8.0, 1e-4)
    i = int(np.argmax(T >= 199.0))
    t199 = t[i - 1] + (199.0 - T[i - 1]) / (T[i] - T[i - 1]) * (t[i] - t[i - 1])
    return [_chk("V14", "Incropera Ex. 5.1: junction diameter D (book 0.706 mm)", "rel err",
                 abs(D * 1e3 - 0.706) / 0.706, 5e-3, computed_mm=D * 1e3, Bi=Bi, Bi_ok=Bi < 0.1),
            _chk("V14", "Incropera Ex. 5.1: time to 199 C (book 5.2 s)", "abs err s",
                 abs(t199 - 5.2), 0.05, computed_s=t199)]


# ---------------------------------------------------------------- baseline convergence
def v15_v17():
    out = []
    runs = {n: run_baseline(n_cells=n, dt=0.002 * 128 / n) for n in (128, 256, 512)}
    for q in ("T_wall_K", "T_mean_K"):
        f3, f2, f1 = (runs[n][q] for n in (128, 256, 512))
        g = gci3(f1, f2, f3, 2.0)
        ok = 1.8 <= g["p"] <= 2.2 and abs(g["asymptotic_ratio"] - 1) <= 0.05 and g["gci_fine"] <= 1e-3
        out.append(_chk("V15", f"baseline grid convergence {q}", "GCI_fine", g["gci_fine"], 1e-3, ok=ok,
                        observed=g["p"], asymptotic_ratio=g["asymptotic_ratio"], f_ext=g["f_ext"],
                        values=[f1, f2, f3]))
    fs = [run_baseline(n_cells=512, dt=dt)["T_wall_K"] for dt in (0.004, 0.002, 0.001)]
    g = gci3(fs[2], fs[1], fs[0], 2.0)
    ok = (1.8 <= g["p"] <= 2.2 or g["gci_fine"] <= 1e-4) and g["gci_fine"] <= 1e-3
    out.append(_chk("V16", "baseline time-step convergence T_wall", "GCI_fine", g["gci_fine"], 1e-3, ok=ok,
                    observed=g["p"], asymptotic_ratio=g["asymptotic_ratio"], f_ext=g["f_ext"], values=fs))
    d = load_inputs()["derived"]; r = runs[512]
    Tw_ex = float(A.semi_infinite_flux(0.0, 10.0, d["q_wall_W_m2"], d["k"], d["alpha"], 300.0))
    out.append(_chk("V17", "baseline T_wall vs semi-infinite closed form", "|err| K", abs(r["T_wall_K"] - Tw_ex), 0.05,
                    exact=Tw_ex))
    Tm_ex = 300.0 + d["q_wall_W_m2"] * 10.0 / (d["rho_c"] * d["H_m"])
    out.append(_chk("V17", "baseline T_mean vs q t/(rho c H)", "|err| K", abs(r["T_mean_K"] - Tm_ex), 0.01,
                    exact=Tm_ex))
    return out


ALL = [v1, v2, v3, v4, v5, v6, v7, v8, v9_v10, v11, v12, v13, v14, v15_v17]


def run_all():
    res = []
    for f in ALL:
        res.extend(f())
    return res
