#!/usr/bin/env bash

set -e
set -x

mkdir -p .mypy_cache
mypy nereid/nereid --install-types --non-interactive
ruff format nereid --check --diff
ruff check nereid
