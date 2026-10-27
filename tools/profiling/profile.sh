#!/usr/bin/env bash
# Profile any Python command with py-spy (sampling flamegraph) and scalene
# (CPU + memory, line level). Runs locally; nothing is uploaded anywhere.
#
#   tools/profiling/profile.sh [-o OUTDIR] [-t pyspy|scalene|both] -- python -m thermal1d verify
#
# Install once (free, pip only):  pip install py-spy scalene
# Output: OUTDIR/pyspy.svg, pyspy.speedscope.json, scalene.json, scalene.txt, scalene-profile.html
# Keep heavy runs off shared research machines unless the owner approved the compute.
set -euo pipefail
out="profile-$(date +%Y%m%d-%H%M%S)"; tool=both
while [ $# -gt 0 ]; do
  case "$1" in
    -o) out="$2"; shift 2;;
    -t) tool="$2"; shift 2;;
    --) shift; break;;
    -h|--help) sed -n 2,9p "$0"; exit 0;;
    *) break;;
  esac
done
[ $# -gt 0 ] || { echo "usage: $0 [-o OUTDIR] [-t pyspy|scalene|both] -- python ARGS..." >&2; exit 2; }
[ "$1" = python ] || [ "$1" = python3 ] || { echo "command must start with python/python3" >&2; exit 2; }
shift  # drop the interpreter; both profilers launch the current python themselves
mkdir -p "$out"
py=$(command -v python3 || command -v python)
rc=0
if [ "$tool" = pyspy ] || [ "$tool" = both ]; then
  if command -v py-spy >/dev/null; then
    py-spy record --rate 200 --subprocesses -o "$out/pyspy.svg" -- "$py" "$@" || rc=$?
    py-spy record --rate 200 --subprocesses -f speedscope -o "$out/pyspy.speedscope.json" -- "$py" "$@" || rc=$?
  else echo "py-spy not installed (pip install py-spy); skipping" >&2; fi
fi
if [ "$tool" = scalene ] || [ "$tool" = both ]; then
  if command -v scalene >/dev/null; then
    # scalene 2.x profiles a script; wrap "-m module" invocations with runpy.
    target=("$@")
    if [ "$1" = -m ]; then
      wrap="$out/_scalene_module_wrapper.py"
      printf 'import runpy, sys\nsys.argv = [%s] + sys.argv[1:]\nrunpy.run_module(%s, run_name="__main__", alter_sys=True)\n' "'$2'" "'$2'" > "$wrap"
      target=("$wrap" --- "${@:3}")
    elif [ $# -gt 1 ]; then
      target=("$1" --- "${@:2}")
    fi
    scalene run -o "$out/scalene.json" "${target[@]}" || rc=$?
    if [ -s "$out/scalene.json" ]; then
      scalene view --cli -r "$out/scalene.json" > "$out/scalene.txt" 2>&1 || true
      (cd "$out" && scalene view --standalone scalene.json >/dev/null 2>&1) || true
    fi
  else echo "scalene not installed (pip install scalene); skipping" >&2; fi
fi
echo "profiles in $out"; ls -l "$out"
exit $rc
