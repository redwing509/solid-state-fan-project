# GPU / big-compute queue — status: **waiting for James's HF GPU**

Created 2026-10-24 ~3:40 PM PDT by Grok Bot, following James's message t75u (3:08 PM PDT): "the finest mesh
jobs can run in parallel and i will get us a huggingface gpu for the biggest jobs so queue those up for a gpu".
Nothing here has been launched, and no HF account, billing or secret has been created. Paid compute is James's call.

| # | bundle | queue item | status | hardware that actually helps | est. wall / cost* | GPU speedup (honest) |
|---|---|---|---|---|---|---|
| 1 | `fan-11-ehd-convergence/` | #11 Fan EHD mesh + time-step convergence | READY (built and smoke-tested on mail) | CPU: cpu-performance 32 vCPU (or cpu-xl) | ~8 h / ~$15 | ~1.0x (OF 4.1 custom solver, no GPU path, meshes up to 75k cells) |
| 2 | `we-08-m13-gci-dualT/` | #8 remainder: M13 3-mesh GCI, normal + hot regimes | BLOCKED until the M13 coarse case completes and `cfd/port13` is committed (owner: Claude), then needs `M13_REF` | CPU: cpu-performance 32 vCPU | ~12–15 h / ~$25–30 (Matrix A) | 1.0–1.3x at best (petsc4Foam pressure offload only); optional A/B image, not for the GCI |

\* HF list prices 2026-10-24: cpu-xl $1.00/h, cpu-performance $1.90/h, a10g-large $1.50/h, a100-large $2.50/h.

**Bottom line:** none of the queued verification jobs is GPU-bound. A *high-vCPU* HF machine (CPU flavor)
is the right purchase. A GPU flavor would only be used for its CPU cores.

## Not queued here (they fit on mail at $0)
- #8 fine meshes (A1/A2-BLEND r225/r150 + mail r100 bases): **running on mail since 2026-10-24 22:13 UTC**
  (`/opt/water-engine/cfd/gci-20261024/finish.log`).
- #8 time-step study (maxCo 0.2 / 0.1 / 0.05 at r150): goes on mail after the fine meshes finish (~1 day).
- #7 Cantera flame grid study: 2–6 h, CPU, ~14 GB per worker. Goes on mail when cpu-heavy is free.

## What James provides
1. HF account with Jobs billing (Pro/Team/Enterprise), with the flavor chosen per bundle README.
2. HF Jobs secret **GH_TOKEN**: a fine-grained GitHub PAT for `redwing509/water-engine` and
   `redwing509/solid-state-fan-project`, Contents read/write, short expiry. Pass it with `--secrets GH_TOKEN`.
   Never put it in a file.
3. `--timeout 24h` on every job (the HF default is too short).
4. For bundle 2 only: the `M13_REF` commit, once M13 works.

## Rules still in force
- Results land on new `hf-results/<RUN_ID>` branches only. Never main, never force-push.
- Nothing counts as verified until a second engine agrees and a peer review is done (2-engine rule).
- Fan results are merged into `simulation-results` after review.
- No Sentinel or vps3 involvement.

Bundles are mirrored in git: branch `gpu-queue/20261024` in water-engine (both bundles) and in
solid-state-fan-project (fan-11), under `gpu-queue/`.
