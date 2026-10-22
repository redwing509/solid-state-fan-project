# Completed EHD benchmark — numerical review

October 21, 2026. Status: execution completed; experimental validation remains open.

## What completed

The supplied OpenFOAM Foundation 4.1 EHD case reached **10 simulated seconds**, exited with code **0**, and logged a normal `End`. The continuation took approximately **2,243 seconds** (37.4 minutes) on mail under the existing two-CPU/4 GB container cap. It restarted from the earlier 0.5-second checkpoint.

All 4,700 saved cell values were finite for temperature, velocity, potential, charge density, electric field and current density. Charge density was nonnegative. Maximum cell speed was **0.688 m/s** and maximum cell temperature was **340.476 K**. These are values inside an open heated-plate benchmark, not delivered fan performance.

Between saved times 9.5 and 10 s, the velocity's relative L2 change was **1.52e-6**. Temperature and electrical fields were unchanged at the saved six-digit precision; that is not proof of exact equality. The stored boundary volume fluxes balance to approximately **8.47e-8** relative to outward flow. Final logged cumulative continuity error was about **−1.09e-10**. These checks support stable numerical execution; charge conservation and experimental error have not yet been fully assessed.

## Thermal-input discrepancy

The repository describes comparison with a **187 W/m²** heated-plate experiment. The supplied case specifies a wall-normal temperature gradient of **9,350 K/m** and a nominal `kf=0.02 W/(m·K)`, which multiply to 187 W/m².

However, the compiled temperature equation uses laminar thermal diffusivity **ν/Pr**, with ν=1e-5 m²/s and Pr=0.9; its supplied `kf` value is not used in that equation. With ρ=1.225 kg/m³ and Cp=1,000 J/(kg·K), the equivalent conductivity is **0.013611 W/(m·K)**, implying **127.264 W/m²** under the prescribed gradient. This is 31.9% below the documented reference heat flux.

The 0.096 m² simulated half-plate therefore corresponds to about **12.217 W** under those equations, versus **17.952 W** using the stated nominal flux. The temperature boundaries also lack a fixed ambient inlet temperature, even though 300 K is used as the initial/reference value. A physically matched comparison must resolve these inputs before calculating a validation error against experimental heat-transfer coefficients.

## Queued controls

The new queue includes controls that separately change Prandtl number, wall gradient, incoming-air temperature treatment, injected charge and time-step restriction. These preserve the upstream case and record all modifications in fresh folders. They are investigations of model sensitivity, not presumptive fixes or commercial fan tests.

The upstream clone contains a comparison JPEG but no tabular experimental dataset. The relevant published reference is Owsenek and Seyed-Yagoobi (1997), DOI **10.1115/1.2824148**. Any values digitized from the figure must be labeled as digitized and carry uncertainty; none has yet been used to assert an accuracy percentage.

## Files and provenance

- `legacy-review/legacy_review.json`: field, stability, flow-balance and thermal audit values.
- `legacy-review/heated_wall_profile.csv`: 65 heated-wall faces, both saved times and explicitly apparent heat-transfer calculations.
- `legacy-review/thermal_review.png`: input mismatch and calculated wall-temperature profile.
- `legacy-review/upstream-comparison.jpg`: author-provided plot, retained as reference material.
- Full source and run remain on mail at `/opt/fan-research/2026-10-21`.
- Pinned solver commit: `cfd66422bce0e17fa4b2ad0b622e37ad7a553fcd`.

Primary sources: https://github.com/nzhtbyn/buoyantBoussinesqPimpleEHDFoam ; temperature equation https://github.com/nzhtbyn/buoyantBoussinesqPimpleEHDFoam/blob/main/buoyantBoussinesqPimpleEHDFoam/TEqn.H ; experimental reference https://doi.org/10.1115/1.2824148 .
