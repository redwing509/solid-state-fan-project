R=/opt/fan-research/2026-10-21; D=$R/queue/cases/legacy-air300-control
setsid nohup ai-job --owner grokbot --resource fan-research --task 'legacy-air300-control self-consistent 300K air' --ttl 600 -- \
  docker run --rm --pull=never --name fan-control-air300 --network none --cpus 2 --memory 8g --memory-swap 8g \
  --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 256 --user 0:0 \
  --mount type=bind,src=$R,dst=/work --entrypoint /bin/bash openfoam/openfoam4-paraview50:4.1 \
  /work/queue/inner-control-air300.sh > $D/launcher.log 2>&1 < /dev/null &
