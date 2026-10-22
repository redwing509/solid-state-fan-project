#!/bin/bash
# 3-level mesh convergence study under ./convergence, then compare with the
# exact solution:  python3 exact_coaxial.py
# Requires the OpenFOAM environment and the compiled solver.
# Runs in parallel on the number of processors set in system/decomposeParDict.
cd "${0%/*}" || exit
set -e

NP=$(grep -oP 'numberOfSubdomains\s+\K\d+' system/decomposeParDict)

for N in 48 96 192; do
    M=$((N*60/96))
    d=convergence/N$N
    rm -rf "$d"
    mkdir -p "$d"
    cp -r 0 constant system "$d"/
    sed -i "s/(96 60 1)/($N $M 1)/" "$d/system/blockMeshDict"
    (
        cd "$d"
        blockMesh > log.blockMesh 2>&1
        decomposePar > log.decomposePar 2>&1
        mpirun -np $NP electrostaticSimpleFoam -parallel > log.run 2>&1
        reconstructPar -latestTime > log.reconstructPar 2>&1
        postProcess -func sample -latestTime > log.sample 2>&1
    )
    echo "=== N=$N ($NP processors) ==="
    grep 'patch outer' "$d/log.run" | tail -1
done
echo "done - now run: python3 exact_coaxial.py"
