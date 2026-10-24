#!/bin/bash
# Runs INSIDE the OpenFOAM 4.1 container; /work = /opt/fan-research/2026-10-21 (host).
# Continues legacy-91be60c7e7 from latestTime (6 s checkpoint) to endTime 10. No re-mesh, no setFields, no deletion.
. /opt/openfoam4/etc/bashrc
export PATH=/work/bin:$PATH HOME=/work/home
cd /work/queue/cases/legacy-91be60c7e7-rerun-active || exit 3
echo "[$(date -u +%FT%TZ)] solver start from latestTime" >> rerun.events
timeout 28800 buoyantBoussinesqPimpleEHDFoam > log.rerun 2>&1; rc=$?
echo "$rc" > rerun.exit; echo "[$(date -u +%FT%TZ)] solver exit=$rc" >> rerun.events
exit $rc
