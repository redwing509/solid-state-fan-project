#!/usr/bin/env python3
# Plot the I-V curve from a Kaptzov voltage sweep (sweep/iv_results.csv)
# against the quadratic corona law and the wire-duct benchmark of
# Ziedan et al., IJPEST 4(2):154 (2010), Fig. 3 (digitized, rc = 1 mm,
# H = 114.3 mm).
#
# usage: plot_iv.py [<iv_results.csv>]

import csv
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    HERE, "sweep", "iv_results.csv")

MU = 1.8e-4   # ion mobility used in constant/electricProperties

# digitized from Ziedan et al. (2010) Fig. 3 (present-calculation curve)
ZIEDAN_F3 = np.array([
    [35, 0.04], [40, 0.10], [45, 0.18], [50, 0.29], [55, 0.42], [60, 0.57]])

rows = list(csv.DictReader(open(CSV)))
V = np.array([float(r["V"]) for r in rows])/1e3
I = np.array([float(r["Iprime"]) for r in rows])*1e3   # mA/m

# quadratic corona law fit, I = C V (V - V0)
A = np.vstack([V, np.ones_like(V)]).T
(C, mCV0), *_ = np.linalg.lstsq(A, I/V, rcond=None)
V0 = -mCV0/C
print(f"quadratic fit: C = {C*1e3:.4g} uA/(m kV^2), V0 = {V0:.2f} kV")

fig, ax = plt.subplots(figsize=(6.5, 5))
vv = np.linspace(V0, V.max()*1.04, 200)
ax.plot(V, I, "bo-", label=f"electrostaticSimpleFoam ($\\mu_i$={MU:g})")
ax.fill_between(V, I*1.4e-4/MU, I*2.2e-4/MU, alpha=0.15, color="b",
                label="$\\mu_i$ = 1.4e-4 ... 2.2e-4 m$^2$/Vs")
ax.plot(ZIEDAN_F3[:, 0], ZIEDAN_F3[:, 1], "ks--", mfc="none",
        label="Ziedan et al. (2010) Fig.3, calc. (digitized)")
ax.plot(vv, C*vv*(vv - V0), "b:", lw=1,
        label=f"quadratic law fit ($V_0$={V0:.1f} kV)")
ax.set_xlabel("applied voltage [kV]")
ax.set_ylabel("corona current [mA/m]")
ax.set_title("one-wire wire-duct ESP, $r_w$=1 mm, H=114.3 mm")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
out = os.path.join(os.path.dirname(CSV), "iv_curve.png")
fig.savefig(out, dpi=150)
print("wrote", out)
