@ECHO off    
if /i "%1" == "" goto :help
if /i %1 == help goto :help
if /i %1 == clean goto :clean
if /i %1 == test goto :test
if /i %1 == develop goto :develop
if /i %1 == typecheck goto :typecheck
if /i %1 == coverage goto :coverage
if /i %1 == dev-server goto :dev-server
if /i %1 == restart goto :restart

:help
echo Commands:
echo   - clean       : removes caches and old test/coverage reports
echo   - test        : runs tests and integration tests in docker
echo   - develop     : builds/rebuilds the development containers
echo   - typecheck   : runs mypy typechecker
echo   - coverage    : calculates code coverage of tests within docker
echo   - dev-server  : starts a local development server with 'reload' and 'foreground' tasks
echo.
echo Usage:
echo $make [command]
goto :eof

:test
call make clean
call make restart
docker-compose exec nereid-tests pytest %2 %3 %4 %5 %6
goto :eof

:typecheck
mypy --config-file=nereid/mypy.ini nereid/nereid
goto :eof

:develop
call make clean
call scripts\build_dev.bat
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
docker-compose run -e NEREID_FORCE_FOREGROUND=1 -p 8080:80 nereid bash /start-reload.sh
goto :eof

:restart
docker-compose restart redis celeryworker
goto :eof
