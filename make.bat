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
if /i %1 == dev-server goto :dev-server

:help
echo Commands:
echo   - clean       : removes caches and old test/coverage reports
echo   - develop     : builds/rebuilds the development containers
echo   - up          : starts the requisite procceses in docker containers
echo   - test        : runs tests and integration tests in docker
echo   - typecheck   : runs mypy typechecker
echo   - coverage    : calculates code coverage of tests within docker
echo   - dev-server  : starts a local development server with 'reload' and 'foreground' tasks
echo   - down        : undoes the up command (shuts down the containers)
echo.
echo Usage:
echo $make [command]
goto :eof

:test
call make clean
docker-compose exec nereid-tests pytest -xvv
goto :eof

:typecheck
call make clean
mypy --config-file=nereid/mypy.ini nereid/nereid
goto :eof

:develop
call make clean
call scripts\build_dev.bat
goto :eof

:up
call make clean
docker-compose up -d
goto :eof

:down
call make clean
docker-compose down -v
goto :eof

:coverage
call make clean
docker-compose restart redis celeryworker
docker-compose exec nereid-tests coverage run -m pytest -x
docker-compose exec nereid-tests coverage report -m
goto :eof

:clean
scripts\clean.bat
goto :eof

:dev-server
docker-compose run -e NEREID_FORCE_FOREGROUND=1 -p 8080:80 nereid bash /start-reload.sh
goto :eof
