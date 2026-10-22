# electrostaticSimpleFoam

![OpenFOAM v2412](https://img.shields.io/badge/OpenFOAM-v2412-blue)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green)

A steady-state OpenFOAM solver for **DC corona discharge coupled with incompressible turbulent flow** — the secondary flow known as **ionic wind** (electrohydrodynamics, EHD). The solver combines the standard `simpleFoam` and `electrostaticFoam` solvers into a single segregated solver, targeted at wire-plate electrostatic precipitator (ESP) type configurations.

![ionic wind](docs/figures/ionic_wind_field_slow.png)

*Ionic wind in a one-wire wire-duct ESP at 50 kV (bottom: EHD force on). The wire-to-plate ion jet and the recirculation rolls are the classical EHD flow structures observed in ESP experiments.*

## Physics

Per SIMPLE iteration the solver sequentially solves:

| Equation | Field |
| --- | --- |
| Poisson equation `laplacian(V) = -rhoq/epsilon0` | electric potential `V` [V], field `E = -grad(V)` |
| Charge transport `div((U + muq*E)*rhoq) = div(Dq*grad(rhoq))` | space charge density `rhoq` [C/m3] |
| Momentum with Coulomb body force `rhoq*E/rhoFluid` [m/s2] | `U`, then SIMPLE pressure correction for `p` |
| Turbulence model update | `k`, `epsilon`, `nut`, ... |

- Two-way coupling: the electric force drives the flow, the flow convects the charge.
- Runtime switch `electricForce on/off` (in `constant/electricProperties`) isolates the ionic-wind effect without changing the electrostatics.
- Per-patch corona current and maximum surface field are printed every iteration, ready for Kaptzov-type corona boundary iteration and I-V curve generation.
- Corona injection follows the **Kaptzov hypothesis** with Peek's onset field, implemented as a boundary-value iteration (automated in `examples/espWirePlate/kaptzov_sweep.py`).

## Repository structure

```text
electrostaticSimpleFoam/
├── Allwmake / Allwclean          build scripts
├── src/
│   └── electrostaticSimpleFoam/  solver source (simpleFoam + electrostatics)
├── examples/
│   ├── coaxialCorona/            verification: coaxial corona with exact solution
│   └── espWirePlate/             validation/demo: one-wire wire-duct ESP, I-V sweep,
│                                 ionic wind on/off
└── docs/
    ├── verification_validation.md   full V&V report
    └── figures/
```

## Quick start

### Prerequisites

- OpenFOAM **v2412** (ESI/OpenCFD; nearby versions are expected to work but are untested) with its MPI environment (the examples run on 4 processors by default)
- Python 3 with `numpy`, `scipy`, `matplotlib` for the sweep/verification scripts (optional)

### Build

```bash
source /usr/lib/openfoam/openfoam2412/etc/bashrc   # adjust to your installation
git clone https://github.com/swtbkim/electrostaticSimpleFoam.git
cd electrostaticSimpleFoam
./Allwmake
```

The binary is installed into `$FOAM_USER_APPBIN`.

### Run the ESP example

```bash
cd examples/espWirePlate
./Allrun
```

This solves the corona + flow problem at 45 kV on a one-wire wire-duct ESP (wire radius 1 mm, wire-plate spacing 114.3 mm, inlet 1 m/s, k-epsilon). The terminal prints the corona current per patch and the wire-average surface field each iteration. See `examples/espWirePlate/README.md` for the voltage sweep (I-V curve) and the ionic wind on/off comparison.

All examples run **in parallel on 4 processors** by default (`decomposePar` → `mpirun -np 4 electrostaticSimpleFoam -parallel` → `reconstructPar`, handled by the run scripts). To change the processor count, edit `numberOfSubdomains` in `system/decomposeParDict` of the case — every script picks it up from there.

### Run the verification example

```bash
cd examples/coaxialCorona
./Allrun                  # single mesh
./run_verification.sh     # 3-level mesh convergence study
python3 exact_coaxial.py  # compare with the exact solution
```

## Verification & validation

Summary (full report: [docs/verification_validation.md](docs/verification_validation.md)):

- **Exact solution** (coaxial wire-cylinder corona): field/charge profiles and corona current reproduced with the formal order of accuracy of the chosen schemes (upwind: p = 1.0, linearUpwind: p = 2.0); current error 0.01 %; discrete charge conservation to 8 digits.
- **Degenerate case**: with `rhoq = 0` the solver reproduces `simpleFoam` **bitwise** (pitzDaily).
- **Wire-duct ESP I-V curves** vs Ziedan et al. (2010), calculation and experiment: quadratic corona law `I = C V (V - V0)` reproduced with onset voltage within 4 % of the analytic estimate; measured I-V matched within the documented mobility/onset uncertainty (current scales exactly linearly with ion mobility).
- **Plate current density** follows the classical Warburg `cos^4.82` distribution.
- **Ionic wind**: classical jet + recirculation structure, with the expected `(u_EHD/u0)^2` parameter scaling, and < 0.1 % back-coupling of the flow on the corona current.

![I-V validation](docs/figures/iv_fig9.png)

## Documentation

- [Verification & validation report](docs/verification_validation.md) (English)
- [Step-by-step tutorial](https://github.com/swtbkim/openfoam-tutorial-ko) (Korean, 예제 18 of `openfoam-tutorial-ko`) — how to build this solver from `simpleFoam` yourself: solver anatomy, wmake, name-collision handling, adding fields and equations, case setup, Kaptzov iteration.

## Citation

If you use this solver in your research, please cite it via the metadata in [CITATION.cff](CITATION.cff).

## Acknowledgements and license

`electrostaticSimpleFoam` is derived from the OpenFOAM standard solvers `simpleFoam` and `electrostaticFoam` (Copyright OpenFOAM Foundation / OpenCFD Ltd). This offering is not approved or endorsed by OpenCFD Limited, producer and distributor of the OpenFOAM software via [openfoam.com](https://openfoam.com), and owner of the OPENFOAM and OpenCFD trade marks.

Distributed under the [GNU General Public License v3](LICENSE), as required for OpenFOAM derivatives.
