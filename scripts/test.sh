#!/bin/bash

set -e
set -x

make init-test
docker compose -f docker-stack.yml exec nereid-tests pytest "$@"
