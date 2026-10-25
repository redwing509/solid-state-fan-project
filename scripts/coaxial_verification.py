"""Compare analytic shooting with independently formulated log-radius BVP.

Reduced steady unipolar charge model; not a fan or OpenFOAM simulation.
"""
import csv
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad, solve_bvp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
A, B, EPS = 0.001, 0.1, 8.854e-12
SOURCE = "https://github.com/swtbkim/electrostaticSimpleFoam/blob/main/examples/coaxialCorona/exact_coaxial.py"



def solve_log_radius_bvp(voltage, injected_charge, n_mesh=200, tol=1e-9,
                         bc_tol=1e-11, max_nodes=20000, allow_max_nodes=False):
    """Method 2 on its own (used by compare() and by the mesh study in tests/coaxial).

    t=log(r/a), v=V/V0, y=rE/V0, k=I' a^2/(2 pi eps mu V0^2).
    v'=-y; y'=k exp(2t)/y. No shooting result enters the initial guess.
    Returns (scipy solution, length = ln(b/a)).
    allow_max_nodes=True accepts scipy status 1 (node limit reached): the Newton solve on
    the given mesh has converged, only further mesh refinement was refused. Used for the
    fixed-mesh study, never by compare().
    """
    length = np.log(B / A)
    coefficient = injected_charge * A ** 2 / (EPS * voltage)

    def ode(t, state, parameter):
        return np.vstack((-state[1], parameter[0] * np.exp(2 * t) / state[1]))

    def boundary(left, right, parameter):
        return np.array([left[0] - 1, right[0],
                         parameter[0] - coefficient * left[1]])

    mesh = np.linspace(0, length, n_mesh)
    guess = np.vstack((1 - mesh / length, np.full(mesh.size, 1 / length)))
    solution = solve_bvp(ode, boundary, mesh, guess,
                         p=[coefficient / length], tol=tol,
                         bc_tol=bc_tol, max_nodes=max_nodes)
    if not solution.success and not (allow_max_nodes and solution.status == 1):
        raise RuntimeError(solution.message)
    return solution, length


def bvp_current_from_solution(solution, voltage, mobility):
    return float(solution.p[0] * 2 * np.pi * EPS * mobility * voltage ** 2 / A ** 2)


def compare(voltage, injected_charge, mobility):
    # Method 1: radial closed-form field, adaptive quadrature and scalar shooting.
    def field(radius, emitter_field):
        current = 2 * np.pi * A * mobility * injected_charge * emitter_field
        return np.sqrt((A * emitter_field / radius) ** 2 +
                       current / (2 * np.pi * EPS * mobility) * (1 - (A / radius) ** 2))

    def mismatch(emitter_field):
        return quad(lambda r: field(r, emitter_field), A, B,
                    epsabs=1e-7, epsrel=1e-11, limit=400)[0] - voltage

    emitter_field = brentq(mismatch, 1e-6, voltage / (A * np.log(B / A)),
                           xtol=1e-7, rtol=1e-12)
    current = 2 * np.pi * A * mobility * injected_charge * emitter_field

    # Method 2: solve Poisson + charge conservation directly, with current unknown.
    solution, length = solve_log_radius_bvp(voltage, injected_charge)

    t = np.linspace(0, length, 401)
    radius = A * np.exp(t)
    exact_field = field(radius, emitter_field)
    exact_potential = np.array([
        voltage - quad(lambda r: field(r, emitter_field), A, ri,
                       epsabs=1e-7, epsrel=1e-11, limit=400)[0]
        for ri in radius])
    state = solution.sol(t)
    bvp_field = state[1] * voltage / radius
    bvp_potential = state[0] * voltage
    bvp_current = solution.p[0] * 2 * np.pi * EPS * mobility * voltage ** 2 / A ** 2
    relative_l2 = lambda numerical, exact: float(np.sqrt(
        np.trapezoid((numerical - exact) ** 2, radius) /
        np.trapezoid(exact ** 2, radius)))
    row = dict(electrode_voltage_V=voltage, injected_charge_C_m3=injected_charge,
               ion_mobility_m2_V_s=mobility,
               shooting_emitter_field_V_m=emitter_field,
               shooting_current_A_per_m=current,
               bvp_current_A_per_m=float(bvp_current),
               relative_current_error=float(abs(bvp_current - current) / current),
               relative_field_L2_error=relative_l2(bvp_field, exact_field),
               relative_potential_L2_error=relative_l2(bvp_potential, exact_potential),
               max_potential_error_over_applied_voltage=float(
                   np.max(np.abs(bvp_potential - exact_potential)) / voltage),
               bvp_nodes=int(solution.x.size),
               bvp_max_rms_residual=float(np.max(solution.rms_residuals)))
    row["passed"] = bool(max(row["relative_current_error"],
                             row["relative_field_L2_error"],
                             row["relative_potential_L2_error"]) < 1e-4)
    return row


def main():
    rows = [compare(v, rho, mu)
            for v in (10000., 20000., 30000., 40000.)
            for rho in (0.5e-5, 1e-5, 2e-5)
            for mu in (1.5e-4, 1.8e-4, 2.3e-4)]
    baseline = next(r for r in rows if r["electrode_voltage_V"] == 30000 and
                    r["injected_charge_C_m3"] == 1e-5 and
                    r["ion_mobility_m2_V_s"] == 1.8e-4)
    report = dict(
        title="Independent coaxial reduced-model numerical verification",
        source=SOURCE,
        geometry=dict(wire_radius_m=A, outer_radius_m=B, permittivity_F_m=EPS),
        methods=["Closed-form field + adaptive quadrature + Brent shooting",
                 "Log-radius Poisson/current-conservation boundary-value collocation; unknown current"],
        limitations=[
            "Fixed injected space charge; no corona onset or ionization chemistry.",
            "Steady unipolar drift, no diffusion and no airflow.",
            "Electrode voltages are distinct from 110/220/330/440 VAC supply inputs.",
            "Numerical agreement verifies this reduced model, not physical fan performance.",
            "No OpenFOAM solver was executed and no material ranking is established."],
        case_count=len(rows), passed_count=sum(r["passed"] for r in rows),
        tolerance_relative=1e-4,
        max_relative_current_error=max(r["relative_current_error"] for r in rows),
        max_relative_field_L2_error=max(r["relative_field_L2_error"] for r in rows),
        max_relative_potential_L2_error=max(r["relative_potential_L2_error"] for r in rows),
        baseline=baseline, cases=rows)
    OUT.mkdir(exist_ok=True)
    (OUT / "coaxial_verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (OUT / "coaxial_verification.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({k: v for k, v in report.items() if k not in ("cases", "limitations", "methods")}, indent=2))
    if report["passed_count"] != len(rows):
        raise SystemExit("Verification tolerance failed")


if __name__ == "__main__":
    main()
