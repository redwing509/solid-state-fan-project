# Contribution validation

Acceptance requires a recorded review proportionate to the contribution. Do not claim a check was performed without retaining its evidence.

1. **Scope and provenance:** identify the question, author, sources, license, model version, solver revision and dependencies. Inspect files before executing code; never run submitted code automatically or provide it with credentials or unrestricted network access.
2. **Reproducibility:** provide inputs, geometry, units, boundary conditions, material grades/properties, waveform, source voltage versus electrode voltage, environment, command/settings and raw outputs with hashes where practical. State CPU/GPU, memory, runtime and storage estimates.
3. **Numerical verification:** use applicable analytical cases, independent solver comparisons, conservation, convergence, mesh/time-step sensitivity, residuals and reproducible tolerances. Explain disagreements and limitations. Identical ideal-conductor models with different metal labels do not constitute a material comparison.
4. **Experimental validation:** where physical performance is claimed, provide measured reference data, instrument/calibration details, matched conditions and uncertainty. Numerical agreement alone cannot establish airflow, ozone, noise, insulation qualification, endurance or commercial suitability.
5. **Decision:** the owner records accepted scope, evidence reviewed, checks performed, remaining limitations and the reason for acceptance or rejection in the pull request. Only then may the owner approve and merge.

Useful review record:

| Item | Record |
| --- | --- |
| Submission and revision | PR / commit |
| Claimed result and intended scope | Description |
| Sources and rights | Links / licenses |
| Reproduction and checks actually performed | Evidence links |
| Numerical verification | Pass / fail / not applicable / pending, with reason |
| Experimental validation | Supported / unsupported / not claimed, with evidence |
| Remaining uncertainty | Limitations |
| Owner decision | Accept / revise / reject |

The automatic `simulation-results` branch is an evidence inbox. A completed upload or successful solver exit does not satisfy this review.
