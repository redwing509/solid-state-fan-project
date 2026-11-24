#!/bin/bash
# Nov 1 wire-plate smoke (FACTORS=1) or mesh study. Mail Gmsh + GetDP, nice 19. PUSH=0.
set -euo pipefail
GMSH=${GMSH:-/opt/fan-tools/bin/gmsh}
GETDP=${GETDP:-/opt/fan-tools/bin/getdp}
ROOT=$(cd "$(dirname "$0")" && pwd)
SRC=${SRC:-smoke}          # smoke or study (same geo/pro today)
FACTORS=${FACTORS:-"1"}
OUT=${OUT:-"$ROOT/results/${SRC}"}
mkdir -p "$OUT"
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}

run_one() {
  local fac=$1
  local tag; tag=$(echo "$fac" | tr . p)
  local dest="$OUT/wp_f${tag}"
  mkdir -p "$dest"
  echo "=== wireplate lc_factor=$fac -> $dest $(date -Is) ==="
  ln -sfn "$ROOT/unipolar.pro" "$dest/unipolar.pro"
  # mesh
  nice -n 19 "$GMSH" -2 -format msh2 -setnumber lc_factor "$fac" \
    "$ROOT/${SRC}/wireplate.geo" -o "$dest/case.msh" > "$dest/gmsh.log" 2>&1
  grep -E "nodes|elements|Error|Warning" "$dest/gmsh.log" | tail -30 > "$dest/mesh_info.txt" || true
  cat "$dest/mesh_info.txt"
  # Laplace wrapper: no GmshRead
  cp "$ROOT/${SRC}/wireplate.pro" "$dest/laplace.pro"
  sed -i 's|Include "../unipolar.pro"|Include "unipolar.pro"|' "$dest/laplace.pro"
  python3 -c "import pathlib,re; p=pathlib.Path('$dest/laplace.pro'); t=p.read_text(); f=float('$fac'); t=re.sub(r'^h_mesh = .*', 'h_mesh = %.6e;'%(8e-6*f), t, count=1, flags=re.M); p.write_text(t)"
  cd "$dest"
  echo "--- Laplace pre-solve ---"
  rm -f v_init.pos   # never start from an older run's Laplace guess
  nice -n 19 "$GETDP" laplace.pro -msh case.msh -solve Laplace -pos LaplaceMap > laplace.log 2>&1
  [[ -f v_init.pos ]]
  # Coupled wrapper: Init from v_init.pos
  cp laplace.pro case.pro
  python3 -c "
from pathlib import Path
p=Path('case.pro')
t=p.read_text()
t=t.replace('use_v_init = 0;', 'use_v_init = 1;')
t=t.replace('Function { V_laplace[] = 0.; }',
            'Function {\n  GmshRead[\"v_init.pos\"];\n  V_laplace[] = ScalarField[XYZ[]]{1};\n}')
p.write_text(t)
print(p.read_text())
"
  echo "--- Unipolar solve ---"
  # The monitor appends one line per step; never mix two runs in one file.
  rm -f monitor_Q.dat monitor_I.dat
  # Never score a table left over from an earlier run in this directory.
  rm -f ctr_e.dat ctr_r.dat I_vol.dat Q_rho.dat I_emitter.dat I_collector.dat \
    v_probe.dat e_probe.dat r_probe.dat ./*_r0*.dat
  if [[ -f "$ROOT/${SRC}/contour.pro" ]]; then
    echo 'Include "contour.pro";' >> case.pro
    ln -sfn "$ROOT/${SRC}/contour.pro" contour.pro
  fi
  # GetDP 3.5.0 keeps only the last repeated -pos flag; pass both names after one -pos
  # so Map and Contour run in the same process on the final in-memory solution.
  # A second getdp -res case.res pass would post every saved Picard step (wrong I_contour).
  if [[ -f contour.pro ]]; then
    nice -n 19 "$GETDP" case.pro -msh case.msh -solve Unipolar -pos Map Contour > getdp.log 2>&1
  else
    nice -n 19 "$GETDP" case.pro -msh case.msh -solve Unipolar -pos Map > getdp.log 2>&1
  fi
  cd "$ROOT"
  echo "=== done $dest $(date -Is) ==="
  tail -5 "$dest/getdp.log"
  for f in I_vol.dat monitor_I.dat I_contour.dat I_emitter.dat I_collector.dat Q_rho.dat v_probe.dat r_probe.dat e_probe.dat v_laplace_probe.dat ctr_e.dat ctr_r.dat; do
    if [[ -f "$dest/$f" ]]; then echo "== $f =="; tail -2 "$dest/$f"; else echo "== $f MISSING =="; fi
  done
}

for f in $FACTORS; do
  run_one "$f"
done
echo "E01_DONE $OUT"
