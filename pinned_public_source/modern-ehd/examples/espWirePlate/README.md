# espWirePlate — one-wire wire-duct ESP

Validation and demonstration case: a single corona wire (radius 1 mm, +45 kV)
centred between grounded plates (wire-plate spacing H = 114.3 mm, the
Penney-Matick configuration), in a duct flow of 1 m/s (k-epsilon). Half
domain with a symmetry plane through the wire; duct length 4H.

All runs in this example (Allrun, the voltage sweep, the ionic wind
comparison) execute in parallel on 4 processors by default; change
`numberOfSubdomains` in `system/decomposeParDict` to adjust — the scripts
read the processor count from there.

## Single run

```bash
./Allrun
```

The wire charge density in `0/rhoq` (4.465e-5 C/m3) is the Kaptzov-converged
value for 45 kV, i.e. the area-averaged wire surface field equals Peek's
onset field E_on = 6.1193e6 V/m (printed by the `EmagWireAvg` function
object). The per-patch corona currents are printed every iteration:

```
patch wire: I = -1.5459e-06 A, max|E| = ...
patch plate: I =  1.5433e-06 A, max|E| = ...
```

Per unit wire length: I' = 2|I_wire|/0.01 (half domain, 0.01 m slab).

## I-V curve (Kaptzov voltage sweep)

```bash
python3 kaptzov_sweep.py     # 35...60 kV, results in sweep/iv_results.csv
python3 plot_iv.py           # plot vs quadratic law + literature benchmark
```

For each voltage the script iterates the wire `rhoq` boundary value (secant
method) until the Kaptzov condition is met, then records the corona current.

## Ionic wind on/off comparison

```bash
./run_ionicWind.sh           # 50 kV, inlet 0.3 m/s, force on vs off
```

At 0.3 m/s the EHD-to-inertia ratio (u_EHD/u0)^2 is about 3 and the force
produces the classical wire-to-plate ion jet with recirculation rolls; the
corona current itself changes by < 0.1 % (drift >> convection). Sampled
line profiles and a mid-plane cut are written to `postProcessing/` of each
sub-case for plotting.

## Other geometries

```bash
python3 make_geometry.py esp935 0.000935 0.2 0.4
```

regenerates the case with a different wire radius / duct height / length
(here: the experimental geometry of Ziedan et al. 2010, Fig. 9). Pass the
new case and its Peek field to `kaptzov_sweep.py` to validate against the
measured I-V curve, e.g.

```bash
python3 kaptzov_sweep.py esp935 esp935/sweep 6.2225e6 32.6e3 40e3,44e3,48e3,52e3,56e3
```
