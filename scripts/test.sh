#!/bin/bash

set -e
set -x

docker compose -f docker-stack.yml exec nereid-tests pytest "$@"
