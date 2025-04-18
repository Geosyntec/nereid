## Nereid CI & Coverage

https://github.com/Geosyntec/nereid/actions?query=workflow%3ATest+branch%3Amain

https://codecov.io/gh/Geosyntec/nereid

## Quick Start

First, ensure you are in the right directory by `cd`-ing into the top level directory of this repo, which contains many docker-compose files (i.e., one level up from this one).

On linux run
`$make develop`

This script will create a docker-compose.yml file that we can carry forward. This approach lets us define services, variables, connections and commands differently depending on if we are developing, deploying, testing, or just playing around. Right now we are in dev, so we are building a dev version of the stack.

Then we can get our containers up by running
`docker compose up -d`

Check that everything is ok by listing the containers:
`docker compose ps`

You should see four containers, `redis`, `celeryworker`, `nereid` and `nereid-tests` and look roughly exactly like this:

```
NAME                    IMAGE                 COMMAND                  SERVICE        CREATED          STATUS          PORTS
nereid-celeryworker-1   nereid-celeryworker   "bash /run-worker.sh"    celeryworker   22 minutes ago   Up 22 minutes
nereid-flower-1         nereid-flower         "celery flower"          flower         5 seconds ago    Up 4 seconds    0.0.0.0:5555->5555/tcp
nereid-nereid-1         nereid-nereid         "/start-reload.sh"       nereid         5 seconds ago    Up 4 seconds    0.0.0.0:80->80/tcp, 0.0.0.0:8080->80/tcp
nereid-nereid-tests-1   nereid-nereid-tests   "bash -c 'while true…"   nereid-tests   22 minutes ago   Up 22 minutes
nereid-redis-1          nereid-redis          "docker-entrypoint.s…"   redis          22 minutes ago   Up 22 minutes   6379/tcp
```

For example, you can run the tests with:
`docker-compose run  nereid-tests  bash /run-tests.sh`

or equivalently:
`docker-compose run  nereid-tests  pytest -v`

check coverage with:
`docker-compose run  nereid-tests  coverage run -m pytest`

then:
`docker-compose run  nereid-tests  coverage report -m`

**to run the service, use:**
`docker-compose run -d -p 8080:80 nereid bash /start.sh`

**and navigate to:**
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

### Requirements

**worker**

- -r requirements_base_unpinned.txt
- -r requirements_base_extras_unpinned.txt
- -r requirements_app_async_unpinned.txt

**nereid**

- -r requirements_worker_unpinned.txt
- -r requirements_app_unpinned.txt

**dev**

- -r requirements_nereid_unpinned.txt
- -r requirements_lint_unpinned.txt
- coverage
- httpx
- pytest
- pytest-cov
- pytest-xdist
- watchfiles

## Contact Info

Austin Orr
github username: austinorr
