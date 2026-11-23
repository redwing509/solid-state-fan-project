# Review-response addendum

Include this block in Codex follow-up briefs and in the controller's
review-response prompt when Claude, the controller, PR-Agent, CodeRabbit,
gitleaks, trufflehog, the board note, or rb.py returns findings.

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

For projects that are not the security suite, keep the same rules and
swap the toolchain line for that repo's compiler or test command. The
official review set and James's merge approval still come first.
