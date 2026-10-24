#!/bin/bash
# Run the corrected legacy thermal baseline (Pr 0.6125, gradient 9350 K/m, 'up' fixed at 300 K)
# on mail under the fan queue worker's container limits, wrapped by run_with_manifest.py.
# Launch:  nohup ai-job --owner grokbot --resource fan-research --ttl 70 --wait -- \
#            bash run_thermal_corrected_baseline.sh <name> > <log> 2>&1 &
# Never overwrites: refuses if the case directory exists.
set -euo pipefail
ROOT=/opt/fan-research/2026-10-21
OUT=$ROOT/thermal-fix-20261024
NAME=${1:-corrected-baseline}
CASE=$OUT/$NAME
HERE=$(cd "$(dirname "$0")" && pwd)
OVERLAY=$HERE/../benchmark/legacy-thermal-corrected-2026-10-24
IMAGE='openfoam/openfoam4-paraview50@sha256:a9cde0fffd6dee35f1d6fac0494d8595850aa8063005997a75c8430666f6c230'
mkdir -p "$OUT"
[ ! -e "$CASE" ] || { echo "refusing to overwrite $CASE"; exit 2; }

# Build the case with the queue worker's own prepare() so inputs match the queue exactly
# (same job as queue consistent_Pr_ambient / legacy-8266a66833, new id).
python3 - "$CASE" <<'PY'
import sys, json
from pathlib import Path
sys.path.insert(0, '/opt/fan-research/2026-10-21/queue')
import fan_queue_worker as w
job = {"family": "legacy", "label": "corrected_baseline_Pr0.6125_up300", "voltage_v": 7540,
       "mobility": 0.00023, "injection": 0.0001743, "Pr": 0.6125, "gradient": 9350,
       "ambient_fixed": True, "maxCo": 2, "timeout_s": 3600,
       "classification": "THERMAL_AND_BOUNDARY_CONTROL_NOT_EXPERIMENTALLY_VALIDATED",
       "supply_mapping_status": "UNAVAILABLE_NO_CONVERTER_MODEL",
       "id": "thermalfix-" + Path(sys.argv[1]).name}
w.validate(job)
w.prepare(job, Path(sys.argv[1]))
PY

# Check the prepared inputs carry the committed overlay values (comments ignored).
strip() { sed -e 's://.*$::' -e 's/[[:space:]]\+/ /g' -e 's/^ //' -e 's/ $//' "$1" | grep -v '^$'; }
for f in constant/transportProperties 0.orig/T; do
  diff <(strip "$OVERLAY/$f") <(strip "$CASE/$f") || { echo "prepared $f differs from overlay"; exit 4; }
done

cat > "$CASE/inner.sh" <<'IN'
. /opt/openfoam4/etc/bashrc
set -e
cd "$1"
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1
cp -r 0.orig 0
setFields > log.setFields 2>&1
timeout --signal=TERM 3600 /work/bin/buoyantBoussinesqPimpleEHDFoam > log.run 2>&1
IN

REL=${CASE#$ROOT/}
exec python3 "$HERE/run_with_manifest.py" --manifest "$CASE/run-manifest.json" --case "$CASE" \
  --log "$CASE/log.run" --label "fan thermal corrected baseline ($NAME)" -- \
  docker run --rm --pull=never --name "fan-grokbot-$NAME" --network none --cpus 2 --memory 4g \
  --memory-swap 4g --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 256 --user 0:0 \
  --mount "type=bind,src=$ROOT,dst=/work" --entrypoint /bin/bash "$IMAGE" "/work/$REL/inner.sh" "/work/$REL"
