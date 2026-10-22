# Fanless fan — voltage and materials campaign

October 21, 2026. Status: first reduced electrical batch completed; full material-aware EHD campaign remains open.

## Completed tests

| Requested supply voltage, AC RMS | Layered-dielectric parameter cases | Numerical checks passed |
| --- | ---: | ---: |
| 110 V | 75 | 75 |
| 220 V | 75 | 75 |
| 330 V | 75 | 75 |
| 440 V | 75 | 75 |
| Total | 300 | 300 |

Each voltage covers all 25 ordered pairs from a five-entry property set (air reference, PTFE, PEEK 450G, BOROFLOAT 33 glass, alumina AD-96), with the first layer occupying 25%, 50% or 75% of the total thickness. Single-material, reversed-layer and equivalent cases are retained as controls. Thus 300 is a parameter-row count, not 300 independent physical designs.

Assumed coupon: flat ideal electrodes, 1 cm² area, 1 mm total thickness, 60 Hz. Supply RMS voltage is applied across this **insulation proxy only**, not directly across an ionic-wind cell. There is no mains-to-HV converter model in this batch.

The test compares:

1. **ngspice 44.2:** two ideal series capacitors, with capacitance derived from each layer's nominal permittivity, area and thickness; AC solution gives interface voltage and source displacement current.
2. **Separate finite-volume field calculation:** solves the 1D variable-permittivity field equation on 20-, 40- and 80-cell interface-aligned grids, then derives capacitance and field distribution.
3. **Closed-form reference:** series capacitance and electric displacement continuity.

All 300 met the preselected relative numerical discrepancy limit of 1e-7. Maximum ngspice discrepancy was **1.33e-15**; maximum field-calculation discrepancy was **2.76e-13**. This near-exact agreement is expected for simple, piecewise-linear fields on aligned grids. It does not establish accuracy for complicated fan geometry or experimental accuracy of the property data.

For a given coupon, raising 110 to 440 V gives four times the displacement current and electric field, and sixteen times stored electrical energy. Those are linear dielectric relationships. Displacement current is not useful fan current, and the ideal model has no real dissipative power. No airflow-per-watt conclusion follows.

## Additional electrical verification

**36 coaxial benchmark cases** compared field-integral/Brent shooting with independently formulated boundary-value collocation. The cases vary electrode voltage (10/20/30/40 kV), injected charge (0.5/1/2 × 10⁻⁵ C/m³), and ion mobility (1.5/1.8/2.3 × 10⁻⁴ m²/V·s). These electrode voltages are separate from the four AC supply scenarios.

All 36 passed a 1e-4 relative comparison threshold. Maximum relative current discrepancy: **6.76e-13**. The 30 kV reference reproduced approximately **67.8117 µA per metre** of electrode. This verifies a fixed-injected-charge, no-diffusion electrical model; it does not test airflow, corona inception, actual metals or a complete upstream solver.

## Material property provenance and limitations

| Entry | Nominal relative permittivity | Source condition |
| --- | ---: | --- |
| Air | 1.0 | Ideal reference approximation |
| PTFE | 2.1 | Daikin representative low-frequency property, not guaranteed |
| PEEK 450G | 3.0 | Victrex, 23°C and 50 Hz; held constant at 60 Hz |
| BOROFLOAT 33 | 4.6 | SCHOTT, 25°C and 1 MHz; unvalidated extrapolation to 60 Hz |
| Alumina AD-96 | 9.0 | CoorsTek, 25°C and 1 MHz; indexed supplier table, direct fetch failed; unvalidated extrapolation to 60 Hz |

These nominal values are inputs for numerical screening. Temperature/frequency dispersion, losses, leakage, surface charge, contamination, voids, edges, mechanical manufacture and dielectric breakdown are absent. Do not select a final insulating material, minimum clearance or voltage rating from this batch. Replace extrapolated values with verified grade- and condition-specific measurements before design decisions.

Metal emitter and collector effects are absent in both the ideal-electrode coupon and the current OpenFOAM fixed-boundary model. Literature reports material-dependent corona behavior and degradation; it would be incorrect to interpret the model's missing material sensitivity as evidence that all metals perform equally.

## Registered next-stage combinations

The register contains **10,800 pending candidates**: 300 voltage/layer parameter rows × six emitter candidates × six collector candidates. Electrode candidates are tungsten, stainless steel, nichrome, copper, aluminum and titanium. This is an expandable starting set, not all materials or grades.

Every candidate is labeled `REGISTERED_NOT_EHD_SIMULATED` and linked to its dielectric screen. None is counted as a completed fan simulation. Charge-injection/onset, grade/surface condition, aging, actual geometry, converter behavior and gas-flow coupling remain necessary before ranking their airflow, efficiency or commercial suitability.

## Continuing project rules

Maintain `TASKS.md` and its user-facing copy `Project_To_Do.md`; add useful simulator/virtual-lab candidates and run matched benchmarks before fan comparisons. The simulator register tracks executed versus proposed tools. Existing OpenFOAM full-case work remains separate from this reduced batch.

The user authorizes this computer/GPU for simulations with a **50% local CPU/GPU utilization ceiling**. No local GPU simulation was launched. **Notify the user before a heavy-load run or a job requiring more compute; choose the resources together.** Existing small capped server jobs remain within their recorded limits. See `Project_Parameters.md`.

## Saved evidence

- `material-campaign/dielectric_results.csv`: all 300 comparisons.
- `material-campaign/dielectric_summary.json`: properties, sources, limits, versions and errors.
- `material-campaign/material_campaign_register.csv`: all 10,800 pending candidates.
- `material-campaign/ngspice-run.log` and `ngspice-version.txt`: execution/version evidence.
- `coaxial_verification.csv` and `coaxial_verification.json`: all 36 reduced electrical comparisons.
- Server copy: `/opt/fan-research/2026-10-21/material-campaign`.

These results are saved project artifacts, not a live backend feeding the existing website. Publishing reviewed imports/shared records into that lab remains on the task list.

## Primary sources

- Daikin property table: https://www.daikinchemicals.com/solutions/technical-challenges/electrical-properties.html
- Victrex 450G: https://www.victrex.com/en/downloads/datasheets/victrex-peek-450g
- SCHOTT technical sheet: https://www.schott.com/-/media/project/onex/products/b/borofloat/downloads/schott-borofloat-technical-data-sheet-english-26032019.pdf?rev=aa66d15af04a4ce7994f5e7699350364
- CoorsTek supplier table: https://www2.coorstek.com/media/4235/advanced-alumina.pdf
- ngspice: https://ngspice.sourceforge.io/docs.html
- Coaxial reference: https://github.com/swtbkim/electrostaticSimpleFoam/blob/main/examples/coaxialCorona/exact_coaxial.py
- Material-dependent corona experiments: https://nht.xjtu.edu.cn/202018E.pdf
- Electrode degradation study: https://www.nature.com/articles/s41598-021-03447-w
