# Adapted Superpowers guides (adopted Nov 22, 2026, t1288u)

<!--
Adapted from obra/superpowers, https://github.com/obra/superpowers
pinned at 22f0b463e7a5e579904dd6211a520321035526f7 (v7.0.2).
MIT License, Copyright (c) 2025 Jesse Vincent.
The original copyright notice and permission notice are in ./LICENSE.
These guides are our shortened adaptations, adopted Nov 22, 2026 (t1288u). They do not install
the Superpowers plugin and they do not replace our review set or James's
merge approval.
-->

These are short, pipeline-specific adaptations of selected
[obra/superpowers](https://github.com/obra/superpowers) skills. James
adopted them on Nov 22, 2026 (t1288u). They are now pointed to from this
repo's `docs/AGENTS.md` and `CONTRIBUTING.md`. They are not installed as
the upstream Superpowers plugin, and they do not replace the official
review set or James's merge approval.

Toolchain example lines in the brief templates are for the security
suite. For this Fan repo, use this repository's own test and solver
commands.

Source pin: `22f0b463e7a5e579904dd6211a520321035526f7` (v7.0.2).
License: MIT, see `LICENSE`.

Telemetry: keep `SUPERPOWERS_DISABLE_TELEMETRY=true`. Do not start the
visual companion server. Do not install the upstream plugin.

Our hard constraints still win:

- Full review set before any push (Claude, controller, PR-Agent, CodeRabbit
  CLI, gitleaks, trufflehog, board note, rb.py, bundle and MANIFEST).
- Merges to main need James's yes.
- Security-suite code is original, Rust std plus vendored aws-lc-rs, CNSA
  2.0, `forbid(unsafe)` outside suite-sys, rustc 1.89.0 `--offline --locked -j 2`.
- Never print secrets. Never sign external CLAs.

## Adopted guides

| File | Source skill | Intended use |
|---|---|---|
| `test-first-for-codex-fixes.md` | `test-driven-development` | Codex security-suite bugfixes and new behavior |
| `bite-sized-plans-for-codex.md` | `writing-plans` | Codex security-suite fixes that touch more than one file or behavior |
| `systematic-debugging-for-gates.md` | `systematic-debugging` | Failing gates, openEMS/GetDP-type harness errors, unexpected test failures |
| `receiving-review-findings.md` | `receiving-code-review` | Handling Claude, CodeRabbit, PR-Agent, and controller findings |

## Deliberately not adapted

The historical proposal is in `BRIEF-TEXT.md`. In short, not adopted: plugin/hooks, visual companion,
mandatory brainstorming, git worktrees (we already have them),
finish-branch / auto-push, subagent-driven development as a default,
using-superpowers mandatory invocation, diagnosing-superpowers,
writing-skills, and informal reviews that would replace the official set.

## Handoff and brief files (added Nov 22, 2026, t1288u)

James asked that other models use these practices. Canonical process
write-up: `CODING-PROCESS.md`. Short section for handoff and
`AGENTS.md` / `CONTRIBUTING.md` / `RULES.md` files: `SECTION.md`
(replace `GUIDES_PATH` with the local copy of this folder). Brief
addenda to paste into new Codex, Claude, and Hermes tasks:
`templates/`.

This folder, including the upstream `LICENSE`, is copied next to the
controller and security-suite handoff trees on the box and on vps3, and
into `docs/superpowers-adopted/` in project repos (via PRs, not direct
pushes to main). The official review set and James's merge approval are
unchanged and come first.
