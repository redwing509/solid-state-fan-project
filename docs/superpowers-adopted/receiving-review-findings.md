<!--
Adapted from obra/superpowers skill "receiving-code-review",
https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/receiving-code-review/SKILL.md
pinned at 22f0b463e7a5e579904dd6211a520321035526f7 (v7.0.2).
MIT License, Copyright (c) 2025 Jesse Vincent.
The original copyright notice and permission notice are in ./LICENSE.
This is a shortened adaptation for our pipeline. It does not install the
Superpowers plugin and does not replace our review set or James's merge approval.
-->

# Receiving official review findings

Use this when Claude, the controller, PR-Agent, CodeRabbit, gitleaks,
trufflehog, the board note, or rb.py returns a finding, and before any
follow-up patch is written.

This is about how to treat those findings. It does not replace the
review set, and it does not authorize a push or a merge.

## Pattern

1. Read the complete finding list before changing code.
2. Restate each item as a technical requirement, or ask if it is unclear.
   If any item is unclear, do not implement the others first.
3. Verify the finding against this codebase, this platform (Linux and
   Windows), and any prior decision James already made.
4. Classify: accept, accept with a smaller fix, or push back with
   evidence.
5. Implement accepted items one at a time and re-run the relevant tests
   after each. Then re-run the review tools that failed or warned.

## External reviewers (Claude, CodeRabbit, PR-Agent)

Be skeptical, but check carefully:

- Is it technically correct for this repo and rustc 1.89.0?
- Would the suggested change break a frozen pass rule, a Windows path,
  or `forbid(unsafe)`?
- Is it asking for a feature we do not need (YAGNI)?
- Does it conflict with a decision James already made? If so, stop and
  ask him. Do not "just implement it."

If the finding is wrong, push back with the file, the test, and the
reason. If you cannot verify it, say what is missing and wait.

## Controller and board notes

Treat these as part of the official set, not as optional style. A
controller FAIL still blocks the push.

## Do not

- Agree performatively and patch without verification.
- Apply every suggestion in one bundled diff and hope the suite stays
  green.
- Let an informal subagent review stand in for Claude, CodeRabbit, the
  secret scans, rb.py, or the bundle.
- Post review replies or merge from this guide. Integration stays on
  the existing pipeline, with James's yes for main.
