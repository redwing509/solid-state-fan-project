#!/bin/bash
# fan-11-ehd-convergence: mesh + time-step convergence of the legacy EHD heated-plate benchmark
# (buoyantBoussinesqPimpleEHDFoam, OpenFOAM Foundation 4.1, pinned solver commit cfd66422).
# Runs entirely on CPU. Env knobs:
#   NPROC (default nproc)  CASES (default "M1 M2 M4 M2-Co1 M2-Co05")  ENDTIME (default 10)
#   OUT (default /out)     PUSH (1 = push results via GH_TOKEN; default 1 if GH_TOKEN set)
#   RESULTS_REPO (default redwing509/solid-state-fan-project)  SMOKE (1 = 20 time steps only)
set -o pipefail
B=$(cd "$(dirname "$0")" && pwd)
. /opt/openfoam4/etc/bashrc || true

NPROC=${NPROC:-$(nproc)}; ENDTIME=${ENDTIME:-10}; OUT=${OUT:-/out}; SMOKE=${SMOKE:-0}
CASES=${CASES:-"M1 M2 M4 M2-Co1 M2-Co05"}
RUN_ID=${RUN_ID:-fan11-$(date -u +%Y%m%dT%H%MZ)}
RESULTS_REPO=${RESULTS_REPO:-redwing509/solid-state-fan-project}
mkdir -p "$OUT/$RUN_ID/cases"; R="$OUT/$RUN_ID"; LOG="$R/finish.log"
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
log "start run_id=$RUN_ID nproc=$NPROC cases='$CASES' endTime=$ENDTIME smoke=$SMOKE host=$(hostname)"
{ nproc; free -g; lscpu | grep -E 'Model name|^CPU\(s\)'; nvidia-smi -L 2>/dev/null || echo "no GPU visible (not needed)"; } > "$R/hardware.txt" 2>&1

# 1. build the pinned solver (GPL, upstream https://github.com/nzhtbyn/buoyantBoussinesqPimpleEHDFoam @ cfd66422)
export FOAM_USER_APPBIN="$R/build/bin"; mkdir -p "$R/build/bin"; cp -a "$B/inputs/buoyantBoussinesqPimpleEHDFoam" "$R/build/src"
sed -i 's|\$(FOAM_APPBIN)|$(FOAM_USER_APPBIN)|' "$R/build/src/Make/files"
( cd "$R/build/src" && wmake ) > "$R/build/build.log" 2>&1 || { log "BUILD FAILED (see build/build.log)"; exit 10; }
export PATH="$FOAM_USER_APPBIN:$PATH"
SOLVER=$(command -v buoyantBoussinesqPimpleEHDFoam) || { log "solver missing after build"; exit 11; }
sha256sum "$SOLVER" > "$R/build/solver.sha256"; log "solver built $(cut -c1-16 "$R/build/solver.sha256")"

# case table: name refine maxCo ranks
spec() { case "$1" in
  M1) echo "1 2 1";;  M2) echo "2 2 4";;  M4) echo "4 2 8";;
  M2-Co1) echo "2 1 4";;  M2-Co05) echo "2 0.5 4";;  M8) echo "8 2 16";;
  *) echo "";; esac; }

run_case() {   # name refine maxCo np
  local n=$1 r=$2 co=$3 np=$4 d="$R/cases/$1" t0 rc
  cp -a "$B/inputs/validationCase" "$d"; cd "$d" || return 20
  python3 "$B/refine_blockmesh.py" system/blockMeshDict "$r" > log.refine 2>&1 || return 21
  sed -i -E "s/^maxCo .*/maxCo           $co;/; s/^endTime .*/endTime         $ENDTIME;/" system/controlDict
  cat > system/decomposeParDict <<EOD
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $np;
method scotch;
EOD
  blockMesh > log.blockMesh 2>&1 || return 22
  checkMesh > log.checkMesh 2>&1
  rm -rf 0; cp -r 0.orig 0; setFields > log.setFields 2>&1 || return 23
  echo "cells $(grep -m1 'cells:' log.checkMesh | awk '{print $2}') refine $r maxCo $co np $np" > run.status
  t0=$(date +%s)
  if [ "$SMOKE" = 1 ]; then  # smoke: 20 fixed steps of 1e-5 s, writes once at the end
    sed -i -E "s/^endTime .*/endTime         0.0002;/; s/^adjustTimeStep .*/adjustTimeStep  no;/; s/^writeInterval .*/writeInterval   0.0002;/" system/controlDict
  fi
  if [ "$np" -gt 1 ]; then
    decomposePar -force > log.decomposePar 2>&1 || return 24
    mpirun --allow-run-as-root --oversubscribe -np "$np" buoyantBoussinesqPimpleEHDFoam -parallel > log.solver 2>&1; rc=$?
    [ $rc = 0 ] && { reconstructPar -latestTime > log.reconstructPar 2>&1 || rc=25; }
    [ $rc = 0 ] && rm -rf processor*
  else
    buoyantBoussinesqPimpleEHDFoam > log.solver 2>&1; rc=$?
  fi
  echo "runtime_s $(( $(date +%s) - t0 )) rc $rc last '$(grep '^Time =' log.solver | tail -1)'" >> run.status
  postProcess -latestTime -func "patchAverage(name=down,T,operation=areaAverage)" > log.patchAverage 2>&1
  postProcess -latestTime -func "patchAverage(name=hole,elecPot)" > log.patchAverageHole 2>&1
  return $rc
}

# 2. rank-budget scheduler: launch a case when enough ranks are free (cases are independent)
declare -A PID NP; free=$NPROC
for c in $CASES; do
  s=$(spec "$c"); [ -n "$s" ] || { log "unknown case $c"; continue; }
  set -- $s; np=$3; [ "$np" -gt "$NPROC" ] && np=$NPROC
  while [ "$free" -lt "$np" ]; do
    wait -n 2>/dev/null
    for k in "${!PID[@]}"; do kill -0 "${PID[$k]}" 2>/dev/null || { wait "${PID[$k]}"; log "$k finished rc=$? $(tail -1 "$R/cases/$k/run.status" 2>/dev/null)"; free=$((free+NP[$k])); unset "PID[$k]"; }; done
  done
  log "launch $c refine=$1 maxCo=$2 np=$np"; ( run_case "$c" "$1" "$2" "$np" ) & PID[$c]=$!; NP[$c]=$np; free=$((free-np))
done
for k in "${!PID[@]}"; do wait "${PID[$k]}"; log "$k finished rc=$? $(tail -1 "$R/cases/$k/run.status" 2>/dev/null)"; done

# 3. post-process + convergence verdicts (pre-registered in ACCEPTANCE_CRITERIA.md)
python3 "$B/post_fan11.py" "$R" > "$R/post.log" 2>&1 || log "post_fan11.py failed (see post.log)"
log "post done: $(tail -1 "$R/post.log")"

# 4. package small outputs (fields at final time for each case + logs); raw meshes not pushed
P="$R/push"; mkdir -p "$P"
cp "$LOG" "$R/hardware.txt" "$R/build/solver.sha256" "$R/build/build.log" "$P/" 2>/dev/null
cp "$R"/summary.json "$R"/summary.md "$P/" 2>/dev/null
for d in "$R"/cases/*/; do n=$(basename "$d"); mkdir -p "$P/cases/$n"
  cp "$d"/run.status "$d"/log.checkMesh "$d"/log.patchAverage* "$P/cases/$n/" 2>/dev/null
  tail -n 400 "$d/log.solver" > "$P/cases/$n/log.solver.tail" 2>/dev/null
  lt=$(cd "$d" && ls -d [0-9]* 2>/dev/null | grep -vx 0 | sort -g | tail -1)
  [ -n "$lt" ] && tar czf "$P/cases/$n/final_fields.tgz" -C "$d" "$lt" constant/polyMesh 2>/dev/null
done
du -sh "$P" | tee -a "$LOG"
if [ "${PUSH:-$([ -n "${GH_TOKEN:-}" ] && echo 1 || echo 0)}" = 1 ]; then
  bash "$B/push_results.sh" "$RESULTS_REPO" "hf-results/$RUN_ID" "$P" "results/hf/$RUN_ID" \
    "fan-11 EHD convergence results ($RUN_ID) from HF job - unreviewed, needs 2-engine peer review" 2>&1 | tee -a "$LOG"
else log "PUSH disabled; results stay in $P"; fi
log "done"
