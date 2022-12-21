@ECHO off    
if /i "%1" == "" goto :help
if /i %1 == help goto :help
if /i %1 == clean goto :clean
if /i %1 == test goto :test
if /i %1 == develop goto :develop
if /i %1 == up goto :up
if /i %1 == down goto :down
if /i %1 == typecheck goto :typecheck
if /i %1 == coverage goto :coverage
if /i %1 == coverage-sync goto :coverage-sync
if /i %1 == coverage-async goto :coverage-async
if /i %1 == coverage-all goto :coverage-all
if /i %1 == cover-src goto :cover-src
if /i %1 == dev-server goto :dev-server
if /i %1 == restart goto :restart
if /i %1 == lint goto :lint
if /i %1 == login goto :login

:help
echo Commands:
echo   - clean       : removes caches and old test/coverage reports
echo   - test        : runs tests and integration tests in docker
echo   - develop     : builds/rebuilds the development containers
echo   - up          : starts containers in '-d' mode
echo   - down        : stops containers and dismounts volumes
echo   - typecheck   : runs mypy typechecker
echo   - coverage    : calculates code coverage of tests within docker
echo   - dev-server  : starts a local development server with 'reload' and 'foreground' tasks
echo   - restart     : restarts worker and broker processes
echo.
echo Usage:
echo $make [command]
goto :eof

set COMPOSE_DOCKER_CLI_BUILD=1

:login
bash scripts/az-login.sh
goto :eof

:test
call make clean
call make restart
for /f "tokens=1,* delims= " %%a in ("%*") do set ALL_BUT_FIRST=%%b
docker compose exec nereid-tests pytest %ALL_BUT_FIRST%
goto :eof

:typecheck
call make clean
call make restart
mypy --config-file=nereid/mypy.ini nereid/nereid
goto :eof

:develop
call make clean
call scripts\build_dev.bat
goto :eof

:up
docker compose up -d
goto :eof

:down
docker compose down -v
goto :eof

:coverage
call make clean
call make restart
docker compose exec nereid-tests coverage run --branch -m pytest nereid/tests -xs
docker compose exec nereid-tests coverage report -m
goto :eof

:coverage-sync
call make clean
call make restart
docker compose exec nereid-tests coverage run --branch -m pytest nereid/tests -xs
docker compose exec nereid-tests coverage report -m --omit=*test*,*bg_*,*celery_*
goto :eof

:coverage-async
call make clean
call make restart
docker compose exec nereid-tests coverage run --branch -m pytest nereid/tests -xs --async
docker compose exec nereid-tests coverage report -m --omit=*test*,*_sync*
goto :eof

:coverage-all
call make clean
call make restart
docker compose exec nereid-tests pytest nereid/tests -xs --dist loadfile -n 4 --cov=nereid/
docker compose exec nereid-tests pytest nereid/tests/test_api -xs --dist loadfile -n 4 --cov=nereid/ --cov-append --async
docker compose exec nereid-tests coverage report -m
goto :eof

:cover-src
call make clean
call make restart
docker compose exec nereid-tests coverage run --source=nereid/src --branch -m pytest nereid/tests/test_src -xv
docker compose exec nereid-tests coverage report -m --omit=*test*
goto :eof

:clean
scripts\clean.bat
goto :eof

:dev-server
docker compose run -p 8080:80 nereid bash /start-reload.sh
goto :eof

:restart
docker compose restart redis celeryworker
goto :eof

:lint
bash scripts/lint.sh
goto :eof

rem docker build --target nereid_install -t nereid_install -f nereid/Dockerfile.multi .
rem docker run -it -v %cd%:/nereid -p 8088:80 --expose 80 nereid_install bash
rem pip install -e .[app]
rem uvicorn nereid.main:app --port 80 --host 0.0.0.0 --reload
