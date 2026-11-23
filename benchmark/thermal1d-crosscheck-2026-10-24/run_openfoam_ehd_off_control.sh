#!/bin/bash
# OpenFOAM control for the thermal1d cross-check: the corrected legacy-air300 baseline
# (Pr 0.6125, plate gradient 9350 K/m, 'up' fixed 300 K) with the EHD drive switched
# off (emitter potential 0 V, injected charge density 0), so the only heat transport
# is conduction - the same physics thermal1d solves. Also caps maxDeltaT so Euler
# time error stays small once Co -> 0.
# Run on mail:  ai-job --owner grokbot --resource fan-research --ttl 60 --wait -- \
#                 bash run_openfoam_ehd_off_control.sh [name]
# Refuses to overwrite. Uses the same pinned image and container limits as the queue.
set -euo pipefail
ROOT=/opt/fan-research/2026-10-21
OUT=$ROOT/thermal-fix-20261024
SRC=$OUT/corrected-baseline           # prepared inputs of the corrected baseline (inputs only)
NAME=${1:-ehd-off-control}
CASE=$OUT/$NAME
MAXDT=${MAXDT:-0.005}
IMAGE='openfoam/openfoam4-paraview50@sha256:a9cde0fffd6dee35f1d6fac0494d8595850aa8063005997a75c8430666f6c230'
[ ! -e "$CASE" ] || { echo "refusing to overwrite $CASE"; exit 2; }
mkdir -p "$CASE"
cp -r "$SRC/system" "$SRC/0.orig" "$CASE/"
mkdir -p "$CASE/constant"
cp "$SRC"/constant/{EHDproperties,g,transportProperties,turbulenceProperties} "$CASE/constant/"
cp -r "$SRC/constant/polyMesh" "$CASE/constant/" 2>/dev/null || true
rm -f "$CASE/constant/polyMesh/"{cellZones,faceZones,pointZones,sets} 2>/dev/null || true
# switch the EHD drive off
python3 - "$CASE" "$MAXDT" <<'PY'
import re, sys
from pathlib import Path
c = Path(sys.argv[1]); maxdt = sys.argv[2]
def sub_hole(f, new):
    s = f.read_text()
    s2, n = re.subn(r'(hole\s*\{[^}]*?value\s+uniform\s+)[-+0-9.eE]+', r'\g<1>' + new, s, flags=re.S)
    assert n == 1, f"{f}: hole value not found"
    f.write_text(s2)
sub_hole(c / '0.orig/elecPot', '0')
sub_hole(c / '0.orig/chargeDens', '0')
cd = c / 'system/controlDict'; s = cd.read_text()
assert 'maxDeltaT' not in s
s = s.replace('maxCo           2;', f'maxCo           2;\nmaxDeltaT       {maxdt};')
assert 'maxDeltaT' in s
cd.write_text(s)
PY
grep -A4 hole "$CASE/0.orig/elecPot" | grep value
grep -A4 hole "$CASE/0.orig/chargeDens" | grep value
grep maxDeltaT "$CASE/system/controlDict"
cat > "$CASE/inner.sh" <<'IN'
. /opt/openfoam4/etc/bashrc
set -e
cd "$1"
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1
cp -r 0.orig 0
setFields > log.setFields 2>&1
timeout --signal=TERM 3000 /work/bin/buoyantBoussinesqPimpleEHDFoam > log.run 2>&1
IN
REL=${CASE#$ROOT/}
exec python3 "$OUT/tools-0565489/scripts/run_with_manifest.py" --manifest "$CASE/run-manifest.json" --case "$CASE" \
  --log "$CASE/log.run" --label "fan thermal EHD-off conduction control ($NAME)" -- \
  docker run --rm --pull=never --name "fan-grokbot-$NAME" --network none --cpus 2 --memory 4g \
  --memory-swap 4g --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 256 --user 0:0 \
  --mount "type=bind,src=$ROOT,dst=/work" --entrypoint /bin/bash "$IMAGE" "/work/$REL/inner.sh" "/work/$REL"
