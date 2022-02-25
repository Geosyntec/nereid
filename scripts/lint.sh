#!/usr/bin/env bash

set -e
set -x

mypy nereid/nereid --install-types --non-interactive
black nereid --check --diff
isort nereid --check --diff 
