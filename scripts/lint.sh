#!/usr/bin/env bash

set -e
set -x

mypy --config-file=nereid/mypy.ini nereid/nereid
black nereid --check
isort \
--multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as \
--line-width 88 --recursive --check-only --thirdparty orjson nereid/nereid
