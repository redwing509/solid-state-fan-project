# Fanless Fan — Project Start and Global Patent Landscape
Research date: October 21, 2026
Phase: 3 — commercial supply scenarios and virtual lab; earlier research retained below

## Project objective
Develop an electrically powered air mover with no rotating blades, no impeller, and ideally no mechanically moving components. Initial working application: a quiet personal or desk fan; this application is an assumption and can be changed. No airflow, noise, power, price, or size targets have yet been agreed.

## First finding
Yes: direct electrical air movement already exists in published patents. The closest match is electrohydrodynamic (EHD) airflow, also called ionic wind, corona wind, or electrostatic air acceleration. Electricity creates ions near an emitter; an electric field accelerates them toward a collector; collisions transfer momentum to neutral air molecules and produce bulk airflow. This differs from the Dyson design previously discussed, which contains a motor-driven impeller.

This establishes prior disclosure of the broad concept. Patent descriptions do not by themselves establish product performance or commercial practicality.

## Search scope and limitations
Initial worldwide landscape searched through Google Patents and public web search, using English keywords and translated patent records: ionic wind generator, electrohydrodynamic air mover, electrostatic fluid accelerator, corona wind pump, solid-state fan, piezoelectric synthetic jet.
Records reviewed cover US, EP, CN and WO publications, plus a Japanese family counterpart and Spanish/international family links. This is not an exhaustive search of every jurisdiction or a direct search of every national patent-office database. Non-English translations, unpublished applications, indexing gaps, later continuations and current prosecution can affect completeness.
Publication dates below refer to the identified document, not necessarily earliest family priority. An A1/A publication is an application publication, not proof of an issued patent. WO publications are international PCT application publications, not worldwide patent grants. Patent-family links identify related filings; they are not additional independent inventions.

## Priority patent records
| Record | Publication date | Applicant / origin | Relevance |
| --- | --- | --- | --- |
| US3361337A — Ionic wind generators | 1968-01-02 | James N. Hurst | Early portable ventilation device using an electrode and grid to generate airflow electrically. |
| US4643745A — Air cleaner using ionic wind | 1987-02-17 | Nippon Soken, Japan | Established ionic-wind air-cleaning architecture; record links Japanese counterpart JPS60132661A. |
| CN104456751A — Ion wind generating device | 2015-03-25 | Gree Electric Appliances, China | Wire, cylinder and plate electrode arrangement; includes filtering, voltage regulation and an ozone-decomposition element. |
| US20220210945A1 — Ionic wind generator | 2022-06-30 | Ventiva | PCB-integrated emitter/collector air mover for cooling electronics. |
| EP4295956A1 — Electrohydrodynamic ventilation device | 2023-12-27 | Cedrion, Spain | Emitter supports and collector channel geometry addressing electrical isolation and arcing. |
| WO2026080334A1 — Isolation housing for electro-hydrodynamic air mover device | 2026-04-16 | Ventiva | Recent packaging of an EHD air mover with shielding, dielectric PCB and insulating chassis. |

### Historical starting point
US3361337A describes a high-voltage DC supply energizing an electrode and grid, drawing air into the housing region and expelling it through the grid. Google Patents labels this record expired by lifetime. It is useful historical prior art, not a guarantee that a modern implementation avoids later claims.

### Modern claims to examine
- Gree: the published independent claim specifies a sequence of wire, cylinder and plate electrodes with separate ionization and acceleration fields. Dependent claims address filtering and ozone treatment.
- Ventiva 2022: the published independent claim specifies an emitter and collector on opposite sides of a PCB opening, producing airflow through that opening.
- Cedrion: the published independent claim specifies an emitter, at least two collectors defining a channel, and insulating support projections between the emitter and collector ends.
- Ventiva 2026: the published independent claim concerns the isolation housing combination, including a shield, dielectric PCB assembly and nonconductive chassis.

These are preliminary technical summaries of published claims, not infringement or validity conclusions. Current issued claims and official registers have not been fully checked.

## International follow-up map
- Japan: JPS60132661A, linked from US4643745A.
- Cedrion family: WO2022175572A1, ES2921523B2 and US20240145222A1, linked from EP4295956A1.
- Ventiva recent record: WO2026080334A1 lists US20260098527A1 as a corresponding publication.
- Search leads for a later pass: Ventiva electrode maintenance and ozone reduction; Tessera/Panasonic EHD flow paths and field shaping; Korean ionic-wind filings.
Do not infer enforceable scope or present legal status from the family list alone.

## Technology selection
| Approach | Mechanically moving components? | Fit to objective |
| --- | --- | --- |
| EHD / ionic wind | Can operate without them | Best match for initial investigation. |
| Piezoelectric / synthetic jet | Vibrating membrane or plate | Electrically powered and blade-free, but does not meet a strict no-moving-parts objective. |
| Dyson annular outlet | Hidden motor and impeller | Does not meet the project objective. |

The piezoelectric distinction is supported by WO2016032473A1, which describes flexible plates and piezoelectric actuation.

## Engineering questions to resolve
1. Air delivery: measure volume flow, velocity distribution and pressure capability; a local jet velocity alone is insufficient.
2. Efficiency: include the entire power supply in wall-power measurements and compare useful airflow at equal measurement conditions.
3. Acoustics: measure at a defined distance with background noise reported; no moving parts does not establish silence.
4. Ozone and other discharge byproducts: characterize emissions rather than assuming clean air; include treatment losses and aging.
5. Electrical design: high-voltage isolation, touch protection, current limiting, discharge behavior and fault handling are central requirements.
6. Reliability: evaluate dust buildup, humidity sensitivity, electrode degradation, cleaning and arcing.
7. Packaging: determine whether a practical personal fan can deliver useful air after guards and any treatment elements.

The reviewed Gree and Ventiva disclosures explicitly discuss ozone treatment; Ventiva's collector-electrode application also identifies sparking and dust as challenges. No verified airflow-per-watt or maximum-noise value has yet been established for our design.

## Proposed development sequence
- Phase 1 (started): establish prior art and shortlist mechanisms. Initial result: EHD is the best conceptual fit.
- Phase 2: set use case and measurable targets; collect independently supported EHD performance data; compare with a conventional fan benchmark.
- Phase 3: map candidate geometry and controls against relevant issued claims and current national records before settling on a commercial design.
- Phase 4: develop an enclosed, instrumented proof of concept with appropriate high-voltage engineering.
- Phase 5: compare airflow, pressure, wall power, noise, emissions and durability; decide whether to continue, revise or stop.

No parts have been purchased and no hardware has been built. Candidate invention areas remain hypotheses until a deeper prior-art search and experiments support them.

## Source register
All accessed October 21, 2026.
1. US3361337A: https://patents.google.com/patent/US3361337A/en
   Original drawing: https://patentimages.storage.googleapis.com/57/8a/01/315a41a6bcc50c/US3361337-drawings-page-1.png
2. US4643745A: https://patents.google.com/patent/US4643745A/en
3. JPS60132661A (family follow-up link): https://patents.google.com/patent/JPS60132661A/en
4. CN104456751A: https://patents.google.com/patent/CN104456751A/en
5. US20220210945A1: https://patents.google.com/patent/US20220210945A1/en
6. EP4295956A1: https://patents.google.com/patent/EP4295956A1/en
7. WO2026080334A1: https://patents.google.com/patent/WO2026080334A1/en
8. WO2016032473A1: https://patents.google.com/patent/WO2016032473A1/en
9. US20110261499A1 — Collector electrode for an ion wind fan: https://patents.google.com/patent/US20110261499A1/en

## Phase 2 — Feasibility findings and first prototype specification
Updated October 21, 2026. Status: research and preliminary design complete for this iteration; hardware performance remains untested.

### Recommendation
Proceed with an enclosed, modular EHD test cell for a close-range personal fan. Begin with a straight, low-obstruction air path. Add a removable air-entrainment outlet only after measuring the basic cell. Use a rectangular cartridge so electrode assemblies, guards and catalyst carriers can be changed independently. Exterior styling and a Dyson-shaped ring are deferred until airflow is demonstrated.

The intended advantage is eliminating mechanical moving parts. Higher efficiency or lower noise than a good conventional fan is a hypothesis, not an established advantage.

### Evidence and practical limits
| Evidence | Finding | What it means for this project |
| --- | --- | --- |
| Rubinetti et al., Frontiers, 2023 experimental paper [10] | Reports up to 15 m³/h, approximately 8.8 CFM, in a 150 × 150 × 1,000 mm test channel. | Supports small-scale feasibility; not compact desk-fan performance. |
| Same paper, methods [10] | Power derived from high-voltage output voltage/current; flow estimated from point velocity. | Supply losses and a fuller velocity survey are needed for our comparison. |
| Ventiva technology FAQ [11] | Manufacturer reports below 15 dBA in anechoic testing. Public FAQ does not specify distance, operating point or complete test report. | Evidence of low-noise potential, not our achievable maximum-speed rating. |
| Ventiva ozone paper [12] | Describes MnO₂ catalyst treatment and about 70% removal in one roughly 1 CFM example. | Removal is configuration-dependent; it cannot be assumed to scale to our airflow. |
| Noctua NF-A12x25 PWM specifications [13] | Manufacturer lists 60.09 CFM maximum, 22.6 dBA maximum noise, 1.2 W typical and 1.68 W maximum electrical input. | A strong conventional comparator; published ratings require verification in our setup. |

Additional limitations of [10]: the paper describes operation as silent but does not provide a numerical acoustic test result in its reported measurement procedure. Its peak flow, best flow-per-power ratio and minimum power are different operating points. No whole-device wall-power or emissions qualification follows from that study.

The Noctua ratings describe a bare DC fan, not a guarded desk product or its AC adapter. Its maximum pressure and maximum airflow also occur at different operating points. Do not divide unrelated catalog maxima to claim a tested efficiency advantage.

Ventiva's 100 W thermal design power claim concerns heat-removal capacity, not fan electrical consumption [11]. Public sample availability is not established: its FAQ asks users to register interest and says laptop applications are prioritized. Treat it as a potential supplier reference, not a confirmed purchasable module.

### Provisional engineering targets
These are proposed development gates chosen for this project, not measured capabilities or user-approved final product specifications.

| Metric | Gate A: functional demonstrator | Gate B: useful personal fan |
| --- | --- | --- |
| Moving components | None used to generate airflow | Same |
| Delivered flow, with final guards and treatment installed | At least 5 CFM (8.5 m³/h) | At least 15 CFM (25.5 m³/h) |
| Total electrical input, including supply and controls | At most 10 W | At most 15 W |
| Noise at 1 m, same operating point as airflow/power | At most 35 dBA | At most 30 dBA |
| Average airspeed at 0.5 m, over a 100 × 100 mm centered grid | Record, with full profile | At least 0.3 m/s |
| Emissions aspiration | Work toward the 5 ppb ozone criterion using a suitable controlled test | Same, including aging and adverse conditions |
| Stability | 1 hour steady run after engineering checks | 8 hour run, then extended endurance |
| Size | Bench enclosure; no aggressive packaging constraint | Aim for roughly 200 mm-wide head; depth determined by data |

All numerical performance gates must be met simultaneously in one operating mode. The 5 ppb aspiration is inspired by UL's ULE 2998 air-cleaner validation criterion [14]; it is not a claim of certification, a universal exposure threshold, or a determination that this fan falls within that procedure's scope. A qualified test lab must establish an appropriate product test method and the relation between device contribution, background concentration and reported result.

### Functional concept
Air path:
Ambient air → inlet guard → EHD emitter/collector cartridge → low-resistance ozone-treatment carrier → outlet guard/diffuser → user.

Control path:
External low-voltage supply → controller and enclosed high-voltage converter → EHD cartridge.
Cover interlock, fault detection and temperature/current monitoring → shutdown control.
Ozone measurement is an external laboratory instrument during development. A built-in ozone sensor is not assumed accurate enough for release decisions.

This is a functional concept, not an electrical schematic or construction-ready high-voltage design. Select electrode clearance, materials, insulation, voltage and discharge provisions through qualified engineering review. A low-voltage input does not make the internal high-voltage circuit touch-safe.

Place the cartridge in a closed test fixture. The catalyst module must have a large open area; a dense filter could consume the available pressure. Check airflow bypass and catalyst shedding. Evaluate a commercial, supported catalyst medium before considering custom coatings. Avoid an added heater: the objective is a breeze, not heated convection.

### Candidate architecture comparison
| Candidate | First use | Decision |
| --- | --- | --- |
| Straight EHD channel with replaceable cartridge | Establish airflow, noise, emissions and stability | Preferred first experiment |
| Same cell with removable Coanda outlet | Test whether entrainment improves useful delivered flow | Controlled A/B experiment after baseline |
| Parallel cells | Increase total flow without relying on a large pressure rise | Evaluate only after one cell passes |
| Cells in series | Investigate pressure capability if treatment losses demand it | Later experiment; emissions, field interactions and power may rise |
| OEM EHD module | Reduce custom-electrode development if obtainable with supporting data | Keep as alternate path; no availability or price confirmed |
| Piezoelectric jet | Generates flow with a vibrating structure | Excluded from strict no-moving-parts objective |

Air entrainment redistributes momentum and draws in surrounding air; it does not create energy. A ring-shaped EHD amplifier is not a novelty claim: published research already combines EHD with the Coanda effect [10].

### Test plan and decision rules
1. **Prepare the fixture.** Resolve touch protection, cover interlock, fault response, stored-charge management and instrument compatibility before energizing. Use an appropriate high-voltage engineering setup.
2. **Measure the conventional comparator.** Test a guarded 120 mm reference fan with its power supply. Record flow, pressure, watts, sound and the velocity grid. This is test equipment, not part of the fanless design.
3. **Characterize one EHD cartridge.** Record temperature, humidity, operating settings, supply input and high-voltage output where safely measurable. Collect three repeat runs at each stable setting.
4. **Map the flow.** Use a calibrated flow facility or a multi-point area traverse with uncertainty reported. Account for low-speed probe sensitivity, turbulence, grid blockage, leaks and fixture backpressure. Do not multiply a centerline peak by the whole outlet area.
5. **Add components one at a time.** Measure guards, catalyst carrier and outlet diffuser separately, then the full assembly. Record pressure drop and complete flow-versus-pressure behavior.
6. **Measure acoustics.** At 1 m, use identical orientation and environment for both devices, avoiding direct wind on the microphone. Record background, A-weighted level and tonal/hissing behavior. If noise is too close to the background, report a measurement limit rather than an unsupported low number.
7. **Measure emissions.** Use calibrated ppb-capable ozone instrumentation and a defined chamber/ventilation method; sample near the outlet and at the intended user position. Assess other discharge byproducts as indicated by the test lab. Cheap general air-quality sensors or smell are insufficient evidence.
8. **Check stability and aging.** After basic operation, test catalyst loading, electrode wear, humidity and dust effects using a defined protocol. Include worst-case intended operating conditions.
9. **Decide.** Advance only if the complete assembly meets Gate A with an acceptable emissions result and reviewed electrical protection. If treatment destroys useful flow, redesign the open-area path before increasing drive. If repeatable performance is poor, retain the research but pause product development.

Electrical fault findings or elevated emissions stop that test; they are not conditions to compensate for with higher airflow or room dilution. General occupied-room use follows satisfactory engineering and emissions evaluation.

### Procurement and work package
No purchase or vendor contact has been made. Prices, supplier stock and a reliable total budget have not been verified. Obtain comparable quotes for:
- Supported EHD evaluation hardware, if available, with pressure-flow curves, input-power accounting and emissions reports.
- Otherwise, a professionally specified current-limited high-voltage supply and replaceable electrode cartridge.
- Interlocked enclosure, guards, dielectric supports and a modular catalyst carrier.
- Calibrated low-speed airflow and differential-pressure instruments, power meter and sound meter.
- Rental or lab access for ppb ozone analysis and controlled emissions testing.

Do not spend the first budget on exterior tooling. The most valuable initial expenditure is access to reliable airflow and ozone measurements.

### Commercial and invention checkpoint
The broad EHD fan concept and EHD-plus-Coanda approach already appear in prior art. Possible work areas include serviceable packaging, catalyst integration and fault/aging controls, but none is established as new. Once geometry and control behavior are specific, update the published-claim comparison in Phase 1 and check current issued claims and national registers. No freedom-to-operate conclusion is made here.

### Immediate project state
Completed: initial patent landscape, evidence review, candidate selection, provisional targets, functional architecture, test sequence and procurement categories.
Pending physical work: supplier quotations, engineering of the protected electrical assembly, instrument access and measured results.
Next deliverable after those inputs: a dimensioned test-fixture drawing, exact component list and test worksheet. No hardware result, noise rating, certification or product-readiness claim is implied by this document.

### Added sources
Accessed October 21, 2026.
10. Rubinetti et al. (2023), Electrohydrodynamic air amplifier for low-energy airflow generation—An experimental proof-of-concept:
https://www.frontiersin.org/journals/energy-efficiency/articles/10.3389/fenef.2023.1140586/full
11. Ventiva technology and FAQ:
https://ventiva.com/technology/
12. Ventiva (2025), Understanding Ozone:
https://ventiva.com/wp-content/uploads/2025/01/WP_Ventiva_Understanding-Ozone-02-2025.pdf
Manufacturer-reported findings; no claim that its treatment efficiency applies to our design.
13. Noctua NF-A12x25 PWM specifications:
https://www.noctua.at/en/products/nf-a12x25-pwm/specifications
14. UL Solutions, Zero Ozone Emissions Validation:
https://www.ul.com/services/zero-ozone-emissions-validation

## Phase 3 — Commercial supply model and independent simulation shortlist
Updated October 21, 2026.

### Confirmed scope
The user confirmed that “straight 440” means a 440-volt AC supply. The virtual lab includes service inputs through 440 VAC and a default balanced three-phase interpretation at 440 V, using line-to-line RMS voltage. Single-phase and DC options are available for comparison. Supply topology, ratings and compatibility remain engineering requirements, not facts established by the calculator.

The lab is a reduced-order scenario calculator. It does not directly energize hardware, solve plasma/CFD equations or test commercial electrical safety. A 440 VAC service must feed suitable conversion hardware; it is not a direct-electrode-drive recommendation. Any power-supply fan would violate the strict no-moving-parts system objective.

### Virtual lab
Private project Site: https://ionic-wind-virtual-lab.spokanelawncare.chatgpt.site
Publication confirmed successful on October 21, 2026. The Site is private to its owner.

Implemented sections:
- Design bench: parallel cells, imposed pressure, loss factors, conversion efficiency and energy/cost inputs.
- Supply sweep: 24/48 V DC and 120/208/240/277/380/400/415/440 V AC examples.
- Commercial scale: 1, 4, 16, 64, 128, 256, 512 and 1,024 parallel cells.
- Physical test notebook: browser-local, user-entered measurements, kept separate from virtual cases.
- Evidence/model: equations, assumptions and source register.
- Independent checks: external tool shortlist, benchmark sequence and signed-difference calculator.
CSV and JSON exports are available. Browser-local entries require export for portable backup.

### Arithmetic model
Qdelivered = N × Qcell × retention × max(0, 1 − imposedPressure/stallPressure).
Pinput = N × Pcell / (inputEfficiency × HVEfficiency) + auxiliaryInput.
Balanced three-phase line current = Pinput / (sqrt(3) × lineToLineVoltage × truePowerFactor).
Annual kWh = Pinput × annualHours / 1,000.
Five-year cost = cellCost × N + supplyCost + housingTreatmentCost + 5 × (annualEnergyCost + annualMaintenance).

The flow equation is an assumed linear pressure sensitivity, not a measured fan curve or a solved system-curve intersection. Array scaling is additive with a user-supplied retention factor; it does not resolve cell interactions, thermal behavior, space charge or large-array stability. Low/high flow multipliers are sensitivity scenarios, not confidence intervals. Acoustic and ozone performance are unknown, rather than fabricated model outputs.

### Executed virtual sweep
80 arithmetic cases: ten supplies × eight cell counts, including eight 440 VAC cases.
All use illustrative cell inputs: 1 CFM at 1 W discharge, 10 Pa stall pressure, 2 Pa imposed pressure, 0.85 retention, 90% input-conversion efficiency, 80% HV conversion efficiency and 2 W auxiliary load. Price inputs are placeholders, not quotes.

Illustrative 128-cell case: 87.04 CFM, 179.78 W total input, 0.484 CFM/W and 0.248 A from balanced 440 VAC at power factor 0.95. This is not a prediction backed by cell measurements. With equal conversion efficiencies, every service voltage yields the same watts and airflow; voltage changes supply current only.

Under placeholder costs ($25/cell, $300 supply, $150 housing/treatment), that case costs $3,650 upfront. At $0.15/kWh for 4,000 h/year its energy bill is $107.87/year. These figures do not establish commercial competitiveness; installation, load-dependent supply sizing/pricing, demand charges, development and certification are excluded.

The 80 cases are exported with explicit UNVALIDATED_MODEL classification. Automated calculation checks passed for input current, loss/energy accounting, zero-flow behavior, invalid inputs, power-factor effects and sweep coverage. Interface checks exercised the commercial preset and virtual sweep.

### External simulation tools found
| Tool | Recommended role | Limits / provenance |
| --- | --- | --- |
| nzhtbyn/buoyantBoussinesqPimpleEHDFoam [15] | First low-license-cost EHD candidate | GPL-3.0; coupled EHD/flow/heat; validation case and cited paper; targets OpenFOAM 4.1. |
| COMSOL Ionic Wind, application 132191 [16] | Independent commercial reference | Official corona-to-flow example; suitable COMSOL licensing/modules required; price unverified. |
| gyf135/EHD-in-point-to-ring-corona [17] | Experimental benchmark companion | Fluent UDF/case linked to Guan et al. (2018); Fluent access/version review needed; root listing did not show a license file. |
| Qucs-S with ngspice [18] | Converter/circuit analysis | Open-source circuit tool; cannot determine EHD airflow or certify a mains product. |

Research provenance is stronger than a generic “EHD” label, but is not a security audit or successful reproduction. No external solver was installed, compiled, executed or integrated as a live backend in this iteration.

Related but deprioritized:
- iroghair/openFoamEHD: older multiphase/electrowetting framework on OpenFOAM 2.1.1 [19].
- rulzco/phenomenological-dbdActuatorSolver: surface DBD actuator model, not a DC corona-fan drop-in; README targets ESI v2506+ and identifies ongoing development [20].
Do not treat either as a confirmed turnkey validator.

### Recommended independent validation workflow
1. Inspect source, licenses, dependencies and run scripts; pin a commit and environment before execution.
2. Reproduce the selected author's benchmark geometry and conditions before adapting it.
3. Record mesh/time-step convergence, mass and charge conservation and boundary-condition sensitivity.
4. Compare integrated flow, current and velocity profiles across several operating points; use experimental uncertainty to judge differences.
5. Use a second solver implementation where practical. Agreement checks consistency; shared assumptions can produce shared errors.
6. Import validated cell pressure-flow and power curves into a later lab model, then evaluate arrays.
7. Model the chosen converter separately for each input supply through 440 VAC and include its load-dependent loss map.
8. Confirm airflow, emissions, acoustics, durability and electrical protection through physical measurements.

COMSOL's tutorial sets viscosity to 1e−4 Pa·s [16]; check tutorial properties against the actual intended gas and temperature before reuse. Our simulator should not be calibrated by copying a tutorial velocity plot.

### Next engineering milestone
Choose and reproduce one published EHD benchmark, then obtain measured or independently reproduced cell curves. This is the necessary bridge from the current cost/planning lab to a defensible physics model. No commercial-performance or product-safety claim is supported yet.

### Added sources
15. OpenFOAM EHD solver and validation README:
https://github.com/nzhtbyn/buoyantBoussinesqPimpleEHDFoam
16. COMSOL official Ionic Wind model and instructions:
https://www.comsol.com/model/ionic-wind-132191
https://doc.comsol.com/6.4/doc/com.comsol.help.models.edis.ionic_wind/ionic_wind.html
17. Fluent case and associated experiment:
https://github.com/gyf135/EHD-in-point-to-ring-corona
https://journals.aps.org/prfluids/abstract/10.1103/PhysRevFluids.3.043701
18. Qucs-S:
https://github.com/ra3xdh/qucs_s
19. Related multiphase framework:
https://github.com/iroghair/openFoamEHD
20. Related DBD actuator solver:
https://github.com/rulzco/phenomenological-dbdActuatorSolver
All reviewed October 21, 2026. README claims are attributed to their maintainers and were not independently reproduced.

## Authorized simulation host — mail VPS
The user authorized using the mail VPS to load and run simulations/programs. Continuation on October 21 established access from the local Windows laptop: existing SSH alias `mail`, key-based root login, strict host-key verification, 16 CPU cores, roughly 60 GB available memory and 317 GB available disk space at the initial check. Persistent project directory: `/opt/fan-research/2026-10-21`. Connection and phone-pairing status are saved in `Phone_Access_and_Server_Connection.md`.

Once connection details are available, begin with a read-only resource and workload check. Use an isolated project directory/environment and conservative CPU/memory limits; preserve existing services. Inspect the selected solver source and run scripts, pin the solver/runtime versions, reproduce the upstream validation case, and retain logs, mesh statistics, convergence data and output curves. Only after reproduction should the EHD fan geometry be adapted. Do not describe the browser's 80 arithmetic scenarios as independently confirmed simulations.

Prior-session verification: nine local calculation checks passed; interface checks covered commercial presets, the 80-case sweep and signed benchmark differences using explicitly synthetic QA values. In this local continuation, the pinned external OpenFOAM 4.1 EHD solver compiled and completed a shortened startup case on mail. The supplied 4,700-cell mesh passed checkMesh. A longer supplied case was launched separately; consult the simulation report for its final outcome. No physical fan or 440 VAC hardware test has run. A successful solver execution does not validate the browser's assumed airflow, array scaling, power, noise or emissions.




