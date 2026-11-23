# Coding process (adopted Nov 22, 2026)

These four practices apply to coding work on our projects. They do not
replace or weaken the full review set, frozen pass rules, or James's
merge approval, which still come first. Following them does not authorize
a push or a merge.

Source: [obra/superpowers](https://github.com/obra/superpowers), pinned at
`22f0b463e7a5e579904dd6211a520321035526f7` (v7.0.2), MIT License,
Copyright (c) 2025 Jesse Vincent. Keep that LICENSE with the adapted
guides. Exact brief text: `BRIEF-TEXT.md` in this folder. Short guides:
`test-first-for-codex-fixes.md`, `bite-sized-plans-for-codex.md`,
`receiving-review-findings.md`, `systematic-debugging-for-gates.md`.

On the box the guides live at
`/workspace/pipeline-guides/superpowers-adopted/` and are also copied next
to the controller handoff at
`/workspace/controller-handoff/pipeline-guides/superpowers-adopted/`.
On vps3 they live at
`/opt/knowledge/controller-handoff/pipeline-guides/superpowers-adopted/`
and
`/opt/knowledge/security-suite/pipeline-guides/superpowers-adopted/`.
In a git repo, use `docs/superpowers-adopted/`.

## 1. Test-first — bug fixes and new behavior

**Applies to:** Codex (and the controller when it writes the fix),
especially security-suite findings that change behavior. Also other
repos when adding or changing tests and production code together.

**Does not apply to:** typo-only or docs-only work.

Write the new test (or tests) before any production-code change. Run
them. The test must fail for the missing behavior or still-present bug,
not because of a typo or a compile error in the test. Only then write
the smallest production change. Re-run the new tests, then the
surrounding suite. If production code for this task was written before
that failing run, delete that production change and start from the
tests. Do not edit a frozen pass rule to match a new result. A green
suite still does not authorize a push.

Security-suite tests use `RUSTUP_TOOLCHAIN=1.89.0 cargo test -p <crate>
--offline --locked -j 2 <test_name>`.

## 2. Bite-sized written plans — more than one behavior, or a control case

**Applies to:** fixes that touch more than one production file, more
than one behavior, or have a "must not change" control case.

**Does not apply to:** one-line typo or docs-only fixes. Do not require a
new design approval when James has already approved the named finding.

Write a short plan before coding. Do not add a `docs/superpowers/`
plugin tree. The plan must include:

- Goal in one sentence, and the finding or pass-rule id.
- Exact file paths to create or modify.
- Each behavior as its own task, with the failing test name and
  assertions first, the command that must fail, then the production
  change, then the command that must pass.
- A Review Focus list: the control case or failure mode most likely to
  be missed, each with a test.

Keep the project's existing toolchain and review constraints in every
task. Do not use subagent-driven-development, do not push, and do not
merge.

## 3. Receiving official review findings — every follow-up patch

**Applies to:** when Claude, the controller, PR-Agent, CodeRabbit,
gitleaks, trufflehog, the board note, or rb.py returns findings, before
the follow-up patch is written. All projects that use the official
review set, starting with the security suite.

Read the complete list before changing code. If any item is unclear,
ask; do not implement the others first. Verify each finding against this
repo, the relevant toolchain (for the security suite: rustc 1.89.0,
Linux and Windows), frozen pass rules, and any decision James already
made. Accept, accept with a smaller fix, or push back with a file,
test, and reason. If you cannot verify it, say what is missing and wait.
If a finding conflicts with a decision James already made, stop and ask
him. Implement accepted items one at a time and re-run the relevant
tests after each, then re-run the tools that failed or warned.
Informal or subagent reviews do not replace Claude, CodeRabbit, secret
scans, rb.py, or the bundle. Do not push or merge from this step.

## 4. Systematic debugging — failing gates and harness errors

**Applies to:** a security-suite gate that fails for a reason not already
pinned by a written finding; or an openEMS / GetDP / solver harness that
crashes, mis-parses input, or misses a known-solution check.

**Does not apply when:** the root cause is already written in an
approved finding.

- Phase 1: Read the full error. Reproduce it. Check recent diffs, pins,
  inputs, and the compiler or solver environment. In a multi-layer
  harness, record what enters and leaves each boundary once and name
  the failing layer. Do not leave temporary debug prints in the
  submitted change. Never print secrets.
- Phase 2: Diff against a working neighbor (passing gate, known-good
  input, sibling test). Read the solver syntax or gate contract
  completely if the failure is in generated input.
- Phase 3: Write one hypothesis and test one variable. Do not stack
  fixes.
- Phase 4: Write a failing test or known-solution assertion first,
  apply one root-cause fix, and re-run the original failing command
  plus the surrounding checks. Do not relax a tolerance or a frozen
  pass rule to obtain a pass.
- If three fix attempts have failed, stop and discuss the approach. Do
  not start a fourth guess.

## Not adopted

Do not install the upstream Superpowers plugin, hooks, or visual
companion. Do not require a brainstorm or a new human-approved spec
before every already-approved fix. Do not add extra helper agents per
task. Do not use any flow that would skip the official review set or
James's merge approval. If that plugin is ever installed later, keep
`SUPERPOWERS_DISABLE_TELEMETRY=true`.
