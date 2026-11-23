<!--
Adapted from obra/superpowers skill "writing-plans",
https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/writing-plans/SKILL.md
pinned at 22f0b463e7a5e579904dd6211a520321035526f7 (v7.0.2).
MIT License, Copyright (c) 2025 Jesse Vincent.
The original copyright notice and permission notice are in ./LICENSE.
This is a shortened adaptation for our pipeline. It does not install the
Superpowers plugin and does not replace our review set or James's merge approval.
-->

# Bite-sized written plans for Codex fixes

Use this when a security-suite fix touches more than one behavior, more
than one file of production code, or has an easy-to-miss control case.
Do not use it for a one-line typo. Do not require a new human design
approval when James has already approved a named finding.

## Where the plan lives

Put the plan in the Codex task brief or in a scratch notes file for that
round. Do not add a `docs/superpowers/` tree to the security-suite repo.
Do not invoke upstream `subagent-driven-development` or auto-push.

## Header

- Goal: one sentence.
- Finding or pass-rule id, if any.
- Files to modify, with exact paths.
- Global constraints: rustc 1.89.0 `--offline --locked -j 2`; original
  code; `forbid(unsafe)` outside suite-sys; no push until the review set
  is clean; no merge without James's yes.

## Each task

A task is one testable behavior. It has:

- Exact file paths (create / modify / test).
- Step 1: the failing test, as a name plus assertions, with the values
  the finding pins.
- Step 2: the command to run and the failure that means the test is
  honest.
- Step 3: the production signature or behavior to implement, not a
  transcript of the function body.
- Step 4: the command that must pass, then the crate test command.
- Review focus: the control case or failure mode most likely to be
  missed (for example the case that must *keep* the old behavior).

Fold docs and changelog updates into the task that owns the behavior.

## Self-check before coding

- Every requirement in the finding has a task.
- There is a control test for the case that must not change.
- The plan is shorter than the code it describes.
- Nothing in the plan tells the implementer to push, merge, or skip the
  official review set.
