#! /usr/bin/env sh

set -e

# If there's a prestart.sh script, run it before starting
PRE_START_PATH=/prestart-worker.sh
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "There is no script $PRE_START_PATH"
fi

celery --app nereid.bg_worker worker -l INFO -O fair
