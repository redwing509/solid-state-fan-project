# Legacy EHD benchmark: corrected thermal inputs (2026-10-24)

Overlay on `pinned_public_source/legacy-ehd/validationCase` (the pinned upstream case is left unchanged).
Only two inputs change:

| File | Original | Corrected |
|---|---|---|
| `constant/transportProperties` | `Pr 0.9` | `Pr 0.6125` |
| `0.orig/T`, patch `up` | `zeroGradient` | `fixedValue 300` (ambient air at TRef) |

The heated-plate gradient stays at **9,350 K/m** on `down`.

## Decision: Pr = 0.6125, not a 13,739 K/m gradient

The solver's `TEqn.H` conducts heat with `alphaEff = nu/Pr`, so the effective conductivity is
`rho0*Cp0*nu/Pr = 1.225*1000*1e-5/0.9 = 0.01361 W/(m K)`, and the imposed wall flux is
`0.01361*9350 = 127.26 W/m^2`, not the documented 187 W/m^2.

The case itself declares `kf 0.02 W/(m K)` and the gradient 9,350 K/m, and `0.02*9350 = 187 W/m^2` exactly.
The documented intent is therefore kf = 0.02 with gradient 9,350; the inconsistency is the Pr that the solver actually uses.
`Pr = rho0*Cp0*nu/kf = 0.6125` restores that kf while keeping the author's gradient. The alternative (gradient 13,738.78 K/m at
Pr 0.9) reaches 187 W/m^2 but contradicts both declared inputs (kf and gradient). Pr only enters the temperature
equation (momentum and EHD are unchanged).

Caveats:
- Real air near 300 K has Pr ~ 0.71 (k ~ 0.026). Pr 0.6125 is chosen for consistency with the case's declared kf, not as a better air property.
- The two 187 W/m^2 fixes give different temperature fields (max 347.0 K vs 359.5 K at 10 s; `reports/Thermal_Mismatch_Report_2026-10-22.md`).
- `up` is an open boundary (p_rgh fixed, U zeroGradient). A fixed 300 K value applies to outflow too; `inletOutlet` would be the next refinement.
- The 187 W/m^2 figure is probably digitized from Owsenek & Seyed-Yagoobi (1997) Fig. 5. This fix is input consistency, not experimental validation.

This baseline is the same input set as queue control `consistent_Pr_ambient` (legacy-8266a66833, 346.913 K max at 10 s).
`scripts/run_thermal_corrected_baseline.sh` reruns it on mail with the queue worker's container limits (2 CPU, 4 GB, 3,600 s),
wrapped by `scripts/run_with_manifest.py` (command, paths, UTC timestamps, return code, NaN/Inf check).
