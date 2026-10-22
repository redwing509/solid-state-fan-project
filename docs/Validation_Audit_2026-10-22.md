# Validation audit — electrical, duct and thermal evidence

October 22, 2026. Read-only analysis of existing fields; no solver run or cap increase. This is an internal independently coded calculation review, not independent laboratory reproduction or experimental validation. Raw results: validation/validation_audit_v2.json. Mathematical cross-check: validation/audit_math_checks.json.

## Electrical reference formulation and coordinate audit

The reduced model assumes steady radial unipolar drift, no diffusion/advection, fixed injected charge and constant mobility/permittivity. Conservation gives current per length I'=2πr μρE. Gauss's law then gives E(r)²=A+B/r², where A=I'/(2πεμ), B=a²(Ea²−A), and I'=2πa μρa Ea. The integral of this field across a=0.001 m to b=0.1 m must equal electrode voltage. Mobility units are m²/(V s), charge density C/m³, and I' is A/m.

The original comparator used adaptive quadrature and Brent's method. This audit instead evaluated a closed-form voltage primitive and used bisection, then independently checked that primitive against log-radius Simpson integration on all 36 physical settings. The worst relative integrated-voltage discrepancy was 5.64e-15. Recalculated reference current agrees with the old calculation across 216 cases to 8.21e-16 relative difference. This confirms the reference calculation within these assumptions; it does not validate the injection law against nature.

The mesh is a quarter annulus of 0.01 m depth. Converting patch current to full-cylinder current per length uses division by 0.25×0.01 m. This normalization is supported by blockMeshDict; polygonal representation and discretization remain part of numerical error.

The sampling file uses distance from start, not radius. Its actual start `(0.00077782,0.00077782,0.005)` has radial magnitude 0.00110000359309 m, rather than exactly 0.0011 m. The old offset differs by about 3.59 nm. Recomputing all 216 profiles with the actual start changes field relative-L2 error by at most 1.51142e-06 in absolute dimensionless error (about 0.000151 percentage points). Preserve both metrics; use corrected coordinates in future comparisons. These are sampled-profile norms, not full-domain norms.

Disposition: analytical formulation, units, sector normalization and coordinate mapping now have a second implementation check. Full iterative-error isolation, quantitative discretization uncertainty, whole-domain checks and qualified independent technical review remain open. No retroactive acceptance threshold is applied.

## Duct paired controls and conservation

All 90 stored final duct fields were read. Maximum relative boundary volume-flux imbalance was 6.29921e-09; maximum relative logged patch-current imbalance was 1.90053e-06. These are final stored/logged quantities at finite output precision, not complete uncertainty estimates.

The inlet explicitly prescribes U=(1,0,0) m/s. Therefore these simulations impose throughflow and cannot demonstrate self-generated fan delivery or an increase in CFM. At nominal 30 kV / mobility 1.8e-4 / injection 4.465e-5, force off/on outlet rates are 0.0011429999995 and 0.0011430000009 m³/s respectively; they are effectively the same prescribed throughput. Maximum cell speed changes from 1.263839 to 1.305362 m/s, a local redistribution rather than a delivered-flow increase.

The source divides electrical force by fluid density and uses kinematic pressure with dimensions m²/s². Multiply pressure differences by rhoFluid to obtain Pa; raw p values are not Pa. A future pressure/flow assessment must define pressure averaging, static versus total pressure, domain thickness/symmetry and external load before a comparison. A self-driven fan curve requires different boundary conditions and a separately documented case; none was launched here. Mesh/domain sensitivity and external measurements remain pending.

## Thermal input and control audit

TEqn.H uses alphaEff=nu/Pr+alphat. The cases select laminar simulation and the stored internal alphat maximum is zero. With rho0=1.225 kg/m³, Cp0=1000 J/(kg K), and nu=1e-5 m²/s, the laminar conductivity is rho0 Cp0 nu/Pr. At Pr=0.9 it is 0.0136111 W/(m K); with gradient 9350 K/m, imposed laminar heat flux is 127.263889 W/m². The separate declared kf=0.02 does not replace nu/Pr in this equation. This discrepancy is **W/m², not W/mA**; no current normalization enters the calculation.

Two controls reach 187 W/m²: Pr=0.6125 with gradient 9350, or Pr=0.9 with gradient 13738.77551. Their ratio to the original heat input is 1.46938776. They change different physics: the first changes thermal diffusivity, whereas the second changes boundary gradient. Equal heat input is insufficient to make their temperature solutions equivalent. The heated patch area calculated from mesh vertices/faces is 0.096 m² in the modeled extrusion. No mirroring multiplier is applied to the following powers.

| Control | Saved time (s) | Imposed heat flux (W/m²) | Modeled heated-wall input (W) | Maximum internal-cell T (K) |
| --- | ---: | ---: | ---: | ---: |
| consistent_Pr | 10 | 187.000 | 17.952 | 347.000 |
| corrected_wall_flux | 10 | 187.000 | 17.952 | 359.475 |
| ambient_control | 10 | 127.264 | 12.217 | 340.412 |
| consistent_Pr_ambient | 10 | 187.000 | 17.952 | 346.913 |
| corrected_wall_flux_ambient | 10 | 187.000 | 17.952 | 359.380 |
| zero_injection_original | 10 | 127.264 | 12.217 | 408.590 |
| consistent_Pr_ambient_zero_injection | 10 | 187.000 | 17.952 | 432.159 |
| consistent_Pr_ambient_timestep | 6 | 187.000 | 17.952 | 347.198 |

At matched 10 s, changing ambient treatment changes the maximum internal temperature from 347.000 to 346.913 K for the consistent-Pr pair and 359.475 to 359.380 K for the corrected-gradient pair. This is only one statistic in these cases and does not establish general ambient insensitivity. The zero-injection controls retain zero volume flow; their heating is transient and cannot be treated as a steady fan-cooling reference.

The timed-out case's last log reached 6.34411 s, but its last saved field is **6.0 s**. The table uses saved-field time. The fixedGradient temperature patch does not store explicit wall values in these fields; exact wall reconstruction is still pending. Cell maxima must not be relabeled wall temperatures. Heated-wall input has been audited, but a full transient energy balance including storage, advection and other boundary diffusion has not yet been closed. Consequently neither thermal validation nor a heat-transfer coefficient is accepted.

## Next controlled work

1. Preserve this audit, corrected-coordinate metrics and all previous snapshots. Review comparator changes before replacing the historical snapshot.
2. Reconstruct wall values using the solver's geometry/discretization and close the transient thermal balance; compare timestep controls only at common saved times. Keep the incomplete case separate.
3. Quantify pressure effects and numerical uncertainty in the prescribed-throughflow duct model before proposing a self-driven boundary-condition study.
4. Resolve physical air properties and source experimental conditions before choosing between the two 187 W/m² controls. Freeze the next model/protocol revision before collecting unseen acceptance data.

No new material ranking, mains-to-electrode mapping, emissions, sound, endurance, insulation or product-performance claim follows from this audit. Results and notes remain on simulation-results pending owner review for main.
