#! /usr/bin/env sh

# ref: https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/master/python3.6/start.sh

set -e

MODULE_NAME=nereid.main
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

export GUNICORN_CONF=/gunicorn_conf.py

# If there's a prestart.sh script in the /nereid directory, run it before starting
PRE_START_PATH=/nereid/prestart.sh
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else 
    echo "There is no script $PRE_START_PATH"
fi

# Start Gunicorn
exec gunicorn -k uvicorn.workers.UvicornWorker -c "$GUNICORN_CONF" "$APP_MODULE"