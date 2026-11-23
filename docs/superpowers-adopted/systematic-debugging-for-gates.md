<!--
Adapted from obra/superpowers skill "systematic-debugging",
https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/SKILL.md
pinned at 22f0b463e7a5e579904dd6211a520321035526f7 (v7.0.2).
MIT License, Copyright (c) 2025 Jesse Vincent.
The original copyright notice and permission notice are in ./LICENSE.
This is a shortened adaptation for our pipeline. It does not install the
Superpowers plugin and does not replace our review set or James's merge approval.
-->

# Systematic debugging for gates and harness errors

Use this when a security-suite gate fails, when an openEMS or GetDP
harness run crashes or disagrees with a known-solution check, or when a
test fails for a reason that is not already pinned by a written finding.

Do not start changing production code until Phase 1 is written down.

## Phase 1 — Root cause

- Read the full error, including line numbers, tool names, and trailing
  context. Do not stop at the first line.
- Reproduce it. If it is not reproducible, gather more evidence; do not
  guess.
- Check recent diffs, pin files, mesh inputs, and environment (compiler
  version, offline/locked flags, working directory).
- In a multi-layer harness (script → solver input → solver → extractor
  → comparison), log what enters and leaves each boundary once, then
  identify the failing layer. Do not leave temporary debug prints in
  the code you will submit.
- Never print secrets, keys, or tokens while gathering evidence.

## Phase 2 — Pattern

Find a working neighbor (a passing gate, a known-good `.pro` file, a
sibling test). List every difference. Read the relevant reference or
solver syntax completely if the failure is in generated input.

## Phase 3 — Hypothesis

Write one hypothesis: "X is the root cause because Y." Change one
variable to test it. If it is wrong, form a new hypothesis; do not stack
fixes.

## Phase 4 — Fix

- Write a failing test or a checked known-solution assertion first
  (see `test-first-for-codex-fixes.md`).
- Apply one root-cause fix.
- Re-run the original failing command and the surrounding suite or
  known-solution checks.
- If three fix attempts have failed, stop and question the approach
  with James or the controller. Do not start a fourth guess.

## Especially for GetDP / openEMS / solver harnesses

A solver syntax error is often a missing argument, a wrong field name,
or a point/time request with no location. Confirm the generated input
against a working file before changing post-processing or tolerances.
Do not relax a known-solution tolerance to make a run "pass."
