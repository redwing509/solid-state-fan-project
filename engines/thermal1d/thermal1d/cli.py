"""Command-line interface: python -m thermal1d {baseline,verify,compare}"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def main(argv=None):
    ap = argparse.ArgumentParser(prog="thermal1d", description="In-house 1-D transient conduction engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("baseline", help="run the Fan corrected legacy-air300 baseline (flow-off limit)")
    b.add_argument("--cells", type=int, default=1024); b.add_argument("--dt", type=float, default=5e-4)
    b.add_argument("--theta", type=float, default=0.5); b.add_argument("--input", default=None)
    v = sub.add_parser("verify", help="run the verification suite and write results/verification.json")
    v.add_argument("--out", default=str(HERE / "results" / "verification.json"))
    c = sub.add_parser("compare", help="compare with stored OpenFOAM metrics (results/openfoam)")
    c.add_argument("--out", default=str(HERE / "results" / "comparison.json"))
    a = ap.parse_args(argv)
    if a.cmd == "baseline":
        from .baseline import run, INPUT
        r = run(n_cells=a.cells, dt=a.dt, theta=a.theta, path=a.input or INPUT)
        print(json.dumps(r, indent=1)); return 0
    if a.cmd == "verify":
        from .verification import run_all
        res = run_all()
        Path(a.out).write_text(json.dumps(res, indent=1))
        for r in res:
            print(f"{r['id']:4s} {'PASS' if r['passed'] else 'FAIL'}  {r['value']:.3e} tol={r['tol']}  {r['name']}")
        ok = all(r["passed"] for r in res)
        print(f"{sum(r['passed'] for r in res)}/{len(res)} checks passed")
        return 0 if ok else 1
    if a.cmd == "compare":
        from .compare import run_comparison
        res = run_comparison(HERE / "results")
        Path(a.out).write_text(json.dumps(res, indent=1))
        for name in ("ehd-off-control", "corrected-baseline"):
            print(f"== {name}: {'PASS' if res[name]['all_pass'] else 'FAIL'}")
            for r in res[name]["rows"]:
                print(f"  {r['quantity']:40s} t1d={r['thermal1d']:.5g} OF={r['openfoam']:.5g} "
                      f"rel={r['rel_diff']:.3e} tol={r['tol']:g} {'PASS' if r['passed'] else 'FAIL'}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
