#!/bin/bash
set -eo pipefail
source /opt/openfoam4/etc/bashrc
export PATH=/work/bin:$PATH
cd /work/benchmark-case
date -u +%FT%TZ > continuation.started
set +e
timeout 3600 buoyantBoussinesqPimpleEHDFoam > log.continuation 2>&1
fan_status=$?
printf '%s\n' "$fan_status" > continuation.exit
date -u +%FT%TZ > continuation.finished
exit "$fan_status"
