<!--
Adapted from obra/superpowers skill "test-driven-development",
https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/test-driven-development/SKILL.md
pinned at 22f0b463e7a5e579904dd6211a520321035526f7 (v7.0.2).
MIT License, Copyright (c) 2025 Jesse Vincent.
The original copyright notice and permission notice are in ./LICENSE.
This is a shortened adaptation for our pipeline. It does not install the
Superpowers plugin and does not replace our review set or James's merge approval.
-->

# Test-first for Codex security-suite fixes

Use this when Codex (or a local trial) implements a security-suite bugfix
or new behavior. Skip it for typo-only or docs-only changes, and for
generated lockfiles.

## Rule

No production-code change for a new behavior until a test for that
behavior has been written, run, and seen to fail for the expected reason
(feature missing or bug still present), not because of a typo or a
compile error in the test itself.

If production code was already written before that failing test, delete
the production change for this task and start from the test. Keep existing
unrelated code.

## Cycle

1. Write one focused test that names the behavior and asserts on real
   results, not on mock internals. Prefer the crate's existing fixture
   style.
2. Run only that test first:
   `RUSTUP_TOOLCHAIN=1.89.0 cargo test -p <crate> --offline --locked -j 2 <test_name>`
   Record the failure. If it passes, the test is not pinning the bug; fix
   the test.
3. Write the smallest production change that should make it pass.
4. Re-run the new test, then the crate's tests (and the frozen pass rule
   if this work has one). A green new test is not a green suite.
5. Refactor only while tests stay green. Do not add behavior during
   refactor.

## Constraints that still apply

- rustc 1.89.0, `--offline --locked -j 2`.
- `forbid(unsafe)` outside suite-sys. Original code only.
- Pre-registered pass rules stay frozen. Do not edit a rule to match a
  new result.
- Tests and a green suite do not authorize a push. The full review set
  still runs, and merges still need James's yes.

## Do not

- Treat "I already read the code and it looks right" as the failing test.
- Skip watching the failure because the case "is obvious."
- Use this as a reason to skip Claude, CodeRabbit, secret scans, or the
  board bundle.
