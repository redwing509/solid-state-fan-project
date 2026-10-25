# thermal1d vs OpenFOAM — corrected legacy-air300 thermal case, t = 10 s

Date: 2026-10-24 (PDT). Tolerances and basis: `ACCEPTANCE_CRITERIA.md` §B, committed before this comparison. No tuning.
thermal1d: 1024 cells, dt = 5e-4 s, Crank–Nicolson, inputs `inputs/legacy_air300_corrected.json` only.
OpenFOAM metrics: extracted with `scripts/extract_openfoam_metrics.py` (pure NumPy, cell volumes from the ASCII polyMesh;
domain volume 7.6838393e-03 m³ = 0.320 × 0.08004 × 0.300; raw cell max of the EHD-on baseline reproduces
the previously reported 346.913 K). Plate temperature = T_P + g·d on patch `down` (d = 0.268–0.287 mm).

OpenFOAM runs (Fan research host, pinned image, OpenFOAM 4 `buoyantBoussinesqPimpleEHDFoam`, run manifests in `results/openfoam/`):
- B1 control: `thermal-fix-20261024/ehd-off-control` — corrected baseline inputs with hole `elecPot` 0 V and `chargeDens` 0, `maxDeltaT 0.005`; status finished, return code 0, no NaN/Inf.
- B2 baseline: `thermal-fix-20261024/corrected-baseline` (EHD on, 7540 V).

## B1 — EHD-off conduction control (same physics): **PASS**

| Quantity | thermal1d | OpenFOAM | rel. diff | tolerance | result |
|---|---|---|---|---|---|
| wall heat flux (W/m2) | 187 | 187 | 0.00e+00 | 0.01 | PASS |
| peak (plate) T rise (K) | 134.81 | 134.85 | 3.34e-04 | 0.02 | PASS |
| mean T rise (K) | 19.072 | 19.071 | 3.03e-05 | 0.01 | PASS |
| OF plate T uniformity (max-min)/rise | 0 | 0.00097423 | 9.74e-04 | 0.02 | PASS |

Absolute values: plate T thermal1d 434.807 K vs OpenFOAM 434.852 K (max) / 434.827 K (area mean);
mean T 319.0721 K vs 319.0715 K. OpenFOAM raw max cell value 432.217 K (cell centre 0.28 mm off the wall; for information).
Wall heat flux is imposed identically by both (k·9350 = 187 W/m², 17.95 W over 0.096 m²); the mean-T agreement confirms the heat actually entered.

## B2 — EHD-on corrected baseline (different physics; reported, not a cross-check): **FAIL (expected)**

| Quantity | thermal1d | OpenFOAM | rel. diff | tolerance | result |
|---|---|---|---|---|---|
| wall heat flux (W/m2) | 187 | 187 | 0.00e+00 | 0.01 | PASS |
| peak (plate) T rise (K) | 134.81 | 49.595 | 1.72e+00 | 0.02 | FAIL |
| mean T rise (K) | 19.072 | 1.0621 | 1.70e+01 | 0.01 | FAIL |
| OF plate T uniformity (max-min)/rise | 0 | 0.86194 | 8.62e-01 | 0.02 | FAIL |

OpenFOAM plate T 306.85–349.60 K (area mean 331.70 K), raw max cell 346.913 K, mean 301.062 K.
As expected, thermal1d (zero-flow limit, 434.81 K) bounds the OpenFOAM plate temperature from above. The OpenFOAM mean-T rise
(1.06 K vs 19.07 K for pure storage) means ~94 % of the 179.5 J supplied in 10 s has been advected out through the open boundaries.
**thermal1d is not a second engine for the EHD-driven result.** A second engine for that case needs a coupled EHD/flow/heat solver
(e.g. an independent OpenFOAM v2412 port or another CFD code), with its own verification.

## Verdict

- Verified (code + solution verification): yes — 34/34 checks, `VERIFICATION.md`.
- Two-engine agreement for the **flow-off conduction control**: yes (B1 PASS, all differences ≤ 0.1 %, tolerances 1–2 %).
- Two-engine agreement for the **EHD-on baseline**: no, and not expected (B2).
- Validated against experiment: no.
