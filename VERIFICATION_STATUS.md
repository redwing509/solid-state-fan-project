# Model verification status (2026-10-24)

Standing rule: every published model must meet the peer-review standard. That means tolerances stated in advance, analytic tests or MMS, a GCI convergence study, energy balance, a benchmark, CI, and a VERIFICATION.md.

- Executed is not verified, and verified is not validated.
- Only models marked verified count toward the 2-engine rule.

| Model | Repo / branch | Status | What is missing |
|---|---|---|---|
| `engines/thermal1d` (1-D transient conduction, θ-method FV) | main (PR #3) | **verified** (code verification) | 34/34 checks pass: analytic, MMS, GCI, energy balance. CI passes. Validation is partial. In the OpenFOAM cross-check, B1 (EHD off) passes: plate ΔT 134.81 vs 134.85 K. B2 (EHD on) fails as expected, because about 94% of the heat is advected. That is outside the model's scope. Results are in `simulation-results:benchmark/thermal1d-crosscheck-2026-10-24/`. |
| Coaxial reduced charge model (`scripts/coaxial_verification.py`) | main | partial | It compares two independent formulations (shooting and log-radius BVP) against the published exact coaxial solution. Missing: a pre-stated tolerance, a pytest/CI test, VERIFICATION.md, and a resolution or GCI study of the BVP mesh. |
| OpenFOAM vs. exact coaxial comparison (`scripts/compare_coaxial_engines.py`) | main | partial | Missing: a mesh-convergence GCI for the OpenFOAM coaxial cases and a pre-stated acceptance tolerance. |
| OpenFOAM EHD fan cases (legacy and modern EHD solvers, queue) | main, simulation-results | none (in-house) | Third-party solvers. Missing: mesh and time-step convergence with GCI and experimental validation. Registered is not executed, and executed is not validated. |
| Run, queue and probe scripts | publish/unpublished-run-scripts-20261024 | n/a | These are tooling, not models. |

Queued verification work, with runtime estimates, is listed in the grokbot relay inbox (`ai-relay/grokbot/inbox`).
