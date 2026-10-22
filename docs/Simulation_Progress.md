# Fanless fan — independent simulation progress

Date: October 21, 2026.

Latest continuation: see `Voltage_and_Materials_Campaign.md` for 300 completed dielectric parameter cases across 110/220/330/440 V, plus 36 reduced coaxial electrical comparisons. All passed their numerical comparison thresholds; none establishes fan/material performance. The 10,800-candidate material register remains pending EHD simulation. Read `Project_To_Do.md`, `Simulator_Comparison_Register.md` and `Project_Parameters.md` before scheduling more work. Local CPU/GPU use is limited to 50%; notify the user before heavy-load simulations and choose additional compute together.

New status: the original full EHD case completed at time 10 s, exit 0. Numerical review is saved in `Legacy_Benchmark_Review.md`. The implied wall heat flux is 127.264 W/m² versus the documented 187 W/m², so experimental validation remains open. A second EHD implementation is now built in OpenCFD v2412; its initial coarse/medium reference runs completed and the finest hit its initial cap. A **314-job serial queue is running on mail**; see `Queue_Status.md` and `queue/manifest.json`. All 314 input preparations passed before launch. Retrieve live status before stating completion counts.

## Verified outcome

The laptop can reach the user's mail VPS using the existing SSH alias with strict host-key checking. The OpenFOAM EHD solver built successfully and completed a short coupled-physics startup run. This is an execution milestone, not validation of a commercial fan.

The original brief has been recovered into `Fanless_Fan_Project.md`. The hosted lab remains active at https://ionic-wind-virtual-lab.spokanelawncare.chatgpt.site and restricted to the owner's account. Its illustrative 80-case sweep has not been calibrated by these simulations. The website has not been connected to a live server backend; browser-local notebook data requires export to move between devices.

## Reproducible setup

| Item | Recorded value |
| --- | --- |
| Server folder | `/opt/fan-research/2026-10-21` |
| Solver | https://github.com/nzhtbyn/buoyantBoussinesqPimpleEHDFoam |
| Solver commit | `cfd66422bce0e17fa4b2ad0b622e37ad7a553fcd` |
| Runtime | OpenFOAM Foundation 4.1 |
| Official image | `openfoam/openfoam4-paraview50:4.1` |
| Image digest | `sha256:a9cde0fffd6dee35f1d6fac0494d8595850aa8063005997a75c8430666f6c230` |
| Container limits | 2 CPUs, 4 GB RAM, 256 processes; no network, no added Linux capabilities |
| Inputs | Upstream supplied geometry and transport/electrical fields |
| Supplied electrode potential | 7,540 V relative to grounded boundary |
| Mesh | 4,700 cells, 9,702 points; `checkMesh` reported `Mesh OK` |

The solver's build output location was changed in a working copy from the runtime's application directory to `/work/bin`. The original public checkout was preserved. The startup case changed end time and write interval to 0.001 s, with at most two saved outputs. It reached 0.001 s and exited normally. At its final reported corrections, cumulative continuity error was approximately 1.25e-10, potential residual 2.08e-6 and charge-density residual 1.39e-5. These are numerical diagnostics, not physical error bounds.

Local evidence: `benchmark-logs/startup-solver.log` and `benchmark-logs/mesh-check.log`. Remote build evidence: `build.log`; scripts: `run-benchmark.sh` and `run-full-case.sh`.

## Longer supplied case

A separate copy named `benchmark-case` uses the original 10 s end time and 0.5 s write interval. The 180 s capped trial ended without completing the case; its last logged simulated time was 0.562753 s and it preserved a 0.5 s restart point. A detached continuation was then launched from that checkpoint with a 3,600 s wall-clock cap. It is named `fan-ehd-long-20261021`, with the same two-CPU, 4 GB, network-disabled limits. It can continue if this chat closes or the laptop disconnects.

Checked `benchmark-case/log.continuation` and `continuation.exit`: exit code 0, normal `End`, final time 10 s. The continuation took 2,243 wall-clock seconds. Finite fields, late-run change and volume-flux balance were reviewed; see `Legacy_Benchmark_Review.md`. The source's thermal discrepancy prevents an experimental validation claim. No notification automation was created.

## Meaning and next work

The author's benchmark compares local heat transfer over a heated plate with a wire electrode. It does not establish our device's pressure-flow curve, wall-power efficiency, ozone emissions or sound level. Next steps are full case completion, conservation and mesh/time-step checks, and a quantitative comparison with the published experiment. Only then should the geometry be adapted to the fan and the browser's assumed cell curves replaced.

The 440 VAC commercial input remains a separate supply/converter question. Applying 440 V directly as the simulated electrode potential would not reproduce the present 7.54 kV corona case. No physical 440 VAC system was tested.

An additional open-source candidate is https://github.com/swtbkim/electrostaticSimpleFoam, documented for OpenCFD v2412, with coaxial-corona verification cases. It was researched but not installed or executed. The official commercial comparison is COMSOL's Ionic Wind model: https://doc.comsol.com/6.4/doc/com.comsol.help.models.edis.ionic_wind/ionic_wind.html . Licensing was not established and no paid service was started.

## Mobile access

The lab URL can be opened from a phone with the same account. The user subsequently confirmed successful phone-to-PC access through the ChatGPT app. This completes the phone → PC → mail working route. The earlier Windows CLI attempt did not establish pairing; the user completed access through the app. Further instructions and connection details are in `Phone_Access_and_Server_Connection.md`.
