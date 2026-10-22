# Solid State Fan Project

Private research workspace for an electricity-driven air mover without mechanically moving airflow components.

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
