# Codex task-brief addendum — security-suite coding process

Include the applicable blocks below in every new Codex (or controller-written)
security-suite task brief. Copy from here; do not invent a shorter version
that drops the frozen-rule or no-push lines. Full process:
`/workspace/pipeline-guides/superpowers-adopted/CODING-PROCESS.md`.
Exact source text: `../BRIEF-TEXT.md`. Authority: James t1287u / t1288u,
adopted Nov 22, 2026. The official review set, frozen pass rules, and
James's merge approval are unchanged and come first.

Source: obra/superpowers, pin `22f0b463e7a5e579904dd6211a520321035526f7`
(v7.0.2), MIT License, Copyright (c) 2025 Jesse Vincent.

## When this is a bug fix or new behavior (skip typo-only and docs-only)

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

## When the fix touches more than one behavior, more than one production file, or a must-not-change control case (skip one-line typo fixes)

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

## When this brief is a follow-up to official review findings

Also include `review-response-addendum.md`.

## When this brief is a failing gate or harness-debug task (root cause not already in an approved finding)

Also include `gate-debug-addendum.md`.
