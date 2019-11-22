## Nereid CI & Coverage

https://travis-ci.org/Geosyntec/nereid

https://codecov.io/gh/Geosyntec/nereid


## Quick Start

First, ensure you are in the right directory by `cd`-ing into the top level directory of this repo, which contains many docker-compose files (i.e., one level up from this one).

On windows run
`>scripts\build_dev.bat`

On linux run
`$bash scripts/build_dev.sh`

This script will create a docker-stack.yml file that we can carry forward. This approach lets us define services, variables, connections and commands differently depending on if we are developing, deploying, testing, or just playing around. Right now we are in dev, so we are building a dev version of the stack.

Then we can get our containers up by running
`docker-compose -f docker-stack.yml up -d`

We aren't using a vanilla docker-compose.yml file for our build stack here, so for docker-compose to recognise the services by name, ensure that your bash or cmd environment includes:

```
COMPOSE_PATH_SEPARATOR=:
COMPOSE_FILE=docker-compose.shared.depends.yml:docker-compose.dev.ports.yml:docker-compose.dev.build.yml:docker-compose.dev.env.yml
```
With these enviroment variables set, you can control the stack without the `-f` jazz.

Check that everything is ok by listing the containers:
`docker-compose ps`

You should see four containers, `redis`, `celeryworker`, `nereid` and `nereid-tests` and look roughly exactly like this:
```
Name                           Command               State                Ports
    ---------------------------------------------------------------------------------------------------------
    nereid_celeryworker_1            bash /run-worker.sh              Up
    nereid_nereid-tests_1            bash -c while true; do sle ...   Up       8888/tcp
    nereid_nereid_1                  python3                          Exit 0
    nereid_nereid_run_db0cede0411e   bash /start.sh                   Up       0.0.0.0:8080->80/tcp, 8888/tcp
    nereid_redis_1                   docker-entrypoint.sh redis ...   Up       0.0.0.0:6379->6379/tcp
```

For example, you can run the tests with:
`docker-compose run  nereid-tests  bash /run-tests.sh`

or equivalently:
`docker-compose run  nereid-tests  pytest -v`

check coverage with:
`docker-compose run  nereid-tests  coverage run -m pytest`

then:
`docker-compose run  nereid-tests  coverage report -m`

__to run the service, use:__
`docker-compose run -d -p 8080:80 nereid bash /start.sh`

__and navigate to:__
http://localhost:8080/docs
or wherever you defined your host, port, and run command.

If something went wrong, try the above commands without the `-d` flag. This will log the running image to `stdout` so you can see what happened.

## Configuration for Development and Deployment
There is a lot of flexibility here while we develop the deployment pattern. I've prepped several environment variables to be easily configurable, but your mileage may vary. Please add issues to the repo with requests for other configuration variables and the `nereid` maintainer will address them.

### Build-Time Environment Variables
`CELERY_BROKER_URL=redis://guest@redis:6379/0`
`CELERY_RESULT_BACKEND=redis://guest@redis:6379/0`

### Run-Time Environment Variables
`HOST=${HOST:-0.0.0.0}`
`PORT=${PORT:-80}`
`BIND=${BIND:-"$HOST:$PORT"}`
`LOG_LEVEL=${LOG_LEVEL:-info}`

## Contact Info
Austin Orr 
github username: austinorr


