# Unpublished run scripts from the simulation server, archived 2026-10-24

**Verification status: not yet peer-review verified.** These files are run and launch scripts plus small probe utilities. None of them is a model. Nothing in this directory counts toward the 2-engine rule.

The files are verbatim copies from `/opt/fan-research/2026-10-21/` on the simulation server. The only change is CRLF converted to LF. They are kept here so that every OpenFOAM run reported in `simulation-results` can be traced back to the script that launched it. This branch is an archive and should not be merged into `main` in its current form.

## Exclusions

- Git-credential and deploy-key setup scripts.
- Logs and raw run output.

## Contents

### `mail-fan-research/queue/`

| Script | Purpose |
|---|---|
| `inner-*.sh`, `launch-*.sh` | Reruns: fixed rerun, air-300 K control, coarse mesh, maxCo=1. |
| `validation_probe.py` | Probe script. |
| `validation_boundary_probe.py` | Probe script. |
| `check_extra_evidence.py` | Probe script. |
| `publish_validation_notes.py` | Drives `scripts/github_result_publisher.py`. |

### `mail-fan-research/thermal-fix-20261024/*/inner.sh`

Job bodies for two OpenFOAM 4 runs:

- the corrected-baseline run;
- the EHD-off control run.

The verified comparison of those runs against `engines/thermal1d` is in PR #3 (`engines/thermal1d/results/COMPARISON.md`).

## Running the scripts

The scripts use the server paths `/opt/openfoam4` and `/work/bin/buoyantBoussinesqPimpleEHDFoam`. Adjust those paths before running anywhere else.
