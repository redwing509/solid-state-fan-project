# Gate-failure or harness-debug brief addendum

Include this block when a security-suite gate fails for a reason not
already pinned by a written finding, or when an openEMS / GetDP / solver
harness crashes, mis-parses input, or misses a known-solution check.
Skip when the root cause is already written in an approved finding.

```
Systematic debugging before any fix:
- Phase 1: Read the full error. Reproduce it. Check recent diffs, pins, inputs, and the compiler or solver environment. In a multi-layer harness, record what enters and leaves each boundary once and name the failing layer. Do not leave temporary debug prints in the submitted change. Never print secrets.
- Phase 2: Diff against a working neighbor (passing gate, known-good input, sibling test). Read the solver syntax or gate contract completely if the failure is in generated input.
- Phase 3: Write one hypothesis and test one variable. Do not stack fixes.
- Phase 4: Write a failing test or known-solution assertion first, apply one root-cause fix, and re-run the original failing command plus the surrounding checks. Do not relax a tolerance or a frozen pass rule to obtain a pass.
- If three fix attempts have failed, stop and discuss the approach. Do not start a fourth guess.
```
