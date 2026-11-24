#!/bin/bash
# Known-solution mesh study for the GetDP unipolar formulation (t1244u).
# Run on a host with /opt/fan-tools/bin/{gmsh,getdp}. nice 19. PUSH=0.
set -euo pipefail
GMSH=${GMSH:-/opt/fan-tools/bin/gmsh}
GETDP=${GETDP:-/opt/fan-tools/bin/getdp}
ROOT=$(cd "$(dirname "$0")" && pwd)
FACTORS=${FACTORS:-"1 0.5 0.25"}
OUT=${OUT:-"$ROOT/results/verify"}
mkdir -p "$OUT"
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}

run_one() {
  local kind=$1 geo=$2 pro=$3 fac=$4
  local dest="$OUT/${kind}_f${fac}"
  mkdir -p "$dest"
  local tag
  tag=$(echo "$fac" | tr . p)
  dest="$OUT/${kind}_f${tag}"
  mkdir -p "$dest"
  echo "=== $kind lc_factor=$fac -> $dest ==="
  cp "$ROOT/$kind/$pro" "$dest/case.pro"
  # getdp Include path: unipolar.pro lives at ROOT
  ln -sfn "$ROOT/unipolar.pro" "$dest/unipolar.pro"
  # rewrite Include if the wrapper uses ../unipolar.pro
  if grep -q 'Include "../unipolar.pro"' "$dest/case.pro"; then
    sed -i 's|Include "../unipolar.pro"|Include "unipolar.pro"|' "$dest/case.pro"
  fi
  nice -n 19 "$GMSH" -2 -format msh2 -setnumber lc_factor "$fac" \
    "$ROOT/$kind/$geo" -o "$dest/case.msh" > "$dest/gmsh.log" 2>&1
  # node/element counts
  grep -E "nodes|elements|Mesh" "$dest/gmsh.log" | tail -20 > "$dest/mesh_info.txt" || true
  cd "$dest"
  nice -n 19 "$GETDP" case.pro -msh case.msh -solve Unipolar -pos Map \
    > getdp.log 2>&1 || nice -n 19 "$GETDP" case.pro -msh case.msh -solve Electrostatics -pos Map \
    > getdp.log 2>&1
  cd "$ROOT"
  echo "done $dest"
}

# A1 capacitor uses Electrostatics resolution (coaxial_cap.pro)
run_cap() {
  local fac=$1
  local tag; tag=$(echo "$fac" | tr . p)
  local dest="$OUT/cap_f${tag}"
  mkdir -p "$dest"
  echo "=== cap lc_factor=$fac -> $dest ==="
  cp "$ROOT/verify/coaxial_cap.pro" "$dest/case.pro"
  nice -n 19 "$GMSH" -2 -format msh2 -setnumber lc_factor "$fac" \
    "$ROOT/verify/coaxial_cap.geo" -o "$dest/case.msh" > "$dest/gmsh.log" 2>&1
  grep -E "nodes|elements|Mesh" "$dest/gmsh.log" | tail -20 > "$dest/mesh_info.txt" || true
  cd "$dest"
  nice -n 19 "$GETDP" case.pro -msh case.msh -solve Electrostatics -pos Map > getdp.log 2>&1
  cd "$ROOT"
  echo "done $dest"
}

run_uni() {
  local fac=$1
  local tag; tag=$(echo "$fac" | tr . p)
  local dest="$OUT/uni_f${tag}"
  mkdir -p "$dest"
  echo "=== uni lc_factor=$fac -> $dest ==="
  cp "$ROOT/verify/coaxial_unipolar.pro" "$dest/case.pro"
  sed -i 's|Include "../unipolar.pro"|Include "unipolar.pro"|' "$dest/case.pro"
  # h = inner mesh size for this factor (lc_in = 8e-5 * factor).
  # Replace the existing assignment; do not insert a second h_mesh line.
  python3 -c "import pathlib,re; p=pathlib.Path('$dest/case.pro'); t=p.read_text(); f=float('$fac'); t=re.sub(r'^h_mesh = .*', 'h_mesh = %.6e;'%(8e-5*f), t, count=1, flags=re.M); p.write_text(t)"
  ln -sfn "$ROOT/unipolar.pro" "$dest/unipolar.pro"
  nice -n 19 "$GMSH" -2 -format msh2 -setnumber lc_factor "$fac" \
    "$ROOT/verify/coaxial_unipolar.geo" -o "$dest/case.msh" > "$dest/gmsh.log" 2>&1
  grep -E "nodes|elements|Mesh" "$dest/gmsh.log" | tail -20 > "$dest/mesh_info.txt" || true
  cd "$dest"
  # The monitor appends one line per step; never mix two runs in one file.
  rm -f monitor_Q.dat monitor_I.dat
  nice -n 19 "$GETDP" case.pro -msh case.msh -solve Unipolar -pos Map > getdp.log 2>&1
  cd "$ROOT"
  echo "done $dest"
}

if [[ "${UNI_ONLY:-0}" != 1 ]]; then
  for f in $FACTORS; do
    run_cap "$f"
  done
fi
for f in $FACTORS; do
  run_uni "$f"
done
echo "VERIFY_DONE $OUT"
