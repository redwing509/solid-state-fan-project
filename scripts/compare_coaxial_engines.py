#!/usr/bin/env python3
"""Three-way comparison of the 36 fixed-injection coaxial electrical cases.

Engines
  exact  : closed-form field + adaptive quadrature + Brent shooting (coaxial_verification.json, shooting_current_A_per_m)
  scipy  : SciPy solve_bvp log-radius collocation (coaxial_verification.json, bvp_current_A_per_m)
  openfoam: OpenFOAM v2412 queue runs (openfoam_v2412_coaxial_runs.json; outer-patch current / (0.01 m depth * 1/4 sector))

Tolerance (fixed before the comparison was run, 2026-10-24):
  every engine's current within 1% of exact, and the engines within 1% of each other.
  The gate is applied to the primary OpenFOAM run per case (mesh_n 192, linearUpwind) AND to all 6 mesh/scheme
  variants (48/96/192 x upwind/linearUpwind), so a case passes only if every OpenFOAM variant passes.
"""
import csv, json, sys
from pathlib import Path

TOL_EXACT = 0.01
TOL_ENGINES = 0.01
here = Path(__file__).resolve().parent
data = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent / 'results' / 'coaxial-electrical'
ver = json.loads((data / 'coaxial_verification.json').read_text())
runs = json.loads((data / 'openfoam_v2412_coaxial_runs.json').read_text())

def key(v, mu, rho):
    return (round(float(v)), round(float(mu) * 1e9), round(float(rho) * 1e12))

of = {}
for cid, rec in runs.items():
    j, r = rec['job'], rec['result']
    if not r or r.get('status') != 'executed' or r['metrics'].get('fatal_marker'):
        raise SystemExit(f'{cid}: not a clean executed run')
    i_of = abs(r['metrics']['last_patch_metrics']['outer']['I']) / (0.01 * 0.25)
    of.setdefault(key(j['voltage_v'], j['mobility'], j['injection']), []).append(
        dict(id=cid, mesh_n=j['mesh_n'], scheme=j['scheme'], current=i_of))

rows, all_pass = [], True
assert ver['case_count'] == 36 and len(ver['cases']) == 36
for c in ver['cases']:
    k = key(c['electrode_voltage_V'], c['ion_mobility_m2_V_s'], c['injected_charge_C_m3'])
    exact, scipy = c['shooting_current_A_per_m'], c['bvp_current_A_per_m']
    variants = of.get(k, [])
    if len(variants) != 6:
        raise SystemExit(f'case {k}: expected 6 OpenFOAM variants, found {len(variants)}')
    prim = next(v for v in variants if v['mesh_n'] == 192 and v['scheme'] == 'linearUpwind')
    e_scipy = abs(scipy - exact) / exact
    e_of = abs(prim['current'] - exact) / exact
    e_of_scipy = abs(prim['current'] - scipy) / scipy
    worst = max(variants, key=lambda v: abs(v['current'] - exact))
    e_worst = abs(worst['current'] - exact) / exact
    e_worst_scipy = abs(worst['current'] - scipy) / scipy
    ok = (e_scipy <= TOL_EXACT and e_of <= TOL_EXACT and e_of_scipy <= TOL_ENGINES
          and e_worst <= TOL_EXACT and e_worst_scipy <= TOL_ENGINES)
    all_pass &= ok
    rows.append(dict(voltage_V=c['electrode_voltage_V'], mobility_m2_Vs=c['ion_mobility_m2_V_s'],
                     injection_C_m3=c['injected_charge_C_m3'], exact_A_per_m=exact, scipy_bvp_A_per_m=scipy,
                     openfoam_192_linUpw_A_per_m=prim['current'], openfoam_case_id=prim['id'],
                     rel_err_scipy_vs_exact=e_scipy, rel_err_openfoam_vs_exact=e_of,
                     rel_diff_openfoam_vs_scipy=e_of_scipy, worst_variant=f"{worst['mesh_n']}/{worst['scheme']}",
                     worst_variant_rel_err_vs_exact=e_worst, worst_variant_rel_diff_vs_scipy=e_worst_scipy,
                     passed=ok))

out = data / 'coaxial_engine_comparison.csv'
with out.open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
summary = dict(tolerance=dict(current_vs_exact=TOL_EXACT, engine_vs_engine=TOL_ENGINES,
                              gate='primary (192/linearUpwind) and all 6 OpenFOAM variants per case'),
               cases=len(rows), passed=sum(r['passed'] for r in rows), all_passed=all_pass,
               max_rel_err_scipy_vs_exact=max(r['rel_err_scipy_vs_exact'] for r in rows),
               max_rel_err_openfoam_primary_vs_exact=max(r['rel_err_openfoam_vs_exact'] for r in rows),
               max_rel_diff_openfoam_primary_vs_scipy=max(r['rel_diff_openfoam_vs_scipy'] for r in rows),
               max_rel_err_any_openfoam_variant_vs_exact=max(r['worst_variant_rel_err_vs_exact'] for r in rows),
               max_rel_diff_any_openfoam_variant_vs_scipy=max(r['worst_variant_rel_diff_vs_scipy'] for r in rows),
               openfoam_runs_checked=sum(len(v) for v in of.values()))
(data / 'coaxial_engine_comparison_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
sys.exit(0 if all_pass else 1)
