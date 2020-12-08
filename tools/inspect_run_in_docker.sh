/usr/bin/env bash
set -euETo pipefail

# run bash to play around
exec docker run --rm -it --init --name memri-pyintegrators memri-pyintegrators:latest bash

