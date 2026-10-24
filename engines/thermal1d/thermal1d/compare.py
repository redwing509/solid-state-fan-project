"""Compare thermal1d with OpenFOAM metrics using the tolerances fixed in
ACCEPTANCE_CRITERIA.md section B (committed before the comparison)."""
from __future__ import annotations

import json
from pathlib import Path

from .baseline import run

TOL = {"wall_heat_flux": 0.01, "peak_rise": 0.02, "mean_rise": 0.01, "plate_uniformity": 0.02}


def compare(of_metrics: dict, t1d: dict, T_ref=300.0) -> dict:
    rows = []
    def rel(a, b): return abs(a - b) / abs(b)
    q1, q2 = t1d["wall_heat_flux_W_m2"], of_metrics["wall_heat_flux_W_m2"]
    rows.append(("wall heat flux (W/m2)", q1, q2, rel(q1, q2), TOL["wall_heat_flux"]))
    p1, p2 = t1d["T_wall_K"] - T_ref, of_metrics["plate_T_face_max_K"] - T_ref
    rows.append(("peak (plate) T rise (K)", p1, p2, rel(p1, p2), TOL["peak_rise"]))
    m1, m2 = t1d["T_mean_K"] - T_ref, of_metrics["T_mean_K"] - T_ref
    rows.append(("mean T rise (K)", m1, m2, rel(m1, m2), TOL["mean_rise"]))
    u = of_metrics["plate_T_uniformity_frac_of_rise"]
    rows.append(("OF plate T uniformity (max-min)/rise", 0.0, u, u, TOL["plate_uniformity"]))
    out = [dict(quantity=r[0], thermal1d=r[1], openfoam=r[2], rel_diff=r[3], tol=r[4], passed=r[3] <= r[4]) for r in rows]
    return {"rows": out, "all_pass": all(r["passed"] for r in out),
            "info": {"thermal1d_T_wall_K": t1d["T_wall_K"], "thermal1d_T_mean_K": t1d["T_mean_K"],
                     "openfoam_plate_T_max_K": of_metrics["plate_T_face_max_K"],
                     "openfoam_plate_T_areamean_K": of_metrics["plate_T_face_areamean_K"],
                     "openfoam_cell_T_max_K": of_metrics["T_cell_max_K"],
                     "openfoam_T_mean_K": of_metrics["T_mean_K"]}}


def run_comparison(results_dir: Path, n_cells=1024, dt=5e-4) -> dict:
    t1d = run(n_cells=n_cells, dt=dt)
    res = {"thermal1d": {k: v for k, v in t1d.items()}}
    for name in ("ehd-off-control", "corrected-baseline"):
        of = json.loads((results_dir / "openfoam" / f"{name}_t10_metrics.json").read_text())
        res[name] = compare(of, t1d)
    return res
