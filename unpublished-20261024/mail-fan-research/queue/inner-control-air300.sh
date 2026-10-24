#!/bin/bash
. /opt/openfoam4/etc/bashrc
export PATH=/work/bin:$PATH HOME=/work/home
cd /work/queue/cases/legacy-air300-control || exit 3
echo "[$(date -u +%FT%TZ)] solver start" >> run.events
timeout 28800 buoyantBoussinesqPimpleEHDFoam > log.run 2>&1; rc=$?
echo "$rc" > run.exit; echo "[$(date -u +%FT%TZ)] solver exit=$rc" >> run.events
exit $rc
