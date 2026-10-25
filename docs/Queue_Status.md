# Mail VPS simulation queue

Latest completion review: see Batch_Completion_Review.md and Validation_Plan.md. All 314 terminal records are backed up; the batch worker, watcher and uploader completed normally. The hourly batch monitor is being paused after final notes are verified. Earlier progress descriptions below are retained historical context.

Submitted October 21, 2026. **314 jobs are terminal: 313 executed, one thermal timeout, none waiting/running.** This document is a saved snapshot; read the live server status before reporting current counts.

## Job inventory

| Family | Jobs | Purpose |
| --- | ---: | --- |
| Coaxial electrical verification | 216 | Four electrode voltages × three injection densities × three ion mobilities × three meshes × two numerical schemes |
| Wire-and-duct sensitivity | 90 | Five electrode voltages × three injection densities × three mobilities × EHD force on/off |
| Legacy thermal/boundary controls | 8 | Isolate thermal conductivity/heat flux, ambient boundary, zero-charge and timestep effects |
| **Total** | **314** | All 314 passed input preparation before launch |

The six main reference combinations run first, followed by paired duct controls, broader sweeps and the longer thermal cases. The first four queued reference jobs completed successfully at the initial review; the next was running. No family was paused at that check. Execution completion is separate from numerical accuracy and experimental validation.

## Resource and scheduling limits

- One simulation container at a time; at most **two CPU cores and 4 GB RAM**; no swap allowance beyond the memory cap.
- Containers have no external network, no extra Linux capabilities and no new privileges. Pinned runtime images and solver commits are retained.
- Per-job wall-clock caps: **10 minutes coaxial, 15 minutes duct, 60 minutes legacy**.
- Three consecutive failures/timeouts pause that family while other families can continue.
- New jobs stop if free disk drops below **30 GiB**, queue output exceeds **20 GiB**, or the queue's `STOP` file exists.
- Runs continue after chat/SSH disconnection. The worker is not configured to restart automatically after a server reboot. It can resume completed records after reviewing interrupted cases; a lock prevents two workers.
- No local GPU run or paid compute was launched. Notify the user before heavier work or raising limits. Local simulation CPU/GPU utilization remains limited to 50%.

Plan for an overnight-to-one-day batch if most cases finish promptly. Slow cases, holds and timeouts can extend this. The sum of all configured per-job maximums is **66.5 hours**, plus setup overhead; that is a ceiling calculation, not an estimated finish time. Existing pilot times range from seconds for smaller electrical cases to 37 minutes for the original thermal case.

## Automatic result comparisons

A lightweight, low-priority companion refreshes comparison snapshots when completed records change. It limits numerical-library threads to one, runs at most once per minute, gives each comparison a 60-second cap, stops for review after three errors and has a 72-hour lifetime. It does not launch simulations or increase their resource limits.

A thread follow-up named **Fan simulation queue check** is active hourly (automation ID `fan-simulation-queue-check`). It stays quiet during healthy progress and notifies on completion or actionable failures, holds, storage issues or a need for more compute. It must pause after the batch is terminal. The server queue continues independently; the app's follow-up still requires an available connected computer and SSH access to inspect it.

For coaxial cases it compares current, electric-field and charge profiles against the exact reduced solution and reports discrete patch-current balance. It labels these reduced electrical comparisons, not fan validation. Duct/thermal executions retain raw results and remain unvalidated pending matched reference/paired analysis.

The first reviewed 30 kV force-off reference cases showed:

| Radial mesh | Scheme | Current error | Electric-field profile relative L2 error |
| --- | --- | ---: | ---: |
| 48 | linearUpwind | 0.1896% | 0.1223% |
| 96 | linearUpwind | 0.0477% | 0.0308% |
| 48 | upwind | 0.1017% | 0.0837% |
| 96 | upwind | 0.0026% | 0.0380% |

The linearUpwind field error fell by about a factor of four under the first refinement. More meshes and settings remain in progress. Do not infer the convergence order of all quantities from these four rows.

## Live paths on mail

Project root: `/opt/fan-research/2026-10-21`.

- `queue/manifest.json`: immutable submitted job definitions.
- `queue/status.json`: worker state, per-job execution outcomes, current job and held families.
- `queue/fan_queue_worker.py` and `queue/worker.log`: execution runner/log.
- `queue/cases/<id>/job.json`, `result.json`, `log.run` and sampled fields: case evidence.
- `queue/comparison_snapshot.json` and `.csv`: refreshed numerical comparisons.
- `queue/analysis_status.json`: companion comparison state.
- `queue/STOP`: create this file to prevent the next job starting; the current job retains its timeout.
- `queue/preflight.json`: all 314 input preparations passed.

Use the existing SSH alias `mail` with strict host-key checking. No credentials are stored in project artifacts. Preserve IDs/hashes when resuming; do not delete failed cases to conceal them or launch a second worker.

## Interpretation and remaining gaps

The electrical and duct sweeps vary **internal electrode voltages** (10–50 kV), injection and transport parameters. They are not models of 110/220/330/440 V mains converters. The four requested supply scenarios remain in the project campaign, with 300 reduced dielectric cases completed; supply-to-electrode predictions need an actual converter architecture and loss map.

Likewise the 10,800 metal/material candidates remain registered, not EHD-simulated. Current field models do not resolve arbitrary metal surface/grade effects. Duct sweeps use fixed charge injection rather than a newly calibrated material-dependent corona boundary. Avoid turning sensitivity trends into material rankings or product performance claims.

The original legacy case completed at 10 s, but its heat input differs from the documented experiment. The eight thermal controls investigate that discrepancy; see `Legacy_Benchmark_Review.md`.