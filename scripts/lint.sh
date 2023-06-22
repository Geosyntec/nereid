#!/usr/bin/env bash

set -e
set -x

mkdir -p .mypy_cache
mypy nereid/nereid --install-types --non-interactive
black nereid --check --diff
isort nereid --check --diff
