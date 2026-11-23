# thermal1d cross-check of the corrected legacy-air300 thermal baseline (2026-10-24)

Engine source, tests and CI: branch `engines/thermal1d` (`engines/thermal1d/`), PR #3.
- `COMPARISON.md` / `comparison.json`: B1 EHD-off control PASS; B2 EHD-on baseline FAIL (expected: different physics).
- `verification.json`: 34/34 verification checks.
- `openfoam/`: metrics extracted from OpenFOAM fields at t = 10 s and the run manifests of both OpenFOAM runs.
- `run_openfoam_ehd_off_control.sh`: launcher used for the EHD-off control run.
Status labels: executed (both OF runs) · verified (thermal1d code) · cross-checked (conduction limit only) · NOT validated.
