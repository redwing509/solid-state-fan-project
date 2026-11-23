# Claude / Hermes brief addendum — adopted coding process

Include a short pointer in Claude review packets and Hermes coding or
debug briefs. The official review set, frozen pass rules, and James's
merge approval are unchanged and come first.

When reviewing or following up on findings, follow
`receiving-review-findings.md` (verify against the repo and James's
decisions before patching; informal reviews do not replace the official
set).

When writing a fix for new behavior, expect test-first evidence: a test
that failed for the right reason before the production change.

When a gate or solver harness fails and the cause is not already in an
approved finding, follow `systematic-debugging-for-gates.md`. Do not
relax a frozen pass rule or a known-solution tolerance.

Guides: `/workspace/pipeline-guides/superpowers-adopted/` on the box;
`/opt/knowledge/controller-handoff/pipeline-guides/superpowers-adopted/`
on vps3. Source: obra/superpowers pin 22f0b463, MIT License,
Copyright (c) 2025 Jesse Vincent.
