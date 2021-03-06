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
if /i %1 == restart goto :restart
if /i %1 == lint goto :lint

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

:test
call make clean
call make restart
docker-compose exec nereid-tests pytest %2 %3 %4 %5 %6
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
docker-compose up -d
goto :eof

:down
docker-compose down -v
goto :eof

:coverage
call make clean
call make restart
docker-compose exec nereid-tests coverage run -m pytest -x
docker-compose exec nereid-tests coverage report -m
goto :eof

:clean
scripts\clean.bat
goto :eof

:dev-server
docker-compose run -p 8080:80 nereid bash /start-reload.sh
goto :eof

:restart
docker-compose restart redis celeryworker
goto :eof

:lint
bash scripts/lint.sh
goto :eof
