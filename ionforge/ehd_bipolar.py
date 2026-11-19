"""Solid State Fan: independent second-engine EHD cross-check (Grok Bot, 2026-11-01 PST). Executed, not validated.
Wire-plate unipolar drift (Poisson + div(rho*mu*E)=0, fixed rho at wire) solved by a finite-volume method on a
bipolar conformal grid (numpy/scipy), independent of OpenFOAM. Inputs copied from the project's corrected-baseline job.json and
blockMeshDict: V=7540 V, mu=2.3e-4 m^2/Vs, rho_wire=1.743e-4 C/m^3, r_wire=39.5 um, plate 20.04 mm below wire.
Reference (OpenFOAM, t=10 s, half domain): I=7.226778e-5 A/m. Differences expected from: OpenFOAM outer boundaries
(x=320 mm, y=+60 mm, zeroGradient) vs this infinite half-plane; gas-flow convection of charge (drift-dominated here).
Usage: python ehd_bipolar.py N1 N2 ...   (grid sizes, writes result.json)"""
import sys, json, time
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl
EPS0 = 8.8541878128e-12
V, MU, RHO_W = 7540.0, 2.3e-4, 1.743e-4
R, D = 39.5e-6, 20.04e-3
A = np.sqrt(D * D - R * R); TAU0 = np.arccosh(D / R)
I_REF = 7.226778e-5

def solve(N, M=None, tol=1e-6, maxit=int(__import__("os").environ.get("MAXIT", 3000)), relax=float(__import__("os").environ.get("RELAX", 0.1))):
    M = M or N
    du, dv = TAU0 / N, np.pi / M
    u = -TAU0 + (np.arange(N) + 0.5) * du          # u=-TAU0 wire, u=0 plate
    v = (np.arange(M) + 0.5) * dv                   # v in (0,pi), symmetry walls at 0 and pi
    U, Vv = np.meshgrid(u, v, indexing="ij")
    w = U + 1j * Vv; e = np.exp(w)
    h2 = np.abs(2 * A * e / (1 - e) ** 2) ** 2      # |dz/dw|^2
    idx = np.arange(N * M).reshape(N, M)
    # Laplacian (uniform grid, Neumann in v, Dirichlet at u ends via ghost)
    rows, cols, vals = [], [], []
    bphi = np.zeros(N * M)
    for (di, dj, dd) in ((1, 0, du), (-1, 0, du), (0, 1, dv), (0, -1, dv)):
        c = 1 / dd ** 2
        for i in range(N):
            ii = i + di
            for j in range(M):
                jj = j + dj
                k = idx[i, j]
                if jj < 0 or jj >= M: continue      # Neumann
                if ii < 0:  rows.append(k); cols.append(k); vals.append(-2 * c); bphi[k] -= 2 * c * V; continue
                if ii >= N: rows.append(k); cols.append(k); vals.append(-2 * c); continue
                rows += [k, k]; cols += [idx[ii, jj], k]; vals += [c, -c]
    L = sp.csc_matrix((vals, (rows, cols)), shape=(N * M, N * M))
    Llu = spl.splu(L)
    rho = np.zeros((N, M)); rho[0, :] = RHO_W
    hist = []
    for it in range(maxit):
        phi = Llu.solve(-(h2 * rho).ravel() / EPS0 + bphi).reshape(N, M)
        # face "E" in computational coords (h cancels in face fluxes)
        pu = np.vstack([np.full((1, M), V), phi, np.zeros((1, M))])
        Eu = -(pu[1:] - pu[:-1]) / np.r_[du / 2, np.full(N - 1, du), du / 2][:, None]   # N+1 u-faces
        Ev = np.zeros((N, M + 1)); Ev[:, 1:-1] = -(phi[:, 1:] - phi[:, :-1]) / dv
        # steady upwind charge conservation: sum of outward fluxes = 0, rho=RHO_W at wire face
        r_, c_, v_ = [], [], []; b = np.zeros(N * M)
        for i in range(N):
            for j in range(M):
                k = idx[i, j]
                for f, s, nb in ((Eu[i + 1, j] * dv, 1, (i + 1, j)), (Eu[i, j] * dv, -1, (i - 1, j)),
                                 (Ev[i, j + 1] * du, 1, (i, j + 1)), (Ev[i, j] * du, -1, (i, j - 1))):
                    F = s * f * MU                  # outward flux per unit rho
                    if F > 0: r_.append(k); c_.append(k); v_.append(F)
                    else:
                        ni, nj = nb
                        if ni < 0: b[k] -= F * RHO_W
                        elif ni >= N or nj < 0 or nj >= M: pass   # plate outflow only / symmetry
                        else: r_.append(k); c_.append(idx[ni, nj]); v_.append(F)
        Cm = sp.csc_matrix((v_, (r_, c_)), shape=(N * M, N * M)) + sp.identity(N * M) * 1e-30
        rn = spl.spsolve(Cm, b).reshape(N, M)
        dr = np.max(np.abs(rn - rho)) / RHO_W
        rho = relax * rn + (1 - relax) * rho
        I_w = np.sum(np.maximum(Eu[0], 0) * RHO_W * MU * dv)
        I_p = np.sum(np.maximum(Eu[-1], 0) * rho[-1] * MU * dv)
        hist.append((it, dr, I_w, I_p))
        if dr < tol and it > 5: break
    return dict(N=N, M=M, iters=it + 1, drho=dr, I_wire=I_w, I_plate=I_p,
                balance=abs(I_w - I_p) / I_w, rel_vs_openfoam=(I_w - I_REF) / I_REF,
                E_cell1_mean=float(np.mean(Eu[0] / np.sqrt(h2[0]))),   # face-normal E divided by metric at the first cell centre (old "E_wire_mean")
                E_wire_face_mean=float(np.mean(Eu[0] / np.abs(2 * A * np.exp(-TAU0 + 1j * v) / (1 - np.exp(-TAU0 + 1j * v)) ** 2))))  # at the wire surface

if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]] or [50, 100, 200]
    out = dict(desc=__doc__.splitlines()[0], I_openfoam_half=I_REF, grids=[])
    for n in Ns:
        t = time.time(); r = solve(n); r["sec"] = round(time.time() - t, 1); out["grids"].append(r); print(json.dumps(r), flush=True)
    if len(out["grids"]) >= 3:
        f = [g["I_wire"] for g in out["grids"][-3:]]
        p = np.log(abs((f[0] - f[1]) / (f[1] - f[2]))) / np.log(2) if f[1] != f[2] else float("nan")
        out["observed_order"] = float(p); out["richardson_I"] = float(f[2] + (f[2] - f[1]) / (2 ** p - 1)) if np.isfinite(p) and p > 0 else None
    json.dump(out, open("result.json", "w"), indent=1, default=float)
