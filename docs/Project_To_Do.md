# Tasks

## Active

- [ ] **Apply the validation plan to the completed batch** - See outputs/Validation_Plan.md revision 0.1 and outputs/Batch_Completion_Review.md. A retrospective 28-record reference set is selected. Independently audit electrical comparison assumptions, quantify numerical uncertainty, and perform duct/thermal conservation and paired analyses before predictive use. Freeze reviewed prospective criteria before unseen acceptance runs; no experimental-validation claim.
- [ ] **Resolve incomplete thermal timestep control without automatic retry** - legacy-91be60c7e7 timed out at simulated 6.34411 s under the existing one-hour cap. Preserve the result; prepare a bounded continuation estimate and obtain the user’s decision before more time/compute. Do not silently raise the two-CPU/4 GB limits.

- [ ] **Review community contributions before inclusion** - Public submissions arrive through issues or fork pull requests. Require owner approval and documented validation before merging into protected main. Never automatically execute submitted code or import it into the queue. Automated evidence uploads go to simulation-results and remain subject to review.

- [ ] **Publish project and completed test records to public GitHub** - Repository `redwing509/solid-state-fan-project` created; user approved mail's dedicated repository-only write key and it is registered. Initial upload verified at commit ce5dd97 (205 queue cases plus baseline); publisher completed this batch; all 314 terminal records are backed up. Preserve incremental publishing for future authorized batches; keep raw compressed records, hashes, comparisons and notes current. Never publish credentials, runtime caches or unrelated host files. Monitor `queue/github_sync_status.json`.

- [x] **Finish the 314-job queue and verify terminal backup** - 313 executed; one thermal timeout; none running or waiting. All 314 terminal case records exported and final remote simulation-results commit verified. Metadata hashes and 630 archive/manifest entries checked without discrepancies. Numerical and physical validation remain separate. See outputs/Batch_Completion_Review.md.
- [x] **Complete hourly batch monitoring** - Pause fan-simulation-queue-check after final notes backup is verified. Worker, comparison watcher and publisher reached normal terminal states; no duplicate jobs or retries launched.

- [ ] **Use local hardware only within the 50% ceiling** - User authorized this computer and GPU for demanding simulations, at no more than 50% utilization. Check headroom; enforce CPU quotas and monitor/throttle GPU usage. Queue work or use mail when the GPU limit cannot be reliably enforced. See `outputs/Project_Parameters.md`.
- [ ] **Notify before heavy-load simulations** - Estimate compute, memory/VRAM, runtime and disk needs; notify the user before starting a heavy job or exceeding existing limits so the required compute can be chosen together. Do not silently increase utilization or provision paid capacity.

- [ ] **Standing priority: maximize useful independent testing and compare results** - User instruction, October 21, 2026. Continue seeking suitable simulators and virtual labs, reproduce their benchmarks, run broad finite test matrices, and compare matched outputs. Keep expanding this list as tools, evidence and results appear. Never count duplicate labels as distinct physics or describe unexecuted cases as tested.
- [ ] **Run the 110 / 220 / 330 / 440 VAC campaign** - Preserve these four requested supply scenarios in each applicable test matrix. Keep supply voltage, phase, converter behavior and electrode-drive voltage separate. For the first screen use 60 Hz, single-phase and nominal RMS voltage as explicit assumptions; no hardware compatibility claim.
- [ ] **Expand the materials and combination register** - Start with tungsten, stainless steel, nichrome, copper, aluminum and titanium electrode/collector candidates; air reference, PTFE, PEEK, borosilicate glass and alumina insulation candidates. Add grades, surface states, coatings, catalysts, geometries, thicknesses, temperature, humidity and aging as defensible property data becomes available. A finite matrix is a starting set, not all possible materials.
- [ ] **Resolve the legacy benchmark’s thermal mismatch before experimental validation** - Original case completed normally at 10 s and passed numerical sanity/stability checks. Its equations imply 127.264 W/m² rather than the documented 187 W/m²; ambient temperature treatment also needs control. Eight queued cases investigate these inputs. Obtain reference data and matched boundary/heat balance before claiming experimental accuracy. See `outputs/Legacy_Benchmark_Review.md`.
- [ ] **Review second-solver numerical accuracy and mesh/scheme convergence** - OpenCFD v2412 `electrostaticSimpleFoam` is built. The upstream force-on coarse/medium cases completed; the largest case hit its initial time cap. The new force-off verification queue matches the analytical electrical assumptions and includes three meshes/two schemes. Compare profiles, current, charge balance and residuals; radial exact verification does not establish fan airflow or material ranking.
- [ ] **Build material-aware corona/flow cases** - Include measured or sourced corona-onset and charge injection, electrode surface effects and dielectric charging/leakage before comparing metals. Preserve model versions and uncertainty.
- [ ] **Maintain the simulator comparison register** - Track purpose, access/license, benchmark status, inputs, output units, limitations, numerical independence and result comparisons. Favor useful complementary models over repeated identical assumptions.
- [ ] **Compare electrical input, airflow, pressure and cost at matched conditions** - Use whole-device power and actual converter loss maps; report CFM/W and cost per delivered airflow. Include guards, ozone-treatment pressure drop and array interactions.
- [ ] **Keep the lab and portable records current** - Save campaign results and notes locally and on mail. The existing private lab is a planning interface; its notebook is browser-local and is not a live shared server backend. Add reviewed result imports/shared storage in a later lab update.

## Waiting On


- [ ] **Specific converter and electrode-drive architecture** - Need actual transfer function, phase/frequency, regulation, efficiency, current limits and compatible supply ranges to turn supply scenarios into predictive fan tests.
- [ ] **Material-grade and surface data** - Need conductivity, permittivity versus frequency/temperature, leakage, roughness/oxidation, corona inception/injection, erosion and catalyst performance. Do not invent missing coefficients.
- [ ] **Commercial simulator access where useful** - COMSOL Electric Discharge/flow and Fluent are candidates; licensing is unverified. No paid compute or software purchase is authorized by this task alone.
- [ ] **Physical validation** - Flow/pressure/wall power, emissions, sound and endurance require measured evidence. Simulation agreement alone does not establish those properties.

## Someday

- [ ] **Expand to thermal, humidity, contamination and endurance studies** - Couple temperature-dependent properties, fouling and electrode/catalyst aging when validated models exist.
- [ ] **Revisit the patent landscape for the selected design** - Compare concrete geometry/material/control choices against current relevant claims before commercialization.

## Done

- [x] ~~Create and name Solid State Fan Project private GitHub repository and register the explicitly approved mail-only repository write key~~ (2026-10-21; `redwing509/solid-state-fan-project`, deploy key ID 167250586; private key remains on mail)

- [x] ~~Finish and numerically review the original full OpenFOAM EHD case~~ (2026-10-21; time 10 s, exit 0, finite fields, stable saved outputs and close boundary flow balance; experimental validation remains open)
- [x] ~~Compile the second EHD implementation in its pinned OpenCFD v2412 environment~~ (2026-10-21)
- [x] ~~Prepare, preflight and launch the 314-job serial mail queue~~ (2026-10-21; case execution/results review remains active)

- [x] ~~Run the first 300 dielectric screening cases at 110 / 220 / 330 / 440 V, with ngspice, finite-volume and analytical comparisons~~ (2026-10-21; all numerical checks passed; no fan/material-performance validation)
- [x] ~~Run 36 reduced coaxial electrical benchmark comparisons~~ (2026-10-21; shooting versus BVP; all numerical checks passed; no airflow or material ranking)
- [x] ~~Register the initial 10,800 voltage/electrode/collector/dielectric-layer candidates~~ (2026-10-21; registered, not EHD-simulated)
- [x] ~~Record local 50% CPU/GPU ceiling and heavy-load notification requirement~~ (2026-10-21)

- [x] ~~Recover prior fan research and retain project files~~ (2026-10-21)
- [x] ~~Verify laptop-to-mail SSH connection and isolated simulation capacity~~ (2026-10-21)
- [x] ~~Build the pinned OpenFOAM 4.1 EHD solver and complete startup/mesh checks~~ (2026-10-21)
- [x] ~~Confirm phone-to-PC access through the ChatGPT app~~ (2026-10-21, user confirmed)
- [x] ~~Create this continuing project task list and record the broad multi-simulator testing priority~~ (2026-10-21)
