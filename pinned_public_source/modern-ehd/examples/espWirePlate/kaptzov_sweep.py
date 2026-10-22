#!/usr/bin/env python3
# Voltage sweep with Kaptzov iteration:
# for each applied voltage, find the wire charge density rhoq_w such that
# the area-averaged |E| on the wire equals Peek's onset field E_on.
# Each (V, rhoq_w) candidate runs in its own case directory under ./sweep,
# cloned from this case (the template).
#
# Requires a sourced OpenFOAM environment and the compiled solver.
#
# usage: kaptzov_sweep.py [<templateCase> <sweepDir> <E_on> <V0est> <V1,V2,...>]
#   defaults: this case, ./sweep, Peek for r_w = 1 mm, 30.5 kV, 35...60 kV

import csv
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = HERE
SWEEP = os.path.join(HERE, "sweep")
E_ON = 6.1193e6          # Peek onset field, r_w = 1 mm, f = 1.0  [V/m]
V0_EST = 30.5e3          # estimated onset voltage [V]
TOL = 0.003              # relative tolerance on E_avg
VOLTAGES = [35e3, 40e3, 45e3, 50e3, 55e3, 60e3]

if len(sys.argv) > 1:
    TEMPLATE, SWEEP = sys.argv[1], sys.argv[2]
    E_ON, V0_EST = float(sys.argv[3]), float(sys.argv[4])
    VOLTAGES = [float(v) for v in sys.argv[5].split(",")]

if shutil.which("electrostaticSimpleFoam") is None:
    raise SystemExit("electrostaticSimpleFoam not found in PATH - "
                     "source the OpenFOAM environment and run ./Allwmake")


def set_bc(case, field, patch, value):
    fn = os.path.join(case, "0", field)
    s = open(fn).read()
    pat = re.compile(
        r"(%s\s*\{\s*type\s+fixedValue;\s*value\s+uniform\s+)[-0-9.eE+]+" % patch)
    s2, n = pat.subn(r"\g<1>%g" % value, s)
    assert n == 1, (field, patch, n)
    open(fn, "w").write(s2)


def n_procs(case):
    s = open(os.path.join(case, "system", "decomposeParDict")).read()
    return int(re.search(r"numberOfSubdomains\s+(\d+)", s).group(1))


def run_case(case):
    with open(os.path.join(case, "log.run"), "w") as log:
        subprocess.run(["mpirun", "-np", str(n_procs(case)),
                        "electrostaticSimpleFoam", "-parallel"], cwd=case,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    fo = os.path.join(case, "postProcessing", "EmagWireAvg", "0",
                      "surfaceFieldValue.dat")
    Eavg = float(open(fo).readlines()[-1].split()[1])
    Iw = Ip = None
    nIter = 0
    for line in open(os.path.join(case, "log.run")):
        if line.startswith("Time = "):
            nIter += 1
        elif line.startswith("patch wire"):
            Iw = float(line.split("I =")[1].split("A")[0])
        elif line.startswith("patch plate"):
            Ip = float(line.split("I =")[1].split("A")[0])
    return Eavg, Iw, Ip, nIter


def fresh_case(case):
    if os.path.exists(case):
        shutil.rmtree(case)
    os.makedirs(case)
    for d in ("0", "constant", "system"):
        shutil.copytree(os.path.join(TEMPLATE, d), os.path.join(case, d))
    subprocess.run(["blockMesh"], cwd=case, check=True,
                   stdout=subprocess.DEVNULL)


os.makedirs(SWEEP, exist_ok=True)
rows = []

for V in VOLTAGES:
    case = os.path.join(SWEEP, "V%d" % int(V/1000))
    r1 = max(3e-6, 2.5e-5*(V - V0_EST)/(45e3 - V0_EST))
    r2 = 1.4*r1
    hist = []

    def evaluate(rho):
        fresh_case(case)
        set_bc(case, "V", "wire", V)
        set_bc(case, "rhoq", "wire", rho)
        # decompose only after the boundary values are set
        subprocess.run(["decomposePar"], cwd=case, check=True,
                       stdout=subprocess.DEVNULL)
        Eavg, Iw, Ip, nIter = run_case(case)
        hist.append((rho, Eavg, Iw, Ip, nIter))
        print(f"  V={V/1e3:.0f} kV rhoq_w={rho:.4e} -> Eavg={Eavg:.4e} "
              f"(target {E_ON:.4e}), I_wire={Iw:.4e} A, iters={nIter}",
              flush=True)
        return Eavg

    E1 = evaluate(r1)
    if abs(E1 - E_ON)/E_ON > TOL:
        E2 = evaluate(r2)
        for _ in range(8):
            if abs(E2 - E_ON)/E_ON <= TOL:
                break
            if E2 == E1:
                break
            r3 = r2 - (E2 - E_ON)*(r2 - r1)/(E2 - E1)
            r3 = max(1e-7, r3)
            r1, E1 = r2, E2
            r2 = r3
            E2 = evaluate(r2)

    rho, Eavg, Iw, Ip, nIter = hist[-1]
    # reconstruct the converged state of this voltage for post-processing
    subprocess.run(["reconstructPar", "-latestTime"], cwd=case, check=True,
                   stdout=subprocess.DEVNULL)
    # half domain (y > 0) of thickness 0.01 m:
    # per unit wire length, I' = 2 * |I_wire| / 0.01  [A/m]
    rows.append(dict(V=V, rhoq_w=rho, Eavg=Eavg,
                     Iwire=Iw, Iplate=Ip,
                     Iprime=2*abs(Iw)/0.01, nIter=nIter))
    print(f"V={V/1e3:.0f} kV done: rhoq_w={rho:.4e}, "
          f"I'={rows[-1]['Iprime']*1e3:.4f} mA/m", flush=True)

with open(os.path.join(SWEEP, "iv_results.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("wrote", os.path.join(SWEEP, "iv_results.csv"))
