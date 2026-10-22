# coaxialCorona — verification case

Unipolar corona between coaxial cylinders (wire radius 1 mm at 30 kV with
fixed surface charge density 1e-5 C/m3, grounded outer cylinder radius
100 mm; quarter annulus, no through-flow). This configuration has an exact
1-D solution for the electric field, space charge and corona current, which
makes it the standard verification problem for the solver.

```bash
./Allrun                  # single mesh (96x60)
./run_verification.sh     # 3-level mesh convergence study (48/96/192)
python3 exact_coaxial.py  # error norms, observed order, plots
```

Everything runs in parallel on 4 processors by default; change
`numberOfSubdomains` in `system/decomposeParDict` to adjust.

Expected behaviour:

- corona current within ~0.01 % of the exact value, wire and outer-cylinder
  currents balanced to 8 digits;
- observed convergence order ~1 for `rhoq` with the default `Gauss upwind`
  charge convection scheme; switch `div((phi+rhoqFlux),rhoq)` in
  `system/fvSchemes` to `Gauss linearUpwind grad(rhoq)` to obtain order ~2;
- max |U| converging to zero with refinement (the radial Coulomb force is
  curl-free and must be balanced by pressure).

`python3 exact_coaxial.py` requires numpy/scipy/matplotlib.
