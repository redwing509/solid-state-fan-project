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

## Coding process (adopted Nov 22, 2026)

These four practices apply to coding work on this project. They do not
replace or weaken the full review set, frozen pass rules, or James's
merge approval, which still come first. Following them does not
authorize a push or a merge.

Source: [obra/superpowers](https://github.com/obra/superpowers), pinned at
`22f0b463e7a5e579904dd6211a520321035526f7` (v7.0.2), MIT License,
Copyright (c) 2025 Jesse Vincent. Adapted guides and that LICENSE:
`docs/superpowers-adopted`. Full text: `docs/superpowers-adopted/CODING-PROCESS.md`. Exact brief
addenda: `docs/superpowers-adopted/BRIEF-TEXT.md` and `docs/superpowers-adopted/templates/`.

1. **Test-first** — For bug fixes and new behavior, write the new test
   first and run it. It must fail for the missing behavior or
   still-present bug, not a typo or a compile error in the test. Only
   then write the smallest production change. Skip typo-only and
   docs-only work. Do not edit a frozen pass rule to match a new
   result. If production code was written before that failing run,
   delete it and start from the tests.
2. **Bite-sized written plans** — For fixes that touch more than one
   behavior, more than one production file, or a "must not change"
   control case, write a short plan first. Include the goal and finding
   id, exact file paths, each behavior as its own task (failing test
   and assertions first), and a Review Focus list with a test for the
   control case most likely to be missed. Skip one-line typo or
   docs-only fixes.
3. **Receiving official review findings** — When Claude, the
   controller, PR-Agent, CodeRabbit, gitleaks, trufflehog, a board
   note, or rb.py returns findings, read the complete list before
   changing code. Verify each finding against this repo, the relevant
   toolchain, frozen pass rules, and any decision James already made.
   Accept, accept with a smaller fix, or push back with a file, test,
   and reason. If a finding conflicts with a decision James already
   made, stop and ask him. Implement accepted items one at a time and
   re-run the relevant tests after each. Informal reviews do not
   replace the official set.
4. **Systematic debugging** — For a failing gate or harness error whose
   root cause is not already written in an approved finding: (1) read
   the full error, reproduce it, and check recent diffs, pins, inputs,
   and the environment; (2) diff against a working neighbor and read
   the solver syntax or gate contract if the failure is in generated
   input; (3) test one hypothesis and one variable; (4) write a failing
   test or known-solution assertion first, apply one root-cause fix,
   and re-run the original failing command plus surrounding checks. Do
   not relax a tolerance or a frozen pass rule. If three attempts fail,
   stop and discuss. Never print secrets; do not leave temporary debug
   prints in the submitted change.

Not adopted: the upstream plugin, hooks, telemetry, mandatory
brainstorming before every already-approved fix, extra helper agents
per task, and any flow that would skip the review set or James's merge
approval.
