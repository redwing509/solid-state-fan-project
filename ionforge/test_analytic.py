"""Analytic checks for IonForge (ehd_bipolar.py, the box finite-volume solver). Tolerances fixed BEFORE running (2026-11-01 PST).
T1 Gauss/low-charge limit: rho_w -> 0 gives I = rho_w*mu*pi*V/TAU0 (half domain; capacitance of cylinder-plane) tol 1%.
T2 charge balance I_wire vs I_plate at converged state, tol 1%.
T3 monotone & sublinear in rho_w (space-charge shielding): I(2x)/I(1x) in (1,2).
T4 Laplace wire field: mean |E| on wire from engine vs exact (V/TAU0)/h averaged over cells, tol 2%."""
import importlib, json, numpy as np
import ehd_bipolar as E
res = {}
N = 60
base = E.RHO_W
E.RHO_W = base * 1e-6; r = E.solve(N, tol=1e-8, maxit=400)
exact = E.RHO_W * E.MU * np.pi * E.V / E.TAU0
res["T1"] = dict(I=r["I_wire"], exact=exact, rel=(r["I_wire"]-exact)/exact, pass_=abs(r["I_wire"]-exact)/exact < 0.01)
# T4 exact mean field over the same v cells at wire face u=-TAU0
M = N; v = (np.arange(M)+0.5)*np.pi/M; e = np.exp(-E.TAU0+1j*v)
h = np.abs(2*E.A*e/(1-e)**2); Eex = float(np.mean((E.V/E.TAU0)/h))
res["T4"] = dict(E=r["E_wire_face_mean"], exact=Eex, rel=(r["E_wire_face_mean"]-Eex)/Eex, pass_=abs(r["E_wire_face_mean"]-Eex)/Eex < 0.02)
E.RHO_W = base; r1 = E.solve(N)
res["T2"] = dict(balance=r1["balance"], pass_=r1["balance"] < 0.01)
E.RHO_W = 2*base; r2 = E.solve(N)
q = r2["I_wire"]/r1["I_wire"]; res["T3"] = dict(ratio=q, pass_=1 < q < 2)
res["all_pass"] = all(v["pass_"] for v in res.values() if isinstance(v, dict))
print(json.dumps(res, indent=1, default=float)); json.dump(res, open("analytic.json","w"), indent=1, default=float)
