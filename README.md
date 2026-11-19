# Solid State Fan Project

Public research project for an electricity-driven air mover without mechanically moving airflow components.

Tracks research, simulator verification, the 110/220/330/440 V supply campaign, candidate materials, numerical comparisons and completed simulation evidence. This is a research record, not a construction-ready electrical design or a claim of validated commercial performance.

## Start here

- `docs/TASKS.md`: continuing task list.
- `docs/Project_Parameters.md`: scope and compute limits.
- `docs/Queue_Status.md`: 314-job queue and its limits.
- `results/queue/status.json`: latest uploaded execution snapshot.
- `results/queue/comparison_snapshot.json`: latest numerical comparisons.
- `docs/Legacy_Benchmark_Review.md`: thermal run and unresolved heat-input mismatch.

Registered is not executed; executed is not validated. Reduced electrical checks do not establish airflow, ozone, noise, electrical protection or commercial readiness. Supply voltage is distinct from electrode voltage and converter behavior.

## Incremental evidence

Completed case inputs, meshes, stored time fields, sampled outputs and logs are retained in compressed raw archives. Large archives are split into bounded pieces; use their manifests to reassemble and check SHA-256 before extracting inside an intended workspace. Runtime images, dependencies/caches, credentials and unrelated host files are excluded. Originals remain on mail.

## Provenance

Pinned public solver snapshots retain their original licenses and attribution. Inclusion does not imply endorsement or experimental validation. See source records and the simulator comparison register.

## Compute policy

Mail runs one simulation job at a time, at most two CPU cores and 4 GB RAM, with per-case timeouts. Local simulation CPU/GPU use is capped at 50%. Notify the user before heavy-load work or requiring more compute; never raise limits or provision paid capacity automatically.


## IonForge

IonForge (`ionforge/ehd_bipolar.py`, the box finite-volume solver) is this project's own electrical EHD solver. It is the second engine for ion current, next to OpenFOAM. It does electrical work only, with no flow. The domain is an infinite half-plane and charge injection at the wire is a fixed density, not a predicted corona law. IonForge reports current, not thrust. Results are model-only and are not experimental validation. Thrust, when reported elsewhere in this project, is single-engine (OpenFOAM) and must be labelled that way.

See [`ionforge/README.md`](ionforge/README.md) for how to run it, its requirements, and its analytic checks.

## Improvements welcome

This project is free and open source under the MIT license. You can use the code, and you can request improvements by opening a GitHub [issue](https://github.com/redwing509/solid-state-fan-project/issues/new) or a pull request from a fork. Every proposed change is reviewed before it is merged. See [CONTRIBUTING.md](CONTRIBUTING.md) and [VALIDATION.md](VALIDATION.md). Submission does not mean acceptance. The project owner reviews the evidence and approves inclusion.

The protected `main` branch contains accepted project changes. The automated [`simulation-results` branch](https://github.com/redwing509/solid-state-fan-project/tree/simulation-results) records incoming simulation evidence every five minutes; these uploads do not mean numerical or experimental validation. Outside submissions are never automatically executed, imported into the research queue or merged. No external contributor receives direct write access by submitting.


## License

MIT — see `LICENSE`. Pinned third-party sources under `pinned_public_source/` keep their original licenses.
