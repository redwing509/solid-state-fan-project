#!/usr/bin/env python3
"""Extract comparison metrics from an OpenFOAM ASCII case (polyMesh + <time>/T),
independently of OpenFOAM utilities (pure NumPy).

Metrics: volume-weighted mean T; max cell T; plate (patch 'down') face temperature
T_f = T_P + g * d (fixedGradient: d = distance from owner-cell centre to face along
the face normal); wall heat flux k*g; plate T uniformity; per-face profile.

Usage: extract_openfoam_metrics.py CASE_DIR TIME --k 0.02 [--out metrics.json]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np


def _body(path):
    s = Path(path).read_text()
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"//[^\n]*", "", s)
    return s


def _list(s, start=0):
    m = re.compile(r"\n\s*(\d+)\s*\n?\s*\(", re.S).search(s, start)
    n = int(m.group(1))
    return n, m.end()


def read_points(p):
    s = _body(p); n, i = _list(s)
    vals = re.findall(r"\(([^()]+)\)", s[i:])[:n]
    return np.array([[float(v) for v in t.split()] for t in vals])


def read_faces(p):
    s = _body(p); n, i = _list(s)
    vals = re.findall(r"\d+\(([^()]+)\)", s[i:])[:n]
    return [list(map(int, t.split())) for t in vals]


def read_labels(p):
    s = _body(p); n, i = _list(s)
    j = s.index(")", i)
    return np.array(list(map(int, s[i:j].split())))[:n]


def read_boundary(p):
    s = _body(p)
    out = {}
    for name, blk in re.findall(r"(\w+)\s*\{([^}]*)\}", s):
        nf = re.search(r"nFaces\s+(\d+)", blk); sf = re.search(r"startFace\s+(\d+)", blk)
        if nf and sf:
            out[name] = (int(sf.group(1)), int(nf.group(1)))
    return out


def read_internal_scalar(p, ncells):
    s = _body(p)
    m = re.search(r"internalField\s+uniform\s+([-+0-9.eE]+)", s)
    if m:
        return np.full(ncells, float(m.group(1)))
    i = s.index("internalField")
    n, j = _list(s, i)
    k = s.index(")", j)
    a = np.array(list(map(float, s[j:k].split())))
    assert a.size == n == ncells, (a.size, n, ncells)
    return a


def mesh_geometry(case):
    pm = Path(case) / "constant" / "polyMesh"
    P = read_points(pm / "points"); F = read_faces(pm / "faces")
    own = read_labels(pm / "owner"); nei = read_labels(pm / "neighbour")
    nc = int(max(own.max(), nei.max())) + 1
    Cf = np.zeros((len(F), 3)); Sf = np.zeros((len(F), 3))
    for fi, f in enumerate(F):  # triangle-fan decomposition about the vertex mean
        v = P[f]; c0 = v.mean(axis=0); S = np.zeros(3); C = np.zeros(3); A = 0.0
        for a in range(len(f)):
            p1, p2 = v[a], v[(a + 1) % len(f)]
            s = 0.5 * np.cross(p1 - c0, p2 - c0); ar = np.linalg.norm(s)
            S += s; C += ar * (p1 + p2 + c0) / 3.0; A += ar
        Sf[fi] = S; Cf[fi] = C / A if A > 0 else c0
    # cell centre estimate = mean of face centres, then pyramid volumes/centroids
    cnt = np.bincount(own, minlength=nc) + np.bincount(nei, minlength=nc)
    Ce = (np.add.reduceat if False else None)
    est = np.zeros((nc, 3))
    np.add.at(est, own, Cf); np.add.at(est, nei[:], Cf[: len(nei)])
    est /= cnt[:, None]
    V = np.zeros(nc); Cc = np.zeros((nc, 3))
    for side, cells, sign in (("o", own, 1.0), ("n", nei, -1.0)):
        idx = np.arange(len(cells))
        pv = sign * np.einsum("ij,ij->i", Sf[idx], Cf[idx] - est[cells]) / 3.0
        np.add.at(V, cells, pv)
        np.add.at(Cc, cells, pv[:, None] * (0.75 * Cf[idx] + 0.25 * est[cells]))
    Cc /= V[:, None]
    return dict(P=P, F=F, own=own, nei=nei, Cf=Cf, Sf=Sf, V=V, C=Cc, nc=nc,
                boundary=read_boundary(pm / "boundary"))


def metrics(case, time, k, gradient=None, patch="down"):
    g = mesh_geometry(case)
    T = read_internal_scalar(Path(case) / str(time) / "T", g["nc"])
    sT = _body(Path(case) / str(time) / "T")
    blk = re.search(patch + r"\s*\{([^}]*)\}", sT.split("boundaryField", 1)[1]).group(1)
    if gradient is None:
        gradient = float(re.search(r"gradient\s+uniform\s+([-+0-9.eE]+)", blk).group(1))
    s0, n = g["boundary"][patch]
    fids = np.arange(s0, s0 + n); cells = g["own"][fids]
    nf = g["Sf"][fids] / np.linalg.norm(g["Sf"][fids], axis=1)[:, None]
    d = np.einsum("ij,ij->i", g["Cf"][fids] - g["C"][cells], nf)
    Tf = T[cells] + gradient * d
    Af = np.linalg.norm(g["Sf"][fids], axis=1)
    order = np.argsort(g["Cf"][fids][:, 0])
    rise_ref = 300.0
    return {
        "case": str(case), "time": str(time), "n_cells": int(g["nc"]),
        "domain_volume_m3": float(g["V"].sum()),
        "T_mean_K": float(np.dot(g["V"], T) / g["V"].sum()),
        "T_cell_max_K": float(T.max()),
        "T_cell_max_location_m": g["C"][int(T.argmax())].tolist(),
        "plate_T_face_max_K": float(Tf.max()), "plate_T_face_min_K": float(Tf.min()),
        "plate_T_face_areamean_K": float(np.dot(Af, Tf) / Af.sum()),
        "plate_T_uniformity_frac_of_rise": float((Tf.max() - Tf.min()) / max(Tf.max() - rise_ref, 1e-30)),
        "plate_area_m2": float(Af.sum()),
        "wall_heat_flux_W_m2": float(k * gradient),
        "wall_heat_W": float(k * gradient * Af.sum()),
        "plate_first_cell_distance_m": [float(d.min()), float(d.max())],
        "plate_profile": [[float(g["Cf"][fids][i, 0]), float(Tf[i])] for i in order],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("case"); ap.add_argument("time")
    ap.add_argument("--k", type=float, required=True, help="effective conductivity rho*Cp*nu/Pr")
    ap.add_argument("--out")
    a = ap.parse_args()
    m = metrics(a.case, a.time, a.k)
    s = json.dumps(m, indent=1)
    if a.out:
        Path(a.out).write_text(s)
    print(json.dumps({k: v for k, v in m.items() if k != "plate_profile"}, indent=1))


if __name__ == "__main__":
    main()
