#!/bin/bash
source /usr/lib/openfoam/openfoam2412/etc/bashrc
set -eo pipefail
export HOME=/work/home
mkdir -p /work/home /work/bin
export FOAM_USER_APPBIN=/work/bin
export PATH=/work/bin:$PATH
cd /work/source
wmake src/electrostaticSimpleFoam > /work/build.log 2>&1
mkdir -p /work/coaxial/convergence
cp examples/coaxialCorona/exact_coaxial.py /work/coaxial/
for fan_N in 48 96 192; do
    fan_M=$((fan_N*60/96))
    fan_case=/work/coaxial/convergence/N$fan_N
    mkdir -p "$fan_case"
    cp -a examples/coaxialCorona/0 examples/coaxialCorona/constant examples/coaxialCorona/system "$fan_case/"
    sed -i "s/(96 60 1)/($fan_N $fan_M 1)/" "$fan_case/system/blockMeshDict"
    (
        cd "$fan_case"
        blockMesh > log.blockMesh 2>&1
        checkMesh > log.checkMesh 2>&1
        timeout 180 electrostaticSimpleFoam > log.run 2>&1
        postProcess -func sample -latestTime > log.sample 2>&1
        printf 'COMPLETED N=%s\n' "$fan_N"
        tail -n 6 log.run
    )
done
printf 'THREE_MESH_EXECUTION_COMPLETED\n'
