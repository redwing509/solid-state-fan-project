# CPU image for fan-11 (no GPU code path exists for this solver/OpenFOAM version).
FROM openfoam/openfoam4-paraview50@sha256:a9cde0fffd6dee35f1d6fac0494d8595850aa8063005997a75c8430666f6c230
USER root
# git is only needed for the results push; Ubuntu 16.04 mirrors may have moved to old-releases
RUN (apt-get update || (sed -i -E 's#http://(archive|security).ubuntu.com#http://old-releases.ubuntu.com#g' /etc/apt/sources.list && apt-get update)) \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY . /bundle
RUN chmod +x /bundle/*.sh /bundle/*.py && mkdir -p /out
WORKDIR /bundle
ENTRYPOINT []
CMD ["bash", "/bundle/run.sh"]
