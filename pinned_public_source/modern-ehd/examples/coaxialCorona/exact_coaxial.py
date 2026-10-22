#!/usr/bin/env python3
# Verification of electrostaticSimpleFoam against the exact 1D solution of
# unipolar corona space charge between coaxial cylinders.
#
# Run ./run_verification.sh first, then:  python3 exact_coaxial.py
#
# Governing equations (no flow, no diffusion, steady):
#   (1/r) d(r E)/dr = rhoq/eps0
#   J = rhoq * mu * E = I'/(2 pi r)   (current per unit length I')
# Closed form:
#   (r E)^2 = (a Ea)^2 + I'/(2 pi eps0 mu) * (r^2 - a^2)
# BCs as in the OpenFOAM case: V(a)=V0, V(b)=0, rhoq(a)=rhoq_a.
# Ea follows from shooting on  integral_a^b E dr = V0,
# with I' = 2 pi a mu rhoq_a Ea.

import os

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# case parameters (must match 0/ and constant/electricProperties)
a, b = 1e-3, 0.1
V0 = 30e3
rhoq_a = 1e-5
mu = 1.8e-4
eps0 = 8.854e-12
zthick = 0.01          # mesh thickness in z
sector = 0.25          # quarter annulus

CASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(CASE, "verification")
os.makedirs(OUT, exist_ok=True)


def E_exact(r, Ea):
    Ip = 2*np.pi*a*mu*rhoq_a*Ea
    C = Ip/(2*np.pi*eps0*mu)
    return np.sqrt((a*Ea/r)**2 + C*(1.0 - (a/r)**2))


def shoot(Ea):
    val, _ = quad(lambda r: E_exact(r, Ea), a, b, limit=400)
    return val - V0


Ea = brentq(shoot, 1e5, 5e7, xtol=1e-2)
Ip = 2*np.pi*a*mu*rhoq_a*Ea

print(f"Exact solution:  Ea = {Ea:.6e} V/m,  I' = {Ip:.6e} A/m")
print(f"(Laplacian Ea would be {V0/(a*np.log(b/a)):.4e} V/m)")


def V_exact(r):
    val, _ = quad(lambda s: E_exact(s, Ea), a, r, limit=400)
    return V0 - val


def rhoq_exact(r):
    return Ip/(2*np.pi*mu*r*E_exact(r, Ea))


# ---------------------------------------------------------------- meshes
levels = [48, 96, 192]
results = {}

for N in levels:
    d = os.path.join(CASE, "convergence", f"N{N}")
    sdir = os.path.join(d, "postProcessing", "sample")
    if not os.path.isdir(sdir):
        raise SystemExit(f"{sdir} not found - run ./run_verification.sh first")
    tdir = os.path.join(sdir, sorted(os.listdir(sdir), key=float)[-1])

    # single combined file: distance, V, rhoq, Ex,Ey,Ez, Ux,Uy,Uz
    fn = os.path.join(tdir, "ray45_V_rhoq_E_U.xy")
    dat = np.loadtxt(fn)
    Vs, rqs = dat[:, 1], dat[:, 2]
    Evec, Uvec = dat[:, 3:6], dat[:, 6:9]

    r = 0.0011 + dat[:, 0]           # ray starts at r = 1.1 mm
    magE = np.linalg.norm(Evec, axis=1)
    magU = np.linalg.norm(Uvec, axis=1)

    Vex = np.array([V_exact(ri) for ri in r])
    Eex = E_exact(r, Ea)
    rqex = rhoq_exact(r)

    def relL2(num, ex):
        return np.sqrt(np.trapz((num - ex)**2, r)/np.trapz(ex**2, r))

    # corona current from the run log
    Isim = None
    with open(os.path.join(d, "log.run")) as fh:
        for line in fh:
            if line.startswith("patch outer"):
                Isim = float(line.split("I =")[1].split("A")[0])
    Ip_sim = Isim/(zthick*sector)

    results[N] = dict(
        r=r, V=Vs, rhoq=rqs, magE=magE,
        eV=relL2(Vs, Vex), eE=relL2(magE, Eex), erq=relL2(rqs, rqex),
        Ip=Ip_sim, eI=abs(Ip_sim - Ip)/Ip, maxU=magU.max())

# ------------------------------------------------------------- report
print()
print(f"{'N':>5} {'relL2(V)':>12} {'relL2(|E|)':>12} {'relL2(rhoq)':>12} "
      f"{'I_sim [A/m]':>13} {'I err %':>8} {'max|U| m/s':>11}")
for N in levels:
    q = results[N]
    print(f"{N:>5} {q['eV']:>12.4e} {q['eE']:>12.4e} {q['erq']:>12.4e} "
          f"{q['Ip']:>13.5e} {100*q['eI']:>8.3f} {q['maxU']:>11.3e}")

print("\nObserved order of accuracy (factor-2 refinement):")
for key, lab in [("eV", "V"), ("eE", "|E|"), ("erq", "rhoq"), ("eI", "I")]:
    e = [results[N][key] for N in levels]
    p1 = np.log(e[0]/e[1])/np.log(2)
    p2 = np.log(e[1]/e[2])/np.log(2)
    print(f"  {lab:5s}: p(48->96) = {p1:5.2f},  p(96->192) = {p2:5.2f}")

# ------------------------------------------------------------- plots
q = results[96]
fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
rr = np.geomspace(a, b, 400)
axs[0].loglog(rr*1e3, E_exact(rr, Ea), "k-", label="exact")
axs[0].loglog(q["r"]*1e3, q["magE"], "ro", ms=3, mfc="none",
              markevery=12, label="OpenFOAM (96x60)")
axs[0].set_xlabel("r [mm]"), axs[0].set_ylabel("|E| [V/m]")
axs[0].legend(), axs[0].set_title("Electric field")

axs[1].loglog(rr*1e3, [rhoq_exact(ri) for ri in rr], "k-", label="exact")
axs[1].loglog(q["r"]*1e3, q["rhoq"], "bo", ms=3, mfc="none",
              markevery=12, label="OpenFOAM (96x60)")
axs[1].set_xlabel("r [mm]"), axs[1].set_ylabel("rhoq [C/m3]")
axs[1].legend(), axs[1].set_title("Space charge density")

e = {k: [results[N][k] for N in levels] for k in ("eV", "eE", "erq")}
h = 1.0/np.array(levels)
axs[2].loglog(h, e["eV"], "o-", label="V")
axs[2].loglog(h, e["eE"], "s-", label="|E|")
axs[2].loglog(h, e["erq"], "^-", label="rhoq")
axs[2].loglog(h, e["eV"][1]*(h/h[1])**2, "k--", label="2nd order")
axs[2].set_xlabel("h ~ 1/N"), axs[2].set_ylabel("relative L2 error")
axs[2].legend(), axs[2].set_title("Grid convergence")

fig.tight_layout()
fig.savefig(os.path.join(OUT, "verification_coaxial.png"), dpi=150)
print(f"\nwrote {OUT}/verification_coaxial.png")
