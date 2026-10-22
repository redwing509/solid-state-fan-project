# Solid State Fan Project — validation plan, revision 0.1

Prepared October 21, 2026, Pacific time, following the owner's instruction to proceed. Status: **working protocol for technical and owner review; not a certification or an approved prediction model**. Existing results are reviewed retrospectively. Freeze the next protocol revision and its hash before collecting new acceptance data. Never describe already inspected cases as blind validation or preregistered tests.

## Intended use and decision boundaries

The immediate purpose is to establish reproducible numerical reference cases and identify model deficiencies before ranking fan designs. Ultimate quantities of interest are delivered flow versus pressure, whole-device wall power, efficiency and temperature, with separately assessed emissions, acoustics, protection and endurance. Define the device configuration and operating envelope for each claim. Do not extrapolate validation beyond that envelope without a documented justification and uncertainty assessment.

Use ASME V&V 20 for CFD/heat-transfer methodology and NASA-STD-7009B for credibility and intended-use discipline. These are methodological references, not an assertion of clause-by-clause compliance. Review the full applicable standard and document any deviations before a formal compliance claim. No standards purchase, laboratory booking or paid compute is authorized by this plan.

## Evidence states and repository review

Track execution, numerical verification, experimental validation and independent reproduction as separate fields; each can be pending, supported within a scope, failed or not applicable, with evidence. A successful run, an accepted pull request and physical validation are different decisions. Each report states what is demonstrated and what remains unknown.

Community submissions start as submitted/unvalidated. Inspect provenance, permission, code and dependencies before execution. No automatic execution, queue import or merge. The owner approves inclusion on protected main; consequential scientific claims should also receive a qualified independent technical review. Incoming server evidence stays on simulation-results. Owner approval records accepted scope and limitations, not merely a pass badge.

## Selected reference set and staged protocols

The 28 existing records selected in validation/reference_cases_and_convergence.json are a retrospective reference set, not new jobs. No new solver workload is launched by this plan.

| Protocol | Cases / purpose | Required checks | Current disposition |
| --- | --- | --- | --- |
| E-01 | 18 coaxial records: nominal 30 kV, mobility 1.8e-4, injection 1e-5; low corner 10 kV/1.5e-4/5e-6; high corner 40 kV/2.3e-4/2e-5; all three meshes and both schemes | Independently check exact solution, geometry, units, current normalization and sampled coordinate mapping; reproduce metrics; assess iteration error, mesh behavior and domain effects | Analytical comparisons available; independent formula/code review and uncertainty analysis pending |
| F-01 | Two matched 30 kV nominal duct records, force off/on | Compare matched inputs; integrate inlet/outlet mass flow, current and force; inspect pressure/velocity fields, boundary sensitivity and iteration history; add mesh study before predictive use | Executed; quantitative paired/conservation review pending; fixed injection is not material validation |
| T-01 | All eight thermal controls plus retained original baseline | Reconcile effective conductivity, imposed heat flux and area; integrate thermal balance including relevant storage, advection and diffusion; check ambient treatment and comparable final states; assess timestep effects | Seven controls complete, one incomplete; missing common final time prevents a full timestep comparison |
| P-01 | Future measured electrical coupon, no new physical test started | Document electrode geometry/material/surface, polarity/waveform, onset/current, humidity/temperature, instrumentation and repeats; fit injection law on calibration subset only | Blocked on apparatus, traceable measurements and source/property data |
| P-02 | Future measured coupled flow and complete device | Freeze predictions; measure matched current, velocity/flow, pressure, wall power and thermal state; repeat across relevant envelope and units | Blocked on credible electrical model, device definition, laboratory method and independent data |

Units for mobility and injection must be explicitly checked against solver dimensions before any physical interpretation. The reference selection uses nominal settings and parameter corners rather than favorable error values. All 216 electrical cases remain in the evidence record; do not discard the nonmonotonic current-error triplets.

## Numerical acceptance protocol for the next unseen regression runs

Before new acceptance runs, record solver revision/image digest, comparison-code revision, immutable inputs, quantities, absolute/relative normalizations, sample locations, run-to-run repeatability expectations and stopping criteria. Code verification should include analytical or manufactured solutions where appropriate. Solution verification includes iterative convergence, spatial refinement and temporal refinement for transient problems. Residuals alone are insufficient.

For E-01, the following are **provisional project engineering targets**, not ASME-mandated limits and not retroactive pass criteria: on the fine mesh, field sampled-profile relative L2 error <=0.1%, charge sampled-profile error <=1%, integrated-current error <=0.25%, and relative discrete patch-current imbalance <=1e-5. Independent review must confirm these metrics are correctly computed and adequate for the intended regression purpose before freezing them. Use absolute tolerances for near-zero quantities; record the physical scale used. A formal acceptance remains pending, regardless of whether old data happen to meet these targets.

Use at least three systematically refined grids when practical. Report observed order and a justified discretization-uncertainty estimate for the actual scalar decision quantities; use Richardson extrapolation/GCI only when its assumptions are supported. Report oscillatory or non-asymptotic behavior instead of forcing an order estimate. Compare full-domain and boundary quantities as well as sampled profiles. Demonstrate tighter solver tolerances do not materially change decision quantities; assess domain/boundary sensitivity. Do not infer independent implementations merely from two solvers using shared OpenFOAM components.

For F-01 and T-01, complete dimensional and balance definitions before assigning numeric acceptance limits. An unexplained source/sink or incomplete transient prevents acceptance. Compare thermal controls at matched time and state; do not substitute 6.344 s for a requested 10 s result.

## Physical validation and uncertainty protocol

Before measurements, define the claim and maximum decision-relevant prediction error T for each output. Establish an uncertainty budget sufficiently smaller than T to distinguish success from an inconclusive comparison. Numeric T values depend on product requirements and instrument capability; they remain undecided. Do not select them after seeing the prediction/measurement discrepancy.

Retain calibration certificates, traceability chains, sensor ranges/resolution, placement and field-perturbation checks, environmental records, repeatability, between-unit variation and drift. Choose repeat counts through a precision/power rationale; preserve failed runs and predeclare exclusions. Randomize or block test order where drift/humidity/temperature could confound material or voltage effects. Evaluate covariance when inputs or measurements share errors.

Propagate numerical error, uncertain inputs, reference-measurement uncertainty and calibration-parameter uncertainty using a documented method. Report prediction-minus-measurement discrepancy alongside validation uncertainty and the separately defined acceptable error. Do not call overlapping error bars a pass by themselves, or inflate uncertainty until disagreement disappears. Expanded uncertainty must state the coverage factor, assumptions and coverage interpretation; k=2 is not universally 95%.

Separate calibration data from independent validation data, including complete holdout operating conditions or physical units where feasible. Freeze the model and predictions before revealing holdout results. Reusing holdout data to tune creates a new calibration set and requires a new independent validation set. Synthetic or published benchmark data must be identified accurately; digitized plots need digitization uncertainty and cannot replace missing raw experimental conditions.

Measure actual converter behavior before mapping 110/220/330/440 VAC supplies to electrode voltage/current. Whole-device wall power includes converter and auxiliary losses. Neither the existing reduced dielectric proxy nor the high-voltage sweep establishes mains compatibility.

## Physical test standards and claim review

For ducted aerodynamic ratings, assess ANSI/AMCA 210-25 / ASHRAE 51-25 with the laboratory. Its scope excludes certain air-circulating products, so select the method after defining the intended device. A custom low-flow EHD apparatus must document departures and uncertainty; do not call it a certified standard test without meeting the applicable requirements. Emissions, sound and electrical protection need their own applicable methods. ULE 2998 addresses a specific air-cleaner ozone claim; applicability and test conditions require review rather than assuming it qualifies every fan.

For consequential public claims, seek independent reproduction and an appropriately accredited laboratory with relevant scope. This is a later decision, not a booking or expenditure. No present result establishes emissions, sound, insulation qualification, endurance or commercial readiness.

## Required evidence package and release decision

Each candidate release contains immutable input and raw-data hashes, solver/runtime and analysis revisions, geometry/material provenance, instrumentation and uncertainty, all execution outcomes, comparisons and their limitations, calibration/holdout separation, reviewer findings and owner disposition. Record the protocol version, deviations, rejected hypotheses and unsuccessful cases. New software/model changes trigger a scoped regression and revalidation impact review.

Next actions: independently audit E-01 comparison assumptions; perform F-01/T-01 field and balance analyses within existing resource limits; resolve the thermal discrepancy; then freeze revision 0.2 before unseen acceptance data. The incomplete thermal run is held for a separate compute proposal. No automatic retry or cap increase.

## Primary references

- ASME V&V 20: https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-fluid-dynamics-and-heat-transfer
- NASA-STD-7009B: https://standards.nasa.gov/standard/nasa/nasa-std-7009
- AMCA 210-25 / ASHRAE 51-25 scope and revision: https://www.amca.org/educate/amca-inmotion-e-news/amca-inmotion-e-news-%E2%80%94-summer-2025.html
- NIST uncertainty guidance: https://physics.nist.gov/cuu/Uncertainty/coverage.html
- UL ozone claim program: https://www.ul.com/services/zero-ozone-emissions-validation
