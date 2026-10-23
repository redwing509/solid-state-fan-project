# Completed batch and retrospective numerical review

Recorded October 21, 2026, Pacific time. This review follows execution; it does not create predeclared acceptance criteria for existing results.

## Execution and backup

The 314-job batch became terminal at October 21, 11:31 p.m. Pacific (2026-10-22 06:31 UTC): **313 executed, one timeout, zero running, zero waiting**. Coaxial: 216 executed; fixed-injection duct: 90 executed; thermal controls: seven executed and one timeout. No family was paused.

All 314 terminal case records, including the timeout, were exported to the public simulation-results branch. Remote commit `334f55e2990c4e2a8ed1f029aae7ecf8bd541e66` matched the publisher record at review. Subsequent note updates may advance this branch. The worker, comparison watcher and publisher exited normally after their terminal/final-refresh conditions. Approximately 307 GiB remained free. No additional compute was launched.

The metadata audit checked all 314 job definitions against recorded job/result hashes and execution statuses: no discrepancies. It also checked 630 raw-cases archive/manifest entries, 400,821,666 bytes, against the export content manifest: no discrepancies. This establishes integrity of this export checkout against its manifest, not experimental accuracy or an independent download/reconstruction of every GitHub archive. See validation/final_integrity_audit.json.

## Coaxial comparisons

All 216 force-off electrical cases have analytical current, field and charge comparisons. There are 36 physical parameter combinations, each with three radial meshes and two schemes. Values below are the worst errors over 36 settings for each mesh/scheme, not a matched convergence trajectory.

| Radial mesh | Scheme | Max field relative L2 error | Max charge relative L2 error | Max current relative error |
| --- | --- | ---: | ---: | ---: |
| 48 | linearUpwind | 0.13665% | 0.20148% | 0.20085% |
| 48 | upwind | 0.76372% | 1.58782% | 0.66034% |
| 96 | linearUpwind | 0.03377% | 0.07472% | 0.05028% |
| 96 | upwind | 0.39250% | 0.80693% | 0.36834% |
| 192 | linearUpwind | 0.00761% | 0.02287% | 0.01258% |
| 192 | upwind | 0.19823% | 0.40504% | 0.19344% |

Across 72 matched mesh triplets, exact-solution error decreased on both refinements in 72 field, 72 charge and 57 current triplets. Exceptions are retained in validation/reference_cases_and_convergence.json. These error trends are not a formal Grid Convergence Index or proof that every quantity reached the asymptotic range. Current cancellation can make a coarse-grid error deceptively small. Maximum relative patch-current imbalance over the electrical cases was 2.73828e-06.

The radial sampled-profile norms are not full-domain error norms. The comparison code and coordinate/normalization assumptions still need independent review. Reduced force-off agreement provides no measured fan airflow, corona-onset or material ranking.

## Duct and thermal limits

The 90 duct and eight thermal snapshot rows currently carry execution outcomes, not quantitative physical-validation metrics. Full-field conservation, paired force-on/off effects, thermal heat balance, timestep sensitivity and comparison to reference measurements remain open.

`legacy-91be60c7e7` (consistent Pr, fixed ambient, maxCo=1) timed out: reported elapsed 3611.697 s, exit 137, last simulated time 6.34411 s, no normal End marker. The final log had max Courant approximately 1 and timestep 4.50816e-5 s; no fatal marker was recorded. These diagnostics are consistent with the time cap terminating an incomplete slow run; they do not alone rule out every resource issue. It must not be used as a completed 10 s comparison. No retry was made. A simple proportional extrapolation to 10 s is roughly 95 minutes total, but late-run cost is uncertain. Any continuation or larger time allowance needs a reviewed proposal and the user's decision before exceeding the recorded limit; retain two CPUs/4 GB unless separately authorized.

The original heat-input discrepancy (127.264 versus documented 187 W/m²) remains a validation blocker. Completing seven controls does not resolve it without reviewing their fields and heat balances. No material-aware corona law or supply-to-electrode converter map was established. Requested 110/220/330/440 VAC scenarios therefore remain separate from electrode-voltage comparisons.

## Review disposition

Evidence is retained for further numerical review. No experimental-validation, product-performance or certification claim is accepted by this report. The next reference set is selected by nominal settings and envelope corners rather than favorable errors; selection is explicitly retrospective. Future acceptance protocols are in Validation_Plan.md. Main remains protected and these notes belong to simulation-results pending owner review.

## 2026-10-22 5:45 PM PDT update (Grok Bot): rerun complete, mismatch diagnosed, air control launched
- legacy-91be60c7e7 rerun finished: restarted from t=6.0 s, reached t=10 s with End marker, solver exit 0 (23:09:32Z to 23:28:30Z, i.e. 4:09-4:28 PM PDT), no FOAM FATAL/nan. Same parameters, nothing changed.
  - On mail: result.json regenerated (status executed, exit 0, last_time 10, continuation block); old record kept as result.json.timeout-original. Time dirs 6.5-10 and log.rerun-from6s copied into the case folder. Copied timeout records in the -rerun and -rerun-active folders renamed to result.json.copy-of-timeout-original so they don't publish as duplicates.
  - validation_audit_v2.json regenerated (backup validation_audit_v2.json.bak-20261022-1745): legacy-91be60c7e7 now time 10.0, executed, internal T range 300-347.198 K (cf. consistent_Pr_ambient 346.913 K at 10 s). Not a physical validation.
- Thermal mismatch diagnosis (report: outputs\Thermal_Mismatch_Report_2026-10-22.md):
  - Cause: the gradient 9350 K/m was sized as 187/kf with kf=0.02, but the solver's TEqn uses k = rho*Cp*nu/Pr = 1.225*1000*1e-5/0.9 = 0.01361 W/m/K, giving 127.264 W/m2. Ratio 1.46939 = 0.02/0.01361 exactly.
  - "W/mA" is a mislabel for W/m2.
  - The 187 W/m2 figure is unverified: not found as text in Owsenek & Seyed-Yagoobi (1997); probably digitized from Fig. 5.
- Control case legacy-air300-control launched 5:34:53 PM PDT via ai-job (resource fan-research, owner grokbot): rho0 1.225, Cp0 1005, nu 1.5167e-5, Pr 0.71 -> k 0.02630 (kf 0.0263), gradient 7110 K/m (q 186.99 W/m2), fixed 300 K inlet (up), maxCo 2, endTime 10. Advancing. Hermes monitors via relay project solid-state-fan-control (no relaunch).
