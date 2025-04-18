#!/bin/bash

set -e
set -x

make init-test
docker compose exec nereid-tests pytest "$@"
