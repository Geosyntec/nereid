MAKEFLAGS += --silent
.PHONY: clean clean-test clean-pyc clean-build restart test develop up down dev-server help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

export COMPOSE_FILE=docker-stack.yml

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
## don't remove pycache dirs for docker mount volume compat
# find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -fr .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .mypy_cache

restart: ## restart the redis server and the background workers
	docker-compose restart redis celeryworker

test: clean restart ## run tests quickly with the default Python
	docker-compose exec nereid-tests pytest -n 4
	docker compose exec nereid-tests pytest nereid/tests/test_api -n 4 --async

coverage: clean restart ## check code coverage quickly with the default Python
	docker-compose exec nereid-tests coverage run -m pytest
	docker-compose exec nereid-tests coverage report -m
# 	coverage html
# 	$(BROWSER) htmlcov/index.html

coverage-all: clean restart ## check complete code coverage
	docker compose exec nereid-tests pytest nereid/tests -n 4 --cov=nereid/
	docker compose exec nereid-tests pytest nereid/tests/test_api -n 4 --cov=nereid/ --cov-append --async
	docker compose exec nereid-tests coverage report -m

typecheck: clean ## run static type checker
	mypy --config-file=nereid/mypy.ini nereid/nereid

develop: clean ## build the development environment and launch containers in background
	bash scripts/build_dev.sh

up: ## bring up the containers in '-d' mode
	docker-compose up -d

down: ## bring down the containers and detach volumes
	docker-compose down -v

dev-server: ## start a development server that runs all tasks in foreground
	docker-compose run -e NEREID_FORCE_FOREGROUND=1 -p 8080:80 nereid bash /start-reload.sh

bump-deps:
	bash scripts/bump_deps.sh
