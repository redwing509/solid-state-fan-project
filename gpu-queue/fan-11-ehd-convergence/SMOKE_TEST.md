# Smoke test — fan-11-ehd-convergence (2026-10-24, mail VPS)

Run under `ai-job --owner grokbot --resource fan-research` within Fan mail policy (`--cpus 2 --memory 4g`),
image built from this Dockerfile (`gpuq/fan-11-ehd-convergence:20261024`, pinned OF 4.1 digest).

Command: `SMOKE=1 NPROC=2 CASES="M1 M2" PUSH=0 RUN_ID=smoke` (endTime 0.0002 s, fixed dt — plumbing test only).

| Step | Result |
|---|---|
| Solver build (buoyantBoussinesqPimpleEHDFoam, upstream nzhtbyn@cfd66422) | OK, binary sha256 e161266febf1d70d… |
| M1 (4,700 cells, serial) | rc 0, 1 s |
| M2 (18,800 cells, 2 ranks: decomposePar → mpirun → reconstructPar) | rc 0, 15 s |
| patchAverage areaAverage(down) of T | M1 300.039 K, M2 300.077 K (parsed) |
| post_fan11.py summary.json / summary.md | written; verdicts NOT-PASSED as expected (no M4, no dt cases, t=0.0002 s) |
| Packaging (logs, tails, final_fields.tgz) | 3.2 MB push dir |
| Push path | not exercised (PUSH=0, no token on mail by design) |

Not tested: real 10 s runs, M4/M8, GH push (needs `GH_TOKEN` HF secret), HF Jobs runtime itself.
These numbers are NOT results — physical fields at 0.2 ms are meaningless.
