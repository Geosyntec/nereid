#!/usr/bin/env bash

set -e
set -x

mypy nereid/nereid
black nereid --check
isort nereid --check --diff 
