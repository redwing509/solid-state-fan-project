#!/bin/bash
set -eo pipefail
cd /work
source /opt/openfoam4/etc/bashrc
mkdir -p /work/home /work/bin
export HOME=/work/home
export FOAM_USER_APPBIN=/work/bin
export PATH=/work/bin:$PATH
cp -a legacy-ehd/buoyantBoussinesqPimpleEHDFoam solver-build
sed -i 's|$(FOAM_APPBIN)|$(FOAM_USER_APPBIN)|' solver-build/Make/files
cd solver-build
wmake > /work/build.log 2>&1
cd /work
cp -a legacy-ehd/validationCase smoke-case
cd smoke-case
foamDictionary system/controlDict -entry endTime -set 0.001
foamDictionary system/controlDict -entry writeInterval -set 0.001
foamDictionary system/controlDict -entry purgeWrite -set 2
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1
cp -a 0.orig 0
setFields > log.setFields 2>&1
timeout 180 buoyantBoussinesqPimpleEHDFoam > log.solver 2>&1
printf 'SMOKE_TEST_COMPLETED\n'
tail -n 14 log.solver
