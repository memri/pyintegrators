#!/usr/bin/env bash
set -euETo pipefail

echo "Stopping container"
docker stop memri-pyintegrators || true
echo "starting container"
docker run --rm -d -it --init --name memri-pyintegrators memri-pyintegrators:latest
echo "running"
docker exec -it memri-pyintegrators sh -c 'apt-get update && apt-get install -y libsqlcipher-dev && apt-get install -y libgl1-mesa-glx && ./tools/test_in_ci.sh'

