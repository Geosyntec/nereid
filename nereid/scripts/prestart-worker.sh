#! /usr/bin/env sh
set -e

prefix="prestart-worker.sh script: "

echo "$prefix pre-start found"
python /nereid/nereid/startup.py start_worker
echo "$prefix pre-start complete"
