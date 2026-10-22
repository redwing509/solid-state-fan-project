# Fanless fan — project parameters

Updated October 21, 2026.

## Objective and standing research direction

Develop an electrically driven air mover without mechanically moving airflow components. Explore supply scenarios at **110, 220, 330 and 440 V**; treat these as nominal AC RMS supply scenarios inherited from the commercial-input discussion. Keep phase, frequency and converter compatibility explicit. Do not confuse supply voltage with the electrode voltage.

Run as many useful tests through as many suitable independent simulators/virtual labs as can be found, and compare matched results. Expand a finite, documented material/combination register over time. Read and update `TASKS.md` (`outputs/Project_To_Do.md` is the user-facing copy).

## Authorized compute and local utilization limit

The user expressly authorized using this computer and its GPU for more demanding simulation software on October 21, 2026, with **no more than 50% utilization**. Apply a conservative ceiling of 50% of total local CPU capacity and 50% GPU utilization to simulation workloads; leave headroom for other applications. Do not interpret this as permission to occupy all free resources or as a 50% power-limit setting.

Before running a local simulation, inspect CPU/GPU availability and current use. Use a CPU job/process/container quota of at most half of total CPU capacity and a workload-appropriate, monitored GPU cap. A power cap, VRAM allocation limit or reduced GPU process priority alone does not enforce 50% compute utilization. Where supported, use explicit GPU partitioning or workload throttling and monitoring; pause/stop if the limit is exceeded. If the selected software/hardware cannot reliably enforce the ceiling, leave GPU work queued or run it on mail. Do not start an unrestricted GPU run merely because average utilization may be low.

No local GPU simulation was launched when this instruction was recorded. Hardware capability and simulator compatibility must be checked before scheduling work. Avoid changing global power plans, GPU firmware or unrelated application settings to implement this research constraint.

**Heavy-load notification rule:** the user instructed, "if a simulation requires heavy load notify me and we will find the compute required." Estimate CPU/GPU, RAM/VRAM, runtime and storage before each new substantial simulation batch. If the job requires heavy load, exceeds current resource limits, risks interfering with normal use, or requires additional compute, notify the user before starting it. Present the estimated requirements and suitable options; decide the compute with the user. Do not automatically escalate local utilization, buy capacity or launch a heavier host job. Existing already-authorized capped jobs may continue within their recorded limits.

The user's mail VPS remains authorized for isolated simulations. Existing fan jobs there are limited to two CPU cores and 4 GB RAM; its separate circuit-setup container is limited to one CPU and 1 GB RAM. Preserve unrelated services. This local 50% permission does not grant paid compute, purchases, or uploading private data to third-party runners.

## Evidence and result labels

Keep proposed/registered, blocked, running, completed and experimentally validated cases separate. A successful numerical test is not proof of fan airflow, ozone control, acoustic output, durability, electrical protection or commercialization readiness. Material-specific predictions require grade/surface/property models; ideal-conductor material names alone do not change the physics.
