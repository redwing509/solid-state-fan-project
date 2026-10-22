# Fanless fan project instructions

Read `TASKS.md` and the latest `outputs/Simulation_Progress.md` and campaign report before continuing this project. Keep `TASKS.md` current as tests finish, fail, reveal gaps or generate new follow-ups. Copy the current user-facing task list to `outputs/Project_To_Do.md` after edits and retain the project notes on the user's mail VPS when working there.

Read `outputs/Project_Parameters.md`. The user authorizes this computer and its GPU for simulations, but local simulation CPU/GPU utilization must not exceed 50%. Use enforceable limits and monitoring. A GPU power cap or memory limit is not a utilization cap; if the software cannot reliably respect the limit, queue it or use mail. Do not launch unrestricted local GPU workloads.

Notify the user before launching a heavy-load simulation or a job needing compute beyond the existing limits. Estimate CPU/GPU, RAM/VRAM, runtime and storage; work with the user to find the compute. Do not silently raise caps or provision paid resources.

Standing user direction (October 21, 2026): run broad tests at 110, 220, 330 and 440 V across materials and material combinations; find and use as many suitable independent simulators/virtual labs as useful, then compare results. Expand finite, documented matrices over time. This is a continuing research priority, not a claim that all materials or simulators have been covered.

Use task-composer and the smallest reliable workflow. Preserve existing authorization for bounded subagents and use of the user's mail VPS. Use public sources read-only when helpful. Never send credentials or unrelated private data to third parties. No paid services, purchases or third-party private uploads without task-level authorization.

Keep line supply voltage and phase separate from electrode voltage and waveform. Do not infer a converter transfer function or label identical perfect-conductor simulations as material comparisons. Distinguish registered, blocked, running, completed and experimentally validated cases. Do not infer fan airflow, ozone, noise, insulation qualification or commercial suitability from reduced electrical models.

Connection: existing SSH alias `mail` with strict host-key verification. Research root `/opt/fan-research/2026-10-21`. Credentials remain in their existing secure locations, never in project files. Isolate server jobs and preserve other services.

Active batch: 314 jobs submitted to mail's single-worker queue on October 21, 2026. Read `queue/status.json` on mail and `outputs/queue/manifest.json` locally before launching more work; do not start a second queue worker or duplicate existing case IDs. Runner: `queue/fan_queue_worker.py`, log: `queue/worker.log`, per-case `queue/cases/<id>/result.json`. One job at a time, 2 CPUs/4 GB, no network, pinned runtime images. `queue/STOP` stops new job starts after the current case; current case time limit still applies. Runtime limits: 600 s coaxial, 900 s duct, 3,600 s legacy. Three consecutive failures pause a family; low disk/output limits halt new jobs. Executed is not validated. Review failures and manifest hashes before retrying. Current worker survives chat/SSH closure; it is not installed as a boot-start service.

Hourly thread follow-up `fan-simulation-queue-check` already exists. Update/reuse it instead of creating another. Stay quiet during healthy progress; notify on completion or actionable failures/resource decisions, then pause the follow-up when the batch becomes terminal. Server-side `queue/watch_comparisons.py` refreshes comparison snapshots and has its own lock; do not start duplicate watchers.
