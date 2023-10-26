#! /usr/bin/env sh
set -e

prefix="prestart.sh script: "

echo "$prefix pre-start found"
python /nereid/nereid/startup.py start_nereid
echo "$prefix pre-start complete"
