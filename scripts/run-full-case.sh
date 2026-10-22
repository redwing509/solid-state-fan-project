#!/bin/bash
set -eo pipefail
source /opt/openfoam4/etc/bashrc
export PATH=/work/bin:$PATH
cd /work
cp -a legacy-ehd/validationCase benchmark-case
cd benchmark-case
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1
cp -a 0.orig 0
setFields > log.setFields 2>&1
timeout 180 buoyantBoussinesqPimpleEHDFoam > log.solver 2>&1
printf 'SUPPLIED_CASE_COMPLETED\n'
tail -n 16 log.solver
