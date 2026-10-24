#!/bin/bash
# Fixed launcher (2026-10-22, Grok Bot). Old /tmp/launch-rerun.sh was broken: inner script lived in host /tmp
# (not mounted in container), escaped $rc, and inner script rm -rf'd/re-meshed the case. Run ONCE; no auto-retry.
# ai-job holds the fan-research lock until the container (solver, foreground) exits; setsid+nohup survives ssh exit.
R=/opt/fan-research/2026-10-21; D=$R/queue/cases/legacy-91be60c7e7-rerun-active
setsid nohup ai-job --owner grokbot --resource fan-research --task 'legacy-91be60c7e7 thermal rerun from 6s' --ttl 600 -- \
  docker run --rm --pull=never --name fan-rerun-legacy-91be60c7e7 --network none --cpus 2 --memory 8g --memory-swap 8g \
  --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 256 --user 0:0 \
  --mount type=bind,src=$R,dst=/work --entrypoint /bin/bash openfoam/openfoam4-paraview50:4.1 \
  /work/queue/inner-rerun-fixed.sh > $D/launcher.log 2>&1 < /dev/null &
echo "launched ai-job wrapper pid $!"
