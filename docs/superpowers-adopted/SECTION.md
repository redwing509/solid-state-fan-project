## Coding process (adopted Nov 22, 2026)

These four practices apply to coding work on this project. They do not
replace or weaken the full review set, frozen pass rules, or James's
merge approval, which still come first. Following them does not
authorize a push or a merge.

Source: [obra/superpowers](https://github.com/obra/superpowers), pinned at
`22f0b463e7a5e579904dd6211a520321035526f7` (v7.0.2), MIT License,
Copyright (c) 2025 Jesse Vincent. Adapted guides and that LICENSE:
`GUIDES_PATH`. Full text: `GUIDES_PATH/CODING-PROCESS.md`. Exact brief
addenda: `GUIDES_PATH/BRIEF-TEXT.md` and `GUIDES_PATH/templates/`.

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
