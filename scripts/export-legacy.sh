#!/bin/bash
set -eo pipefail
source /opt/openfoam4/etc/bashrc
cd /work/benchmark-case
foamToVTK -ascii -noPointValues -useTimeName -time '9.5,10' -fields '(T U chargeDens elecPot elec curDens)' > log.export 2>&1
find VTK -type f | sort
