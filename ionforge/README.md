# IonForge

IonForge (`ehd_bipolar.py`, the box finite-volume solver) is the Solid State Fan project's own electrical EHD solver. It is the second engine for ion current, next to OpenFOAM. It does electrical work only. It does not solve flow.

This directory is the public copy of that solver and its analytic checks.

## Honest limits

- Electrical only: Poisson plus unipolar ion drift, with no gas-flow convection of charge.
- The domain is an infinite half-plane, which is not the same as OpenFOAM's finite outer boundaries.
- Charge injection at the wire is a fixed density, not a predicted corona law.
- Results from this solver are model-only. They are not experimental validation. Thrust claims, if any, are single-engine (OpenFOAM) and must be labelled that way. IonForge reports current, not thrust.

## Requirements

- Python 3.10 or newer
- `numpy` and `scipy` (see `requirements.txt`)

Install:

```
python3 -m pip install -r requirements.txt
```

## How to run

From this directory:

```
python3 ehd_bipolar.py 50 100 200
```

Grid sizes are the command-line arguments. The solver writes `result.json` in the current directory and prints one JSON record per grid. The default grids are 50, 100, and 200 if you pass no arguments.

Analytic checks (four tests: low-charge current, charge balance, space-charge shielding, and the Laplace wire field):

```
python3 test_analytic.py
```

That script writes `analytic.json` and prints whether all checks passed.

## License

MIT, same as the repository. Dependencies: NumPy (BSD-3-Clause) and SciPy (BSD-3-Clause).
