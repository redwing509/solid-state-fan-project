"""Write the C5/C6/C7 study numbers to JSON (for the record and CI artifact)."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_coaxial as T  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--out", default="coaxial_mesh_study.json")
a = ap.parse_args()
out, p, p_fine, ref = T.mesh_study()
v, q, m = T.BASE
tol_rows = []
for tol in (1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9):
    sol, _ = T.cv.solve_log_radius_bvp(v, q, tol=tol)
    c = T.cv.bvp_current_from_solution(sol, v, m)
    tol_rows.append(dict(tol=tol, nodes=int(sol.x.size), current=c, rel_err=abs(c - ref) / ref))
rec = dict(case=dict(voltage_V=v, injected_charge_C_m3=q, mobility_m2_V_s=m), shooting_reference_A_per_m=ref,
           fixed_mesh=out, observed_order_coarse_triplet=p, observed_order_fine_triplet=p_fine, tolerance_sweep=tol_rows)
Path(a.out).write_text(json.dumps(rec, indent=2))
print(json.dumps(rec, indent=2))
