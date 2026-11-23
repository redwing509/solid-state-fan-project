#!/usr/bin/env python3
"""Recompute the Nov 1 E-01 current-verification headline numbers from summary.json.

Exit 0 if the recorded Richardson currents and gaps are reproduced.
Does not read raw meshes or OpenFOAM fields. Not a validation of the physics.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "results/ehd-current-verification-20261101/summary.json"


def richardson(i_coarse: float, i_mid: float, i_fine: float, r: float = 2.0):
    p = math.log(abs((i_coarse - i_mid) / (i_mid - i_fine))) / math.log(r)
    i_inf = i_fine + (i_fine - i_mid) / (r ** p - 1)
    return p, i_inf


def main() -> int:
    data = json.loads(SUMMARY.read_text())
    of = data["openfoam"]
    box = data["box_fv"]
    e = of["meshes_orig"]
    p_of, i_of = richardson(
        e["E2"]["I_wire_A_per_m_t0.06"],
        e["E4"]["I_wire_A_per_m_t0.06"],
        e["E8"]["I_wire_A_per_m_t0.06"],
    )
    rec_of = of["richardson_E2_E4_E8_t0.06"]
    grids = {g["N"]: g["I_wire"] for g in box["grids"]}
    p_box, i_box = richardson(grids[100], grids[200], grids[400])
    rec_box = box["richardson_N100_200_400"]
    gap = (i_of - i_box) / i_box * 100.0
    # Domain correction as in summary.txt: F2/C2 at t=0.1 applied to I_of.
    c2 = 7.859337963376164e-05
    f2 = 7.866490984081711e-05
    i_corr = i_of * (f2 / c2)
    gap_corr = (i_corr - i_box) / i_box * 100.0
    print(f"OpenFOAM E2/E4/E8  p={p_of:.6f}  I_inf={i_of:.12e} A/m")
    print(f"Box N=100/200/400  p={p_box:.6f}  I_inf={i_box:.12e} A/m")
    print(f"Gap OF_Rich vs box_Rich: {gap:.3f}%")
    print(f"Domain-corrected OF Rich: {i_corr:.12e} A/m   gap vs box: {gap_corr:.3f}%")
    ok = (
        abs(p_of - rec_of["p"]) < 1e-12
        and abs(i_of - rec_of["I_inf_A_per_m"]) < 1e-18
        and abs(p_box - rec_box["p"]) < 1e-12
        and abs(i_box - rec_box["I_inf_A_per_m"]) < 1e-18
        and abs(gap - 0.10385560505756875) < 1e-12
        and abs(i_corr - 8.234239670890651e-05) < 1e-18
    )
    if not ok:
        print("MISMATCH against recorded summary.json values", file=sys.stderr)
        return 1
    print("OK: recorded headline numbers reproduced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
