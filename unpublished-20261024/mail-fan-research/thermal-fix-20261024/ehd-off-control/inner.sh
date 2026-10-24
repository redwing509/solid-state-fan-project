. /opt/openfoam4/etc/bashrc
set -e
cd "$1"
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1
cp -r 0.orig 0
setFields > log.setFields 2>&1
timeout --signal=TERM 3000 /work/bin/buoyantBoussinesqPimpleEHDFoam > log.run 2>&1
