"""Fan legacy-air300 corrected baseline, flow-off (pure conduction) limit.

All inputs are taken from the documented case set-up (blockMeshDict,
transportProperties, 0.orig/T of the corrected legacy EHD benchmark), never
from OpenFOAM output fields. See inputs/legacy_air300_corrected.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .solver import Boundary, Problem, solve, uniform_grid

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "legacy_air300_corrected.json"


def load_inputs(path=INPUT) -> dict:
    d = json.loads(Path(path).read_text())
    d["derived"] = derive(d)
    return d


def derive(d: dict) -> dict:
    g = d["geometry"]; pr = d["properties"]; bc = d["boundary_conditions"]
    H = (g["y_top_mm"] - g["y_plate_mm"]) * 1e-3
    rho_c = pr["rho0"] * pr["Cp0"]
    k_solver = rho_c * pr["nu"] / pr["Pr"]       # conductivity the OpenFOAM TEqn actually uses
    q = k_solver * bc["plate_gradient_K_per_m"]
    return {"H_m": H, "rho_c": rho_c, "k": k_solver, "alpha": k_solver / rho_c,
            "q_wall_W_m2": q, "k_declared": pr["kf"],
            "plate_area_m2": g["x_extent_mm"] * 1e-3 * g["depth_mm"] * 1e-3}


def run(n_cells=1024, dt=1e-3, theta=0.5, t_end=None, path=INPUT) -> dict:
    d = load_inputs(path); D = d["derived"]
    t_end = d["time"]["t_end_s"] if t_end is None else t_end
    T_amb = d["boundary_conditions"]["T_top_K"]
    p = Problem(x=uniform_grid(0.0, D["H_m"], n_cells), k=D["k"], rho_c=D["rho_c"],
                left=Boundary("flux", D["q_wall_W_m2"]), right=Boundary("dirichlet", T_amb),
                T0=d["initial"]["T_K"])
    r = solve(p, t_end, dt, theta=theta)
    E_err = (r.energy[-1] - r.energy[0]) - r.heat_in[-1]
    return {"n_cells": n_cells, "dt": dt, "theta": theta, "t_end_s": t_end,
            "wall_heat_flux_W_m2": D["q_wall_W_m2"],
            "T_wall_K": float(r.T[-1][0]), "T_max_K": r.max_T(), "T_mean_K": r.mean_T(),
            "heat_out_top_J_m2": float(-r.heat_in_right[-1]),
            "energy_residual_J_m2": float(E_err), "derived": D}
