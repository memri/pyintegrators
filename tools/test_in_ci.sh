#!/usr/bin/env bash

curl https://gitlab.memri.io/memri/pod/uploads/83961119f78969e6accdd0453f4dfbc2/pod-from-docker-v0.2.0-9-ga68dee2 -o pod_docker
./pod_docker & 
pid=$$
nbdev_test_nbs
kill $pid