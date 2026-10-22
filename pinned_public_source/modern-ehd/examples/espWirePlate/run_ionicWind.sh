#!/bin/bash
# Ionic-wind on/off comparison: run the case to convergence with the EHD
# force enabled and disabled, under ./ionicWind/{on,off}.
# Run after Allrun (or standalone). Low inlet velocity (0.3 m/s) makes the
# ionic wind dominate ((u_EHD/u0)^2 ~ 3 at 50 kV).
# Runs in parallel on the number of processors set in system/decomposeParDict.
cd "${0%/*}" || exit
set -e

V=${1:-50000}        # applied voltage [V]
RHOQW=${2:-6.815e-05}  # Kaptzov-converged wire charge density at 50 kV
U0=${3:-0.3}         # inlet velocity [m/s]
NP=$(grep -oP 'numberOfSubdomains\s+\K\d+' system/decomposeParDict)

rm -rf ionicWind
for mode in on off; do
    d=ionicWind/$mode
    mkdir -p $d
    cp -r 0 constant system $d/
    sed -i "s/uniform (1 0 0)/uniform ($U0 0 0)/" $d/0/U
    sed -i "/wire/,/}/ s/value           uniform .*;/value           uniform $V;/" $d/0/V
    sed -i "/wire/,/}/ s/value           uniform .*;/value           uniform $RHOQW;/" $d/0/rhoq
    sed -i "s/electricForce   on;/electricForce   $mode;/" $d/constant/electricProperties
    (
        cd $d
        blockMesh > log.blockMesh 2>&1
        decomposePar > log.decomposePar 2>&1
        mpirun -np $NP electrostaticSimpleFoam -parallel > log.run 2>&1
        reconstructPar -latestTime > log.reconstructPar 2>&1
        postProcess -func sampleLines -latestTime > log.sampleLines 2>&1
        postProcess -func samplePlane -latestTime > log.samplePlane 2>&1
    )
    echo "=== electricForce $mode ==="
    grep -E 'SIMPLE solution converged|^Time =' $d/log.run | tail -1
    grep 'patch plate' $d/log.run | tail -1
done
