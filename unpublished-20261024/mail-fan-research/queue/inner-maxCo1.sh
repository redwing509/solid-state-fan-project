#!/bin/bash
# Inner script for legacy-air300-maxCo1 (runs inside Docker container)
# Runs buoyantBoussinesPimpleEHDFoam directly (no mpirun)
# Standard limit: 2 CPU, 4 GB, 1 hour (3540s timeout)
set -eo pipefail

# Source OpenFOAM environment FIRST
. /opt/openfoam4/etc/bashrc
# Then prepend our custom bin path AFTER bashrc resets PATH
export PATH=/work/bin:$PATH HOME=/work/home

cd /work/queue/cases/legacy-air300-maxCo1 || exit 3

echo "[$(date -u +%FT%TZ)] solver start" >> run.events
echo "[$(date -u +%FT%TZ)] maxCo1 launch (no mpirun)" >> run.events
timeout 3540 buoyantBoussinesqPimpleEHDFoam > log.run 2>&1; rc=$?
echo "$rc" > run.exit
echo "[$(date -u +%FT%TZ)] solver exit=$rc" >> run.events
exit "$rc"