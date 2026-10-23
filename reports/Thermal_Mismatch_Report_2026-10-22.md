<!-- project=solid-state-fan-mismatch round=3 rc=0 secs=620.5 session=20261022_153421_fe3885 ok=True -->
Now I have everything needed for a corrected report.

---

**Corrected Diagnosis — Solid State Fan Legacy Benchmark Thermal Mismatch**
All values verified read-only against live files on mail and local artifacts. No heavy jobs run, no data modified.

---

**1) Units and definition of "W/mA"**

The unit is **W/m²** (heat flux per unit area). "W/mA" is a mislabel and should be corrected in all downstream documents.

- Upstream: `/opt/fan-research/2026-10-21/legacy-ehd/README.md` lines 39 and 41: "heat flux of 187 W/m²", "heat flux of 187 W/m2".
- Solver: `buoyantBoussinesqPimpleEHDFoam/TEqn.H` has no Joule-heating source term and no current-normalized flux. The only thermal input is the wall temperature gradient.
- `Validation_Audit_2026-10-22.md` line 27 (local copy) states explicitly: "This discrepancy is W/m², not W/mA; no current normalization enters the calculation."

---

**2) Inputs producing 127.264 W/m² — full recomputation**

All from `/opt/fan-research/2026-10-21/benchmark-case/`:

| Parameter | Value | File / line |
|---|---|---|
| ρ₀ | 1.225 kg/m³ | `constant/transportProperties` line 42 |
| Cp₀ | 1000 J/(kg·K) | line 44 |
| ν (kinematic viscosity) | 1e-5 m²/s | line 40 |
| kf (declared, **unused by TEqn.H**) | 0.02 W/(m·K) | line 46 |
| Pr (laminar) | 0.9 | line 57 |
| TRef | 300 K | line 54 |
| beta (thermal expansion) | 3e-3 1/K | line 51 |
| Wall gradient (TBC) | 9350 K/m | `0/T` line 35 (`down` fixedGradient) |
| Ambient (internalField) | 300 K | `0/T` line 20 |

`TEqn.H`: `alphaEff = turbulence->nu()/Pr + alphat`; laminar → alphat=0 (confirmed: `alphat_internal_max_m2_s = 0.0` in all 8 controls).

Effective conductivity: k_eff = ρ₀ × Cp₀ × ν / Pr = 1.225 × 1000 × 1e-5 / 0.9 = **0.0136111 W/(m·K)**

Imposed heat flux: q = k_eff × gradient = 0.0136111 × 9350 = **127.2639 W/m²**

Heated-wall area (65 faces, sum of `face_area_m2` in `legacy-review/heated_wall_profile.csv`): **0.096 m²**
Wall heat input: 127.2639 × 0.096 = **12.217 W**

**Voltage**: `0/elecPot` lines 46-50: `hole` patch = `fixedValue uniform 7540` V; `down` (plate) = 0 V. **Imposed: 7540 V.**

**Current**: No current boundary condition exists anywhere. The wire surface charge density (`0/chargeDens` line 49) is `1.743e-4 C/m³` — a charge density, not a current. The resulting current is a **computed output** (`10/curDens`, `type calculated`), not an input. Integration of the `curDens` y-component over the 65 heated-wall faces at t=10 s gives **≈21.7 μA** (0.0217 mA) total. No prescribed current appears in any case input file.

**Joule heating**: TEqn.H has no `curDens · elec` source term. Voltage and current feed the momentum equation (EHD body force ρₑE) but do **not** enter the thermal calculation. They are inputs to the electrical/momentum system only.

---

**3) Origin of documented 187 W/m²**

- Source: `/opt/fan-research/2026-10-21/legacy-ehd/README.md` line 39, attributed to Owsenek & Seyed-Yagoobi (1997), DOI 10.1115/1.2824148.
- The 1997 paper text (extracted in full via doi.org) does **not** contain the literal "187". It cites currents in μA/m (e.g. 188 μA/m at 20 kV, 4 cm wire height) and peak h ≈ 17 W/m²·K. The 187 W/m² figure is treated as **digitized** from Fig. 5 (2 cm wire height — matching our 2 cm gap) and carries digitization uncertainty.
- **Arithmetic proof of internal inconsistency**: 187 = 0.02 × 9350 exactly. The case author sized the gradient as 187/kf = 9350 K/m assuming kf=0.02 would be the effective conductivity. The solver uses 0.0136111 W/(m·K) instead.
- Ratio: 187 / 127.2639 = **1.46939** = 0.02 / 0.0136111 exactly.
- Two single-parameter changes reproduce 187.0 W/m² (both verified in `validation_audit_v2.json`):
  - Pr: 0.9 → 0.6125 (gradient stays 9350): flux = 1.225×1000×1e-5/0.6125 × 9350 = **186.99999 W/m²**
  - gradient: 9350 → 13738.77551 K/m (Pr stays 0.9): flux = 0.0136111 × 13738.77551 = **187.0 W/m²**
- Neither control uses standard 300 K air (real air: k≈0.0262 W/(m·K), Pr≈0.71, ν≈1.46e-5 m²/s). Both 0.02 and 0.0136111 are outside the physically expected range.

---

**4) Ambient-temperature treatment**

- Original case (`0/T`): `internalField uniform 300` K, but inlet patches (`right`, `up`) are `zeroGradient` — no fixed ambient inlet temperature. `legacy_review.json`: `ambient_fixed_temperature_boundary: false`. This deviates from the paper's Table 1, which specifies "T = T₀ for inflow" (Neumann/Dirichlet inflow BC).
- Ambient controls (e.g. `legacy-8266a66833` = consistent_Pr_ambient): set `fixedValue uniform 300` on inlet patches (`ambient_fixed: true`).
- Effect at matched 10 s (max internal cell T):
  - consistent-Pr pair: 347.000 K (no fixed ambient) → 346.913 K (fixed 300 K): Δ = **−0.087 K**
  - corrected-gradient pair: 359.475 K → 359.380 K: Δ = **−0.095 K**
- The effect is negligible at 10 s, but the missing fixed inlet T remains a real boundary-condition deviation for long-time energy closure. The 300 K internalField is the reference/initial value, not an imposed boundary.

---

**5) Eight thermal control cases**

From `validation_audit_v2.json` (`thermal` array, 8 entries; 7 executed, 1 timeout):

| Label | Case ID | Pr | gradient (K/m) | ambient_fixed | flux (W/m²) | wall W | Tmax (K) | time (s) | status |
|---|---|---|---|---|---|---|---|---|---|
| consistent_Pr | legacy-92814a16d6 | 0.6125 | 9350 | false | 187.000 | 17.952 | 347.000 | 10 | executed |
| corrected_wall_flux | legacy-828b718f0d | 0.9 | 13738.78 | false | 187.000 | 17.952 | 359.475 | 10 | executed |
| ambient_control | legacy-43ef982684 | 0.9 | 9350 | true | 127.264 | 12.217 | 340.412 | 10 | executed |
| consistent_Pr_ambient | legacy-8266a66833 | 0.6125 | 9350 | true | 187.000 | 17.952 | 346.913 | 10 | executed |
| corrected_wall_flux_ambient | legacy-78246e4701 | 0.9 | 13738.78 | true | 187.000 | 17.952 | 359.380 | 10 | executed |
| zero_injection_original | legacy-202fc5f9af | 0.9 | 9350 | false | 127.264 | 12.217 | 408.590 | 10 | executed |
| consistent_Pr_ambient_zero_injection | legacy-bad9d0c386 | 0.6125 | 9350 | true | 187.000 | 17.952 | 432.159 | 10 | executed |
| consistent_Pr_ambient_timestep | legacy-91be60c7e7 | 0.6125 | 9350 | true | 187.000 | 17.952 | 347.198 | 6 (log: 6.34) | **timeout** |

All cases: laminar, alphat=0, boundary volume-flux imbalance ≤3.4e-07.

**What they demonstrate:**
- The two 187 W/m² fixes (Pr=0.6125 vs gradient=13738.78) produce materially different temperature fields (347.0 K vs 359.5 K max): equal imposed heat input is not a unique fix; the choice of which parameter to change changes the physics.
- Ambient fixing (300 K inlets) shifts max internal T by <0.1 K at 10 s — negligible short-term, but a real BC deviation for long-time closure.
- Zero-injection cases (no EHD body force) run 50–70 K hotter with zero volume flux: the EHD flow carries the heat; without it, temperature accumulates transiently. These are not steady-state references.
- The timestep control (maxCo=1) timed out before 10 s (last saved field at 6.0 s); its 347.198 K is not comparable to the 10 s cases.
- No wall-temperature reconstruction was completed (fixedGradient fields do not store patch T values); no heat-transfer coefficient was accepted.

---

**Conclusion**

**Likely cause** (high confidence — arithmetic is exact and closed): the benchmark case is internally inconsistent. The upstream author sized the wall gradient as 187/kf = 9350 K/m assuming kf=0.02 W/(m·K) would be the effective conductivity, but the solver's TEqn.H computes k = ρ₀·Cp₀·ν/Pr = 0.0136111 W/(m·K) from ν=1e-5 and Pr=0.9. The ratio 187/127.264 = 1.46939 equals 0.02/0.0136111 exactly, confirming the gradient was back-computed from the wrong k.

**Secondary issues** (medium confidence):
- The 187 W/m² figure's provenance in the 1997 paper is unverified (literal value not found in extracted text; likely digitized from Fig. 5).
- kf=0.02 and Pr=0.9 do not match standard 300 K air (k≈0.0262, Pr≈0.71).
- No fixed ambient inlet temperature in the original case (300 K is initial field only, not a boundary condition).
- No current is imposed; the 21.7 μA at t=10 s is a computed output. Voltage (7540 V) and current do not enter the thermal equation.

**No physical-validation claim is made.** This is a numerical/audit diagnosis only.

**Proposed next numerical test** (single control run, not a fix to main): one case with self-consistent 300 K air (ρ=1.225, Cp=1005, ν=1.46e-5, Pr=0.71 → k≈0.0263 W/(m·K)), gradient = 187/0.0263 ≈ 7110 K/m, fixed 300 K inlets, maxCo=2. In parallel, digitize the 1997 paper's Fig. 5 h(x) curve (labeled "digitized, with uncertainty") to determine what heat flux the experiment actually used before freezing any acceptance protocol.

---

RESULT

Diagnosis confirmed and refined. The "W/mA" label is definitively wrong — the unit is W/m². No current normalization exists in TEqn.H; voltage (7540 V, `0/elecPot` line 49) and charge density (1.743e-4 C/m³, `0/chargeDens` line 49) feed the momentum equation only, not the thermal calculation. No current is imposed; the ≈21.7 μA at t=10 s is a computed output (`10/curDens`, type calculated). Heated-wall area is 0.096 m² (65 faces, `heated_wall_profile.csv`, confirmed in `legacy_review.json` and the audit). Ambient: original case has no fixed inlet T (300 K is initial field only, `ambient_fixed_temperature_boundary: false`); ambient controls set fixedValue 300 K and shift max T by <0.1 K at 10 s. The 127.264 vs 187 W/m² mismatch is caused by the solver using k=ρCpν/Pr=0.0136111 W/(m·K) while the author sized the gradient from kf=0.02; ratio 1.46939=0.02/0.0136111 exactly. The 187 W/m² provenance in the 1997 paper remains unverified (digitized from Fig. 5). All five items resolved with file paths and line numbers. No data modified, no heavy jobs run, no physical-validation claim.

