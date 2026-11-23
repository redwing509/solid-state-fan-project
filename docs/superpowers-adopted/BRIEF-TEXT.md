# Proposal: adopt a few Superpowers habits, not the plugin

Sunday, Nov 22, 2026, 9:40 PM PST (America/Los_Angeles)

This is a proposal only. No live routine, review-set step, repo
`CLAUDE.md`/`AGENTS.md`, or installed skill was changed. James can
accept, edit, or reject the brief text below before anything is wired
in.

Source: [obra/superpowers](https://github.com/obra/superpowers), pinned
at `22f0b463e7a5e579904dd6211a520321035526f7` (v7.0.2), MIT License,
Copyright (c) 2025 Jesse Vincent. Adapted guides and license:
`/workspace/tools-eval/superpowers-adopted/`. Audit:
`/workspace/tools-eval/SAFETY_AUDIT.md`. A/B:
`/workspace/tools-eval/ab-results/COMPARISON.md`.

## Recommend adopting

Use our short adapted guides, copied into Codex task briefs or review
prompts when the case matches. Do not install the upstream plugin,
hooks, or visual companion. Keep `SUPERPOWERS_DISABLE_TELEMETRY=true`
if that plugin is ever installed later. Nothing here authorizes a push
or a merge.

### 1. Test-first — Codex security-suite bugfixes and new behavior

**Where:** Codex (and the controller when it writes the fix) on
security-suite findings that change behavior. Skip typo-only and
docs-only work.

**Why it helped:** In the CR8-F1 scratch A/B, the adopted arm watched
two tests fail for the real bug (`NoneFound` still returned) before any
production edit. The baseline wrote code and one test together and never
proved the test could catch the bug.

**Exact text to add to a Codex task brief:**

```
Test-first for this fix:
- Write the new test (or tests) before any production-code change.
- Run them with RUSTUP_TOOLCHAIN=1.89.0 cargo test -p <crate> --offline --locked -j 2 <test_name>.
- The test must fail for the missing behavior or still-present bug, not because of a typo or a compile error in the test.
- Only then write the smallest production change. Re-run the new tests, then the crate suite.
- If production code for this task was written before that failing run, delete that production change and start from the tests.
- Do not edit a frozen pass rule to match a new result.
- A green suite still does not authorize a push. The full review set runs, and merges need James's yes.
```

### 2. Bite-sized written plans — Codex fixes with more than one behavior or a control case

**Where:** Security-suite fixes that touch more than one production file,
more than one behavior, or have a "must not change" control case (as
CR8-F1 did: leader-only empty listings must still export `NoneFound`).
Skip one-line typo fixes. Do not require a new design approval when
James has already approved the named finding.

**Why it helped:** The adopted plan's Review Focus is why the control
and fail-closed tests existed. Baseline missed both; the stand-in
review called those Important. Adopted added 29 seconds of process and
avoided a predicted rework round.

**Exact text to add to a Codex task brief:**

```
Write a short plan in this brief (or a scratch notes file for this round) before coding. Do not add a docs/superpowers/ tree to the repo.
The plan must include:
- Goal in one sentence, and the finding or pass-rule id.
- Exact file paths to create or modify.
- Each behavior as its own task, with the failing test name and assertions first, the command that must fail, then the production change, then the command that must pass.
- A Review Focus list: the control case or failure mode most likely to be missed, each with a test.
Constraints that stay in every task: rustc 1.89.0 --offline --locked -j 2; original code; forbid(unsafe) outside suite-sys; no push until the official review set is clean; no merge without James's yes.
Do not use subagent-driven-development, do not push, and do not merge.
```

### 3. Receiving official review findings — every follow-up patch

**Where:** When Claude, the controller, PR-Agent, CodeRabbit, gitleaks,
trufflehog, the board note, or rb.py returns findings, before the
follow-up patch is written. All projects that use the official review
set, starting with the security suite.

**Why it helped:** This A/B did not generate a false reviewer
suggestion, so there is no defect-count delta. The value is
preventing a known failure mode: agreeing with a reviewer and patching
without checking this codebase, a frozen rule, or a decision James
already made. The cost is low.

**Exact text to add to Codex follow-up briefs and to the controller's
review-response prompt:**

```
Receiving official review findings:
- Read the complete list before changing code. If any item is unclear, ask; do not implement the others first.
- Verify each finding against this repo, rustc 1.89.0, Linux and Windows, frozen pass rules, and any decision James already made.
- Accept, accept with a smaller fix, or push back with a file, test, and reason. If you cannot verify it, say what is missing and wait.
- If a finding conflicts with a decision James already made, stop and ask him.
- Implement accepted items one at a time and re-run the relevant tests after each, then re-run the tools that failed or warned.
- Informal or subagent reviews do not replace Claude, CodeRabbit, secret scans, rb.py, or the bundle.
- Do not push or merge from this step.
```

### 4. Systematic debugging — failing gates and harness errors only

**Where:** A security-suite gate fails for a reason not already pinned
by a written finding; or an openEMS / GetDP / solver harness crashes,
mis-parses input, or misses a known-solution check. Not needed when
the root cause is already written in an approved finding (as in this
CR8-F1 replay).

**Why recommend it without an A/B delta here:** The scratch finding
already stated the cause, so the four-phase loop was not exercised.
The same day's Fan E-01 GetDP failure is the kind of case it is for:
the crash came from generated GetDP syntax (a field read with no
point), and an earlier draft needed a Claude re-review. The guide
requires reading the solver input, comparing it to a working file,
and not loosening a known-solution tolerance.

**Exact text to add to a gate-failure or harness-debug brief:**

```
Systematic debugging before any fix:
- Phase 1: Read the full error. Reproduce it. Check recent diffs, pins, inputs, and the compiler or solver environment. In a multi-layer harness, record what enters and leaves each boundary once and name the failing layer. Do not leave temporary debug prints in the submitted change. Never print secrets.
- Phase 2: Diff against a working neighbor (passing gate, known-good input, sibling test). Read the solver syntax or gate contract completely if the failure is in generated input.
- Phase 3: Write one hypothesis and test one variable. Do not stack fixes.
- Phase 4: Write a failing test or known-solution assertion first, apply one root-cause fix, and re-run the original failing command plus the surrounding checks. Do not relax a tolerance or a frozen pass rule to obtain a pass.
- If three fix attempts have failed, stop and discuss the approach. Do not start a fourth guess.
```

## Rejected (do not adopt, do not install)

- **Upstream plugin, SessionStart hooks, and the visual companion
  server.** They change default agent behavior globally, and the
  companion loads a versioned image from primeradiant.com unless
  telemetry is disabled. James asked us not to install the plugin.
  Telemetry stays off.
- **Mandatory brainstorming and a human-approved spec before every
  fix.** We already get James's yes on named findings and pass rules.
  A forced brainstorm would slow every Codex round and burn usage.
- **using-git-worktrees.** We already use worktrees.
- **finishing-a-development-branch.** As written it can merge locally
  or push a PR once the human picks a menu option, without our review
  set. That conflicts with t997u and with James's merge approval.
- **subagent-driven-development, and requesting-code-review as a
  substitute for the official set.** Fresh agents per 2–5 minute task
  would raise usage. Informal reviews must not replace Claude,
  controller, PR-Agent, CodeRabbit, secret scans, the board, rb.py, or
  the bundle.
- **using-superpowers mandatory "invoke a skill before any response."**
  Overkill, and it requires the plugin.
- **diagnosing-superpowers and writing-skills.** Not relevant unless
  we become Superpowers users or skill authors.
- **verification-before-completion as a separate adopted guide.** We
  already have frozen pre-registered pass rules and a rule against
  claiming a pass without a fresh run. A one-line reminder is already
  inside the test-first brief text.

## What I did not change

- No plugin install on the box, rig1, or the laptop.
- No edits to live routines, the review set, or any repo's CLAUDE or
  AGENTS files.
- No push from the trial repo.
- Live CR6R-02 work was left alone.
